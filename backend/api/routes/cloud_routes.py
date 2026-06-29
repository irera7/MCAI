"""
Cloud Training API Routes
FastAPI endpoints for AWS SageMaker cloud training
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

from engine.cloud_trainer import CloudTrainer

router = APIRouter(prefix="/api/cloud", tags=["cloud-training"])

# Initialize cloud trainer
cloud_trainer = CloudTrainer()

class CloudTrainingConfig(BaseModel):
    """Cloud training configuration"""
    project_id: str
    provider: str = "aws"
    instance_type: str
    region: str
    use_spot: bool = False
    estimated_epochs: int = 50
    batch_size: int = 32
    learning_rate: float = 0.001

class CloudTrainingResponse(BaseModel):
    """Cloud training job response"""
    job_id: str
    status: str
    provider: str
    instance_type: str
    region: str
    started_at: str
    message: Optional[str] = None

@router.post("/start", response_model=CloudTrainingResponse)
async def start_cloud_training(
    config: CloudTrainingConfig,
    background_tasks: BackgroundTasks
):
    """
    Start a cloud training job on AWS SageMaker
    
    - **project_id**: ID of the project to train
    - **provider**: Cloud provider (currently only 'aws' supported)
    - **instance_type**: AWS instance type (e.g., 'aws-p3.2xlarge')
    - **region**: AWS region
    - **use_spot**: Whether to use spot instances for cost savings
    - **estimated_epochs**: Number of training epochs
    - **batch_size**: Training batch size
    - **learning_rate**: Learning rate
    """
    
    # Validate AWS credentials
    if not os.getenv('AWS_SAGEMAKER_ROLE'):
        raise HTTPException(
            status_code=500,
            detail="AWS SageMaker role not configured. Please set AWS_SAGEMAKER_ROLE environment variable."
        )
    
    try:
        # Start training job
        result = cloud_trainer.start_training(config.dict())
        
        return CloudTrainingResponse(
            job_id=result['job_id'],
            status=result['status'],
            provider=result['provider'],
            instance_type=result['instance_type'],
            region=result['region'],
            started_at=result['started_at'],
            message="Training job started successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}")
async def get_cloud_training_status(job_id: str):
    """
    Get the status of a cloud training job
    
    - **job_id**: The training job ID returned from start_cloud_training
    """
    try:
        status = cloud_trainer.get_training_status(job_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{job_id}")
async def stop_cloud_training(job_id: str):
    """
    Stop a running cloud training job
    
    - **job_id**: The training job ID to stop
    """
    try:
        result = cloud_trainer.stop_training(job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def list_cloud_training_jobs():
    """
    List all cloud training jobs
    """
    try:
        # This would query SageMaker for all training jobs
        # For now, return empty list
        return {
            "jobs": [],
            "message": "Cloud training jobs list feature coming soon"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download/{job_id}")
async def download_trained_model(job_id: str, local_path: str = None):
    """
    Download a trained model from cloud storage
    
    - **job_id**: The training job ID
    - **local_path**: Optional local path to save the model
    """
    try:
        if not local_path:
            local_path = f"projects/cloud_models/{job_id}/model.tar.gz"
        
        model_path = cloud_trainer.download_trained_model(job_id, local_path)
        
        return {
            "job_id": job_id,
            "model_path": model_path,
            "status": "downloaded",
            "message": "Model downloaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def cloud_training_health():
    """Check if cloud training service is configured correctly"""
    
    aws_configured = bool(os.getenv('AWS_SAGEMAKER_ROLE'))
    s3_configured = bool(os.getenv('AWS_S3_BUCKET'))
    
    return {
        "status": "healthy" if aws_configured else "not_configured",
        "aws_sagemaker_configured": aws_configured,
        "s3_configured": s3_configured,
        "message": "Cloud training ready" if aws_configured else "AWS credentials not configured"
    }

