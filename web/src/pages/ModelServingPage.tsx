import React, { useState } from 'react';
import { Card, Button, Table, Space, Typography, Tag, Row, Col, Statistic, Upload, Divider, Select, App } from 'antd';
import {
  CloudServerOutlined,
  PlayCircleOutlined,
  StopOutlined,
  UploadOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { servingApi, projectApi } from '../api/endpoints';
import type { UploadFile } from 'antd';

const { Title, Paragraph, Text } = Typography;

const ModelServingPage: React.FC = () => {
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [testFile, setTestFile] = useState<UploadFile | null>(null);
  const [inferenceResult, setInferenceResult] = useState<any>(null);

  // Fetch available projects (models)
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectApi.list();
      return response.data;
    },
  });

  // Fetch loaded models
  const { data: loadedModels, isLoading } = useQuery({
    queryKey: ['loaded-models'],
    queryFn: async () => {
      const response = await servingApi.listModels();
      return response.data;
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  // Load model mutation
  const loadMutation = useMutation({
    mutationFn: (modelId: string) => servingApi.load(modelId, 'cuda'),
    onSuccess: () => {
      message.success('Model loaded successfully');
      queryClient.invalidateQueries({ queryKey: ['loaded-models'] });
    },
    onError: (error: any) => {
      message.error(`Failed to load model: ${error.detail || error.message}`);
    },
  });

  // Unload model mutation
  const unloadMutation = useMutation({
    mutationFn: (modelId: string) => servingApi.unload(modelId),
    onSuccess: () => {
      message.success('Model unloaded successfully');
      queryClient.invalidateQueries({ queryKey: ['loaded-models'] });
    },
    onError: (error: any) => {
      message.error(`Failed to unload model: ${error.detail || error.message}`);
    },
  });

  // Run inference mutation
  const inferenceMutation = useMutation({
    mutationFn: async ({ modelId, file }: { modelId: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await servingApi.predict(modelId, formData);
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
    if (!selectedModel) {
      message.warning('Please select a model');
      return;
    }
    if (!testFile) {
      message.warning('Please upload a test file');
      return;
    }

    inferenceMutation.mutate({
      modelId: selectedModel,
      file: testFile as unknown as File,
    });
  };

  const availableModels = projectsData?.projects?.filter((p) => p.status === 'completed') || [];

  const loadedModelColumns = [
    {
      title: 'Model ID',
      dataIndex: 'model_id',
      key: 'model_id',
      render: (id: string) => <Tag color="blue">{id}</Tag>,
    },
    {
      title: 'Type',
      dataIndex: 'model_type',
      key: 'model_type',
    },
    {
      title: 'Device',
      dataIndex: 'device',
      key: 'device',
      render: (device: string) => <Tag color={device === 'cuda' ? 'green' : 'default'}>{device.toUpperCase()}</Tag>,
    },
    {
      title: 'Memory (MB)',
      dataIndex: 'memory_mb',
      key: 'memory',
      render: (mem: number) => `${mem.toFixed(2)} MB`,
    },
    {
      title: 'Requests',
      dataIndex: 'request_count',
      key: 'requests',
    },
    {
      title: 'Avg Latency (ms)',
      dataIndex: 'avg_latency',
      key: 'latency',
      render: (latency: number) => `${latency.toFixed(2)} ms`,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: any) => (
        <Button
          danger
          size="small"
          icon={<StopOutlined />}
          onClick={() => unloadMutation.mutate(record.model_id)}
          loading={unloadMutation.isPending}
        >
          Unload
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <CloudServerOutlined style={{ fontSize: 64, color: '#6366F1' }} />
          <Title level={2}>☁️ Model Serving</Title>
          <Paragraph>
            Load trained models into memory and serve them for real-time inference.
          </Paragraph>
        </div>

        <Divider />

        {/* Statistics */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card>
              <Statistic
                title="Models Loaded"
                value={loadedModels?.loaded_models?.length || 0}
                prefix={<CloudServerOutlined />}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="Total Requests"
                value={loadedModels?.loaded_models?.reduce((sum, m) => sum + (m.request_count || 0), 0) || 0}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="Avg Latency"
                value={
                  loadedModels?.loaded_models?.length
                    ? (
                        loadedModels.loaded_models.reduce((sum, m) => sum + (m.avg_latency || 0), 0) /
                        loadedModels.loaded_models.length
                      ).toFixed(2)
                    : '0.00'
                }
                suffix="ms"
              />
            </Card>
          </Col>
        </Row>

        {/* Available Models to Load */}
        <Card title="Available Models" style={{ marginBottom: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Text>Select a trained model to load into serving:</Text>
            <Row gutter={16}>
              {availableModels.map((project) => (
                <Col key={project.id} xs={24} sm={12} md={8} lg={6}>
                  <Card
                    hoverable
                    onClick={() => loadMutation.mutate(project.id)}
                    style={{ marginBottom: 8 }}
                  >
                    <Space direction="vertical" size="small">
                      <Text strong>{project.name}</Text>
                      <Tag color="blue">{project.modality}</Tag>
                      <Button
                        type="primary"
                        size="small"
                        icon={<PlayCircleOutlined />}
                        loading={loadMutation.isPending}
                        block
                      >
                        Load
                      </Button>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
            {availableModels.length === 0 && (
              <Text type="secondary">No trained models available. Train a model first.</Text>
            )}
          </Space>
        </Card>

        {/* Loaded Models */}
        <Card title="Loaded Models" style={{ marginBottom: 16 }}>
          <Table
            columns={loadedModelColumns}
            dataSource={loadedModels?.loaded_models || []}
            rowKey="model_id"
            loading={isLoading}
            pagination={false}
            size="small"
          />
          {(!loadedModels?.loaded_models || loadedModels.loaded_models.length === 0) && (
            <div style={{ textAlign: 'center', padding: 32 }}>
              <Text type="secondary">No models loaded. Load a model to start serving.</Text>
            </div>
          )}
        </Card>

        {/* Test Inference */}
        {loadedModels?.loaded_models && loadedModels.loaded_models.length > 0 && (
          <Card
            title={<><RocketOutlined /> Test Inference</>}
            style={{ background: '#f0f9ff', border: '1px solid #bae6fd' }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text strong>Select Model:</Text>
                <Select
                  size="large"
                  placeholder="Choose a loaded model"
                  value={selectedModel}
                  onChange={setSelectedModel}
                  style={{ width: '100%', marginTop: 8 }}
                >
                  {loadedModels.loaded_models.map((model) => (
                    <Select.Option key={model.model_id} value={model.model_id}>
                      {model.model_id} - {model.model_type}
                    </Select.Option>
                  ))}
                </Select>
              </div>

              <div>
                <Text strong>Upload Test File:</Text>
                <Upload
                  maxCount={1}
                  beforeUpload={(file) => {
                    setTestFile(file as any);
                    return false;
                  }}
                  onRemove={() => setTestFile(null)}
                >
                  <Button icon={<UploadOutlined />} block style={{ marginTop: 8 }}>
                    Select File
                  </Button>
                </Upload>
              </div>

              <Button
                type="primary"
                size="large"
                icon={<RocketOutlined />}
                onClick={handleRunInference}
                loading={inferenceMutation.isPending}
                disabled={!selectedModel || !testFile}
                block
              >
                Run Inference
              </Button>

              {inferenceResult && (
                <Card title="Inference Result" style={{ background: '#f0fdf4', border: '1px solid #bbf7d0' }}>
                  <Row gutter={16}>
                    <Col span={8}>
                      <Statistic
                        title="Predicted Class"
                        value={inferenceResult.predicted_class}
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="Confidence"
                        value={(inferenceResult.confidence * 100).toFixed(2)}
                        suffix="%"
                        valueStyle={{ color: '#3f8600' }}
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="Latency"
                        value={inferenceResult.latency_ms?.toFixed(2) || 'N/A'}
                        suffix="ms"
                      />
                    </Col>
                  </Row>

                  {inferenceResult.probabilities && (
                    <div style={{ marginTop: 16 }}>
                      <Text strong>Probabilities:</Text>
                      <pre style={{ background: '#fff', padding: 16, borderRadius: 8, marginTop: 8 }}>
                        {JSON.stringify(inferenceResult.probabilities, null, 2)}
                      </pre>
                    </div>
                  )}
                </Card>
              )}
            </Space>
          </Card>
        )}
      </Card>
    </div>
  );
};

export default ModelServingPage;

