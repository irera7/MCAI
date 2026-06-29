"""
AWS SageMaker Cloud Training Integration
Handles training ML models on AWS cloud infrastructure
"""

import os
import json
import boto3
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class CloudTrainer:
    """Manages cloud training on AWS SageMaker"""
    
    def __init__(self):
        self.sagemaker_client = None
        self.s3_client = None
        self.s3_bucket = os.getenv('AWS_S3_BUCKET', 'modelcreator-training')
        self.sagemaker_role = os.getenv('AWS_SAGEMAKER_ROLE')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
    def _initialize_aws_clients(self):
        """Initialize AWS clients"""
        if not self.sagemaker_client:
            self.sagemaker_client = boto3.client('sagemaker', region_name=self.region)
            self.s3_client = boto3.client('s3', region_name=self.region)
    
    def _upload_to_s3(self, local_path: str, s3_key: str) -> str:
        """Upload file to S3 and return S3 URI"""
        self._initialize_aws_clients()
        
        try:
            self.s3_client.upload_file(local_path, self.s3_bucket, s3_key)
            s3_uri = f"s3://{self.s3_bucket}/{s3_key}"
            return s3_uri
        except Exception as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
    
    def _package_training_code(self, project_id: str) -> str:
        """Package training code and dependencies into zip file"""
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "training_code.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add training script
            training_script = self._generate_training_script(project_id)
            script_path = os.path.join(temp_dir, "train.py")
            with open(script_path, 'w') as f:
                f.write(training_script)
            zipf.write(script_path, "train.py")
            
            # Add requirements
            requirements = self._generate_requirements()
            req_path = os.path.join(temp_dir, "requirements.txt")
            with open(req_path, 'w') as f:
                f.write(requirements)
            zipf.write(req_path, "requirements.txt")
        
        return zip_path
    
    def _generate_training_script(self, project_id: str) -> str:
        """Generate SageMaker-compatible training script"""
        script = """
import os
import sys
import json
import torch
import argparse
from pathlib import Path

def train(args):
    # Import your training code
    # This would use the same training logic as local training
    print(f"Starting training with config: {args}")
    
    # Load data from /opt/ml/input/data/training
    data_dir = Path(args.data_dir)
    
    # Train model
    # ... your training code here ...
    
    # Save model to /opt/ml/model
    model_dir = Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # torch.save(model.state_dict(), model_dir / 'model.pth')
    print("Training completed successfully")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    # SageMaker specific arguments
    parser.add_argument('--data-dir', type=str, default=os.environ.get('SM_CHANNEL_TRAINING', '/opt/ml/input/data/training'))
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR', '/opt/ml/model'))
    parser.add_argument('--output-data-dir', type=str, default=os.environ.get('SM_OUTPUT_DATA_DIR', '/opt/ml/output/data'))
    
    # Training hyperparameters
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--learning-rate', type=float, default=0.001)
    
    args = parser.parse_args()
    train(args)
"""
        return script
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt for SageMaker"""
        requirements = """
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
pillow>=9.0.0
scikit-learn>=1.2.0
"""
        return requirements
    
    def _get_instance_type_mapping(self, instance_type: str) -> str:
        """Map UI instance types to SageMaker instance types"""
        mapping = {
            'aws-p3.2xlarge': 'ml.p3.2xlarge',
            'aws-p3.8xlarge': 'ml.p3.8xlarge',
            'aws-p3.16xlarge': 'ml.p3.16xlarge',
            'aws-p2.xlarge': 'ml.p2.xlarge',
            'aws-g4dn.xlarge': 'ml.g4dn.xlarge',
            'aws-g5.xlarge': 'ml.g5.xlarge',
        }
        return mapping.get(instance_type, 'ml.p3.2xlarge')
    
    def start_training(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start cloud training job on AWS SageMaker
        
        Args:
            config: Training configuration including:
                - project_id: Project identifier
                - instance_type: AWS instance type
                - region: AWS region
                - use_spot: Whether to use spot instances
                - estimated_epochs: Number of training epochs
                - learning_rate: Learning rate
                - batch_size: Batch size
        
        Returns:
            Dict with job_id, status, and metadata
        """
        self._initialize_aws_clients()
        
        project_id = config['project_id']
        job_name = f"modelcreator-{project_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Package training code
        zip_path = self._package_training_code(project_id)
        
        # Upload training code to S3
        code_s3_key = f"training-code/{project_id}/{job_name}.zip"
        code_s3_uri = self._upload_to_s3(zip_path, code_s3_key)
        
        # Upload training data to S3
        data_s3_uri = self._upload_training_data(project_id)
        
        # Get SageMaker instance type
        instance_type = self._get_instance_type_mapping(config['instance_type'])
        
        # Configure training job
        training_config = {
            'TrainingJobName': job_name,
            'RoleArn': self.sagemaker_role,
            'AlgorithmSpecification': {
                'TrainingImage': self._get_training_image(),
                'TrainingInputMode': 'File',
            },
            'InputDataConfig': [
                {
                    'ChannelName': 'training',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': data_s3_uri,
                            'S3DataDistributionType': 'FullyReplicated',
                        }
                    },
                    'ContentType': 'application/x-image',
                    'CompressionType': 'None',
                }
            ],
            'OutputDataConfig': {
                'S3OutputPath': f"s3://{self.s3_bucket}/output/{project_id}",
            },
            'ResourceConfig': {
                'InstanceType': instance_type,
                'InstanceCount': 1,
                'VolumeSizeInGB': 50,
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 86400,  # 24 hours
            },
            'HyperParameters': {
                'epochs': str(config.get('estimated_epochs', 50)),
                'batch-size': str(config.get('batch_size', 32)),
                'learning-rate': str(config.get('learning_rate', 0.001)),
            },
        }
        
        # Add spot instance configuration if requested
        if config.get('use_spot', False):
            training_config['EnableManagedSpotTraining'] = True
            training_config['StoppingCondition']['MaxWaitTimeInSeconds'] = 86400
        
        try:
            # Start training job
            response = self.sagemaker_client.create_training_job(**training_config)
            
            return {
                'job_id': job_name,
                'job_arn': response['TrainingJobArn'],
                'status': 'InProgress',
                'provider': 'aws',
                'instance_type': instance_type,
                'region': self.region,
                'started_at': datetime.now().isoformat(),
            }
        except Exception as e:
            raise Exception(f"Failed to start training job: {str(e)}")
    
    def _upload_training_data(self, project_id: str) -> str:
        """Upload training data to S3"""
        # Get project data directory
        project_dir = Path(f"projects/{project_id}/data")
        
        # Create tar.gz of training data
        import tarfile
        temp_dir = tempfile.mkdtemp()
        tar_path = os.path.join(temp_dir, "training_data.tar.gz")
        
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(project_dir, arcname="data")
        
        # Upload to S3
        s3_key = f"training-data/{project_id}/data.tar.gz"
        return self._upload_to_s3(tar_path, s3_key)
    
    def _get_training_image(self) -> str:
        """Get SageMaker PyTorch training container image"""
        # Use AWS Deep Learning Container
        account_mapping = {
            'us-east-1': '763104351884',
            'us-west-2': '763104351884',
            'eu-west-1': '763104351884',
        }
        account = account_mapping.get(self.region, '763104351884')
        
        # PyTorch 2.0.0 GPU image
        return f"{account}.dkr.ecr.{self.region}.amazonaws.com/pytorch-training:2.0.0-gpu-py310-cu118-ubuntu20.04-sagemaker"
    
    def get_training_status(self, job_id: str) -> Dict[str, Any]:
        """Get current status of training job"""
        self._initialize_aws_clients()
        
        try:
            response = self.sagemaker_client.describe_training_job(TrainingJobName=job_id)
            
            status_mapping = {
                'InProgress': 'training',
                'Completed': 'completed',
                'Failed': 'failed',
                'Stopping': 'stopping',
                'Stopped': 'stopped',
            }
            
            return {
                'job_id': job_id,
                'status': status_mapping.get(response['TrainingJobStatus'], 'unknown'),
                'progress': self._calculate_progress(response),
                'metrics': response.get('FinalMetricDataList', []),
                'started_at': response.get('TrainingStartTime'),
                'ended_at': response.get('TrainingEndTime'),
                'billable_seconds': response.get('BillableTimeInSeconds', 0),
                'model_artifacts': response.get('ModelArtifacts', {}).get('S3ModelArtifacts'),
            }
        except Exception as e:
            raise Exception(f"Failed to get training status: {str(e)}")
    
    def _calculate_progress(self, job_info: Dict) -> float:
        """Calculate training progress percentage"""
        if job_info['TrainingJobStatus'] == 'Completed':
            return 100.0
        elif job_info['TrainingJobStatus'] == 'InProgress':
            # Estimate based on time elapsed
            start_time = job_info.get('TrainingStartTime')
            if start_time:
                # Rough estimate - would need actual epoch reporting for accuracy
                return 50.0  # Placeholder
        return 0.0
    
    def stop_training(self, job_id: str) -> Dict[str, Any]:
        """Stop a running training job"""
        self._initialize_aws_clients()
        
        try:
            self.sagemaker_client.stop_training_job(TrainingJobName=job_id)
            return {
                'job_id': job_id,
                'status': 'stopping',
                'message': 'Training job stop requested'
            }
        except Exception as e:
            raise Exception(f"Failed to stop training job: {str(e)}")
    
    def download_trained_model(self, job_id: str, local_path: str) -> str:
        """Download trained model from S3"""
        self._initialize_aws_clients()
        
        # Get model artifacts location
        status = self.get_training_status(job_id)
        model_uri = status.get('model_artifacts')
        
        if not model_uri:
            raise Exception("Model artifacts not available yet")
        
        # Parse S3 URI
        s3_path = model_uri.replace('s3://', '').split('/', 1)
        bucket = s3_path[0]
        key = s3_path[1]
        
        # Download from S3
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        self.s3_client.download_file(bucket, key, local_path)
        
        return local_path

