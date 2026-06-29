"""
AutoML API Routes
API endpoints for automated hyperparameter optimization using Optuna
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from pathlib import Path
import torch
import json
import logging

from engine.hyperparameter_optimizer import HyperparameterOptimizer
from engine.data_loader import create_data_loaders
from engine.text_data_loader import create_text_loaders
from engine.audio_data_loader import create_audio_loaders

router = APIRouter(prefix="/api/automl", tags=["AutoML"])
logger = logging.getLogger(__name__)


class AutoMLRequest(BaseModel):
    """AutoML optimization request"""
    project_id: str
    n_trials: int = 50
    timeout: Optional[int] = 3600  # seconds
    optimizer: str = "tpe"  # tpe, random, grid
    metric: str = "accuracy"  # accuracy, loss, f1
    search_space: Dict[str, Any] = {}


class TrialResult(BaseModel):
    """Single trial result"""
    number: int
    score: float
    params: Dict[str, Any]


class AutoMLResponse(BaseModel):
    """AutoML optimization response"""
    status: str
    best_score: float
    total_trials: int
    best_params: Dict[str, Any]
    trial_history: List[TrialResult]
    optimization_time: float


@router.post("/start")
async def start_automl(request: AutoMLRequest):
    """
    Start AutoML hyperparameter optimization
    
    این endpoint یک optimization study با Optuna شروع می‌کند و
    بهترین hyperparameter‌ها را پیدا می‌کند.
    
    Args:
        request: AutoML configuration
        
    Returns:
        Best parameters and trial history
    """
    try:
        # Load project info
        project_dir = Path(f"../projects/{request.project_id}")
        
        if not project_dir.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load project config
        config_file = project_dir / "config.json"
        if not config_file.exists():
            raise HTTPException(status_code=404, detail="Project config not found")
        
        with open(config_file, 'r') as f:
            project_config = json.load(f)
        
        modality = project_config.get('modality', 'image')
        num_classes = project_config.get('num_classes', 2)
        model_name = project_config.get('model_name', 'resnet18')
        
        # Create data loaders based on modality
        data_dir = str(project_dir / "data")
        
        if modality == 'image':
            config = {
                'batch_size': 32,
                'num_workers': 4,
                'augmentation': True
            }
            train_loader, val_loader, _ = create_data_loaders(data_dir, config)
            
        elif modality == 'text':
            config = {
                'batch_size': 16,
                'max_length': 128,
                'num_workers': 2
            }
            train_loader, val_loader, _ = create_text_loaders(data_dir, config)
            
        elif modality == 'audio':
            config = {
                'batch_size': 16,
                'num_workers': 2,
                'sample_rate': 16000,
                'n_mels': 128
            }
            train_loader, val_loader, _ = create_audio_loaders(data_dir, config)
            
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Modality '{modality}' not supported for AutoML yet"
            )
        
        # Setup device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Create optimizer
        logger.info(f"Starting AutoML for project {request.project_id}")
        logger.info(f"Modality: {modality}, Trials: {request.n_trials}, Device: {device}")
        
        optimizer = HyperparameterOptimizer(
            train_loader=train_loader,
            val_loader=val_loader,
            num_classes=num_classes,
            modality=modality,
            model_name=model_name,
            device=device,
            n_trials=request.n_trials,
            timeout=request.timeout,
            study_name=f"{request.project_id}_automl",
            direction='maximize' if request.metric == 'accuracy' else 'minimize',
            pruning=True,
            save_dir=str(project_dir / "automl_results")
        )
        
        # Run optimization
        logger.info("Running optimization...")
        best_params, study_info = optimizer.optimize()
        
        logger.info(f"Optimization completed. Best score: {study_info['best_score']}")
        
        # Build trial history
        trial_history = []
        for trial in study_info.get('all_trials', [])[:20]:  # Last 20 trials
            trial_history.append(TrialResult(
                number=trial.get('number', 0),
                score=trial.get('value', 0.0),
                params=trial.get('params', {})
            ))
        
        # Save best params to project
        best_params_file = project_dir / "best_params.json"
        with open(best_params_file, 'w') as f:
            json.dump(best_params, f, indent=2)
        
        logger.info(f"Best parameters saved to {best_params_file}")
        
        return AutoMLResponse(
            status="success",
            best_score=study_info['best_score'],
            total_trials=study_info['n_trials'],
            best_params=best_params,
            trial_history=trial_history,
            optimization_time=study_info.get('duration', 0.0)
        )
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except Exception as e:
        logger.error(f"AutoML error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{project_id}")
async def get_automl_status(project_id: str):
    """
    Get AutoML optimization status for a project
    
    Args:
        project_id: Project ID
        
    Returns:
        Status and progress information
    """
    try:
        project_dir = Path(f"../projects/{project_id}")
        
        if not project_dir.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if AutoML results exist
        automl_dir = project_dir / "automl_results"
        best_params_file = project_dir / "best_params.json"
        
        if best_params_file.exists():
            with open(best_params_file, 'r') as f:
                best_params = json.load(f)
            
            return JSONResponse({
                "status": "completed",
                "has_results": True,
                "best_params": best_params
            })
        else:
            return JSONResponse({
                "status": "not_started",
                "has_results": False
            })
            
    except Exception as e:
        logger.error(f"Error getting AutoML status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{project_id}")
async def get_automl_history(project_id: str):
    """
    Get AutoML trial history for a project
    
    Args:
        project_id: Project ID
        
    Returns:
        Trial history and statistics
    """
    try:
        project_dir = Path(f"../projects/{project_id}")
        automl_dir = project_dir / "automl_results"
        
        if not automl_dir.exists():
            raise HTTPException(status_code=404, detail="No AutoML results found")
        
        # Look for study JSON files
        study_files = list(automl_dir.glob("study_*.json"))
        
        if not study_files:
            raise HTTPException(status_code=404, detail="No study results found")
        
        # Load the most recent study
        latest_study = max(study_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_study, 'r') as f:
            study_data = json.load(f)
        
        return JSONResponse(study_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AutoML history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply/{project_id}")
async def apply_best_params(project_id: str):
    """
    Apply best parameters from AutoML to project config
    
    Args:
        project_id: Project ID
        
    Returns:
        Success status
    """
    try:
        project_dir = Path(f"../projects/{project_id}")
        best_params_file = project_dir / "best_params.json"
        config_file = project_dir / "config.json"
        
        if not best_params_file.exists():
            raise HTTPException(
                status_code=404, 
                detail="No AutoML results found. Run AutoML first."
            )
        
        # Load best params
        with open(best_params_file, 'r') as f:
            best_params = json.load(f)
        
        # Load current config
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Update config with best params
        config.update(best_params)
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Applied best parameters to project {project_id}")
        
        return JSONResponse({
            "status": "success",
            "message": "Best parameters applied successfully",
            "params": best_params
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying best params: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/results/{project_id}")
async def delete_automl_results(project_id: str):
    """
    Delete AutoML results for a project
    
    Args:
        project_id: Project ID
        
    Returns:
        Success status
    """
    try:
        project_dir = Path(f"../projects/{project_id}")
        automl_dir = project_dir / "automl_results"
        best_params_file = project_dir / "best_params.json"
        
        # Delete automl directory
        if automl_dir.exists():
            import shutil
            shutil.rmtree(automl_dir)
        
        # Delete best params file
        if best_params_file.exists():
            best_params_file.unlink()
        
        logger.info(f"Deleted AutoML results for project {project_id}")
        
        return JSONResponse({
            "status": "success",
            "message": "AutoML results deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Error deleting AutoML results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("AutoML API Routes")
    print("Endpoints:")
    print("  POST /api/automl/start - Start AutoML optimization")
    print("  GET /api/automl/status/{project_id} - Get optimization status")
    print("  GET /api/automl/history/{project_id} - Get trial history")
    print("  POST /api/automl/apply/{project_id} - Apply best parameters")
    print("  DELETE /api/automl/results/{project_id} - Delete results")

