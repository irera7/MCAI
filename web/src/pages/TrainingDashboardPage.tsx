import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Space, Button, Progress, Statistic, Row, Col, Table, Tag, Divider, App } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, ArrowLeftOutlined, LineChartOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { trainingApi, projectApi } from '../api/endpoints';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const { Title, Text, Paragraph } = Typography;

const TrainingDashboardPage: React.FC = () => {
  const { message } = App.useApp();
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isPolling, setIsPolling] = useState(false);

  // Fetch project info
  const { data: projectData } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      if (!projectId) throw new Error('No project ID');
      const response = await projectApi.get(projectId);
      return response.data;
    },
    enabled: !!projectId,
  });

  // Fetch training status with polling
  const { data: statusData, isLoading } = useQuery({
    queryKey: ['training-status', projectId],
    queryFn: async () => {
      if (!projectId) throw new Error('No project ID');
      const response = await trainingApi.status(projectId);
      return response.data;
    },
    enabled: !!projectId,
    refetchInterval: isPolling ? 2000 : false, // Poll every 2 seconds if training
  });

  // Start polling when training
  useEffect(() => {
    if (statusData?.status === 'training') {
      setIsPolling(true);
    } else {
      setIsPolling(false);
    }
  }, [statusData?.status]);

  // Stop training mutation
  const stopMutation = useMutation({
    mutationFn: () => {
      if (!projectId) throw new Error('No project ID');
      return trainingApi.stop(projectId);
    },
    onSuccess: () => {
      message.success('Training stopped');
      queryClient.invalidateQueries({ queryKey: ['training-status', projectId] });
    },
    onError: (error: any) => {
      message.error(`Failed to stop training: ${error.detail || error.message}`);
    },
  });

  // Resume training mutation
  const resumeMutation = useMutation({
    mutationFn: () => {
      if (!projectId) throw new Error('No project ID');
      return trainingApi.resume(projectId);
    },
    onSuccess: () => {
      message.success('Training resumed');
      queryClient.invalidateQueries({ queryKey: ['training-status', projectId] });
    },
    onError: (error: any) => {
      message.error(`Failed to resume training: ${error.detail || error.message}`);
    },
  });

  // Launch TensorBoard mutation
  const launchTensorBoardMutation = useMutation({
    mutationFn: () => {
      if (!projectId) throw new Error('No project ID');
      return trainingApi.tensorboard.launch(projectId);
    },
    onSuccess: (response: any) => {
      message.success('TensorBoard launched! Opening in new tab...');
      setTimeout(() => {
        window.open('http://localhost:6006', '_blank');
      }, 2000);
    },
    onError: (error: any) => {
      message.error(`Failed to launch TensorBoard: ${error.detail || error.message}`);
    },
  });

  // Prepare chart data
  const chartData = React.useMemo(() => {
    if (!statusData) return [];
    
    const data = [];
    for (let i = 0; i <= statusData.current_epoch; i++) {
      data.push({
        epoch: i,
        train_loss: statusData.train_loss || 0,
        val_loss: statusData.val_loss || 0,
        train_acc: statusData.train_acc || 0,
        val_acc: statusData.val_acc || 0,
      });
    }
    return data;
  }, [statusData]);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      idle: 'default',
      training: 'processing',
      completed: 'success',
      stopped: 'warning',
      error: 'error',
    };
    return colors[status] || 'default';
  };

  const formatTime = (seconds: number | undefined) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  return (
    <div style={{ padding: 24 }}>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/projects')}
        style={{ marginBottom: 16 }}
      >
        Back to Projects
      </Button>

      <Title level={2}>🎯 Training Dashboard</Title>
      <Paragraph>
        Monitor your model training progress in real-time
      </Paragraph>

      {/* Project Info */}
      <Card style={{ marginBottom: 16 }}>
        <Space size="large">
          <Text strong>Project: {projectData?.name || projectId}</Text>
          <Text>Modality: <Tag>{projectData?.modality || 'N/A'}</Tag></Text>
          <Text>Status: <Tag color={getStatusColor(statusData?.status || 'idle')}>
            {(statusData?.status || 'idle').toUpperCase()}
          </Tag></Text>
        </Space>
      </Card>

      {/* Key Metrics */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Current Epoch"
              value={statusData?.current_epoch || 0}
              suffix={`/ ${statusData?.total_epochs || 0}`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Progress"
              value={statusData?.progress_percentage || 0}
              suffix="%"
            />
            <Progress
              percent={statusData?.progress_percentage || 0}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Training Loss"
              value={statusData?.train_loss?.toFixed(4) || '0.0000'}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Validation Accuracy"
              value={statusData?.val_acc ? (statusData.val_acc * 100).toFixed(2) : '0.00'}
              suffix="%"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Card title={<><LineChartOutlined /> Training Metrics</>} style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={12}>
            <Title level={5}>Loss</Title>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="epoch" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="train_loss" stroke="#8884d8" name="Train Loss" />
                <Line type="monotone" dataKey="val_loss" stroke="#82ca9d" name="Val Loss" />
              </LineChart>
            </ResponsiveContainer>
          </Col>
          <Col span={12}>
            <Title level={5}>Accuracy</Title>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="epoch" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="train_acc" stroke="#8884d8" name="Train Acc" />
                <Line type="monotone" dataKey="val_acc" stroke="#82ca9d" name="Val Acc" />
              </LineChart>
            </ResponsiveContainer>
          </Col>
        </Row>
      </Card>

      {/* Training Info */}
      <Card title="Training Information">
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="Best Validation Accuracy"
              value={statusData?.best_val_acc ? (statusData.best_val_acc * 100).toFixed(2) : '0.00'}
              suffix="%"
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="ETA"
              value={formatTime(statusData?.eta_seconds)}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="Current Train Accuracy"
              value={statusData?.train_acc ? (statusData.train_acc * 100).toFixed(2) : '0.00'}
              suffix="%"
            />
          </Col>
        </Row>

        <Divider />

        {/* Debug: Show current status */}
        {statusData && (
          <div style={{ marginBottom: 16, padding: 8, background: '#f0f0f0', borderRadius: 4 }}>
            <Text type="secondary">
              <strong>Status:</strong> {statusData.status || 'undefined'} | 
              <strong> Model:</strong> {projectData?.model_name || 'none'}
            </Text>
          </div>
        )}

        <Space>
          {statusData?.status === 'training' ? (
            <Button
              danger
              icon={<PauseCircleOutlined />}
              onClick={() => stopMutation.mutate()}
              loading={stopMutation.isPending}
            >
              Stop Training
            </Button>
          ) : (
            <>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={() => resumeMutation.mutate()}
                loading={resumeMutation.isPending}
                disabled={!projectData?.model_name}
              >
                Resume Training
              </Button>
              <Button
                onClick={() => navigate(`/project/${projectId}/training-config/${projectData?.modality}?model=${projectData?.model_name || ''}`)}
                disabled={!projectData?.modality}
              >
                Edit Configuration
              </Button>
            </>
          )}
          {statusData?.status === 'completed' && (
            <Button
              type="primary"
              onClick={() => navigate(`/results/${projectId}`)}
            >
              View Results
            </Button>
          )}
          <Button 
            icon={<LineChartOutlined />}
            onClick={() => launchTensorBoardMutation.mutate()}
            loading={launchTensorBoardMutation.isPending}
          >
            Launch TensorBoard
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default TrainingDashboardPage;

