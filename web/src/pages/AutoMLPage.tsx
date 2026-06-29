import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Select,
  Button,
  Form,
  InputNumber,
  Radio,
  Space,
  Typography,
  Divider,
  Progress,
  Table,
  Tag,
  message,
  Row,
  Col,
  Statistic,
} from 'antd';
import { RobotOutlined, PlayCircleOutlined, DownloadOutlined, CheckOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectApi, automlApi } from '../api/endpoints';

const { Title, Paragraph, Text } = Typography;

const AutoMLPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<any>(null);

  // Fetch projects
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectApi.list();
      return response.data;
    },
  });

  // Fetch AutoML status
  const { data: statusData } = useQuery({
    queryKey: ['automl-status', selectedProject],
    queryFn: async () => {
      const response = await automlApi.status(selectedProject);
      return response.data;
    },
    enabled: !!selectedProject && isOptimizing,
    refetchInterval: isOptimizing ? 3000 : false,
  });

  // Start AutoML optimization
  const startMutation = useMutation({
    mutationFn: (config: any) => automlApi.start(config),
    onSuccess: (response) => {
      message.success('AutoML optimization started');
      setIsOptimizing(true);
      setOptimizationResult(response.data);
    },
    onError: (error: any) => {
      message.error(`Failed to start AutoML: ${error.detail || error.message}`);
    },
  });

  // Apply best parameters
  const applyMutation = useMutation({
    mutationFn: () => automlApi.apply(selectedProject),
    onSuccess: () => {
      message.success('Best parameters applied to project');
      queryClient.invalidateQueries({ queryKey: ['project', selectedProject] });
    },
    onError: (error: any) => {
      message.error(`Failed to apply parameters: ${error.detail || error.message}`);
    },
  });

  const handleStartOptimization = () => {
    if (!selectedProject) {
      message.warning('Please select a project');
      return;
    }

    form.validateFields().then((values) => {
      const config = {
        project_id: selectedProject,
        n_trials: values.n_trials,
        timeout: values.timeout,
        optimizer: values.optimizer,
        metric: values.metric,
        search_space: {
          learning_rate: {
            type: 'float',
            low: values.lr_min,
            high: values.lr_max,
            log: true,
          },
          batch_size: {
            type: 'categorical',
            choices: values.batch_sizes,
          },
          dropout: {
            type: 'float',
            low: values.dropout_min,
            high: values.dropout_max,
          },
          optimizer_type: {
            type: 'categorical',
            choices: values.optimizer_types,
          },
        },
      };

      startMutation.mutate(config);
    });
  };

  const trialColumns = [
    {
      title: 'Trial #',
      dataIndex: 'number',
      key: 'number',
      render: (num: number) => <Tag color="blue">#{num}</Tag>,
    },
    {
      title: 'Score',
      dataIndex: 'score',
      key: 'score',
      render: (score: number) => <Text strong>{score.toFixed(4)}</Text>,
      sorter: (a: any, b: any) => a.score - b.score,
    },
    {
      title: 'Learning Rate',
      dataIndex: ['params', 'learning_rate'],
      key: 'lr',
      render: (lr: number) => lr?.toFixed(6) || 'N/A',
    },
    {
      title: 'Batch Size',
      dataIndex: ['params', 'batch_size'],
      key: 'batch_size',
    },
    {
      title: 'Dropout',
      dataIndex: ['params', 'dropout'],
      key: 'dropout',
      render: (dropout: number) => dropout?.toFixed(3) || 'N/A',
    },
    {
      title: 'Optimizer',
      dataIndex: ['params', 'optimizer_type'],
      key: 'optimizer',
      render: (opt: string) => <Tag>{opt}</Tag>,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <RobotOutlined style={{ fontSize: 64, color: '#6366F1' }} />
          <Title level={2}>🤖 AutoML - Hyperparameter Optimization</Title>
          <Paragraph>
            Automatically find the best hyperparameters for your model using Optuna optimization.
          </Paragraph>
        </div>

        <Divider />

        {/* Project Selection */}
        <Card style={{ marginBottom: 16, background: '#f9fafb' }}>
          <Form.Item label={<Text strong>Select Project</Text>} style={{ marginBottom: 0 }}>
            <Select
              size="large"
              placeholder="Choose a project to optimize"
              value={selectedProject}
              onChange={setSelectedProject}
              style={{ width: '100%' }}
            >
              {projectsData?.projects?.map((project) => (
                <Select.Option key={project.id} value={project.id}>
                  {project.name} - <Tag>{project.modality}</Tag>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </Card>

        {/* Configuration Form */}
        {selectedProject && !isOptimizing && (
          <Form form={form} layout="vertical" initialValues={{
            n_trials: 50,
            timeout: 3600,
            optimizer: 'tpe',
            metric: 'accuracy',
            lr_min: 0.0001,
            lr_max: 0.01,
            dropout_min: 0.1,
            dropout_max: 0.5,
            batch_sizes: [16, 32, 64],
            optimizer_types: ['adam', 'adamw', 'sgd'],
          }}>
            <Title level={4}>Optimization Settings</Title>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="Number of Trials" name="n_trials">
                  <InputNumber min={10} max={500} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Timeout (seconds)" name="timeout">
                  <InputNumber min={60} max={36000} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="Optimization Method" name="optimizer">
                  <Radio.Group>
                    <Radio value="tpe">TPE (Recommended)</Radio>
                    <Radio value="random">Random</Radio>
                    <Radio value="grid">Grid Search</Radio>
                  </Radio.Group>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Objective Metric" name="metric">
                  <Radio.Group>
                    <Radio value="accuracy">Accuracy</Radio>
                    <Radio value="loss">Loss</Radio>
                    <Radio value="f1">F1 Score</Radio>
                  </Radio.Group>
                </Form.Item>
              </Col>
            </Row>

            <Divider />

            <Title level={4}>Search Space</Title>

            <Title level={5}>Learning Rate Range</Title>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="Minimum" name="lr_min">
                  <InputNumber min={0.00001} max={0.1} step={0.0001} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Maximum" name="lr_max">
                  <InputNumber min={0.0001} max={1} step={0.001} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>

            <Title level={5}>Dropout Range</Title>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item label="Minimum" name="dropout_min">
                  <InputNumber min={0} max={0.9} step={0.1} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Maximum" name="dropout_max">
                  <InputNumber min={0.1} max={1} step={0.1} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item label="Batch Sizes" name="batch_sizes">
              <Select mode="multiple" placeholder="Select batch sizes">
                <Select.Option value={8}>8</Select.Option>
                <Select.Option value={16}>16</Select.Option>
                <Select.Option value={32}>32</Select.Option>
                <Select.Option value={64}>64</Select.Option>
                <Select.Option value={128}>128</Select.Option>
              </Select>
            </Form.Item>

            <Form.Item label="Optimizers" name="optimizer_types">
              <Select mode="multiple" placeholder="Select optimizers">
                <Select.Option value="adam">Adam</Select.Option>
                <Select.Option value="adamw">AdamW</Select.Option>
                <Select.Option value="sgd">SGD</Select.Option>
              </Select>
            </Form.Item>

            <Button
              type="primary"
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={handleStartOptimization}
              loading={startMutation.isPending}
              block
            >
              Start Optimization
            </Button>
          </Form>
        )}

        {/* Optimization Progress */}
        {isOptimizing && statusData && (
          <div>
            <Title level={4}>Optimization in Progress</Title>
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={8}>
                <Card>
                  <Statistic
                    title="Trials Completed"
                    value={statusData.total_trials || 0}
                    suffix={`/ ${form.getFieldValue('n_trials')}`}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card>
                  <Statistic
                    title="Best Score"
                    value={statusData.best_score?.toFixed(4) || '0.0000'}
                    valueStyle={{ color: '#3f8600' }}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card>
                  <Statistic
                    title="Time Elapsed"
                    value={statusData.optimization_time || 0}
                    suffix="s"
                  />
                </Card>
              </Col>
            </Row>

            <Progress
              percent={((statusData.total_trials || 0) / form.getFieldValue('n_trials')) * 100}
              status="active"
              style={{ marginBottom: 16 }}
            />

            {statusData.status === 'completed' && (
              <Card style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', marginBottom: 16 }}>
                <Title level={5}>
                  <CheckOutlined style={{ color: '#22c55e' }} /> Optimization Complete!
                </Title>
                <Paragraph>Best parameters have been found. Review the results below.</Paragraph>
                <Space>
                  <Button
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={() => applyMutation.mutate()}
                    loading={applyMutation.isPending}
                  >
                    Apply Best Parameters
                  </Button>
                  <Button icon={<DownloadOutlined />}>Export Trial History</Button>
                  <Button onClick={() => setIsOptimizing(false)}>Start New Optimization</Button>
                </Space>
              </Card>
            )}

            {/* Best Parameters */}
            {statusData.best_params && (
              <Card title="Best Parameters" style={{ marginBottom: 16 }}>
                <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 8 }}>
                  {JSON.stringify(statusData.best_params, null, 2)}
                </pre>
              </Card>
            )}

            {/* Trial History */}
            {statusData.trial_history && statusData.trial_history.length > 0 && (
              <Card title="Trial History">
                <Table
                  columns={trialColumns}
                  dataSource={statusData.trial_history}
                  rowKey="number"
                  pagination={{ pageSize: 10 }}
                  size="small"
                />
              </Card>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default AutoMLPage;

