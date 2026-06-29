"""
Ensemble Methods API Routes
مسیرهای API برای ایجاد و مدیریت ensemble models

این API امکان ترکیب چند مدل آموزش‌دیده را فراهم می‌کند
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pathlib import Path
import torch
import torch.nn as nn
from pydantic import BaseModel

router = APIRouter(prefix="/api/ensemble", tags=["ensemble"])


# ============================================
# Request/Response Models
# ============================================

class EnsembleCreateRequest(BaseModel):
    """درخواست ایجاد ensemble"""
    project_ids: List[str]  # لیست project IDهایی که مدل‌هایشان را ensemble می‌کنیم
    ensemble_type: str  # 'voting', 'stacking', یا 'bagging'
    voting_type: Optional[str] = 'soft'  # برای voting: 'hard' یا 'soft'
    weights: Optional[List[float]] = None  # وزن‌های دلخواه
    ensemble_name: str  # نام ensemble


class EnsembleEvaluateRequest(BaseModel):
    """درخواست ارزیابی ensemble"""
    ensemble_id: str
    test_data_path: str


# ============================================
# Helper Functions
# ============================================

def get_project_model_path(project_id: str) -> Path:
    """
    دریافت مسیر مدل یک پروژه
    
    Args:
        project_id: شناسه پروژه
        
    Returns:
        مسیر فایل مدل
    """
    project_dir = Path("projects") / project_id
    model_path = project_dir / "model.pt"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found for project {project_id}")
    
    return model_path


def get_project_info(project_id: str) -> Dict[str, Any]:
    """
    دریافت اطلاعات یک پروژه
    
    Args:
        project_id: شناسه پروژه
        
    Returns:
        دیکشنری اطلاعات پروژه
    """
    import json
    
    project_dir = Path("projects") / project_id
    project_file = project_dir / "project.json"
    
    if not project_file.exists():
        raise FileNotFoundError(f"Project file not found: {project_id}")
    
    with open(project_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_model(model_path: Path, model_architecture: str, num_classes: int, device: str = 'cpu'):
    """
    لود کردن یک مدل
    
    Args:
        model_path: مسیر فایل مدل
        model_architecture: نام معماری (e.g. 'resnet18')
        num_classes: تعداد کلاس‌ها
        device: دستگاه
        
    Returns:
        مدل لود شده
    """
    from engine import ModelBuilder
    
    # ساخت مدل
    model = ModelBuilder.build_image_model(
        model_architecture,
        num_classes=num_classes,
        pretrained=False
    )
    
    # لود weights
    checkpoint = torch.load(model_path, map_location=device)
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)
    
    model.to(device)
    model.eval()
    
    return model


# ============================================
# API Endpoints
# ============================================

@router.post("/create")
async def create_ensemble(request: EnsembleCreateRequest):
    """
    ایجاد یک ensemble از چند مدل
    
    Args:
        request: اطلاعات ensemble
        
    Returns:
        اطلاعات ensemble ایجاد شده
    """
    try:
        from engine import quick_ensemble
        
        # بررسی تعداد مدل‌ها
        if len(request.project_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="حداقل 2 مدل برای ensemble نیاز است"
            )
        
        # لود کردن اطلاعات پروژه‌ها
        projects_info = []
        for project_id in request.project_ids:
            try:
                info = get_project_info(project_id)
                projects_info.append(info)
            except Exception as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"پروژه {project_id} یافت نشد: {str(e)}"
                )
        
        # بررسی سازگاری مدل‌ها
        num_classes_list = [p.get('num_classes') for p in projects_info]
        if len(set(num_classes_list)) > 1:
            raise HTTPException(
                status_code=400,
                detail=f"تمام مدل‌ها باید تعداد کلاس‌های یکسانی داشته باشند. پیدا شد: {num_classes_list}"
            )
        
        num_classes = num_classes_list[0]
        
        # لود کردن مدل‌ها
        models = []
        model_details = []
        
        for i, (project_id, info) in enumerate(zip(request.project_ids, projects_info)):
            try:
                model_path = get_project_model_path(project_id)
                architecture = info.get('model_architecture', 'resnet18')
                
                model = load_model(model_path, architecture, num_classes)
                models.append(model)
                
                model_details.append({
                    'project_id': project_id,
                    'project_name': info.get('name', f'Model {i+1}'),
                    'architecture': architecture,
                    'accuracy': info.get('best_accuracy', 0.0)
                })
                
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"خطا در لود مدل {project_id}: {str(e)}"
                )
        
        # ایجاد ensemble
        ensemble_kwargs = {}
        
        if request.ensemble_type == 'voting':
            ensemble_kwargs['voting'] = request.voting_type
            if request.weights:
                ensemble_kwargs['weights'] = request.weights
        
        ensemble = quick_ensemble(
            models,
            ensemble_type=request.ensemble_type,
            **ensemble_kwargs
        )
        
        # ذخیره ensemble
        import uuid
        ensemble_id = str(uuid.uuid4())
        ensemble_dir = Path("ensembles") / ensemble_id
        ensemble_dir.mkdir(parents=True, exist_ok=True)
        
        # ذخیره مدل ensemble
        torch.save({
            'ensemble_state_dict': ensemble.state_dict(),
            'ensemble_type': request.ensemble_type,
            'num_classes': num_classes,
            'models': model_details,
            'config': {
                'voting_type': request.voting_type if request.ensemble_type == 'voting' else None,
                'weights': request.weights
            }
        }, ensemble_dir / "ensemble.pt")
        
        # ذخیره metadata
        import json
        metadata = {
            'id': ensemble_id,
            'name': request.ensemble_name,
            'type': request.ensemble_type,
            'num_models': len(models),
            'models': model_details,
            'num_classes': num_classes,
            'created_at': str(torch.cuda.current_device() if torch.cuda.is_available() else 'cpu')
        }
        
        with open(ensemble_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return JSONResponse({
            'status': 'success',
            'message': f'Ensemble "{request.ensemble_name}" created successfully',
            'ensemble_id': ensemble_id,
            'ensemble_type': request.ensemble_type,
            'num_models': len(models),
            'models': model_details,
            'num_classes': num_classes
        })
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"خطا در ایجاد ensemble: {str(e)}"
        )


@router.get("/list")
async def list_ensembles():
    """
    دریافت لیست ensembles ذخیره شده
    
    Returns:
        لیست ensembles
    """
    try:
        import json
        
        ensembles_dir = Path("ensembles")
        if not ensembles_dir.exists():
            return JSONResponse({
                'status': 'success',
                'ensembles': [],
                'total': 0
            })
        
        ensembles = []
        
        for ensemble_path in ensembles_dir.iterdir():
            if ensemble_path.is_dir():
                metadata_file = ensemble_path / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        ensembles.append(metadata)
        
        return JSONResponse({
            'status': 'success',
            'ensembles': ensembles,
            'total': len(ensembles)
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"خطا در دریافت لیست: {str(e)}"
        )


@router.get("/info/{ensemble_id}")
async def get_ensemble_info(ensemble_id: str):
    """
    دریافت اطلاعات یک ensemble
    
    Args:
        ensemble_id: شناسه ensemble
        
    Returns:
        اطلاعات ensemble
    """
    try:
        import json
        
        ensemble_dir = Path("ensembles") / ensemble_id
        if not ensemble_dir.exists():
            raise HTTPException(status_code=404, detail="Ensemble not found")
        
        metadata_file = ensemble_dir / "metadata.json"
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Ensemble metadata not found")
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return JSONResponse({
            'status': 'success',
            'ensemble': metadata
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"خطا در دریافت اطلاعات: {str(e)}"
        )


@router.get("/available-models")
async def get_available_models():
    """
    دریافت لیست مدل‌های موجود برای ensemble
    
    Returns:
        لیست مدل‌های آموزش دیده
    """
    try:
        import json
        
        projects_dir = Path("projects")
        if not projects_dir.exists():
            return JSONResponse({
                'status': 'success',
                'models': [],
                'total': 0
            })
        
        available_models = []
        
        for project_path in projects_dir.iterdir():
            if project_path.is_dir():
                project_file = project_path / "project.json"
                model_file = project_path / "model.pt"
                
                # فقط پروژه‌هایی که مدل آموزش دیده دارند
                if project_file.exists() and model_file.exists():
                    with open(project_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        
                        # فقط مدل‌های تکمیل شده
                        if info.get('status') == 'completed':
                            available_models.append({
                                'project_id': info.get('id', project_path.name),
                                'project_name': info.get('name', 'Unknown'),
                                'architecture': info.get('model_architecture', 'Unknown'),
                                'accuracy': info.get('best_accuracy', 0.0),
                                'num_classes': info.get('num_classes', 0),
                                'modality': info.get('modality', 'image'),
                                'created_at': info.get('created_at', '')
                            })
        
        # مرتب‌سازی بر اساس accuracy
        available_models.sort(key=lambda x: x['accuracy'], reverse=True)
        
        return JSONResponse({
            'status': 'success',
            'models': available_models,
            'total': len(available_models)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"خطا در دریافت مدل‌ها: {str(e)}"
        )


@router.delete("/{ensemble_id}")
async def delete_ensemble(ensemble_id: str):
    """
    حذف یک ensemble
    
    Args:
        ensemble_id: شناسه ensemble
        
    Returns:
        وضعیت عملیات
    """
    try:
        import shutil
        
        ensemble_dir = Path("ensembles") / ensemble_id
        if not ensemble_dir.exists():
            raise HTTPException(status_code=404, detail="Ensemble not found")
        
        # حذف پوشه
        shutil.rmtree(ensemble_dir)
        
        return JSONResponse({
            'status': 'success',
            'message': f'Ensemble {ensemble_id} deleted successfully'
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"خطا در حذف ensemble: {str(e)}"
        )

