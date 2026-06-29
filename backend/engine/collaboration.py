"""
Collaboration System
سیستم همکاری چند کاربره

این ماژول امکان کار تیمی روی پروژه‌ها را فراهم می‌کند
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel
from enum import Enum
import json
from pathlib import Path
import hashlib
import secrets


class UserRole(str, Enum):
    """نقش‌های کاربری"""
    OWNER = "owner"  # مالک - دسترسی کامل
    ADMIN = "admin"  # مدیر - تقریباً همه دسترسی‌ها
    EDITOR = "editor"  # ویرایشگر - می‌تواند training کند
    VIEWER = "viewer"  # بیننده - فقط مشاهده


class Permission(str, Enum):
    """مجوزها"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    TRAIN = "train"
    EXPORT = "export"
    MANAGE_USERS = "manage_users"


# نقش‌ها و مجوزهای آن‌ها
ROLE_PERMISSIONS = {
    UserRole.OWNER: [
        Permission.READ, Permission.WRITE, Permission.DELETE,
        Permission.TRAIN, Permission.EXPORT, Permission.MANAGE_USERS
    ],
    UserRole.ADMIN: [
        Permission.READ, Permission.WRITE, Permission.TRAIN,
        Permission.EXPORT, Permission.MANAGE_USERS
    ],
    UserRole.EDITOR: [
        Permission.READ, Permission.WRITE, Permission.TRAIN
    ],
    UserRole.VIEWER: [
        Permission.READ
    ]
}


class User(BaseModel):
    """کاربر"""
    user_id: str
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: str = datetime.now().isoformat()


class ProjectMember(BaseModel):
    """عضو پروژه"""
    user_id: str
    role: UserRole
    added_at: str = datetime.now().isoformat()
    added_by: str = ""


class Team(BaseModel):
    """تیم"""
    team_id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    members: List[str] = []  # user_ids
    created_at: str = datetime.now().isoformat()


class CollaborationManager:
    """
    مدیریت همکاری و تیم‌ها
    
    این کلاس امکانات زیر را فراهم می‌کند:
    - مدیریت کاربران
    - مدیریت تیم‌ها
    - کنترل دسترسی به پروژه‌ها
    - Sharing پروژه‌ها
    
    Example:
        collab = CollaborationManager('workspace/')
        
        # ایجاد کاربر
        user = collab.create_user('john', 'john@example.com')
        
        # ایجاد تیم
        team = collab.create_team('ML Team', user.user_id)
        
        # اضافه کردن عضو به پروژه
        collab.add_project_member(project_id, user.user_id, UserRole.EDITOR)
        
        # بررسی دسترسی
        if collab.has_permission(user_id, project_id, Permission.TRAIN):
            # انجام training
            pass
    """
    
    def __init__(self, workspace_dir: str = "workspace"):
        """
        مقداردهی اولیه
        
        Args:
            workspace_dir: پوشه workspace
        """
        self.workspace_dir = Path(workspace_dir)
        self.users_file = self.workspace_dir / "users.json"
        self.teams_file = self.workspace_dir / "teams.json"
        self.projects_file = self.workspace_dir / "projects_members.json"
        
        self.workspace_dir.mkdir(exist_ok=True)
        
        # بارگذاری داده‌ها
        self.users = self._load_users()
        self.teams = self._load_teams()
        self.project_members = self._load_project_members()
        
        print(f"✅ CollaborationManager initialized ({len(self.users)} users, {len(self.teams)} teams)")
    
    def _load_users(self) -> Dict[str, User]:
        """بارگذاری کاربران"""
        if self.users_file.exists():
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {uid: User(**u) for uid, u in data.items()}
        return {}
    
    def _save_users(self):
        """ذخیره کاربران"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            data = {uid: u.dict() for uid, u in self.users.items()}
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_teams(self) -> Dict[str, Team]:
        """بارگذاری تیم‌ها"""
        if self.teams_file.exists():
            with open(self.teams_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {tid: Team(**t) for tid, t in data.items()}
        return {}
    
    def _save_teams(self):
        """ذخیره تیم‌ها"""
        with open(self.teams_file, 'w', encoding='utf-8') as f:
            data = {tid: t.dict() for tid, t in self.teams.items()}
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_project_members(self) -> Dict[str, Dict[str, ProjectMember]]:
        """بارگذاری اعضای پروژه‌ها"""
        if self.projects_file.exists():
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    pid: {uid: ProjectMember(**m) for uid, m in members.items()}
                    for pid, members in data.items()
                }
        return {}
    
    def _save_project_members(self):
        """ذخیره اعضای پروژه‌ها"""
        with open(self.projects_file, 'w', encoding='utf-8') as f:
            data = {
                pid: {uid: m.dict() for uid, m in members.items()}
                for pid, members in self.project_members.items()
            }
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_user(
        self,
        username: str,
        email: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        ایجاد کاربر جدید
        
        Args:
            username: نام کاربری
            email: ایمیل
            full_name: نام کامل
            
        Returns:
            User object
        """
        # ایجاد user_id یکتا
        user_id = hashlib.sha256(f"{username}:{email}".encode()).hexdigest()[:16]
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            full_name=full_name
        )
        
        self.users[user_id] = user
        self._save_users()
        
        print(f"✅ User created: {username} ({user_id})")
        
        return user
    
    def create_team(
        self,
        name: str,
        owner_id: str,
        description: Optional[str] = None
    ) -> Team:
        """
        ایجاد تیم جدید
        
        Args:
            name: نام تیم
            owner_id: شناسه مالک
            description: توضیحات
            
        Returns:
            Team object
        """
        team_id = secrets.token_urlsafe(12)
        
        team = Team(
            team_id=team_id,
            name=name,
            description=description,
            owner_id=owner_id,
            members=[owner_id]
        )
        
        self.teams[team_id] = team
        self._save_teams()
        
        print(f"✅ Team created: {name} ({team_id})")
        
        return team
    
    def add_team_member(self, team_id: str, user_id: str) -> bool:
        """
        اضافه کردن عضو به تیم
        
        Args:
            team_id: شناسه تیم
            user_id: شناسه کاربر
            
        Returns:
            True اگر موفق بود
        """
        if team_id not in self.teams:
            print(f"❌ Team not found: {team_id}")
            return False
        
        if user_id not in self.users:
            print(f"❌ User not found: {user_id}")
            return False
        
        team = self.teams[team_id]
        if user_id not in team.members:
            team.members.append(user_id)
            self._save_teams()
            print(f"✅ User {user_id} added to team {team.name}")
            return True
        
        print(f"ℹ️ User already in team")
        return False
    
    def add_project_member(
        self,
        project_id: str,
        user_id: str,
        role: UserRole,
        added_by: str = "system"
    ) -> bool:
        """
        اضافه کردن عضو به پروژه
        
        Args:
            project_id: شناسه پروژه
            user_id: شناسه کاربر
            role: نقش کاربر
            added_by: توسط چه کسی اضافه شد
            
        Returns:
            True اگر موفق بود
        """
        if user_id not in self.users:
            print(f"❌ User not found: {user_id}")
            return False
        
        if project_id not in self.project_members:
            self.project_members[project_id] = {}
        
        member = ProjectMember(
            user_id=user_id,
            role=role,
            added_by=added_by
        )
        
        self.project_members[project_id][user_id] = member
        self._save_project_members()
        
        print(f"✅ User {user_id} added to project {project_id} as {role.value}")
        
        return True
    
    def remove_project_member(self, project_id: str, user_id: str) -> bool:
        """حذف عضو از پروژه"""
        if project_id in self.project_members:
            if user_id in self.project_members[project_id]:
                del self.project_members[project_id][user_id]
                self._save_project_members()
                print(f"✅ User {user_id} removed from project {project_id}")
                return True
        
        print(f"❌ Member not found")
        return False
    
    def get_user_role(self, user_id: str, project_id: str) -> Optional[UserRole]:
        """
        دریافت نقش کاربر در پروژه
        
        Args:
            user_id: شناسه کاربر
            project_id: شناسه پروژه
            
        Returns:
            UserRole یا None
        """
        if project_id in self.project_members:
            if user_id in self.project_members[project_id]:
                return self.project_members[project_id][user_id].role
        
        return None
    
    def has_permission(
        self,
        user_id: str,
        project_id: str,
        permission: Permission
    ) -> bool:
        """
        بررسی دسترسی کاربر
        
        این تابع چک می‌کند که آیا کاربر دسترسی مورد نظر را دارد یا خیر
        
        Args:
            user_id: شناسه کاربر
            project_id: شناسه پروژه
            permission: مجوز مورد نیاز
            
        Returns:
            True اگر دسترسی داشته باشد
            
        Example:
            if collab.has_permission(user_id, project_id, Permission.TRAIN):
                # کاربر می‌تواند training کند
                start_training()
        """
        role = self.get_user_role(user_id, project_id)
        
        if role is None:
            return False
        
        return permission in ROLE_PERMISSIONS[role]
    
    def get_project_members(self, project_id: str) -> List[Dict]:
        """
        دریافت لیست اعضای پروژه
        
        Args:
            project_id: شناسه پروژه
            
        Returns:
            لیست اعضا با اطلاعاتشان
        """
        if project_id not in self.project_members:
            return []
        
        members = []
        for user_id, member in self.project_members[project_id].items():
            if user_id in self.users:
                user = self.users[user_id]
                members.append({
                    "user_id": user_id,
                    "username": user.username,
                    "email": user.email,
                    "role": member.role.value,
                    "added_at": member.added_at
                })
        
        return members
    
    def get_user_projects(self, user_id: str) -> List[str]:
        """
        دریافت پروژه‌هایی که کاربر در آن‌ها عضو است
        
        Args:
            user_id: شناسه کاربر
            
        Returns:
            لیست project_ids
        """
        projects = []
        for project_id, members in self.project_members.items():
            if user_id in members:
                projects.append(project_id)
        
        return projects
    
    def share_project_with_team(
        self,
        project_id: str,
        team_id: str,
        role: UserRole
    ) -> int:
        """
        اشتراک‌گذاری پروژه با یک تیم
        
        تمام اعضای تیم به پروژه با نقش مشخص اضافه می‌شوند
        
        Args:
            project_id: شناسه پروژه
            team_id: شناسه تیم
            role: نقش اعضا
            
        Returns:
            تعداد اعضای اضافه شده
        """
        if team_id not in self.teams:
            print(f"❌ Team not found: {team_id}")
            return 0
        
        team = self.teams[team_id]
        count = 0
        
        for user_id in team.members:
            if self.add_project_member(project_id, user_id, role):
                count += 1
        
        print(f"✅ Project shared with team {team.name}: {count} members added")
        
        return count

