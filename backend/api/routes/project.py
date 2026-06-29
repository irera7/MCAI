"""
Project management API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import json
import uuid
import shutil

from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Pydantic models for request/response
class ProjectCreate(BaseModel):
    """Project creation request"""
    name: str
    modality: str  # image, text, audio, video, tabular, timeseries, medical, genomic
    description: Optional[str] = ""

class ProjectInfo(BaseModel):
    """Project information response"""
    id: str
    name: str
    modality: str
    description: str
    model_type: Optional[str] = None
    created_at: str
    updated_at: str
    status: str  # new, data_imported, configured, training, trained, exported
    data: Optional[dict] = None
    training: Optional[dict] = None
    metrics: Optional[dict] = None
    
    # Training status fields (populated dynamically)
    training_status: Optional[str] = None  # training, completed, not_started
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    training_progress: Optional[int] = None  # percentage 0-100
    train_loss: Optional[float] = None
    train_accuracy: Optional[float] = None

class ProjectUpdate(BaseModel):
    """Project update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = None
    status: Optional[str] = None
    data: Optional[dict] = None
    training: Optional[dict] = None
    metrics: Optional[dict] = None

@router.post("/create", response_model=ProjectInfo, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    """
    Create a new project
    
    Args:
        project: Project creation parameters
        
    Returns:
        Created project information
    """
    try:
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        project_dir = settings.PROJECTS_DIR / project_id
        
        # Create project directory structure
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "data").mkdir(exist_ok=True)
        (project_dir / "models").mkdir(exist_ok=True)
        (project_dir / "logs").mkdir(exist_ok=True)
        (project_dir / "exports").mkdir(exist_ok=True)
        
        # Create project metadata
        now = datetime.now().isoformat()
        project_data = {
            "id": project_id,
            "name": project.name,
            "modality": project.modality,
            "description": project.description,
            "model_type": None,
            "created_at": now,
            "updated_at": now,
            "status": "new",
            "data": {
                "path": "./data",
                "num_classes": 0,
                "class_labels": [],
                "train_size": 0,
                "val_size": 0,
                "test_size": 0
            },
            "training": {
                "epochs": 50,
                "batch_size": 32,
                "learning_rate": 0.001,
                "optimizer": "adam",
                "device": "cuda",
                "use_augmentation": True,
                "dropout": 0.2,
                "weight_decay": 0.0001
            },
            "model_path": None,
            "metrics": {}
        }
        
        # Save project file
        project_file = project_dir / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created project: {project_id} - {project.name}")
        
        return ProjectInfo(**project_data)
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/load/{project_id}", response_model=ProjectInfo)
async def load_project(project_id: str):
    """
    Load an existing project
    
    Args:
        project_id: Project identifier
        
    Returns:
        Project information
    """
    try:
        project_file = settings.PROJECTS_DIR / project_id / "project.json"
        
        if not project_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        logger.info(f"Loaded project: {project_id}")
        
        return ProjectInfo(**project_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load project: {str(e)}"
        )

@router.post("/save/{project_id}")
async def save_project(project_id: str, updates: ProjectUpdate):
    """
    Save project updates
    
    Args:
        project_id: Project identifier
        updates: Project updates
        
    Returns:
        Success message
    """
    try:
        project_file = settings.PROJECTS_DIR / project_id / "project.json"
        
        if not project_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        # Load existing project
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Update fields
        update_dict = updates.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                if key in ['data', 'training', 'metrics'] and isinstance(value, dict):
                    # Merge nested dictionaries
                    project_data[key].update(value)
                else:
                    project_data[key] = value
        
        # Update timestamp
        project_data["updated_at"] = datetime.now().isoformat()
        
        # Save updated project
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved project: {project_id}")
        
        return {"message": "Project saved successfully", "project_id": project_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save project: {str(e)}"
        )

@router.delete("/delete/{project_id}")
async def delete_project(project_id: str):
    """
    Delete a project
    
    Args:
        project_id: Project identifier
        
    Returns:
        Success message
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        # Delete project directory
        shutil.rmtree(project_dir)
        
        logger.info(f"Deleted project: {project_id}")
        
        return {"message": "Project deleted successfully", "project_id": project_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )

@router.get("/list")
async def list_projects():
    """
    List all projects with live training status
    
    Returns:
        Dict with projects list and total count
    """
    try:
        from .training import active_trainings  # Import to check training status
        
        projects = []
        
        if not settings.PROJECTS_DIR.exists():
            return {"projects": [], "total": 0}
        
        # Iterate through project directories
        for project_dir in settings.PROJECTS_DIR.iterdir():
            if project_dir.is_dir():
                project_file = project_dir / "project.json"
                if project_file.exists():
                    with open(project_file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        
                        # Check if this project is currently training
                        project_id = project_data['id']
                        if project_id in active_trainings:
                            training_info = active_trainings[project_id]
                            project_data['training_status'] = training_info.get('status', 'not_started')
                            project_data['current_epoch'] = training_info.get('current_epoch', 0)
                            project_data['total_epochs'] = training_info.get('total_epochs', 0)
                            project_data['training_progress'] = training_info.get('progress_percent', 0)
                            project_data['train_loss'] = training_info.get('train_loss', 0.0)
                            project_data['train_accuracy'] = training_info.get('train_acc', 0.0)
                        else:
                            # Check if model exists (trained)
                            model_path = project_dir / "model.pt"
                            checkpoint_path = project_dir / "checkpoints" / "best_model.pt"
                            
                            if model_path.exists() or checkpoint_path.exists():
                                # Model exists, so it's trained
                                project_data['training_status'] = 'completed'
                                project_data['status'] = 'trained'
                                
                                # Try to load accuracy from model metadata
                                try:
                                    import torch
                                    model_to_load = checkpoint_path if checkpoint_path.exists() else model_path
                                    checkpoint = torch.load(model_to_load, map_location='cpu')
                                    if 'metrics' in checkpoint:
                                        metrics = checkpoint['metrics']
                                        if 'val_acc' in metrics:
                                            project_data['train_accuracy'] = metrics['val_acc']
                                except:
                                    pass
                            else:
                                project_data['training_status'] = 'not_started'
                        
                        projects.append(project_data)
        
        return {"projects": projects, "total": len(projects)}
        
        # Sort by updated_at (most recent first)
        projects.sort(key=lambda x: x.updated_at, reverse=True)
        
        logger.info(f"Listed {len(projects)} projects")
        
        return projects
        
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )

@router.get("/{project_id}")
async def get_project(project_id: str):
    """
    Get a single project by ID
    
    Args:
        project_id: Project identifier
        
    Returns:
        Project information
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        project_file = project_dir / "project.json"
        if not project_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project metadata not found: {project_id}"
            )
        
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Check training status
        from .training import active_trainings
        if project_id in active_trainings:
            training_info = active_trainings[project_id]
            project_data['training_status'] = training_info.get('status', 'not_started')
            project_data['current_epoch'] = training_info.get('current_epoch', 0)
            project_data['total_epochs'] = training_info.get('total_epochs', 0)
        else:
            # Check if model exists
            model_path = project_dir / "model.pt"
            if model_path.exists():
                project_data['training_status'] = 'completed'
                project_data['status'] = 'trained'
            else:
                project_data['training_status'] = 'not_started'
        
        return project_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )


@router.put("/{project_id}")
async def update_project(project_id: str, updates: dict):
    """
    Update project configuration
    
    Args:
        project_id: Project identifier
        updates: Dictionary of fields to update
        
    Returns:
        Updated project information
    """
    try:
        project_dir = settings.PROJECTS_DIR / project_id
        if not project_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found: {project_id}"
            )
        
        project_file = project_dir / "project.json"
        if not project_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project metadata not found: {project_id}"
            )
        
        # Load existing project data
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Update allowed fields
        allowed_fields = ['name', 'description', 'training', 'model_name', 'model_type']
        for key, value in updates.items():
            if key in allowed_fields:
                if key == 'training' and isinstance(value, dict):
                    # Merge training config
                    if 'training' not in project_data:
                        project_data['training'] = {}
                    project_data['training'].update(value)
                else:
                    project_data[key] = value
        
        # Update timestamp
        from datetime import datetime
        project_data['updated_at'] = datetime.now().isoformat()
        
        # Save updated project
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2)
        
        logger.info(f"Updated project {project_id}")
        
        return project_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )

