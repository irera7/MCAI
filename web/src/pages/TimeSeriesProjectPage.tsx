import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Select, Steps, Space, Typography, Divider, Radio, Checkbox, InputNumber, App } from 'antd';
import { ArrowLeftOutlined, ArrowRightOutlined, CheckOutlined } from '@ant-design/icons';
import { useMutation, useQuery } from '@tanstack/react-query';
import { projectApi, dataApi, systemApi } from '../api/endpoints';
import FileUploader from '../components/FileUploader';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;

const TimeSeriesProjectPage: React.FC = () => {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [projectId, setProjectId] = useState<string>('');
  const [projectName, setProjectName] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [datasetUploaded, setDatasetUploaded] = useState(false);
  const [taskType, setTaskType] = useState<'forecasting' | 'classification'>('forecasting');
  const [preprocessing, setPreprocessing] = useState({
    removeTrend: false,
    removeSeasonality: false,
    differencing: false,
    normalize: true,
    windowSize: 24,
  });
  const [form] = Form.useForm();

  const { data: modelsData } = useQuery({
    queryKey: ['models', 'timeseries'],
    queryFn: async () => {
      const response = await systemApi.models('timeseries');
      return response.data;
    },
  });

  const createProjectMutation = useMutation({
    mutationFn: (data: { name: string; modality: string; description?: string }) =>
      projectApi.create(data),
    onSuccess: (response) => {
      setProjectId(response.data.id);
      message.success('Project created successfully');
      setCurrentStep(1);
    },
    onError: (error: any) => {
      message.error(`Failed to create project: ${error.detail || error.message}`);
    },
  });

  const handleUpload = async (file: File, onProgress: (progress: number) => void) => {
    if (!projectId) throw new Error('Project not created yet');

    const formData = new FormData();
    formData.append('file', file);

    await dataApi.upload(projectId, formData, onProgress);
    setDatasetUploaded(true);
    message.success('Time series data uploaded successfully');
  };

  const handleCreateProject = () => {
    form.validateFields().then((values) => {
      setProjectName(values.projectName);
      createProjectMutation.mutate({
        name: values.projectName,
        modality: 'timeseries',
        description: values.description,
      });
    });
  };

  const handleNext = () => {
    if (currentStep === 0) {
      handleCreateProject();
    } else if (currentStep === 1) {
      if (!datasetUploaded) {
        message.warning('Please upload time series data');
        return;
      }
      setCurrentStep(2);
    } else if (currentStep === 2) {
      // Navigate to Model Selection page
      navigate(`/project/${projectId}/model-selection/timeseries`);
    } else if (currentStep === 3) {
      if (!selectedModel) {
        message.warning('Please select a model');
        return;
      }
      navigate(`/training/${projectId}`);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')} style={{ marginBottom: 16 }}>
        Back to Home
      </Button>

      <Card>
        <Title level={2}>📈 Time Series Project</Title>
        <Paragraph>
          Create a project for time series forecasting or classification using LSTM and Attention-LSTM models.
        </Paragraph>

        <Steps current={currentStep} style={{ marginBottom: 32 }}>
          <Step title="Project Setup" />
          <Step title="Upload Data" />
          <Step title="Preprocessing" />
          <Step title="Model Selection" />
        </Steps>

        {currentStep === 0 && (
          <div>
            <Title level={4}>Step 1: Project Setup</Title>
            <Form form={form} layout="vertical" style={{ maxWidth: 600 }}>
              <Form.Item
                label="Project Name"
                name="projectName"
                rules={[{ required: true, message: 'Please enter project name' }]}
              >
                <Input placeholder="e.g., Stock Price Prediction" size="large" />
              </Form.Item>
              <Form.Item label="Description" name="description">
                <Input.TextArea placeholder="Optional: Describe your project" rows={3} />
              </Form.Item>
              <Form.Item label="Task Type">
                <Radio.Group value={taskType} onChange={(e) => setTaskType(e.target.value)}>
                  <Radio value="forecasting">Forecasting</Radio>
                  <Radio value="classification">Classification</Radio>
                </Radio.Group>
              </Form.Item>
            </Form>
          </div>
        )}

        {currentStep === 1 && (
          <div>
            <Title level={4}>Step 2: Upload Time Series Data</Title>
            <Paragraph>
              Upload your CSV file with time series data. Format: timestamp, value columns.
            </Paragraph>

            <FileUploader
              accept=".csv"
              multiple={false}
              maxSize={50}
              onUpload={handleUpload}
              description="Upload CSV file with time series data"
            />
          </div>
        )}

        {currentStep === 2 && (
          <div>
            <Title level={4}>Step 3: Preprocessing Options</Title>
            <Paragraph>Configure time series preprocessing methods.</Paragraph>

            <Form layout="vertical" style={{ maxWidth: 700 }}>
              <Form.Item label="Preprocessing Methods">
                <Space direction="vertical">
                  <Checkbox
                    checked={preprocessing.removeTrend}
                    onChange={(e) => setPreprocessing({ ...preprocessing, removeTrend: e.target.checked })}
                  >
                    Remove Trend (Detrending)
                  </Checkbox>
                  <Checkbox
                    checked={preprocessing.removeSeasonality}
                    onChange={(e) => setPreprocessing({ ...preprocessing, removeSeasonality: e.target.checked })}
                  >
                    Remove Seasonality
                  </Checkbox>
                  <Checkbox
                    checked={preprocessing.differencing}
                    onChange={(e) => setPreprocessing({ ...preprocessing, differencing: e.target.checked })}
                  >
                    Apply Differencing
                  </Checkbox>
                  <Checkbox
                    checked={preprocessing.normalize}
                    onChange={(e) => setPreprocessing({ ...preprocessing, normalize: e.target.checked })}
                  >
                    Normalize Data
                  </Checkbox>
                </Space>
              </Form.Item>

              <Form.Item label="Window Size (Lookback Period)">
                <InputNumber
                  min={1}
                  max={365}
                  value={preprocessing.windowSize}
                  onChange={(val) => setPreprocessing({ ...preprocessing, windowSize: val || 24 })}
                  style={{ width: 200 }}
                />
                <Text type="secondary" style={{ marginLeft: 8 }}>
                  Number of past time steps to use for prediction
                </Text>
              </Form.Item>
            </Form>
          </div>
        )}

        {currentStep === 3 && (
          <div>
            <Title level={4}>Step 4: Choose Model</Title>
            <Form layout="vertical" style={{ maxWidth: 600 }}>
              <Form.Item label="Model Architecture">
                <Select
                  size="large"
                  placeholder="Select a model"
                  value={selectedModel}
                  onChange={setSelectedModel}
                >
                  {modelsData?.models?.map((model) => (
                    <Select.Option key={model.id} value={model.id}>
                      <Text strong>{model.name}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: 12 }}>{model.description}</Text>
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Form>
          </div>
        )}

        <Divider />

        <Space>
          {currentStep > 0 && (
            <Button onClick={() => setCurrentStep(currentStep - 1)} icon={<ArrowLeftOutlined />}>
              Back
            </Button>
          )}
          <Button
            type="primary"
            onClick={handleNext}
            icon={currentStep === 3 ? <CheckOutlined /> : <ArrowRightOutlined />}
            loading={createProjectMutation.isPending}
          >
            {currentStep === 0 && 'Create Project'}
            {currentStep === 1 && 'Continue to Preprocessing'}
            {currentStep === 2 && 'Continue to Model Selection'}
            {currentStep === 3 && 'Start Training'}
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default TimeSeriesProjectPage;

