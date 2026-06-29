import React, { useState } from 'react';
import { Card, Form, Select, InputNumber, Button, Space, Typography, Divider, Row, Col, Tag, Statistic, Alert, App } from 'antd';
import { CloudServerOutlined, DollarOutlined, RocketOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useQuery, useMutation } from '@tanstack/react-query';
import { projectApi, cloudApi } from '../api/endpoints';

const { Title, Paragraph, Text } = Typography;

const CloudTrainingPage: React.FC = () => {
  const { message } = App.useApp();
  const [form] = Form.useForm();
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [estimatedCost, setEstimatedCost] = useState<number>(0);
  const [trainingJobId, setTrainingJobId] = useState<string>('');

  // Fetch projects
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectApi.list();
      return response.data;
    },
  });

  // Check cloud service health
  const { data: healthData } = useQuery({
    queryKey: ['cloud-health'],
    queryFn: async () => {
      const response = await cloudApi.health();
      return response.data;
    },
  });

  // Start training mutation
  const startTrainingMutation = useMutation({
    mutationFn: (config: any) => cloudApi.start(config),
    onSuccess: (response) => {
      const jobId = response.data.job_id;
      setTrainingJobId(jobId);
      message.success(`Cloud training started! Job ID: ${jobId}`);
    },
    onError: (error: any) => {
      message.error(`Failed to start training: ${error.detail || error.message}`);
    },
  });

  const handleEstimateCost = () => {
    const values = form.getFieldsValue();
    // Simple cost estimation (example pricing)
    const hourlyRates: Record<string, number> = {
      'aws-p3.2xlarge': 3.06,
      'aws-p3.8xlarge': 12.24,
      'azure-nc6': 0.90,
      'azure-nc12': 1.80,
      'gcp-v100': 2.48,
      'gcp-a100': 3.67,
    };

    const hourlyRate = hourlyRates[values.instanceType] || 2;
    const estimatedHours = values.estimatedEpochs * 2 / 60; // Rough estimate
    const cost = hourlyRate * estimatedHours * (values.useSpot ? 0.3 : 1);
    
    setEstimatedCost(cost);
  };

  const handleStartTraining = () => {
    if (!selectedProject) {
      message.warning('Please select a project');
      return;
    }

    form.validateFields().then((values) => {
      const config = {
        project_id: selectedProject,
        provider: values.provider,
        instance_type: values.instanceType,
        region: values.region,
        use_spot: values.useSpot,
        estimated_epochs: values.estimatedEpochs,
        batch_size: 32,
        learning_rate: 0.001,
      };

      startTrainingMutation.mutate(config);
    });
  };

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <CloudServerOutlined style={{ fontSize: 64, color: '#6366F1' }} />
          <Title level={2}>☁️ Cloud Training</Title>
          <Paragraph>
            Train your models on powerful cloud GPUs (AWS, Azure, GCP) for faster training.
          </Paragraph>
        </div>

        <Divider />

        {/* Health Status */}
        {healthData && !healthData.aws_sagemaker_configured && (
          <Alert
            message="AWS Configuration Required"
            description="To use cloud training, please configure AWS credentials (AWS_SAGEMAKER_ROLE and AWS_S3_BUCKET environment variables)."
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        {trainingJobId && (
          <Alert
            message="Training Job Started!"
            description={
              <div>
                <p>Your cloud training job has been started successfully.</p>
                <p><strong>Job ID:</strong> {trainingJobId}</p>
                <p>You can monitor the progress in the AWS SageMaker console or check the status via API.</p>
              </div>
            }
            type="success"
            showIcon
            icon={<CheckCircleOutlined />}
            style={{ marginBottom: 16 }}
            closable
            onClose={() => setTrainingJobId('')}
          />
        )}

        <Form
          form={form}
          layout="vertical"
          initialValues={{
            provider: 'aws',
            instanceType: 'aws-p3.2xlarge',
            region: 'us-east-1',
            estimatedEpochs: 50,
            useSpot: true,
          }}
          onValuesChange={handleEstimateCost}
        >
          <Card title="Project Selection" style={{ marginBottom: 16 }}>
            <Form.Item label="Select Project" name="projectId">
              <Select
                size="large"
                placeholder="Choose a project"
                value={selectedProject}
                onChange={setSelectedProject}
              >
                {projectsData?.projects?.map((project) => (
                  <Select.Option key={project.id} value={project.id}>
                    {project.name} - <Tag color="blue">{project.modality}</Tag>
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          </Card>

          <Card title="Cloud Provider" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="Provider" name="provider">
                  <Select size="large">
                    <Select.Option value="aws">AWS (Amazon Web Services)</Select.Option>
                    <Select.Option value="azure">Azure (Microsoft)</Select.Option>
                    <Select.Option value="gcp">GCP (Google Cloud)</Select.Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Region" name="region">
                  <Select size="large">
                    <Select.Option value="us-east-1">US East (N. Virginia)</Select.Option>
                    <Select.Option value="us-west-2">US West (Oregon)</Select.Option>
                    <Select.Option value="eu-west-1">EU (Ireland)</Select.Option>
                    <Select.Option value="ap-southeast-1">Asia Pacific (Singapore)</Select.Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="Instance Configuration" style={{ marginBottom: 16 }}>
            <Form.Item label="Instance Type" name="instanceType">
              <Select size="large">
                <Select.Option value="aws-p3.2xlarge">
                  AWS P3.2xlarge - 1x V100 GPU (16GB) - $3.06/hr
                </Select.Option>
                <Select.Option value="aws-p3.8xlarge">
                  AWS P3.8xlarge - 4x V100 GPU (64GB) - $12.24/hr
                </Select.Option>
                <Select.Option value="azure-nc6">
                  Azure NC6 - 1x K80 GPU (12GB) - $0.90/hr
                </Select.Option>
                <Select.Option value="azure-nc12">
                  Azure NC12 - 2x K80 GPU (24GB) - $1.80/hr
                </Select.Option>
                <Select.Option value="gcp-v100">
                  GCP V100 - 1x V100 GPU (16GB) - $2.48/hr
                </Select.Option>
                <Select.Option value="gcp-a100">
                  GCP A100 - 1x A100 GPU (40GB) - $3.67/hr
                </Select.Option>
              </Select>
            </Form.Item>

            <Form.Item label="Estimated Epochs" name="estimatedEpochs">
              <InputNumber min={10} max={1000} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item label="Use Spot Instances (70% cheaper, may be interrupted)" name="useSpot" valuePropName="checked">
              <input type="checkbox" />
            </Form.Item>
          </Card>

          <Card
            title={<><DollarOutlined /> Cost Estimation</>}
            style={{ marginBottom: 16, background: '#fef3c7', border: '1px solid #fde68a' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic title="Estimated Cost" value={`$${estimatedCost.toFixed(2)}`} valueStyle={{ color: '#f59e0b' }} />
                </Col>
                <Col span={12}>
                  <Statistic title="Estimated Time" value="~2-4 hours" />
                </Col>
              </Row>
              <Text type="secondary" style={{ fontSize: 12 }}>
                *This is an estimate. Actual costs may vary based on training time.
              </Text>
            </Space>
          </Card>

          <Button
            type="primary"
            size="large"
            icon={<RocketOutlined />}
            onClick={handleStartTraining}
            block
            disabled={!selectedProject || !healthData?.aws_sagemaker_configured}
            loading={startTrainingMutation.isPending}
          >
            Start Cloud Training
          </Button>

          <Divider />

          <Card style={{ background: '#dbeafe', border: '1px solid #93c5fd' }}>
            <Title level={5}>💡 Benefits of Cloud Training</Title>
            <ul>
              <li>Access to powerful GPUs (V100, A100)</li>
              <li>Train models 10-100x faster</li>
              <li>Pay only for what you use</li>
              <li>Automatic scaling and management</li>
              <li>No local hardware required</li>
            </ul>
          </Card>
        </Form>
      </Card>
    </div>
  );
};

export default CloudTrainingPage;

