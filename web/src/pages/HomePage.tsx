import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Typography, Button, Space, Grid } from 'antd';
import {
  CameraOutlined,
  FileTextOutlined,
  AudioOutlined,
  VideoCameraOutlined,
  TableOutlined,
  LineChartOutlined,
  MedicineBoxOutlined,
  ExperimentOutlined,
  RobotOutlined,
  CloudServerOutlined,
  FundOutlined,
  AppstoreOutlined,
} from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { useBreakpoint } = Grid;

interface FeatureCard {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  route: string;
  models?: string[];
}

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const screens = useBreakpoint();
  const isMobile = !screens.md;

  const modalityCards: FeatureCard[] = [
    {
      title: 'Image Classification',
      description: 'Train powerful CNN models for image recognition',
      icon: <CameraOutlined style={{ fontSize: 48 }} />,
      color: '#EEF2FF',
      route: '/project/new/image',
      models: ['ResNet', 'EfficientNet', 'ViT'],
    },
    {
      title: 'Text Classification',
      description: 'Build NLP models for text analysis',
      icon: <FileTextOutlined style={{ fontSize: 48 }} />,
      color: '#FEF3C7',
      route: '/project/new/text',
      models: ['LSTM', 'BERT', 'Transformer'],
    },
    {
      title: 'Audio Classification',
      description: 'Classify audio and sound patterns',
      icon: <AudioOutlined style={{ fontSize: 48 }} />,
      color: '#DBEAFE',
      route: '/project/new/audio',
      models: ['Spectrogram CNN'],
    },
    {
      title: 'Video Classification',
      description: 'Analyze video sequences and actions',
      icon: <VideoCameraOutlined style={{ fontSize: 48 }} />,
      color: '#FCE7F3',
      route: '/project/new/video',
      models: ['3D CNN', 'R2Plus1D'],
    },
    {
      title: 'Tabular Data',
      description: 'Train models on structured data',
      icon: <TableOutlined style={{ fontSize: 48 }} />,
      color: '#DCFCE7',
      route: '/project/new/tabular',
      models: ['XGBoost', 'LightGBM'],
    },
    {
      title: 'Time Series',
      description: 'Forecast future values from time series',
      icon: <LineChartOutlined style={{ fontSize: 48 }} />,
      color: '#FEE2E2',
      route: '/project/new/timeseries',
      models: ['LSTM', 'Attention-LSTM'],
    },
    {
      title: 'Medical Imaging',
      description: 'Process MRI, ECG, EEG for diagnosis',
      icon: <MedicineBoxOutlined style={{ fontSize: 48 }} />,
      color: '#FCE7F3',
      route: '/project/new/medical',
      models: ['MRI CNN', 'ECG CNN'],
    },
    {
      title: 'Genomic Analysis',
      description: 'Analyze DNA/RNA sequences',
      icon: <ExperimentOutlined style={{ fontSize: 48 }} />,
      color: '#E0E7FF',
      route: '/project/new/genomic',
      models: ['DNA CNN'],
    },
  ];

  const advancedFeatures: FeatureCard[] = [
    {
      title: 'Model Comparison',
      description: 'Compare multiple trained models side by side',
      icon: <FundOutlined style={{ fontSize: 32 }} />,
      color: '#F3F4F6',
      route: '/comparison',
    },
    {
      title: 'Ensemble Methods',
      description: 'Combine models for better accuracy',
      icon: <AppstoreOutlined style={{ fontSize: 32 }} />,
      color: '#F3F4F6',
      route: '/ensemble',
    },
    {
      title: 'Cloud Training',
      description: 'Train on AWS, Azure, or GCP',
      icon: <CloudServerOutlined style={{ fontSize: 32 }} />,
      color: '#F3F4F6',
      route: '/cloud',
    },
    {
      title: 'AutoML',
      description: 'Automatic hyperparameter optimization',
      icon: <RobotOutlined style={{ fontSize: 32 }} />,
      color: '#F3F4F6',
      route: '/automl',
    },
  ];

  return (
    <div style={{ padding: isMobile ? '12px' : '24px' }}>
      {/* Hero Section */}
      <div
        style={{
          background: 'linear-gradient(135deg, #6366F1 0%, #818CF8 100%)',
          borderRadius: isMobile ? 12 : 16,
          padding: isMobile ? '24px 16px' : '48px',
          marginBottom: isMobile ? 20 : 32,
          color: 'white',
          boxShadow: '0 10px 40px rgba(99, 102, 241, 0.3)',
        }}
      >
        <Title level={isMobile ? 2 : 1} style={{ color: 'white', marginBottom: isMobile ? 8 : 16 }}>
          🚀 {isMobile ? 'AI Model Builder' : 'Welcome to AI Model Builder'}
        </Title>
        <Paragraph style={{ color: 'white', fontSize: isMobile ? 14 : 18, marginBottom: isMobile ? 12 : 16 }}>
          Build, train, and deploy AI models without writing code
        </Paragraph>
        <Space wrap style={{ marginTop: isMobile ? 8 : 16 }}>
          <Button 
            type="primary" 
            size={isMobile ? 'middle' : 'large'} 
            style={{ background: 'rgba(255,255,255,0.2)', borderColor: 'white' }}
          >
            8 Data Types
          </Button>
          <Button 
            type="primary" 
            size={isMobile ? 'middle' : 'large'} 
            style={{ background: 'rgba(255,255,255,0.2)', borderColor: 'white' }}
          >
            20+ Models
          </Button>
          {!isMobile && (
            <Button type="primary" size="large" style={{ background: 'rgba(255,255,255,0.2)', borderColor: 'white' }}>
              AutoML
            </Button>
          )}
        </Space>
      </div>

      {/* Data Types Section */}
      <Title level={isMobile ? 3 : 2} style={{ marginBottom: isMobile ? 16 : 24 }}>
        📊 Data Types
      </Title>
      <Row gutter={[isMobile ? 8 : 16, isMobile ? 8 : 16]} style={{ marginBottom: isMobile ? 24 : 48 }}>
        {modalityCards.map((card, index) => (
          <Col key={index} xs={12} sm={12} md={8} lg={6}>
            <Card
              hoverable
              onClick={() => navigate(card.route)}
              style={{
                height: '100%',
                borderRadius: isMobile ? 8 : 12,
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              }}
              styles={{ body: { padding: isMobile ? 12 : 20 } }}
            >
              <div style={{ textAlign: 'center' }}>
                <div
                  style={{
                    background: card.color,
                    width: isMobile ? 56 : 80,
                    height: isMobile ? 56 : 80,
                    borderRadius: isMobile ? 8 : 12,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto',
                    marginBottom: isMobile ? 8 : 16,
                    color: '#6366F1',
                  }}
                >
                  {React.cloneElement(card.icon as React.ReactElement, {
                    style: { fontSize: isMobile ? 28 : 48 }
                  })}
                </div>
                <Title level={isMobile ? 5 : 4} style={{ marginBottom: isMobile ? 4 : 8, fontSize: isMobile ? 13 : undefined }}>
                  {card.title}
                </Title>
                {!isMobile && (
                  <Paragraph style={{ fontSize: 13, marginBottom: 12 }}>
                    {card.description}
                  </Paragraph>
                )}
                {card.models && !isMobile && (
                  <Space wrap size="small">
                    {card.models.map((model) => (
                      <span
                        key={model}
                        style={{
                          background: '#EEF2FF',
                          padding: '2px 8px',
                          borderRadius: 12,
                          fontSize: 11,
                          color: '#6366F1',
                        }}
                      >
                        {model}
                      </span>
                    ))}
                  </Space>
                )}
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Advanced Features Section */}
      <Title level={isMobile ? 3 : 2} style={{ marginBottom: isMobile ? 16 : 24 }}>
        ⚡ Advanced Features
      </Title>
      <Row gutter={[isMobile ? 8 : 16, isMobile ? 8 : 16]} style={{ marginBottom: isMobile ? 24 : 48 }}>
        {advancedFeatures.map((card, index) => (
          <Col key={index} xs={12} sm={12} md={6}>
            <Card
              hoverable
              onClick={() => navigate(card.route)}
              style={{
                height: '100%',
                borderRadius: isMobile ? 8 : 12,
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              }}
              styles={{ body: { padding: isMobile ? 12 : 24 } }}
            >
              <div style={{ textAlign: 'center' }}>
                <div style={{ marginBottom: isMobile ? 8 : 12, color: '#6366F1' }}>
                  {React.cloneElement(card.icon as React.ReactElement, {
                    style: { fontSize: isMobile ? 24 : 32 }
                  })}
                </div>
                <Title level={5} style={{ marginBottom: isMobile ? 4 : 8, fontSize: isMobile ? 13 : undefined }}>
                  {card.title}
                </Title>
                {!isMobile && (
                  <Paragraph style={{ fontSize: 13, marginBottom: 0 }}>
                    {card.description}
                  </Paragraph>
                )}
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Getting Started */}
      <Card
        style={{
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(129, 140, 248, 0.1) 100%)',
          borderRadius: isMobile ? 12 : 16,
          border: 'none',
        }}
        styles={{ body: { padding: isMobile ? 16 : 24 } }}
      >
        <Title level={isMobile ? 4 : 3}>💡 Getting Started</Title>
        <ol style={{ fontSize: isMobile ? 13 : 14, lineHeight: 2, paddingLeft: isMobile ? 20 : 40 }}>
          <li>Select a data type from above</li>
          <li>Upload your dataset and choose a model</li>
          <li>Configure training parameters</li>
          <li>Monitor results and deploy</li>
        </ol>
        <Button type="primary" size={isMobile ? 'middle' : 'large'} onClick={() => navigate('/projects')}>
          View All Projects
        </Button>
      </Card>
    </div>
  );
};

export default HomePage;

