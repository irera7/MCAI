import React, { useState } from 'react';
import { Card, Checkbox, Button, Table, Space, Typography, Tag, Divider, Row, Col, App } from 'antd';
import { FundOutlined, CompressOutlined, DownloadOutlined } from '@ant-design/icons';
import { useQuery, useMutation } from '@tanstack/react-query';
import { projectApi, comparisonApi } from '../api/endpoints';

const { Title, Paragraph, Text } = Typography;

const ModelComparisonPage: React.FC = () => {
  const { message } = App.useApp();
  const [selectedProjects, setSelectedProjects] = useState<string[]>([]);
  const [comparisonResult, setComparisonResult] = useState<any>(null);

  // Fetch projects
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectApi.list();
      return response.data;
    },
  });

  // Compare models mutation
  const compareMutation = useMutation({
    mutationFn: (projectIds: string[]) => comparisonApi.compare(projectIds),
    onSuccess: (response) => {
      setComparisonResult(response.data);
      message.success('Models compared successfully');
    },
    onError: (error: any) => {
      message.error(`Comparison failed: ${error.detail || error.message}`);
    },
  });

  const handleCompare = () => {
    if (selectedProjects.length < 2) {
      message.warning('Please select at least 2 models to compare');
      return;
    }
    compareMutation.mutate(selectedProjects);
  };

  const completedProjects = projectsData?.projects?.filter((p) => p.status === 'completed') || [];

  const comparisonColumns = [
    {
      title: 'Metric',
      dataIndex: 'metric',
      key: 'metric',
      fixed: 'left' as const,
      render: (text: string) => <Text strong>{text}</Text>,
    },
    ...selectedProjects.map((projectId) => {
      const project = completedProjects.find((p) => p.id === projectId);
      return {
        title: project?.name || projectId,
        dataIndex: projectId,
        key: projectId,
        render: (val: number) => (
          <Text style={{ color: val === Math.max(...selectedProjects.map((id) => comparisonResult?.data?.[id] || 0)) ? '#22c55e' : '#000' }}>
            {typeof val === 'number' ? val.toFixed(4) : val || 'N/A'}
          </Text>
        ),
      };
    }),
  ];

  const comparisonData = comparisonResult
    ? [
        { metric: 'Accuracy', ...selectedProjects.reduce((acc, id) => ({ ...acc, [id]: comparisonResult[id]?.accuracy || 0 }), {}) },
        { metric: 'Precision', ...selectedProjects.reduce((acc, id) => ({ ...acc, [id]: comparisonResult[id]?.precision || 0 }), {}) },
        { metric: 'Recall', ...selectedProjects.reduce((acc, id) => ({ ...acc, [id]: comparisonResult[id]?.recall || 0 }), {}) },
        { metric: 'F1 Score', ...selectedProjects.reduce((acc, id) => ({ ...acc, [id]: comparisonResult[id]?.f1_score || 0 }), {}) },
      ]
    : [];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <FundOutlined style={{ fontSize: 64, color: '#6366F1' }} />
          <Title level={2}>📊 Model Comparison</Title>
          <Paragraph>
            Compare multiple trained models side by side to find the best performer.
          </Paragraph>
        </div>

        <Divider />

        {/* Project Selection */}
        <Card title="Select Models to Compare" style={{ marginBottom: 16 }}>
          <Checkbox.Group
            value={selectedProjects}
            onChange={(values) => setSelectedProjects(values as string[])}
            style={{ width: '100%' }}
          >
            <Row gutter={[16, 16]}>
              {completedProjects.map((project) => (
                <Col key={project.id} xs={24} sm={12} md={8}>
                  <Card hoverable size="small">
                    <Checkbox value={project.id}>
                      <Space direction="vertical" size="small">
                        <Text strong>{project.name}</Text>
                        <Space>
                          <Tag color="blue">{project.modality}</Tag>
                          <Tag color="green">{project.model_name || 'Model'}</Tag>
                        </Space>
                      </Space>
                    </Checkbox>
                  </Card>
                </Col>
              ))}
            </Row>
          </Checkbox.Group>

          {completedProjects.length === 0 && (
            <div style={{ textAlign: 'center', padding: 32 }}>
              <Text type="secondary">No completed models available. Train some models first.</Text>
            </div>
          )}

          <Divider />

          <Space>
            <Button
              type="primary"
              icon={<CompressOutlined />}
              onClick={handleCompare}
              loading={compareMutation.isPending}
              disabled={selectedProjects.length < 2}
            >
              Compare Models ({selectedProjects.length})
            </Button>
            <Button onClick={() => setSelectedProjects([])}>Clear Selection</Button>
          </Space>
        </Card>

        {/* Comparison Results */}
        {comparisonResult && (
          <Card
            title="Comparison Results"
            extra={
              <Button icon={<DownloadOutlined />}>
                Export CSV
              </Button>
            }
          >
            <Table
              columns={comparisonColumns}
              dataSource={comparisonData}
              rowKey="metric"
              pagination={false}
              bordered
              size="middle"
            />

            <Divider />

            <Card style={{ background: '#f0fdf4', border: '1px solid #bbf7d0' }}>
              <Title level={5}>Best Model</Title>
              <Text>
                Based on accuracy, the best model is: <Tag color="green">
                  {completedProjects.find((p) => p.id === selectedProjects[0])?.name || 'N/A'}
                </Tag>
              </Text>
            </Card>
          </Card>
        )}
      </Card>
    </div>
  );
};

export default ModelComparisonPage;

