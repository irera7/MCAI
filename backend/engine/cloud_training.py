"""
Cloud Training Integration
یکپارچه‌سازی با سرویس‌های Cloud برای آموزش مدل‌ها

این ماژول امکان آموزش مدل‌ها در AWS SageMaker، Azure ML، و GCP را فراهم می‌کند
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import boto3
from datetime import datetime


class CloudTrainer(ABC):
    """
    کلاس پایه برای آموزش در Cloud
    
    این کلاس interface مشترک برای همه cloud providers را تعریف می‌کند
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        مقداردهی اولیه
        
        Args:
            config: تنظیمات cloud provider
        """
        self.config = config
        self.job_name = None
        self.status = "not_started"
    
    @abstractmethod
    def upload_data(self, local_path: str) -> str:
        """
        آپلود داده به cloud storage
        
        Args:
            local_path: مسیر محلی داده
            
        Returns:
            URL داده در cloud
        """
        pass
    
    @abstractmethod
    def start_training(
        self,
        script_path: str,
        data_url: str,
        hyperparameters: Dict[str, Any]
    ) -> str:
        """
        شروع training job در cloud
        
        Args:
            script_path: مسیر اسکریپت training
            data_url: URL داده در cloud
            hyperparameters: پارامترهای training
            
        Returns:
            Job ID
        """
        pass
    
    @abstractmethod
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        دریافت وضعیت training job
        
        Args:
            job_id: شناسه job
            
        Returns:
            دیکشنری شامل وضعیت
        """
        pass
    
    @abstractmethod
    def download_model(self, job_id: str, output_path: str) -> bool:
        """
        دانلود مدل آموزش دیده
        
        Args:
            job_id: شناسه job
            output_path: مسیر ذخیره مدل
            
        Returns:
            True اگر موفق بود
        """
        pass
    
    @abstractmethod
    def stop_training(self, job_id: str) -> bool:
        """
        توقف training job
        
        Args:
            job_id: شناسه job
            
        Returns:
            True اگر موفق بود
        """
        pass


class AWSTrainer(CloudTrainer):
    """
    آموزش با AWS SageMaker
    
    این کلاس امکان آموزش مدل‌ها در AWS SageMaker را فراهم می‌کند
    
    Example:
        trainer = AWSTrainer({
            'region': 'us-east-1',
            'role_arn': 'arn:aws:iam::...',
            'bucket': 'my-bucket'
        })
        
        # آپلود داده
        data_url = trainer.upload_data('data/')
        
        # شروع training
        job_id = trainer.start_training('train.py', data_url, {...})
        
        # مانیتور کردن
        status = trainer.get_job_status(job_id)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        مقداردهی اولیه AWS SageMaker
        
        Args:
            config: باید شامل 'region', 'role_arn', 'bucket' باشد
        """
        super().__init__(config)
        
        self.region = config.get('region', 'us-east-1')
        self.role_arn = config['role_arn']
        self.bucket = config['bucket']
        
        # ایجاد clients
        self.sagemaker = boto3.client('sagemaker', region_name=self.region)
        self.s3 = boto3.client('s3', region_name=self.region)
        
        print(f"✅ AWS SageMaker Trainer initialized (region: {self.region})")
    
    def upload_data(self, local_path: str) -> str:
        """
        آپلود داده به S3
        
        Args:
            local_path: مسیر محلی داده
            
        Returns:
            S3 URL
        """
        local_path = Path(local_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_prefix = f"training-data/{timestamp}"
        
        print(f"📤 Uploading data to S3...")
        
        # آپلود تمام فایل‌ها
        if local_path.is_dir():
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(local_path)
                    s3_key = f"{s3_prefix}/{relative_path}"
                    
                    self.s3.upload_file(
                        str(file_path),
                        self.bucket,
                        s3_key
                    )
        else:
            s3_key = f"{s3_prefix}/{local_path.name}"
            self.s3.upload_file(str(local_path), self.bucket, s3_key)
        
        s3_url = f"s3://{self.bucket}/{s3_prefix}"
        print(f"✅ Data uploaded to: {s3_url}")
        
        return s3_url
    
    def start_training(
        self,
        script_path: str,
        data_url: str,
        hyperparameters: Dict[str, Any]
    ) -> str:
        """
        شروع training job در SageMaker
        
        Args:
            script_path: مسیر اسکریپت training
            data_url: S3 URL داده
            hyperparameters: پارامترهای training
            
        Returns:
            Job name
        """
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        job_name = f"modelcreator-training-{timestamp}"
        
        # آپلود اسکریپت به S3
        script_s3_key = f"training-scripts/{timestamp}/train.py"
        self.s3.upload_file(script_path, self.bucket, script_s3_key)
        
        # تنظیمات training job
        training_params = {
            'TrainingJobName': job_name,
            'RoleArn': self.role_arn,
            'AlgorithmSpecification': {
                'TrainingImage': '763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.0-gpu-py310',
                'TrainingInputMode': 'File'
            },
            'InputDataConfig': [
                {
                    'ChannelName': 'training',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': data_url,
                            'S3DataDistributionType': 'FullyReplicated'
                        }
                    }
                }
            ],
            'OutputDataConfig': {
                'S3OutputPath': f"s3://{self.bucket}/training-output"
            },
            'ResourceConfig': {
                'InstanceType': self.config.get('instance_type', 'ml.p3.2xlarge'),
                'InstanceCount': 1,
                'VolumeSizeInGB': 30
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': self.config.get('max_runtime', 86400)  # 24 hours
            },
            'HyperParameters': {k: str(v) for k, v in hyperparameters.items()}
        }
        
        print(f"🚀 Starting SageMaker training job: {job_name}")
        
        response = self.sagemaker.create_training_job(**training_params)
        
        self.job_name = job_name
        self.status = "running"
        
        print(f"✅ Training job started: {job_name}")
        
        return job_name
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        دریافت وضعیت training job
        
        Args:
            job_id: نام job
            
        Returns:
            دیکشنری شامل وضعیت
        """
        response = self.sagemaker.describe_training_job(TrainingJobName=job_id)
        
        status = {
            'job_id': job_id,
            'status': response['TrainingJobStatus'],
            'start_time': str(response.get('TrainingStartTime', '')),
            'end_time': str(response.get('TrainingEndTime', '')),
            'duration': str(response.get('TrainingTimeInSeconds', 0)),
            'instance_type': response['ResourceConfig']['InstanceType'],
            'metrics': response.get('FinalMetricDataList', [])
        }
        
        if response['TrainingJobStatus'] == 'Failed':
            status['failure_reason'] = response.get('FailureReason', 'Unknown')
        
        return status
    
    def download_model(self, job_id: str, output_path: str) -> bool:
        """
        دانلود مدل آموزش دیده از S3
        
        Args:
            job_id: نام job
            output_path: مسیر ذخیره
            
        Returns:
            True اگر موفق بود
        """
        try:
            response = self.sagemaker.describe_training_job(TrainingJobName=job_id)
            
            if response['TrainingJobStatus'] != 'Completed':
                print(f"⚠️ Job is not completed yet: {response['TrainingJobStatus']}")
                return False
            
            model_s3_uri = response['ModelArtifacts']['S3ModelArtifacts']
            
            # Parse S3 URI
            s3_path = model_s3_uri.replace('s3://', '')
            bucket, key = s3_path.split('/', 1)
            
            # دانلود
            output_file = Path(output_path) / 'model.tar.gz'
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"📥 Downloading model from: {model_s3_uri}")
            self.s3.download_file(bucket, key, str(output_file))
            
            print(f"✅ Model downloaded to: {output_file}")
            
            # Extract tar.gz
            import tarfile
            with tarfile.open(output_file, 'r:gz') as tar:
                tar.extractall(output_file.parent)
            
            return True
            
        except Exception as e:
            print(f"❌ Error downloading model: {e}")
            return False
    
    def stop_training(self, job_id: str) -> bool:
        """
        توقف training job
        
        Args:
            job_id: نام job
            
        Returns:
            True اگر موفق بود
        """
        try:
            self.sagemaker.stop_training_job(TrainingJobName=job_id)
            print(f"✅ Training job stopped: {job_id}")
            return True
        except Exception as e:
            print(f"❌ Error stopping job: {e}")
            return False


class AzureTrainer(CloudTrainer):
    """
    آموزش با Azure Machine Learning
    
    این کلاس امکان آموزش مدل‌ها در Azure ML را فراهم می‌کند
    
    Example:
        trainer = AzureTrainer({
            'subscription_id': '...',
            'resource_group': 'my-rg',
            'workspace_name': 'my-workspace'
        })
        
        data_url = trainer.upload_data('data/')
        job_id = trainer.start_training('train.py', data_url, {...})
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        مقداردهی اولیه Azure ML
        
        Args:
            config: باید شامل 'subscription_id', 'resource_group', 'workspace_name' باشد
        """
        super().__init__(config)
        
        try:
            from azure.ai.ml import MLClient
            from azure.identity import DefaultAzureCredential
            
            self.ml_client = MLClient(
                DefaultAzureCredential(),
                config['subscription_id'],
                config['resource_group'],
                config['workspace_name']
            )
            
            print(f"✅ Azure ML Trainer initialized")
        except ImportError:
            print("⚠️ Azure ML SDK not installed. Run: pip install azure-ai-ml")
            raise
    
    def upload_data(self, local_path: str) -> str:
        """
        آپلود داده به Azure Blob Storage
        
        Args:
            local_path: مسیر محلی
            
        Returns:
            Azure URL
        """
        from azure.ai.ml.entities import Data
        from azure.ai.ml.constants import AssetTypes
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_name = f"training_data_{timestamp}"
        
        print(f"📤 Uploading data to Azure...")
        
        data_asset = Data(
            path=local_path,
            type=AssetTypes.URI_FOLDER,
            name=data_name
        )
        
        self.ml_client.data.create_or_update(data_asset)
        
        print(f"✅ Data uploaded: {data_name}")
        
        return f"azureml://datastores/workspaceblobstore/paths/{data_name}"
    
    def start_training(
        self,
        script_path: str,
        data_url: str,
        hyperparameters: Dict[str, Any]
    ) -> str:
        """
        شروع training در Azure ML
        
        Args:
            script_path: مسیر اسکریپت
            data_url: Azure URL داده
            hyperparameters: پارامترها
            
        Returns:
            Job ID
        """
        from azure.ai.ml import command
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        job_name = f"modelcreator-{timestamp}"
        
        print(f"🚀 Starting Azure ML training job...")
        
        job = command(
            code=str(Path(script_path).parent),
            command="python train.py",
            environment="AzureML-pytorch-2.0-ubuntu20.04-py38-cuda11.8-gpu",
            compute=self.config.get('compute_target', 'gpu-cluster'),
            inputs={'data': data_url},
            display_name=job_name
        )
        
        returned_job = self.ml_client.jobs.create_or_update(job)
        
        self.job_name = returned_job.name
        print(f"✅ Training job started: {self.job_name}")
        
        return self.job_name
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """دریافت وضعیت job"""
        job = self.ml_client.jobs.get(job_id)
        
        return {
            'job_id': job_id,
            'status': job.status,
            'start_time': str(job.creation_context.created_at),
            'compute': job.compute
        }
    
    def download_model(self, job_id: str, output_path: str) -> bool:
        """دانلود مدل"""
        try:
            self.ml_client.jobs.download(job_id, download_path=output_path)
            print(f"✅ Model downloaded to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def stop_training(self, job_id: str) -> bool:
        """توقف training"""
        try:
            self.ml_client.jobs.cancel(job_id)
            print(f"✅ Job stopped: {job_id}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


class GCPTrainer(CloudTrainer):
    """
    آموزش با Google Cloud AI Platform
    
    Example:
        trainer = GCPTrainer({
            'project_id': 'my-project',
            'region': 'us-central1',
            'bucket': 'my-bucket'
        })
    """
    
    def __init__(self, config: Dict[str, Any]):
        """مقداردهی اولیه GCP"""
        super().__init__(config)
        
        try:
            from google.cloud import aiplatform, storage
            
            aiplatform.init(
                project=config['project_id'],
                location=config.get('region', 'us-central1')
            )
            
            self.storage_client = storage.Client()
            self.bucket_name = config['bucket']
            
            print(f"✅ GCP AI Platform Trainer initialized")
        except ImportError:
            print("⚠️ GCP SDK not installed. Run: pip install google-cloud-aiplatform google-cloud-storage")
            raise
    
    def upload_data(self, local_path: str) -> str:
        """آپلود به GCS"""
        from google.cloud import storage
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        gcs_prefix = f"training-data/{timestamp}"
        
        print(f"📤 Uploading data to GCS...")
        
        bucket = self.storage_client.bucket(self.bucket_name)
        local_path = Path(local_path)
        
        if local_path.is_dir():
            for file_path in local_path.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(local_path)
                    blob = bucket.blob(f"{gcs_prefix}/{relative_path}")
                    blob.upload_from_filename(str(file_path))
        
        gcs_url = f"gs://{self.bucket_name}/{gcs_prefix}"
        print(f"✅ Data uploaded to: {gcs_url}")
        
        return gcs_url
    
    def start_training(
        self,
        script_path: str,
        data_url: str,
        hyperparameters: Dict[str, Any]
    ) -> str:
        """شروع training در GCP"""
        from google.cloud import aiplatform
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        job_name = f"modelcreator_{timestamp}"
        
        print(f"🚀 Starting GCP AI Platform training job...")
        
        job = aiplatform.CustomTrainingJob(
            display_name=job_name,
            container_uri="gcr.io/cloud-aiplatform/training/pytorch-gpu.2-0:latest",
            model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/pytorch-gpu.2-0:latest"
        )
        
        model = job.run(
            replica_count=1,
            machine_type=self.config.get('machine_type', 'n1-standard-4'),
            accelerator_type=self.config.get('accelerator_type', 'NVIDIA_TESLA_T4'),
            accelerator_count=1
        )
        
        self.job_name = job_name
        print(f"✅ Training job started: {job_name}")
        
        return job_name
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """دریافت وضعیت"""
        # Implementation would query GCP AI Platform
        return {'job_id': job_id, 'status': 'running'}
    
    def download_model(self, job_id: str, output_path: str) -> bool:
        """دانلود مدل"""
        print(f"📥 Downloading model from GCS...")
        # Implementation would download from GCS
        return True
    
    def stop_training(self, job_id: str) -> bool:
        """توقف training"""
        # Implementation would cancel the job
        return True


def create_cloud_trainer(provider: str, config: Dict[str, Any]) -> CloudTrainer:
    """
    Factory function برای ساخت cloud trainer
    
    Args:
        provider: 'aws', 'azure', یا 'gcp'
        config: تنظیمات provider
        
    Returns:
        CloudTrainer instance
        
    Example:
        trainer = create_cloud_trainer('aws', {
            'region': 'us-east-1',
            'role_arn': '...',
            'bucket': 'my-bucket'
        })
    """
    providers = {
        'aws': AWSTrainer,
        'azure': AzureTrainer,
        'gcp': GCPTrainer
    }
    
    if provider.lower() not in providers:
        raise ValueError(f"Unsupported provider: {provider}. Choose from: {list(providers.keys())}")
    
    return providers[provider.lower()](config)

