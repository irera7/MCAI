import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Select, Steps, Space, Typography, Divider, Table, Tag, Radio, App } from 'antd';
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

const MedicalProjectPage: React.FC = () => {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [projectId, setProjectId] = useState<string>('');
  const [projectName, setProjectName] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [currentClass, setCurrentClass] = useState('');
  const [classes, setClasses] = useState<ClassData[]>([]);
  const [dataType, setDataType] = useState<'mri' | 'ecg' | 'eeg'>('mri');
  const [form] = Form.useForm();

  const { data: modelsData } = useQuery({
    queryKey: ['models', 'medical'],
    queryFn: async () => {
      const response = await systemApi.models('medical');
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
    formData.append('data_type', dataType);

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
        modality: 'medical',
        description: values.description,
      });
    });
  };

  const handleNext = () => {
    if (currentStep === 0) {
      handleCreateProject();
    } else if (currentStep === 1) {
      if (classes.length < 2) {
        message.warning('Please upload medical data for at least 2 classes');
        return;
      }
      // Navigate to Model Selection page
      navigate(`/project/${projectId}/model-selection/medical`);
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
      render: (name: string) => <Tag color="purple">{name}</Tag>,
    },
    {
      title: 'Sample Count',
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
        <Title level={2}>🏥 Medical Imaging Project</Title>
        <Paragraph>
          Create a project for medical data classification using specialized CNN architectures for MRI, ECG, and EEG analysis.
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
                <Input placeholder="e.g., Brain Tumor Detection" size="large" />
              </Form.Item>
              <Form.Item label="Description" name="description">
                <Input.TextArea placeholder="Optional: Describe your project" rows={3} />
              </Form.Item>
              <Form.Item label="Medical Data Type">
                <Radio.Group value={dataType} onChange={(e) => setDataType(e.target.value)}>
                  <Radio value="mri">MRI Scans</Radio>
                  <Radio value="ecg">ECG Signals</Radio>
                  <Radio value="eeg">EEG Signals</Radio>
                </Radio.Group>
              </Form.Item>
            </Form>
          </div>
        )}

        {currentStep === 1 && (
          <div>
            <Title level={4}>Step 2: Upload Medical Data</Title>
            <Paragraph>
              Upload {dataType.toUpperCase()} files for each class (diagnosis/condition).
            </Paragraph>

            <Card style={{ marginBottom: 16, background: '#f9fafb' }}>
              <Text strong>Current Class (Diagnosis):</Text>
              <Input
                placeholder="Enter diagnosis/class name (e.g., 'normal', 'tumor')"
                value={currentClass}
                onChange={(e) => setCurrentClass(e.target.value)}
                size="large"
                style={{ marginTop: 8 }}
              />
            </Card>

            <FileUploader
              accept={dataType === 'mri' ? '.nii,.nii.gz,.dcm' : '.csv,.txt'}
              multiple={true}
              maxSize={100}
              onUpload={handleUpload}
              disabled={!currentClass}
              description={`Upload ${dataType.toUpperCase()} files for the current diagnosis`}
            />

            <Divider />

            <Title level={5}>Uploaded Classes</Title>
            <Table columns={classColumns} dataSource={classes} rowKey="name" pagination={false} size="small" />

            {classes.length > 0 && (
              <Card style={{ marginTop: 16, background: '#fce7f3', border: '1px solid #f9a8d4' }}>
                <Space>
                  <CheckOutlined style={{ color: '#a855f7' }} />
                  <Text>Total: {classes.length} classes, {classes.reduce((sum, c) => sum + c.count, 0)} samples</Text>
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

export default MedicalProjectPage;

