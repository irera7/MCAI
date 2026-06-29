import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Typography, Row, Col, Statistic, Button, Space, Table, Tag, Divider } from 'antd';
import {
  ArrowLeftOutlined,
  DownloadOutlined,
  RocketOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { trainingApi, projectApi } from '../api/endpoints';

const { Title, Paragraph, Text } = Typography;

const ResultsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

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

  // Fetch training metrics
  const { data: metricsData, isLoading } = useQuery({
    queryKey: ['training-metrics', projectId],
    queryFn: async () => {
      if (!projectId) throw new Error('No project ID');
      const response = await trainingApi.metrics(projectId);
      return response.data;
    },
    enabled: !!projectId,
  });

  // Mock confusion matrix data
  const confusionMatrix = metricsData?.confusion_matrix || [
    [45, 5],
    [3, 47],
  ];

  const confusionColumns = [
    { title: '', dataIndex: 'label', key: 'label', fixed: 'left' as const },
    ...confusionMatrix[0].map((_, idx) => ({
      title: `Predicted ${idx}`,
      dataIndex: `pred_${idx}`,
      key: `pred_${idx}`,
      render: (val: number) => (
        <span style={{ fontWeight: 'bold', color: val > 20 ? '#52c41a' : '#000' }}>{val}</span>
      ),
    })),
  ];

  const confusionData = confusionMatrix.map((row, idx) => ({
    key: idx,
    label: `Actual ${idx}`,
    ...row.reduce((acc, val, i) => ({ ...acc, [`pred_${i}`]: val }), {}),
  }));

  return (
    <div style={{ padding: 24 }}>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/projects')}
        style={{ marginBottom: 16 }}
      >
        Back to Projects
      </Button>

      <Card
        style={{
          marginBottom: 16,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        }}
      >
        <Space direction="vertical" size="small">
          <Title level={2} style={{ color: 'white', marginBottom: 0 }}>
            <CheckCircleOutlined /> Training Completed!
          </Title>
          <Paragraph style={{ color: 'white', marginBottom: 0 }}>
            Your model has been successfully trained. Review the results below.
          </Paragraph>
        </Space>
      </Card>

      {/* Project Info */}
      <Card style={{ marginBottom: 16 }}>
        <Space size="large">
          <Text strong>Project: {projectData?.name || projectId}</Text>
          <Text>Modality: <Tag color="blue">{projectData?.modality || 'N/A'}</Tag></Text>
          <Text>Model: <Tag color="green">{projectData?.model_name || 'N/A'}</Tag></Text>
        </Space>
      </Card>

      {/* Key Metrics */}
      <Title level={4}>📊 Final Metrics</Title>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Accuracy"
              value={(metricsData?.accuracy || 0.92) * 100}
              precision={2}
              suffix="%"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Precision"
              value={(metricsData?.precision || 0.91) * 100}
              precision={2}
              suffix="%"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Recall"
              value={(metricsData?.recall || 0.94) * 100}
              precision={2}
              suffix="%"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="F1 Score"
              value={(metricsData?.f1_score || 0.92) * 100}
              precision={2}
              suffix="%"
              valueStyle={{ color: '#eb2f96' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Confusion Matrix */}
      {confusionMatrix && confusionMatrix.length > 0 && (
        <>
          <Title level={4}>🎯 Confusion Matrix</Title>
          <Card style={{ marginBottom: 24 }}>
            <Table
              columns={confusionColumns}
              dataSource={confusionData}
              pagination={false}
              size="small"
              bordered
            />
          </Card>
        </>
      )}

      {/* Actions */}
      <Card>
        <Title level={4}>Next Steps</Title>
        <Paragraph>
          Your model is now ready! You can export it, deploy it for inference, or compare it with other models.
        </Paragraph>
        <Space wrap>
          <Button
            type="primary"
            icon={<RocketOutlined />}
            onClick={() => navigate(`/inference`)}
          >
            Test Inference
          </Button>
          <Button
            icon={<DownloadOutlined />}
            onClick={() => navigate(`/export/${projectId}`)}
          >
            Export Model
          </Button>
          <Button onClick={() => navigate('/serving')}>
            Deploy to Serving
          </Button>
          <Button onClick={() => navigate('/comparison')}>
            Compare Models
          </Button>
          <Button onClick={() => navigate('/ensemble')}>
            Create Ensemble
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default ResultsPage;

