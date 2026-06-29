import React, { useState } from 'react';
import { Card, Checkbox, Button, Select, Radio, Space, Typography, Divider, Row, Col, InputNumber, App } from 'antd';
import { AppstoreOutlined, PlusOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectApi, ensembleApi } from '../api/endpoints';

const { Title, Paragraph, Text } = Typography;

const EnsembleMethodsPage: React.FC = () => {
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [ensembleMethod, setEnsembleMethod] = useState<'voting' | 'stacking' | 'bagging'>('voting');
  const [votingType, setVotingType] = useState<'hard' | 'soft' | 'weighted'>('soft');
  const [ensembleName, setEnsembleName] = useState('');

  // Fetch projects
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectApi.list();
      return response.data;
    },
  });

  // Fetch ensembles
  const { data: ensemblesData } = useQuery({
    queryKey: ['ensembles'],
    queryFn: async () => {
      const response = await ensembleApi.list();
      return response.data;
    },
  });

  // Create ensemble mutation
  const createMutation = useMutation({
    mutationFn: (config: any) => ensembleApi.create(config),
    onSuccess: () => {
      message.success('Ensemble created successfully');
      queryClient.invalidateQueries({ queryKey: ['ensembles'] });
      setSelectedModels([]);
      setEnsembleName('');
    },
    onError: (error: any) => {
      message.error(`Failed to create ensemble: ${error.detail || error.message}`);
    },
  });

  const handleCreateEnsemble = () => {
    if (selectedModels.length < 2) {
      message.warning('Please select at least 2 models');
      return;
    }
    if (!ensembleName) {
      message.warning('Please enter an ensemble name');
      return;
    }

    const config = {
      ensemble_name: ensembleName,
      model_ids: selectedModels,
      method: ensembleMethod,
      voting_type: ensembleMethod === 'voting' ? votingType : undefined,
    };

    createMutation.mutate(config);
  };

  const completedProjects = projectsData?.projects?.filter((p) => p.status === 'completed') || [];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <AppstoreOutlined style={{ fontSize: 64, color: '#6366F1' }} />
          <Title level={2}>🎯 Ensemble Methods</Title>
          <Paragraph>
            Combine multiple models to achieve better accuracy through ensemble learning.
          </Paragraph>
        </div>

        <Divider />

        {/* Model Selection */}
        <Card title="Select Models for Ensemble" style={{ marginBottom: 16 }}>
          <Checkbox.Group
            value={selectedModels}
            onChange={(values) => setSelectedModels(values as string[])}
            style={{ width: '100%' }}
          >
            <Row gutter={[16, 16]}>
              {completedProjects.map((project) => (
                <Col key={project.id} xs={24} sm={12} md={8}>
                  <Card hoverable size="small">
                    <Checkbox value={project.id}>
                      <Space direction="vertical" size="small">
                        <Text strong>{project.name}</Text>
                        <Text type="secondary">{project.modality}</Text>
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
        </Card>

        {/* Ensemble Configuration */}
        {selectedModels.length >= 2 && (
          <Card title="Ensemble Configuration" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Text strong>Ensemble Name:</Text>
                <input
                  type="text"
                  placeholder="e.g., My Image Ensemble"
                  value={ensembleName}
                  onChange={(e) => setEnsembleName(e.target.value)}
                  style={{
                    width: '100%',
                    marginTop: 8,
                    padding: '8px 12px',
                    border: '1px solid #d9d9d9',
                    borderRadius: 6,
                    fontSize: 14,
                  }}
                />
              </div>

              <div>
                <Text strong>Ensemble Method:</Text>
                <Radio.Group
                  value={ensembleMethod}
                  onChange={(e) => setEnsembleMethod(e.target.value)}
                  style={{ marginTop: 8, display: 'block' }}
                >
                  <Space direction="vertical">
                    <Radio value="voting">
                      <div>
                        <Text strong>Voting</Text>
                        <br />
                        <Text type="secondary">Combine predictions by majority vote</Text>
                      </div>
                    </Radio>
                    <Radio value="stacking">
                      <div>
                        <Text strong>Stacking</Text>
                        <br />
                        <Text type="secondary">Use a meta-model to combine predictions</Text>
                      </div>
                    </Radio>
                    <Radio value="bagging">
                      <div>
                        <Text strong>Bagging</Text>
                        <br />
                        <Text type="secondary">Bootstrap aggregating with resampling</Text>
                      </div>
                    </Radio>
                  </Space>
                </Radio.Group>
              </div>

              {ensembleMethod === 'voting' && (
                <div>
                  <Text strong>Voting Type:</Text>
                  <Radio.Group
                    value={votingType}
                    onChange={(e) => setVotingType(e.target.value)}
                    style={{ marginTop: 8, display: 'block' }}
                  >
                    <Radio value="hard">Hard Voting (Majority)</Radio>
                    <Radio value="soft">Soft Voting (Average Probabilities)</Radio>
                    <Radio value="weighted">Weighted Voting (Custom Weights)</Radio>
                  </Radio.Group>
                </div>
              )}

              <Button
                type="primary"
                size="large"
                icon={<PlusOutlined />}
                onClick={handleCreateEnsemble}
                loading={createMutation.isPending}
                block
              >
                Create Ensemble ({selectedModels.length} models)
              </Button>
            </Space>
          </Card>
        )}

        {/* Existing Ensembles */}
        {ensemblesData && ensemblesData.length > 0 && (
          <Card title="Your Ensembles">
            <Row gutter={[16, 16]}>
              {ensemblesData.map((ensemble: any, idx: number) => (
                <Col key={idx} xs={24} sm={12} md={8}>
                  <Card>
                    <Space direction="vertical">
                      <Text strong>{ensemble.name}</Text>
                      <Text type="secondary">Method: {ensemble.method}</Text>
                      <Text type="secondary">Models: {ensemble.model_count}</Text>
                      <Button size="small">View Details</Button>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        )}
      </Card>
    </div>
  );
};

export default EnsembleMethodsPage;

