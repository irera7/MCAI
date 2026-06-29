import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Select, Steps, Space, Typography, Divider, Table, Tag, Radio, App } from 'antd';
import { ArrowLeftOutlined, ArrowRightOutlined, CheckOutlined } from '@ant-design/icons';
import { useMutation, useQuery } from '@tanstack/react-query';
import { projectApi, dataApi, systemApi } from '../api/endpoints';
import FileUploader from '../components/FileUploader';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;
const { TextArea } = Input;

interface ClassData {
  name: string;
  count: number;
}

const TextProjectPage: React.FC = () => {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [projectId, setProjectId] = useState<string>('');
  const [projectName, setProjectName] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [currentClass, setCurrentClass] = useState('');
  const [classes, setClasses] = useState<ClassData[]>([]);
  const [inputMethod, setInputMethod] = useState<'file' | 'text'>('file');
  const [textInput, setTextInput] = useState('');
  const [form] = Form.useForm();

  // Fetch available models
  const { data: modelsData } = useQuery({
    queryKey: ['models', 'text'],
    queryFn: async () => {
      const response = await systemApi.models('text');
      return response.data;
    },
  });

  // Create project mutation
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

  // Upload file handler
  const handleUpload = async (file: File, onProgress: (progress: number) => void) => {
    if (!projectId) throw new Error('Project not created yet');
    if (!currentClass) throw new Error('Please enter a class name first');

    const formData = new FormData();
    formData.append('files', file);  // Changed from 'file' to 'files'
    formData.append('label', currentClass);  // Changed from 'class_name' to 'label'

    await dataApi.upload(projectId, formData, onProgress);
    
    setClasses((prev) => {
      const existing = prev.find((c) => c.name === currentClass);
      if (existing) {
        return prev.map((c) =>
          c.name === currentClass ? { ...c, count: c.count + 1 } : c
        );
      }
      return [...prev, { name: currentClass, count: 1 }];
    });
  };

  // Add text manually
  const handleAddText = async () => {
    if (!textInput.trim()) {
      message.warning('Please enter some text');
      return;
    }
    if (!currentClass) {
      message.warning('Please enter a class name');
      return;
    }

    // Create a text file blob
    const blob = new Blob([textInput], { type: 'text/plain' });
    const file = new File([blob], `text_${Date.now()}.txt`, { type: 'text/plain' });

    await handleUpload(file, () => {});
    setTextInput('');
    message.success('Text added successfully');
  };

  const handleCreateProject = () => {
    form.validateFields().then((values) => {
      setProjectName(values.projectName);
      createProjectMutation.mutate({
        name: values.projectName,
        modality: 'text',
        description: values.description,
      });
    });
  };

  const handleNext = () => {
    if (currentStep === 0) {
      handleCreateProject();
    } else if (currentStep === 1) {
      if (classes.length < 2) {
        message.warning('Please upload text data for at least 2 classes');
        return;
      }
      // Navigate to Model Selection page
      navigate(`/project/${projectId}/model-selection/text`);
    } else if (currentStep === 2) {
      if (!selectedModel) {
        message.warning('Please select a model');
        return;
      }
      navigate(`/training/${projectId}`);
    }
  };

  const classColumns = [
    {
      title: 'Class Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => <Tag color="gold">{name}</Tag>,
    },
    {
      title: 'Text Count',
      dataIndex: 'count',
      key: 'count',
      render: (count: number) => <Text strong>{count}</Text>,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/')}
        style={{ marginBottom: 16 }}
      >
        Back to Home
      </Button>

      <Card>
        <Title level={2}>📝 Text Classification Project</Title>
        <Paragraph>
          Create a project to train text classification models using LSTM, BERT, or Transformer architectures.
        </Paragraph>

        <Steps current={currentStep} style={{ marginBottom: 32 }}>
          <Step title="Project Setup" description="Create project" />
          <Step title="Upload Data" description="Upload text data" />
          <Step title="Model Selection" description="Choose model" />
        </Steps>

        {/* Step 0: Project Setup */}
        {currentStep === 0 && (
          <div>
            <Title level={4}>Step 1: Project Setup</Title>
            <Form form={form} layout="vertical" style={{ maxWidth: 600 }}>
              <Form.Item
                label="Project Name"
                name="projectName"
                rules={[{ required: true, message: 'Please enter project name' }]}
              >
                <Input placeholder="e.g., Sentiment Analysis" size="large" />
              </Form.Item>
              <Form.Item label="Description" name="description">
                <TextArea placeholder="Optional: Describe your project" rows={3} />
              </Form.Item>
            </Form>
          </div>
        )}

        {/* Step 1: Upload Data */}
        {currentStep === 1 && (
          <div>
            <Title level={4}>Step 2: Upload Text Data</Title>
            <Paragraph>
              Upload text files for each class or manually enter text samples.
            </Paragraph>

            <Card style={{ marginBottom: 16, background: '#f9fafb' }}>
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                <div>
                  <Text strong>Current Class:</Text>
                  <Input
                    placeholder="Enter class name (e.g., 'positive', 'negative')"
                    value={currentClass}
                    onChange={(e) => setCurrentClass(e.target.value)}
                    size="large"
                    style={{ marginTop: 8 }}
                  />
                </div>

                <div>
                  <Text strong>Input Method:</Text>
                  <Radio.Group
                    value={inputMethod}
                    onChange={(e) => setInputMethod(e.target.value)}
                    style={{ marginTop: 8, display: 'block' }}
                  >
                    <Radio value="file">Upload Text Files</Radio>
                    <Radio value="text">Enter Text Manually</Radio>
                  </Radio.Group>
                </div>
              </Space>
            </Card>

            {inputMethod === 'file' ? (
              <FileUploader
                accept=".txt,.csv"
                multiple={true}
                maxSize={5}
                onUpload={handleUpload}
                disabled={!currentClass}
                description="Upload text files (.txt, .csv) for the current class"
              />
            ) : (
              <div>
                <TextArea
                  rows={6}
                  placeholder="Enter text sample here..."
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  disabled={!currentClass}
                />
                <Button
                  type="primary"
                  onClick={handleAddText}
                  style={{ marginTop: 8 }}
                  disabled={!currentClass || !textInput.trim()}
                >
                  Add Text
                </Button>
              </div>
            )}

            <Divider />

            <Title level={5}>Uploaded Classes</Title>
            <Table
              columns={classColumns}
              dataSource={classes}
              rowKey="name"
              pagination={false}
              size="small"
            />

            {classes.length > 0 && (
              <Card style={{ marginTop: 16, background: '#fef3c7', border: '1px solid #fde68a' }}>
                <Space>
                  <CheckOutlined style={{ color: '#f59e0b' }} />
                  <Text>
                    Total: {classes.length} classes, {classes.reduce((sum, c) => sum + c.count, 0)} samples
                  </Text>
                </Space>
              </Card>
            )}
          </div>
        )}

        {/* Step 2: Model Selection */}
        {currentStep === 2 && (
          <div>
            <Title level={4}>Step 3: Choose Model</Title>
            <Paragraph>
              Select a model architecture for text classification.
            </Paragraph>

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
                      <div>
                        <Text strong>{model.name}</Text>
                        <br />
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {model.description}
                        </Text>
                      </div>
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Form>

            <Card style={{ marginTop: 16, background: '#fef3c7', border: '1px solid #fde68a' }}>
              <Title level={5}>Project Summary</Title>
              <Space direction="vertical">
                <Text><Text strong>Project:</Text> {projectName}</Text>
                <Text><Text strong>Classes:</Text> {classes.length}</Text>
                <Text><Text strong>Total Samples:</Text> {classes.reduce((sum, c) => sum + c.count, 0)}</Text>
                <Text><Text strong>Model:</Text> {selectedModel || 'Not selected'}</Text>
              </Space>
            </Card>
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
            icon={currentStep === 2 ? <CheckOutlined /> : <ArrowRightOutlined />}
            loading={createProjectMutation.isPending}
          >
            {currentStep === 0 && 'Create Project'}
            {currentStep === 1 && 'Next: Select Model →'}
            {currentStep === 2 && 'Start Training'}
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default TextProjectPage;

