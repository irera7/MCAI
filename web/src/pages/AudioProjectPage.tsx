import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Select, Steps, Space, Typography, Divider, Table, Tag, App } from 'antd';
import { ArrowLeftOutlined, ArrowRightOutlined, CheckOutlined } from '@ant-design/icons';
import { useMutation, useQuery } from '@tanstack/react-query';
import { projectApi, dataApi, systemApi } from '../api/endpoints';
import FileUploader from '../components/FileUploader';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;

interface ClassData {
  name: string;
  count: number;
}

const AudioProjectPage: React.FC = () => {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [projectId, setProjectId] = useState<string>('');
  const [projectName, setProjectName] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [currentClass, setCurrentClass] = useState('');
  const [classes, setClasses] = useState<ClassData[]>([]);
  const [form] = Form.useForm();

  const { data: modelsData } = useQuery({
    queryKey: ['models', 'audio'],
    queryFn: async () => {
      const response = await systemApi.models('audio');
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
    if (!currentClass) throw new Error('Please enter a class name first');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('class_name', currentClass);

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

  const handleCreateProject = () => {
    form.validateFields().then((values) => {
      setProjectName(values.projectName);
      createProjectMutation.mutate({
        name: values.projectName,
        modality: 'audio',
        description: values.description,
      });
    });
  };

  const handleNext = () => {
    if (currentStep === 0) {
      handleCreateProject();
    } else if (currentStep === 1) {
      if (classes.length < 2) {
        message.warning('Please upload audio files for at least 2 classes');
        return;
      }
      // Navigate to Model Selection page
      navigate(`/project/${projectId}/model-selection/audio`);
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
      render: (name: string) => <Tag color="cyan">{name}</Tag>,
    },
    {
      title: 'Audio Count',
      dataIndex: 'count',
      key: 'count',
      render: (count: number) => <Text strong>{count}</Text>,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')} style={{ marginBottom: 16 }}>
        Back to Home
      </Button>

      <Card>
        <Title level={2}>🎵 Audio Classification Project</Title>
        <Paragraph>
          Create a project to train audio classification models using Spectrogram CNN and other audio processing networks.
        </Paragraph>

        <Steps current={currentStep} style={{ marginBottom: 32 }}>
          <Step title="Project Setup" />
          <Step title="Upload Data" />
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
                <Input placeholder="e.g., Music Genre Classifier" size="large" />
              </Form.Item>
              <Form.Item label="Description" name="description">
                <Input.TextArea placeholder="Optional: Describe your project" rows={3} />
              </Form.Item>
            </Form>
          </div>
        )}

        {currentStep === 1 && (
          <div>
            <Title level={4}>Step 2: Upload Audio Files</Title>
            <Paragraph>
              Upload audio files for each class. Supported formats: WAV, MP3, FLAC.
            </Paragraph>

            <Card style={{ marginBottom: 16, background: '#f9fafb' }}>
              <Text strong>Current Class:</Text>
              <Input
                placeholder="Enter class name (e.g., 'jazz', 'rock')"
                value={currentClass}
                onChange={(e) => setCurrentClass(e.target.value)}
                size="large"
                style={{ marginTop: 8 }}
              />
            </Card>

            <FileUploader
              accept=".wav,.mp3,.flac"
              multiple={true}
              maxSize={50}
              onUpload={handleUpload}
              disabled={!currentClass}
              description="Upload audio files for the current class"
            />

            <Divider />

            <Title level={5}>Uploaded Classes</Title>
            <Table columns={classColumns} dataSource={classes} rowKey="name" pagination={false} size="small" />

            {classes.length > 0 && (
              <Card style={{ marginTop: 16, background: '#cffafe', border: '1px solid #67e8f9' }}>
                <Space>
                  <CheckOutlined style={{ color: '#0891b2' }} />
                  <Text>Total: {classes.length} classes, {classes.reduce((sum, c) => sum + c.count, 0)} files</Text>
                </Space>
              </Card>
            )}
          </div>
        )}

        {currentStep === 2 && (
          <div>
            <Title level={4}>Step 3: Choose Model</Title>
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
            icon={currentStep === 2 ? <CheckOutlined /> : <ArrowRightOutlined />}
            loading={createProjectMutation.isPending}
          >
            {currentStep === 0 && 'Create Project'}
            {currentStep === 1 && 'Continue to Model Selection'}
            {currentStep === 2 && 'Start Training'}
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default AudioProjectPage;

