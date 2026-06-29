import React, { useState } from 'react';
import { Card, Select, Button, Upload, Space, Typography, Divider, Row, Col, Statistic, Tag, App } from 'antd';
import { BulbOutlined, UploadOutlined, RocketOutlined } from '@ant-design/icons';
import { useQuery, useMutation } from '@tanstack/react-query';
import { projectApi, inferenceApi } from '../api/endpoints';
import type { UploadFile } from 'antd';

const { Title, Paragraph, Text } = Typography;

const InferencePlaygroundPage: React.FC = () => {
  const { message } = App.useApp();
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [testFile, setTestFile] = useState<UploadFile | null>(null);
  const [inferenceResult, setInferenceResult] = useState<any>(null);

  // Fetch projects
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectApi.list();
      return response.data;
    },
  });

  // Run inference mutation
  const inferenceMutation = useMutation({
    mutationFn: async ({ projectId, file }: { projectId: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await inferenceApi.predict(projectId, formData);
      return response.data;
    },
    onSuccess: (data) => {
      setInferenceResult(data);
      message.success('Inference completed');
    },
    onError: (error: any) => {
      message.error(`Inference failed: ${error.detail || error.message}`);
    },
  });

  const handleRunInference = () => {
    if (!selectedProject) {
      message.warning('Please select a project');
      return;
    }
    if (!testFile) {
      message.warning('Please upload a test file');
      return;
    }

    inferenceMutation.mutate({
      projectId: selectedProject,
      file: testFile as unknown as File,
    });
  };

  const completedProjects = projectsData?.projects?.filter((p) => p.status === 'completed') || [];
  const selectedProjectData = completedProjects.find((p) => p.id === selectedProject);

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <BulbOutlined style={{ fontSize: 64, color: '#6366F1' }} />
          <Title level={2}>💡 Inference Playground</Title>
          <Paragraph>
            Test your trained models with new data and see predictions in real-time.
          </Paragraph>
        </div>

        <Divider />

        {/* Model Selection */}
        <Card style={{ marginBottom: 16, background: '#f9fafb' }}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <Text strong>Select Model:</Text>
              <Select
                size="large"
                placeholder="Choose a trained model"
                value={selectedProject}
                onChange={setSelectedProject}
                style={{ width: '100%', marginTop: 8 }}
              >
                {completedProjects.map((project) => (
                  <Select.Option key={project.id} value={project.id}>
                    {project.name} - <Tag color="blue">{project.modality}</Tag>
                  </Select.Option>
                ))}
              </Select>
            </div>

            {selectedProjectData && (
              <Card size="small" style={{ background: '#e0e7ff' }}>
                <Space>
                  <Text>Model: <Tag color="green">{selectedProjectData.model_name || 'N/A'}</Tag></Text>
                  <Text>Modality: <Tag color="blue">{selectedProjectData.modality}</Tag></Text>
                  {selectedProjectData.num_classes && (
                    <Text>Classes: <Tag>{selectedProjectData.num_classes}</Tag></Text>
                  )}
                </Space>
              </Card>
            )}
          </Space>
        </Card>

        {/* File Upload */}
        {selectedProject && (
          <Card title="Upload Test Data" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Upload
                  maxCount={1}
                  beforeUpload={(file) => {
                    setTestFile(file as any);
                    setInferenceResult(null);
                    return false;
                  }}
                  onRemove={() => {
                    setTestFile(null);
                    setInferenceResult(null);
                  }}
                >
                  <Button icon={<UploadOutlined />} size="large" block>
                    Select File to Test
                  </Button>
                </Upload>
                {selectedProjectData && (
                  <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
                    Accepted formats for {selectedProjectData.modality}:{' '}
                    {selectedProjectData.modality === 'image' && 'JPG, PNG, BMP'}
                    {selectedProjectData.modality === 'text' && 'TXT, CSV'}
                    {selectedProjectData.modality === 'audio' && 'WAV, MP3, FLAC'}
                    {selectedProjectData.modality === 'video' && 'MP4, AVI, MOV'}
                    {selectedProjectData.modality === 'tabular' && 'CSV'}
                    {selectedProjectData.modality === 'timeseries' && 'CSV'}
                    {selectedProjectData.modality === 'medical' && 'NII, DICOM, CSV'}
                    {selectedProjectData.modality === 'genomic' && 'FASTA, TXT'}
                  </Text>
                )}
              </div>

              <Button
                type="primary"
                size="large"
                icon={<RocketOutlined />}
                onClick={handleRunInference}
                loading={inferenceMutation.isPending}
                disabled={!testFile}
                block
              >
                Run Inference
              </Button>
            </Space>
          </Card>
        )}

        {/* Inference Results */}
        {inferenceResult && (
          <Card
            title="🎯 Prediction Results"
            style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}
            headStyle={{ color: 'white', borderBottom: '1px solid rgba(255,255,255,0.2)' }}
          >
            <Row gutter={16}>
              <Col xs={24} sm={8}>
                <Card style={{ background: 'rgba(255,255,255,0.95)' }}>
                  <Statistic
                    title="Predicted Class"
                    value={inferenceResult.predicted_class}
                    valueStyle={{ color: '#6366F1', fontWeight: 'bold' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card style={{ background: 'rgba(255,255,255,0.95)' }}>
                  <Statistic
                    title="Confidence"
                    value={(inferenceResult.confidence * 100).toFixed(2)}
                    suffix="%"
                    valueStyle={{ color: '#22c55e' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card style={{ background: 'rgba(255,255,255,0.95)' }}>
                  <Statistic
                    title="Latency"
                    value={inferenceResult.latency_ms?.toFixed(2) || 'N/A'}
                    suffix="ms"
                    valueStyle={{ color: '#f59e0b' }}
                  />
                </Card>
              </Col>
            </Row>

            {inferenceResult.probabilities && (
              <Card style={{ marginTop: 16, background: 'rgba(255,255,255,0.95)' }}>
                <Title level={5}>Class Probabilities</Title>
                <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 8, maxHeight: 300, overflow: 'auto' }}>
                  {JSON.stringify(inferenceResult.probabilities, null, 2)}
                </pre>
              </Card>
            )}
          </Card>
        )}

        {completedProjects.length === 0 && (
          <Card style={{ textAlign: 'center', padding: 48 }}>
            <BulbOutlined style={{ fontSize: 48, color: '#d1d5db', marginBottom: 16 }} />
            <Title level={4}>No Trained Models</Title>
            <Paragraph>Train a model first to start testing inference.</Paragraph>
            <Button type="primary" onClick={() => window.location.href = '/'}>
              Create New Project
            </Button>
          </Card>
        )}
      </Card>
    </div>
  );
};

export default InferencePlaygroundPage;

