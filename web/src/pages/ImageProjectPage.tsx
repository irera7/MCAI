import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Card, Form, Input, Button, Select, Steps, Space, Typography, Divider, 
  Table, Tag, App, Row, Col, Statistic, Upload, Progress, message as antdMessage 
} from 'antd';
import { 
  ArrowLeftOutlined, ArrowRightOutlined, CheckOutlined, 
  InboxOutlined, PlusOutlined, DeleteOutlined,
  FileImageOutlined 
} from '@ant-design/icons';
import { useMutation, useQuery } from '@tanstack/react-query';
import { projectApi, dataApi, systemApi } from '../api/endpoints';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;
const { Dragger } = Upload;

interface ClassData {
  name: string;
  count: number;
}

interface FileItem {
  file: File;
  label: string | null;
  preview?: string;
}

const ImageProjectPage: React.FC = () => {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [projectId, setProjectId] = useState<string>('');
  const [projectName, setProjectName] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [labels, setLabels] = useState<string[]>([]);
  const [newLabel, setNewLabel] = useState('');
  const [files, setFiles] = useState<FileItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [form] = Form.useForm();

  // Fetch available models
  const { data: modelsData } = useQuery({
    queryKey: ['models', 'image'],
    queryFn: async () => {
      const response = await systemApi.models('image');
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

  // Add label
  const handleAddLabel = () => {
    if (!newLabel.trim()) {
      message.warning('Please enter a label name');
      return;
    }
    if (labels.includes(newLabel.trim())) {
      message.warning('This label already exists');
      return;
    }
    setLabels([...labels, newLabel.trim()]);
    setNewLabel('');
    message.success(`Label "${newLabel}" added`);
  };

  // Remove label
  const handleRemoveLabel = (label: string) => {
    setLabels(labels.filter(l => l !== label));
    // Remove label from files
    setFiles(files.map(f => f.label === label ? { ...f, label: null } : f));
    message.success(`Label "${label}" removed`);
  };

  // Handle folder upload
  const handleFolderUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = Array.from(e.target.files || []);
    if (fileList.length === 0) return;

    const newFiles: FileItem[] = [];
    const csvMappings = (window as any).csvLabelMappings || {};
    let processedCount = 0;

    // Show progress
    setUploadStatus(`Processing ${fileList.length} files...`);

    for (const file of fileList) {
      // Check if there's a CSV mapping for this filename
      const mappedLabel = csvMappings[file.name];
      
      newFiles.push({
        file,
        label: mappedLabel || null,
        preview: URL.createObjectURL(file),
      });

      processedCount++;
      
      // Update progress every 10 files to avoid too many re-renders
      if (processedCount % 10 === 0 || processedCount === fileList.length) {
        setUploadStatus(`Processed ${processedCount}/${fileList.length} files`);
      }
    }

    setFiles([...files, ...newFiles]);
    setUploadStatus('');
    
    const autoLabeled = newFiles.filter(f => f.label).length;
    if (autoLabeled > 0) {
      message.success(`${fileList.length} files added (${autoLabeled} auto-labeled from CSV)`, 3);
    } else {
      message.success(`${fileList.length} files added`, 3);
    }

    // Reset input
    e.target.value = '';
  };

  const handleCSVImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const csvFile = e.target.files?.[0];
    if (!csvFile) return;

    try {
      const text = await csvFile.text();
      const lines = text.split('\n').filter(line => line.trim());
      
      if (lines.length === 0) {
        message.error('CSV file is empty');
        return;
      }

      // Check if first line is header
      const firstLine = lines[0].toLowerCase();
      const hasHeader = firstLine.includes('filename') || firstLine.includes('file') || 
                       firstLine.includes('label') || firstLine.includes('class');
      
      const startIndex = hasHeader ? 1 : 0;
      const csvMappings: { [filename: string]: string } = {};
      const newLabels = new Set<string>(labels);

      // Parse CSV
      for (let i = startIndex; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const parts = line.split(',').map(p => p.trim());
        if (parts.length >= 2) {
          const filename = parts[0];
          const label = parts[1];
          csvMappings[filename] = label;
          newLabels.add(label);
        }
      }

      // Update labels
      setLabels(Array.from(newLabels));

      // Apply labels to existing files
      const updatedFiles = files.map(f => {
        const mapping = csvMappings[f.file.name];
        if (mapping) {
          return { ...f, label: mapping };
        }
        return f;
      });
      setFiles(updatedFiles);

      message.success(`CSV imported! ${Object.keys(csvMappings).length} filename-label mappings loaded.`);
      
      // Store mappings for future file uploads
      (window as any).csvLabelMappings = csvMappings;
      
    } catch (error: any) {
      message.error(`Failed to parse CSV: ${error.message}`);
    }

    // Reset input
    e.target.value = '';
  };

  // Handle file drop/selection
  const handleFilesAdd = (fileList: FileList | File[]) => {
    const csvMappings = (window as any).csvLabelMappings || {};
    
    const newFiles: FileItem[] = Array.from(fileList).map(file => {
      // Check if there's a CSV mapping for this filename
      const mappedLabel = csvMappings[file.name];
      
      return {
        file,
        label: mappedLabel || null,
        preview: URL.createObjectURL(file),
      };
    });
    
    setFiles([...files, ...newFiles]);
    
    const autoLabeled = newFiles.filter(f => f.label).length;
    if (autoLabeled > 0) {
      message.success(`${newFiles.length} files added (${autoLabeled} auto-labeled from CSV)`);
    } else {
      message.success(`${newFiles.length} files added`);
    }
  };

  // Update file label
  const handleUpdateFileLabel = (index: number, label: string) => {
    setFiles(files.map((f, i) => i === index ? { ...f, label } : f));
  };

  // Remove file
  const handleRemoveFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
  };

  // Upload all labeled files
  const handleUploadAll = async () => {
    const labeledFiles = files.filter(f => f.label);
    if (labeledFiles.length === 0) {
      message.warning('Please assign labels to files before uploading');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setUploadStatus('Starting upload...');
    let uploaded = 0;
    let failed = 0;

    for (const fileItem of labeledFiles) {
      try {
        const formData = new FormData();
        formData.append('files', fileItem.file);  // Changed from 'file' to 'files'
        formData.append('label', fileItem.label!);  // Changed from 'class_name' to 'label'

        await dataApi.upload(projectId, formData, () => {
          // Don't show individual progress to avoid slowdown
        });

        uploaded++;
        
        // Update progress
        const progress = Math.round((uploaded / labeledFiles.length) * 100);
        setUploadProgress(progress);
        setUploadStatus(`Uploading: ${uploaded}/${labeledFiles.length} files (${failed} failed)`);
        
      } catch (error: any) {
        failed++;
        console.error(`Failed to upload ${fileItem.file.name}:`, error);
      }
    }

    setUploading(false);
    setUploadProgress(0);
    setUploadStatus('');
    
    if (failed === 0) {
      message.success(`Successfully uploaded ${uploaded} files!`, 5);
    } else {
      message.warning(`Uploaded ${uploaded} files, ${failed} failed. Check console for details.`, 8);
    }
    
    // Clear uploaded files
    setFiles(files.filter(f => !f.label));
  };

  // Calculate statistics
  const getLabelCounts = (): ClassData[] => {
    const counts: { [key: string]: number } = {};
    files.forEach(f => {
      if (f.label) {
        counts[f.label] = (counts[f.label] || 0) + 1;
      }
    });
    return Object.entries(counts).map(([name, count]) => ({ name, count }));
  };

  const totalFiles = files.length;
  const labeledFiles = files.filter(f => f.label).length;
  const unlabeledFiles = totalFiles - labeledFiles;

  const handleCreateProject = () => {
    form.validateFields().then((values) => {
      setProjectName(values.projectName);
      createProjectMutation.mutate({
        name: values.projectName,
        modality: 'image',
        description: values.description,
      });
    });
  };

  const handleNext = () => {
    if (currentStep === 0) {
      handleCreateProject();
    } else if (currentStep === 1) {
      const labelCounts = getLabelCounts();
      if (labelCounts.length < 2) {
        message.warning('Please upload images for at least 2 classes');
        return;
      }
      // Navigate to Model Selection page
      navigate(`/project/${projectId}/model-selection/image`);
    } else if (currentStep === 2) {
      if (!selectedModel) {
        message.warning('Please select a model');
        return;
      }
      navigate(`/training/${projectId}`);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const fileColumns = [
    {
      title: 'Preview',
      dataIndex: 'preview',
      key: 'preview',
      width: 80,
      render: (preview: string) => (
        <img src={preview} alt="preview" style={{ width: 50, height: 50, objectFit: 'cover', borderRadius: 4 }} />
      ),
    },
    {
      title: 'File Name',
      dataIndex: 'file',
      key: 'file',
      render: (file: File) => <Text>{file.name}</Text>,
    },
    {
      title: 'Label',
      dataIndex: 'label',
      key: 'label',
      render: (label: string | null, record: FileItem, index: number) => (
        <Select
          style={{ width: 150 }}
          placeholder="Select label"
          value={label}
          onChange={(value) => handleUpdateFileLabel(index, value)}
          options={labels.map(l => ({ label: l, value: l }))}
        />
      ),
    },
    {
      title: 'Action',
      key: 'action',
      width: 80,
      render: (_: any, __: FileItem, index: number) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleRemoveFile(index)}
        />
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Steps current={currentStep} style={{ marginBottom: 32 }}>
          <Step title="Project Setup" description="Create project" icon={<CheckOutlined />} />
          <Step title="Import & Label Data" description="Upload and label images" icon={<FileImageOutlined />} />
          <Step title="Model Selection" description="Choose model" />
        </Steps>

        {/* Step 0: Project Setup */}
        {currentStep === 0 && (
          <div>
            <Title level={4}>Step 1: Project Setup</Title>
            <Paragraph>Create a new image classification project.</Paragraph>

            <Form form={form} layout="vertical">
              <Form.Item
                label="Project Name"
                name="projectName"
                rules={[{ required: true, message: 'Please enter project name' }]}
              >
                <Input placeholder="My Image Classifier" size="large" />
              </Form.Item>

              <Form.Item label="Description" name="description">
                <Input.TextArea rows={3} placeholder="Project description (optional)" />
              </Form.Item>
            </Form>
          </div>
        )}

        {/* Step 1: Import & Label Data */}
        {currentStep === 1 && (
          <Row gutter={24}>
            {/* Left: Data Import */}
            <Col span={16}>
              <Title level={4}>Step 2: Import & Label Data</Title>
              <Paragraph>
                💡 <strong>Workflow:</strong> 1) Add labels manually OR import CSV → 2) Drag & drop image files → 3) Upload
              </Paragraph>

              {/* Drop Zone */}
              <Dragger
                multiple
                accept="image/*"
                showUploadList={false}
                beforeUpload={(file) => {
                  handleFilesAdd([file]);
                  return false;
                }}
                style={{ marginBottom: 16 }}
              >
                <p className="ant-upload-drag-icon">
                  <InboxOutlined style={{ fontSize: 48, color: '#6366F1' }} />
                </p>
                <p className="ant-upload-text">Click or drag images to this area</p>
                <p className="ant-upload-hint">
                  Supports: JPG, PNG, BMP | Multiple files supported
                </p>
              </Dragger>

              {/* Additional Import Options */}
              <Space style={{ marginBottom: 16 }}>
                <input
                  id="csv-upload"
                  type="file"
                  accept=".csv"
                  style={{ display: 'none' }}
                  onChange={handleCSVImport}
                />
                <Button 
                  icon={<FileImageOutlined />}
                  onClick={() => {
                    const input = document.getElementById('csv-upload') as HTMLInputElement;
                    if (input) input.click();
                  }}
                >
                  Import CSV (Auto-label)
                </Button>

                <input
                  id="folder-upload"
                  type="file"
                  // @ts-ignore - webkitdirectory is not in TypeScript types
                  webkitdirectory=""
                  directory=""
                  multiple
                  style={{ display: 'none' }}
                  onChange={handleFolderUpload}
                />
                <Button 
                  icon={<InboxOutlined />}
                  onClick={() => {
                    const input = document.getElementById('folder-upload') as HTMLInputElement;
                    if (input) input.click();
                  }}
                  disabled={!!uploadStatus}
                >
                  Import Folder
                </Button>

                <Button
                  type="primary"
                  onClick={handleUploadAll}
                  disabled={labeledFiles === 0 || uploading}
                  loading={uploading}
                >
                  Upload {labeledFiles} Labeled Files
                </Button>
              </Space>

              {/* Status indicator */}
              {uploadStatus && (
                <div style={{ marginBottom: 16 }}>
                  <Text type="secondary">{uploadStatus}</Text>
                </div>
              )}

              {uploading && (
                <div style={{ marginBottom: 16 }}>
                  <Progress percent={uploadProgress} status="active" />
                  <Text type="secondary">{uploadStatus}</Text>
                </div>
              )}

              <Paragraph type="secondary" style={{ fontSize: 12, marginBottom: 16 }}>
                💡 <strong>Tips:</strong>
                <br />
                • <strong>CSV Format:</strong> filename,label (e.g., image1.jpg,cat)
                <br />
                • <strong>Folder Import:</strong> Select folder with all images (6000+ files supported!)
                <br />
                • After CSV import, folder/files will auto-label based on filename matches
              </Paragraph>

              {/* Files List */}
              <Card 
                title={`Imported Files (${totalFiles})`}
                extra={
                  <Space>
                    <Text type="success">Labeled: {labeledFiles}</Text>
                    <Text type="warning">Unlabeled: {unlabeledFiles}</Text>
                    <Button size="small" danger onClick={() => setFiles([])}>
                      Clear All
                    </Button>
                  </Space>
                }
              >
                <Table
                  dataSource={files}
                  columns={fileColumns}
                  rowKey={(record) => record.file.name}
                  pagination={{ pageSize: 10 }}
                  size="small"
                  scroll={{ y: 400 }}
                />
              </Card>
            </Col>

            {/* Right: Labels Panel */}
            <Col span={8}>
              <Card title="Class Labels" style={{ marginBottom: 16 }}>
                <Space.Compact style={{ width: '100%', marginBottom: 16 }}>
                  <Input
                    placeholder="Enter label (e.g., cat, dog)"
                    value={newLabel}
                    onChange={(e) => setNewLabel(e.target.value)}
                    onPressEnter={handleAddLabel}
                  />
                  <Button type="primary" icon={<PlusOutlined />} onClick={handleAddLabel}>
                    Add
                  </Button>
                </Space.Compact>

                <Paragraph type="secondary" style={{ fontSize: 12 }}>
                  💡 Example: cat, dog, bird
                </Paragraph>

                <Divider />

                <div style={{ maxHeight: 200, overflow: 'auto' }}>
                  {labels.length === 0 ? (
                    <Text type="secondary">No labels yet. Add at least 2 labels.</Text>
                  ) : (
                    labels.map(label => (
                      <div key={label} style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        padding: '8px 0',
                        borderBottom: '1px solid #f0f0f0'
                      }}>
                        <Tag color="blue">{label}</Tag>
                        <Space>
                          <Text type="secondary">
                            ({files.filter(f => f.label === label).length} files)
                          </Text>
                          <Button
                            type="text"
                            danger
                            size="small"
                            icon={<DeleteOutlined />}
                            onClick={() => handleRemoveLabel(label)}
                          />
                        </Space>
                      </div>
                    ))
                  )}
                </div>
              </Card>

              {/* Statistics */}
              <Card title="Statistics">
                <Row gutter={16}>
                  <Col span={12}>
                    <Statistic title="Total Files" value={totalFiles} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Labels" value={labels.length} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Labeled" value={labeledFiles} valueStyle={{ color: '#3f8600' }} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="Unlabeled" value={unlabeledFiles} valueStyle={{ color: '#cf1322' }} />
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>
        )}

        {/* Step 2: Model Selection */}
        {currentStep === 2 && (
          <div>
            <Title level={4}>Step 3: Model Selection</Title>
            <Paragraph>Choose a model architecture for your image classification task.</Paragraph>

            <Row gutter={16}>
              {modelsData?.models?.map((model: any) => (
                <Col span={12} key={model.id}>
                  <Card
                    hoverable
                    style={{
                      marginBottom: 16,
                      borderColor: selectedModel === model.id ? '#6366F1' : undefined,
                      borderWidth: selectedModel === model.id ? 2 : 1,
                    }}
                    onClick={() => setSelectedModel(model.id)}
                  >
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Text strong style={{ fontSize: 16 }}>{model.name}</Text>
                      <Text type="secondary">{model.description}</Text>
                      <Space>
                        <Tag color="blue">Accuracy: {model.accuracy || 'High'}</Tag>
                        <Tag color="green">Speed: {model.speed || 'Fast'}</Tag>
                      </Space>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        )}

        {/* Navigation */}
        <Divider />
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={handleBack}
            disabled={currentStep === 0}
          >
            Back
          </Button>
          <Button
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={handleNext}
            loading={createProjectMutation.isPending}
          >
            {currentStep === 0 ? 'Create Project' : currentStep === 1 ? 'Next: Select Model →' : 'Start Training'}
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default ImageProjectPage;

