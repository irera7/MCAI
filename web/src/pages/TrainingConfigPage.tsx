import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import {
  Card,
  Button,
  Form,
  Slider,
  InputNumber,
  Select,
  Checkbox,
  Typography,
  Row,
  Col,
  Space,
  Statistic,
  Tag,
  App
} from 'antd';
import { LeftOutlined, RocketOutlined } from '@ant-design/icons';
import { trainingApi, projectApi } from '../api/endpoints';
import { useQuery } from '@tanstack/react-query';

const { Title, Text } = Typography;
const { Option } = Select;

const TrainingConfigPage: React.FC = () => {
  const { projectId, modality } = useParams<{ projectId: string; modality?: string }>();
  const [searchParams] = useSearchParams();
  const modelId = searchParams.get('model');
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const { message } = App.useApp();
  
  const [epochs, setEpochs] = useState(50);
  const [batchSize, setBatchSize] = useState(32);
  const [learningRate, setLearningRate] = useState(0.001);
  const [optimizer, setOptimizer] = useState('adam');
  const [dropout, setDropout] = useState(0.2);
  const [gpuAvailable, setGpuAvailable] = useState(false);
  const [gpuName, setGpuName] = useState('Checking...');
  const [starting, setStarting] = useState(false);

  // Load existing project configuration
  const { data: projectData } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      if (!projectId) throw new Error('No project ID');
      const response = await projectApi.get(projectId);
      return response.data;
    },
    enabled: !!projectId,
  });

  // Load configuration from project data
  useEffect(() => {
    if (projectData?.training) {
      const config = projectData.training;
      setEpochs(config.epochs || 50);
      setBatchSize(config.batch_size || 32);
      setLearningRate(config.learning_rate || 0.001);
      setOptimizer(config.optimizer || 'adam');
      setDropout(config.dropout || 0.2);
      
      // Update form fields
      form.setFieldsValue({
        trainSplit: (config.train_split || 0.8) * 100,
        valSplit: (config.val_split || 0.1) * 100,
        testSplit: (config.test_split || 0.1) * 100,
        weightDecay: config.weight_decay || 0.0001,
        dataAugmentation: config.use_augmentation ?? true,
        earlyStopping: config.early_stopping ?? true,
        mixedPrecision: config.mixed_precision ?? false,
      });
    }
  }, [projectData, form]);

  useEffect(() => {
    // Check GPU availability (mock for now)
    setTimeout(() => {
      setGpuAvailable(true);
      setGpuName('NVIDIA GeForce RTX 4060');
    }, 500);
  }, []);

  const handleEpochsChange = (value: number | null) => {
    if (value) setEpochs(value);
  };

  const handleDropoutChange = (value: number | null) => {
    if (value !== null) setDropout(value);
  };

  const handleStartTraining = async () => {
    try {
      setStarting(true);
      
      // Get model_id from URL param or from loaded project data
      const selectedModel = modelId || projectData?.model_name || projectData?.model_type;
      
      if (!selectedModel) {
        message.error('No model selected. Please select a model architecture first.');
        setStarting(false);
        return;
      }
      
      const config = {
        epochs,
        batch_size: batchSize,
        learning_rate: learningRate,
        optimizer,
        model_id: selectedModel,  // Use determined model
        dropout,
        train_split: (form.getFieldValue('trainSplit') || 70) / 100,  // Convert to 0.0-1.0
        val_split: (form.getFieldValue('valSplit') || 20) / 100,
        test_split: (form.getFieldValue('testSplit') || 10) / 100,
        weight_decay: form.getFieldValue('weightDecay') || 0.0001,
        use_augmentation: form.getFieldValue('dataAugmentation') ?? true,
        early_stopping: form.getFieldValue('earlyStopping') ?? true,
        early_stopping_patience: 10,
        mixed_precision: form.getFieldValue('mixedPrecision') ?? false,
        device: 'cuda',
        training_mode: 'local'
      };

      await trainingApi.start(projectId!, config);
      message.success('Training started successfully!');
      navigate(`/training/${projectId}`);
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || 'Unknown error';
      message.error(`Failed to start training: ${errorMessage}`);
      console.error('Training start error:', error);
    } finally {
      setStarting(false);
    }
  };

  const handleBack = () => {
    navigate(-1);
  };

  const estimatedTime = useMemo(() => {
    // Simple estimation based on epochs and batch size
    const baseTime = epochs * (batchSize <= 16 ? 1.5 : batchSize <= 32 ? 1.0 : 0.7);
    return `~${Math.round(baseTime)}-${Math.round(baseTime * 1.3)} minutes`;
  }, [epochs, batchSize]);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#F5F7FA' }}>
      <Row gutter={0} style={{ minHeight: '100vh' }}>
        {/* Left Panel - Configuration */}
        <Col xs={24} lg={16} style={{ padding: 40 }}>
          <Button
            icon={<LeftOutlined />}
            onClick={handleBack}
            style={{ marginBottom: 20 }}
          >
            Back
          </Button>
          
          <Title level={2}>Training Configuration</Title>
          <Text type="secondary" style={{ fontSize: 16, marginBottom: 10, display: 'block' }}>
            Configure hyperparameters and training settings
          </Text>
          
          {/* Show selected model with change option */}
          {(modelId || projectData?.model_name) ? (
            <div style={{ marginBottom: 20, padding: 12, background: '#e6f7ff', borderRadius: 8, border: '1px solid #91d5ff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Text strong>Selected Model: </Text>
                <Tag color="blue" style={{ fontSize: 14 }}>
                  {modelId || projectData?.model_name || projectData?.model_type}
                </Tag>
              </div>
              <Button 
                size="small"
                onClick={() => {
                  const projectModality = modality || projectData?.modality;
                  if (projectModality) {
                    navigate(`/project/${projectId}/model-selection/${projectModality}`);
                  } else {
                    message.warning('Cannot determine project modality');
                  }
                }}
              >
                Change Model
              </Button>
            </div>
          ) : (
            <div style={{ marginBottom: 20, padding: 12, background: '#fff2e8', borderRadius: 8, border: '1px solid #ffbb96' }}>
              <Text type="warning" strong>⚠️ No model selected. </Text>
              <Button 
                type="link" 
                size="small"
                onClick={() => {
                  const projectModality = modality || projectData?.modality;
                  if (projectModality) {
                    navigate(`/project/${projectId}/model-selection/${projectModality}`);
                  } else {
                    message.warning('Cannot determine project modality');
                  }
                }}
              >
                Select Model
              </Button>
            </div>
          )}

          <Form
            form={form}
            layout="vertical"
            initialValues={{
              trainSplit: 70,
              valSplit: 20,
              testSplit: 10,
              weightDecay: 0.0001,
              dataAugmentation: true,
              earlyStopping: true,
              mixedPrecision: false
            }}
          >
            {/* Basic Settings */}
            <Card title="⚙️ Basic Settings" style={{ marginBottom: 20 }}>
              <Form.Item 
                label={
                  <div>
                    <Text strong>Number of Epochs</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 11 }}>Complete passes through the training data</Text>
                  </div>
                }
              >
                <Row gutter={16}>
                  <Col flex="auto">
                    <Slider
                      min={10}
                      max={200}
                      step={10}
                      value={epochs}
                      onChange={handleEpochsChange}
                    />
                  </Col>
                  <Col>
                    <InputNumber
                      min={10}
                      max={200}
                      value={epochs}
                      onChange={handleEpochsChange}
                      style={{ width: 80 }}
                    />
                  </Col>
                </Row>
              </Form.Item>

              <Form.Item
                label={
                  <div>
                    <Text strong>Batch Size</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 11 }}>Number of samples per training batch</Text>
                  </div>
                }
              >
                <Select value={batchSize} onChange={setBatchSize} size="large">
                  <Option value={8}>8 (Very small datasets)</Option>
                  <Option value={16}>16 (Small datasets)</Option>
                  <Option value={32}>32 (Recommended)</Option>
                  <Option value={64}>64 (Large datasets, GPU required)</Option>
                  <Option value={128}>128 (Very large datasets, powerful GPU)</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label={
                  <div>
                    <Text strong>Learning Rate</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 11 }}>Step size for model updates</Text>
                  </div>
                }
              >
                <Select value={learningRate} onChange={setLearningRate} size="large">
                  <Option value={0.0001}>0.0001 (Very conservative)</Option>
                  <Option value={0.0005}>0.0005 (Conservative)</Option>
                  <Option value={0.001}>0.001 (Recommended)</Option>
                  <Option value={0.005}>0.005 (Aggressive)</Option>
                  <Option value={0.01}>0.01 (Very aggressive)</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label={
                  <div>
                    <Text strong>Optimizer</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 11 }}>Algorithm for updating model weights</Text>
                  </div>
                }
              >
                <Select value={optimizer} onChange={setOptimizer} size="large">
                  <Option value="adam">Adam (Recommended - Most versatile)</Option>
                  <Option value="adamw">AdamW (Adam with weight decay)</Option>
                  <Option value="sgd">SGD (Stochastic Gradient Descent)</Option>
                  <Option value="rmsprop">RMSprop (Good for RNNs)</Option>
                </Select>
              </Form.Item>
            </Card>

            {/* Advanced Settings */}
            <Card title="🔧 Advanced Settings">
              <Row gutter={16} style={{ marginBottom: 20 }}>
                <Col span={8}>
                  <Form.Item label="Train Split %" name="trainSplit">
                    <InputNumber min={50} max={90} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="Validation Split %" name="valSplit">
                    <InputNumber min={5} max={30} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="Test Split %" name="testSplit">
                    <InputNumber min={5} max={30} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                label={
                  <div>
                    <Text strong>Dropout Rate</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 11 }}>Regularization to prevent overfitting (0.0 - 0.5)</Text>
                  </div>
                }
              >
                <Row gutter={16}>
                  <Col flex="auto">
                    <Slider
                      min={0}
                      max={0.5}
                      step={0.05}
                      value={dropout}
                      onChange={handleDropoutChange}
                    />
                  </Col>
                  <Col>
                    <InputNumber
                      min={0}
                      max={0.5}
                      step={0.05}
                      value={dropout}
                      onChange={handleDropoutChange}
                      style={{ width: 80 }}
                    />
                  </Col>
                </Row>
              </Form.Item>

              <Form.Item
                label={
                  <div>
                    <Text strong>Weight Decay</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 11 }}>L2 regularization strength</Text>
                  </div>
                }
                name="weightDecay"
              >
                <Select size="large">
                  <Option value={0}>0 (No regularization)</Option>
                  <Option value={0.00001}>0.00001 (Light)</Option>
                  <Option value={0.0001}>0.0001 (Recommended)</Option>
                  <Option value={0.001}>0.001 (Strong)</Option>
                </Select>
              </Form.Item>

              <Space direction="vertical" size="small">
                <Form.Item name="dataAugmentation" valuePropName="checked" style={{ marginBottom: 0 }}>
                  <Checkbox>Enable Data Augmentation</Checkbox>
                </Form.Item>
                <Form.Item name="earlyStopping" valuePropName="checked" style={{ marginBottom: 0 }}>
                  <Checkbox>Enable Early Stopping (patience: 10 epochs)</Checkbox>
                </Form.Item>
                <Form.Item name="mixedPrecision" valuePropName="checked" style={{ marginBottom: 0 }}>
                  <Checkbox>Mixed Precision Training (FP16, requires GPU)</Checkbox>
                </Form.Item>
              </Space>
            </Card>
          </Form>
        </Col>

        {/* Right Panel - Summary */}
        <Col 
          xs={24} 
          lg={8} 
          style={{ 
            backgroundColor: '#FFFFFF', 
            borderLeft: '1px solid #E5E7EB', 
            padding: 30 
          }}
        >
          <Title level={4}>Configuration Summary</Title>

          <Card size="small" style={{ marginBottom: 16 }}>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Row justify="space-between">
                <Text type="secondary">Epochs:</Text>
                <Text strong>{epochs}</Text>
              </Row>
              <Row justify="space-between">
                <Text type="secondary">Batch Size:</Text>
                <Text strong>{batchSize}</Text>
              </Row>
              <Row justify="space-between">
                <Text type="secondary">Learning Rate:</Text>
                <Text strong>{learningRate}</Text>
              </Row>
              <Row justify="space-between">
                <Text type="secondary">Optimizer:</Text>
                <Text strong>{optimizer.toUpperCase()}</Text>
              </Row>
              <Row justify="space-between">
                <Text type="secondary">Augmentation:</Text>
                <Tag color={form.getFieldValue('dataAugmentation') ? 'success' : 'default'}>
                  {form.getFieldValue('dataAugmentation') ? 'Enabled' : 'Disabled'}
                </Tag>
              </Row>
            </Space>
          </Card>

          <Card size="small" style={{ marginBottom: 16, textAlign: 'center' }}>
            <Statistic 
              title="Estimated Training Time" 
              value={estimatedTime} 
              valueStyle={{ color: '#6366F1', fontSize: 18 }}
            />
            <Text type="secondary" style={{ fontSize: 10 }}>(Based on selected configuration)</Text>
          </Card>

          <Card size="small" title="💻 System" style={{ marginBottom: 30 }}>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Row justify="space-between">
                <Text type="secondary">GPU:</Text>
                <Text strong style={{ color: gpuAvailable ? '#22C55E' : '#EF4444' }}>
                  {gpuAvailable ? '✓ ' + gpuName : 'Not detected'}
                </Text>
              </Row>
              <Row justify="space-between">
                <Text type="secondary">GPU Memory:</Text>
                <Text>8.0 GB</Text>
              </Row>
              <Row justify="space-between">
                <Text type="secondary">RAM:</Text>
                <Text>Available</Text>
              </Row>
            </Space>
          </Card>

          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Button 
              size="large" 
              icon={<LeftOutlined />}
              onClick={handleBack}
              style={{ width: '100%' }}
            >
              Back
            </Button>
            <Button 
              type="primary" 
              size="large" 
              icon={<RocketOutlined />}
              onClick={handleStartTraining}
              loading={starting}
              style={{ width: '100%', height: 55, fontSize: 18, fontWeight: 'bold' }}
            >
              Start Training
            </Button>
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default TrainingConfigPage;

