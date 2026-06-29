# AWS SageMaker Cloud Training Setup Guide

## 🎯 Overview

This guide will help you set up AWS SageMaker integration for cloud training. With this setup, you can train your models on powerful AWS GPU instances (P3, G4dn, G5) without needing local GPU hardware.

## 📋 Prerequisites

1. **AWS Account** with billing enabled
2. **AWS CLI** installed and configured
3. **Python 3.8+** with boto3
4. **S3 Bucket** for storing training data and models
5. **IAM Role** with SageMaker permissions

## 🔧 Installation Steps

### Step 1: Install AWS Dependencies

```bash
cd backend
pip install boto3 sagemaker
```

Or add to your `requirements.txt`:
```
boto3>=1.28.0
sagemaker>=2.180.0
```

### Step 2: Configure AWS Credentials

**Option A: Using AWS CLI**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Enter your default region (e.g., us-east-1)
```

**Option B: Using Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Step 3: Create S3 Bucket

```bash
aws s3 mb s3://modelcreator-training --region us-east-1
```

### Step 4: Create SageMaker IAM Role

1. Go to **AWS IAM Console** → **Roles** → **Create Role**
2. Select **AWS Service** → **SageMaker**
3. Add these policies:
   - `AmazonSageMakerFullAccess`
   - `AmazonS3FullAccess` (or limited to your bucket)
4. Name it: `ModelCreator-SageMaker-Role`
5. Copy the **Role ARN**

### Step 5: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# AWS Configuration
AWS_SAGEMAKER_ROLE=arn:aws:iam::YOUR_ACCOUNT_ID:role/ModelCreator-SageMaker-Role
AWS_S3_BUCKET=modelcreator-training
AWS_REGION=us-east-1

# Optional: If not using AWS CLI credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

Replace:
- `YOUR_ACCOUNT_ID` with your AWS account ID
- `your-access-key` and `your-secret-key` with your credentials

### Step 6: Test Configuration

Start the backend and check the cloud training health endpoint:

```bash
curl http://localhost:8181/api/cloud/health
```

Expected response:
```json
{
  "status": "healthy",
  "aws_sagemaker_configured": true,
  "s3_configured": true,
  "message": "Cloud training ready"
}
```

## 🚀 Usage

### From Web Application

1. Navigate to **Cloud Training** page (`http://localhost:3333/cloud`)
2. Select a project to train
3. Choose cloud provider settings:
   - Provider: AWS
   - Instance type: `aws-p3.2xlarge` (1x V100 GPU)
   - Region: `us-east-1`
   - Enable spot instances (70% cost savings)
4. Click **Start Cloud Training**
5. Monitor the job in AWS SageMaker console

### Available Instance Types

| Instance Type | GPUs | GPU Memory | Cost/Hour | Use Case |
|--------------|------|------------|-----------|----------|
| ml.p3.2xlarge | 1x V100 | 16GB | $3.06 | Small-medium models |
| ml.p3.8xlarge | 4x V100 | 64GB | $12.24 | Large models, faster training |
| ml.p3.16xlarge | 8x V100 | 128GB | $24.48 | Very large models |
| ml.g4dn.xlarge | 1x T4 | 16GB | $0.526 | Cost-effective option |
| ml.g5.xlarge | 1x A10G | 24GB | $1.006 | Latest generation |

**Spot Instances**: Save up to 70% by using spot instances (may be interrupted)

## 📊 Monitoring Training Jobs

### Check Status via API

```bash
curl http://localhost:8181/api/cloud/status/your-job-id
```

### AWS SageMaker Console

1. Go to **AWS Console** → **SageMaker**
2. Click **Training jobs** in the sidebar
3. Find your job (name starts with `modelcreator-`)
4. View logs, metrics, and progress

### CloudWatch Logs

Training logs are automatically sent to CloudWatch:
1. Go to **CloudWatch** → **Log groups**
2. Find `/aws/sagemaker/TrainingJobs`
3. Select your job to view detailed logs

## 💰 Cost Management

### Estimating Costs

The UI provides automatic cost estimation based on:
- Instance type hourly rate
- Estimated training time (based on epochs)
- Spot vs On-Demand pricing

### Cost-Saving Tips

1. **Use Spot Instances**: 70% cheaper, but can be interrupted
2. **Choose Right Instance**: Start with smaller instances (g4dn.xlarge)
3. **Set Max Runtime**: Add stopping conditions to prevent runaway costs
4. **Monitor Usage**: Use AWS Cost Explorer to track spending
5. **Delete Old Models**: Clean up S3 to avoid storage costs

### Example Costs

Training a ResNet50 model for 50 epochs:
- **g4dn.xlarge**: ~2 hours × $0.526/hr = **$1.05**
- **p3.2xlarge**: ~1 hour × $3.06/hr = **$3.06**
- **p3.2xlarge (spot)**: ~1 hour × $0.92/hr = **$0.92**

## 🔐 Security Best Practices

1. **Use IAM Roles**: Don't hardcode credentials
2. **Limit S3 Access**: Create bucket-specific policies
3. **Enable Encryption**: Use S3 bucket encryption
4. **VPC Configuration**: Run SageMaker in private VPC (optional)
5. **Rotate Keys**: Regularly rotate AWS access keys

## 🐛 Troubleshooting

### Error: "AWS SageMaker role not configured"
- Check `AWS_SAGEMAKER_ROLE` environment variable is set
- Verify the IAM role exists and has correct permissions

### Error: "Failed to upload to S3"
- Check S3 bucket exists: `aws s3 ls s3://your-bucket`
- Verify IAM role has S3 write permissions
- Check bucket region matches `AWS_REGION`

### Error: "ResourceLimitExceeded"
- You've hit AWS service limits
- Request limit increase in AWS Service Quotas console
- Or use different instance type

### Training Job Stuck
- Check CloudWatch logs for errors
- Verify training data was uploaded correctly
- Check instance has enough memory for your model

## 📚 Additional Resources

- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [SageMaker Python SDK](https://sagemaker.readthedocs.io/)
- [AWS Deep Learning Containers](https://github.com/aws/deep-learning-containers)
- [SageMaker Pricing](https://aws.amazon.com/sagemaker/pricing/)

## 🎓 Training Flow Diagram

```
Local Machine (Web UI)
    ↓
Backend API (/api/cloud/start)
    ↓
Package Training Code + Data
    ↓
Upload to S3
    ↓
Create SageMaker Training Job
    ↓
AWS SageMaker
    ├─ Provision GPU Instance
    ├─ Download Code/Data from S3
    ├─ Run Training
    ├─ Send Logs to CloudWatch
    └─ Upload Model to S3
    ↓
Download Trained Model
    ↓
Use Locally or Deploy
```

## ✅ Checklist

Before starting cloud training, ensure:

- [ ] AWS CLI configured
- [ ] S3 bucket created
- [ ] IAM role created with permissions
- [ ] Environment variables set
- [ ] Backend running and `/api/cloud/health` shows "healthy"
- [ ] Project created and data uploaded
- [ ] Billing alerts configured (recommended)

## 🎉 You're Ready!

Once configured, you can train models on AWS SageMaker with just a few clicks from the web interface!

