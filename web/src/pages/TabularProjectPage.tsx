import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Select, Steps, Space, Typography, Divider, Checkbox, Radio, App } from 'antd';
import { ArrowLeftOutlined, ArrowRightOutlined, CheckOutlined } from '@ant-design/icons';
import { useMutation, useQuery } from '@tanstack/react-query';
import { projectApi, dataApi, systemApi } from '../api/endpoints';
import FileUploader from '../components/FileUploader';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;

const TabularProjectPage: React.FC = () => {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [projectId, setProjectId] = useState<string>('');
  const [projectName, setProjectName] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [datasetUploaded, setDatasetUploaded] = useState(false);
  const [featureEngineering, setFeatureEngineering] = useState({
    scaling: 'standard',
    missingValues: 'mean',
    encoding: 'onehot',
    featureSelection: false,
  });
  const [form] = Form.useForm();

  const { data: modelsData } = useQuery({
    queryKey: ['models', 'tabular'],
    queryFn: async () => {
      const response = await systemApi.models('tabular');
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
    message.success('Dataset uploaded successfully');
  };

  const handleCreateProject = () => {
    form.validateFields().then((values) => {
      setProjectName(values.projectName);
      createProjectMutation.mutate({
        name: values.projectName,
        modality: 'tabular',
        description: values.description,
      });
    });
  };

  const handleNext = () => {
    if (currentStep === 0) {
      handleCreateProject();
    } else if (currentStep === 1) {
      if (!datasetUploaded) {
        message.warning('Please upload a dataset');
        return;
      }
      setCurrentStep(2);
    } else if (currentStep === 2) {
      // Navigate to Model Selection page
      navigate(`/project/${projectId}/model-selection/tabular`);
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
        <Title level={2}>📊 Tabular Data Project</Title>
        <Paragraph>
          Create a project for tabular data classification using XGBoost, LightGBM, or Neural Networks.
        </Paragraph>

        <Steps current={currentStep} style={{ marginBottom: 32 }}>
          <Step title="Project Setup" />
          <Step title="Upload Data" />
          <Step title="Feature Engineering" />
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
                <Input placeholder="e.g., Customer Churn Prediction" size="large" />
              </Form.Item>
              <Form.Item label="Description" name="description">
                <Input.TextArea placeholder="Optional: Describe your project" rows={3} />
              </Form.Item>
            </Form>
          </div>
        )}

        {currentStep === 1 && (
          <div>
            <Title level={4}>Step 2: Upload Tabular Dataset</Title>
            <Paragraph>
              Upload your CSV file with features and target column.
            </Paragraph>

            <FileUploader
              accept=".csv"
              multiple={false}
              maxSize={100}
              onUpload={handleUpload}
              description="Upload CSV file with labeled data"
            />
          </div>
        )}

        {currentStep === 2 && (
          <div>
            <Title level={4}>Step 3: Feature Engineering</Title>
            <Paragraph>Configure preprocessing and feature engineering options.</Paragraph>

            <Form layout="vertical" style={{ maxWidth: 700 }}>
              <Form.Item label="Feature Scaling">
                <Radio.Group
                  value={featureEngineering.scaling}
                  onChange={(e) => setFeatureEngineering({ ...featureEngineering, scaling: e.target.value })}
                >
                  <Radio value="standard">Standard Scaler</Radio>
                  <Radio value="minmax">MinMax Scaler</Radio>
                  <Radio value="robust">Robust Scaler</Radio>
                  <Radio value="none">None</Radio>
                </Radio.Group>
              </Form.Item>

              <Form.Item label="Missing Value Handling">
                <Radio.Group
                  value={featureEngineering.missingValues}
                  onChange={(e) => setFeatureEngineering({ ...featureEngineering, missingValues: e.target.value })}
                >
                  <Radio value="mean">Fill with Mean</Radio>
                  <Radio value="median">Fill with Median</Radio>
                  <Radio value="drop">Drop Rows</Radio>
                </Radio.Group>
              </Form.Item>

              <Form.Item label="Categorical Encoding">
                <Radio.Group
                  value={featureEngineering.encoding}
                  onChange={(e) => setFeatureEngineering({ ...featureEngineering, encoding: e.target.value })}
                >
                  <Radio value="onehot">One-Hot Encoding</Radio>
                  <Radio value="label">Label Encoding</Radio>
                </Radio.Group>
              </Form.Item>

              <Form.Item>
                <Checkbox
                  checked={featureEngineering.featureSelection}
                  onChange={(e) => setFeatureEngineering({ ...featureEngineering, featureSelection: e.target.checked })}
                >
                  Enable Feature Selection (Remove low-importance features)
                </Checkbox>
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
            {currentStep === 1 && 'Continue to Feature Engineering'}
            {currentStep === 2 && 'Continue to Model Selection'}
            {currentStep === 3 && 'Start Training'}
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default TabularProjectPage;

