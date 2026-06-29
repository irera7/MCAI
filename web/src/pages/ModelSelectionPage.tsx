import React, { useState, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, Button, Row, Col, Typography, Progress, Badge, Space } from 'antd';
import { LeftOutlined, RightOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface ModelInfo {
  id: string;
  name: string;
  category: string;
  description: string;
  icon: string;
  isRecommended: boolean;
  speed: number; // 1-5
  accuracy: number; // 1-5
  memory: number; // 1-5
  trainingTime: string;
  parameters: string;
}

const modelsByModality: Record<string, ModelInfo[]> = {
  image: [
    {
      id: 'resnet18',  // Changed from 'simple_cnn'
      name: 'Simple CNN',
      category: 'Convolutional Neural Network',
      description: 'Fast and lightweight CNN perfect for quick prototyping and simple image classification tasks.',
      icon: '🏃',
      isRecommended: false,
      speed: 5,
      accuracy: 3,
      memory: 2,
      trainingTime: '~5-10 min',
      parameters: '~11M'
    },
    {
      id: 'mobilenetv3_small_100',  // Changed from 'mobilenet_v3'
      name: 'MobileNetV3',
      category: 'Efficient Architecture',
      description: 'Optimized for mobile deployment. Excellent balance of speed, accuracy, and model size.',
      icon: '📱',
      isRecommended: true,
      speed: 4,
      accuracy: 4,
      memory: 2,
      trainingTime: '~15-20 min',
      parameters: '~5.4M'
    },
    {
      id: 'resnet50',
      name: 'ResNet-50',
      category: 'Deep Residual Network',
      description: 'Industry-standard architecture with excellent accuracy. Best for complex image classification.',
      icon: '🎯',
      isRecommended: false,
      speed: 2,
      accuracy: 5,
      memory: 4,
      trainingTime: '~30-45 min',
      parameters: '~25M'
    },
    {
      id: 'vit_small_patch16_224',  // Changed from 'vision_transformer'
      name: 'Vision Transformer',
      category: 'Transformer-based',
      description: 'State-of-the-art transformer architecture. Requires more data but achieves top accuracy.',
      icon: '✨',
      isRecommended: false,
      speed: 1,
      accuracy: 5,
      memory: 5,
      trainingTime: '~1-2 hours',
      parameters: '~22M'
    }
  ],
  text: [
    {
      id: 'tfidf',  // Simplified ID
      name: 'TF-IDF + Classifier',
      category: 'Classical ML',
      description: 'Fast traditional approach using TF-IDF features. Great for quick results with small datasets.',
      icon: '📝',
      isRecommended: false,
      speed: 5,
      accuracy: 3,
      memory: 1,
      trainingTime: '~1-2 min',
      parameters: '~100K'
    },
    {
      id: 'lstm',
      name: 'LSTM Network',
      category: 'Recurrent Neural Network',
      description: 'Effective for sequence understanding. Good balance of performance and speed.',
      icon: '🔄',
      isRecommended: true,
      speed: 3,
      accuracy: 4,
      memory: 3,
      trainingTime: '~10-15 min',
      parameters: '~2M'
    },
    {
      id: 'bert',  // Changed from 'bert_small'
      name: 'BERT-Small',
      category: 'Transformer',
      description: 'Contextual language model. Best accuracy for text classification tasks.',
      icon: '🤖',
      isRecommended: false,
      speed: 2,
      accuracy: 5,
      memory: 4,
      trainingTime: '~20-30 min',
      parameters: '~30M'
    }
  ],
  audio: [
    {
      id: 'spectrogram_cnn',
      name: 'Spectrogram CNN',
      category: '2D Convolutional',
      description: 'Converts audio to spectrograms and uses CNN. Excellent for most audio tasks.',
      icon: '🎵',
      isRecommended: true,
      speed: 4,
      accuracy: 4,
      memory: 3,
      trainingTime: '~15-20 min',
      parameters: '~3M'
    },
    {
      id: 'audio_transformer',
      name: 'Audio Transformer',
      category: 'Transformer-based',
      description: 'Advanced architecture for complex audio patterns. Best for large datasets.',
      icon: '🎼',
      isRecommended: false,
      speed: 2,
      accuracy: 5,
      memory: 4,
      trainingTime: '~30-45 min',
      parameters: '~12M'
    }
  ],
  video: [
    {
      id: '3d_cnn',
      name: '3D CNN',
      category: 'Spatiotemporal',
      description: 'Processes video frames spatially and temporally. Good for action recognition.',
      icon: '🎬',
      isRecommended: true,
      speed: 2,
      accuracy: 4,
      memory: 5,
      trainingTime: '~1-2 hours',
      parameters: '~10M'
    }
  ],
  tabular: [
    {
      id: 'mlp',
      name: 'Multi-Layer Perceptron',
      category: 'Neural Network',
      description: 'Simple and fast neural network. Good starting point for tabular data.',
      icon: '📊',
      isRecommended: false,
      speed: 5,
      accuracy: 3,
      memory: 1,
      trainingTime: '~2-5 min',
      parameters: '~50K'
    },
    {
      id: 'xgboost',
      name: 'XGBoost',
      category: 'Gradient Boosting',
      description: 'Industry-standard for tabular data. Excellent accuracy with minimal tuning.',
      icon: '🚀',
      isRecommended: true,
      speed: 4,
      accuracy: 5,
      memory: 2,
      trainingTime: '~5-10 min',
      parameters: 'Variable'
    },
    {
      id: 'random_forest',
      name: 'Random Forest',
      category: 'Ensemble Learning',
      description: 'Reliable and interpretable. Great for feature importance analysis.',
      icon: '🌲',
      isRecommended: false,
      speed: 3,
      accuracy: 4,
      memory: 2,
      trainingTime: '~3-8 min',
      parameters: 'Variable'
    }
  ],
  timeseries: [
    {
      id: 'lstm_ts',
      name: 'LSTM',
      category: 'Recurrent Network',
      description: 'Specialized for sequential data. Captures temporal dependencies effectively.',
      icon: '📈',
      isRecommended: true,
      speed: 3,
      accuracy: 4,
      memory: 3,
      trainingTime: '~15-20 min',
      parameters: '~1.5M'
    },
    {
      id: 'temporal_cnn',
      name: 'Temporal CNN',
      category: 'Convolutional',
      description: 'Fast and efficient for time series. Good for pattern recognition.',
      icon: '⚡',
      isRecommended: false,
      speed: 4,
      accuracy: 3,
      memory: 2,
      trainingTime: '~10-15 min',
      parameters: '~800K'
    },
    {
      id: 'transformer_ts',
      name: 'Transformer',
      category: 'Attention-based',
      description: 'State-of-the-art for complex time series. Handles long sequences well.',
      icon: '🔮',
      isRecommended: false,
      speed: 2,
      accuracy: 5,
      memory: 4,
      trainingTime: '~30-40 min',
      parameters: '~8M'
    }
  ],
  medical: [
    {
      id: 'medical_cnn',
      name: 'Medical CNN',
      category: '2D Convolutional',
      description: 'Optimized for medical images (MRI, CT scans). Includes preprocessing steps.',
      icon: '🏥',
      isRecommended: true,
      speed: 3,
      accuracy: 4,
      memory: 3,
      trainingTime: '~20-30 min',
      parameters: '~5M'
    },
    {
      id: 'signal_cnn',
      name: 'Signal 1D CNN',
      category: '1D Convolutional',
      description: 'For ECG, EEG signals. Specialized for time-series medical data.',
      icon: '💓',
      isRecommended: false,
      speed: 4,
      accuracy: 4,
      memory: 2,
      trainingTime: '~15-20 min',
      parameters: '~2M'
    }
  ],
  genomic: [
    {
      id: 'dna_cnn',
      name: 'DNA CNN',
      category: '1D Convolutional',
      description: 'Specialized for DNA sequence analysis. One-hot encoding built-in.',
      icon: '🧬',
      isRecommended: true,
      speed: 3,
      accuracy: 4,
      memory: 3,
      trainingTime: '~15-25 min',
      parameters: '~3M'
    },
    {
      id: 'sequence_embedding',
      name: 'Sequence Embedding',
      category: 'Embedding + LSTM',
      description: 'Learns sequence representations. Good for variable-length sequences.',
      icon: '🔬',
      isRecommended: false,
      speed: 2,
      accuracy: 4,
      memory: 4,
      trainingTime: '~20-30 min',
      parameters: '~5M'
    }
  ]
};

const ModelSelectionPage: React.FC = () => {
  const { projectId, modality } = useParams<{ projectId: string; modality: string }>();
  const navigate = useNavigate();
  const [selectedModel, setSelectedModel] = useState<string | null>(null);

  const models = useMemo(() => {
    return modelsByModality[modality || 'image'] || [];
  }, [modality]);

  const handleModelSelect = (modelId: string) => {
    setSelectedModel(modelId);
  };

  const handleNext = () => {
    if (selectedModel) {
      navigate(`/project/${projectId}/training-config/${modality}?model=${selectedModel}`);
    }
  };

  const handleBack = () => {
    navigate(`/project/new/${modality}`);
  };

  return (
    <div style={{ padding: 40, maxWidth: 1400, margin: '0 auto' }}>
      <Title level={2}>Select Model Architecture</Title>
      <Paragraph type="secondary" style={{ fontSize: 16, marginBottom: 30 }}>
        Choose a pre-configured model architecture for your data type
      </Paragraph>

      <Row gutter={[24, 24]}>
        {models.map((model) => (
          <Col xs={24} lg={12} key={model.id}>
            <Card
              hoverable
              onClick={() => handleModelSelect(model.id)}
              style={{
                height: '100%',
                borderColor: selectedModel === model.id ? '#6366F1' : undefined,
                borderWidth: selectedModel === model.id ? 2 : 1,
                backgroundColor: selectedModel === model.id ? '#F0F5FF' : undefined,
                cursor: 'pointer'
              }}
              styles={{ body: { padding: 24 } }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                <Space>
                  <span style={{ fontSize: 32 }}>{model.icon}</span>
                  <div>
                    <Title level={4} style={{ margin: 0 }}>{model.name}</Title>
                    <Text type="secondary" style={{ fontSize: 12 }}>{model.category}</Text>
                  </div>
                </Space>
                {model.isRecommended && (
                  <Badge count="⭐ Recommended" style={{ backgroundColor: '#6366F1' }} />
                )}
              </div>

              <Paragraph type="secondary" style={{ fontSize: 13, marginBottom: 16 }}>
                {model.description}
              </Paragraph>

              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={8}>
                  <Text type="secondary" style={{ fontSize: 11 }}>Speed</Text>
                  <Progress 
                    percent={(model.speed / 5) * 100} 
                    showInfo={false} 
                    strokeColor="#22C55E" 
                    size="small"
                  />
                </Col>
                <Col span={8}>
                  <Text type="secondary" style={{ fontSize: 11 }}>Accuracy</Text>
                  <Progress 
                    percent={(model.accuracy / 5) * 100} 
                    showInfo={false} 
                    strokeColor="#6366F1" 
                    size="small"
                  />
                </Col>
                <Col span={8}>
                  <Text type="secondary" style={{ fontSize: 11 }}>Memory</Text>
                  <Progress 
                    percent={(model.memory / 5) * 100} 
                    showInfo={false} 
                    strokeColor="#F59E0B" 
                    size="small"
                  />
                </Col>
              </Row>

              <div 
                style={{ 
                  backgroundColor: '#F5F5F5', 
                  borderRadius: 4, 
                  padding: 12,
                  display: 'flex',
                  justifyContent: 'space-between'
                }}
              >
                <div>
                  <Text type="secondary" style={{ fontSize: 10 }}>Training Time</Text>
                  <div><Text strong style={{ fontSize: 12 }}>{model.trainingTime}</Text></div>
                </div>
                <div>
                  <Text type="secondary" style={{ fontSize: 10 }}>Parameters</Text>
                  <div><Text strong style={{ fontSize: 12 }}>{model.parameters}</Text></div>
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <div style={{ marginTop: 30, display: 'flex', justifyContent: 'space-between' }}>
        <Button 
          size="large" 
          icon={<LeftOutlined />}
          onClick={handleBack}
        >
          Back
        </Button>
        <Button 
          type="primary" 
          size="large" 
          icon={<RightOutlined />}
          onClick={handleNext}
          disabled={!selectedModel}
        >
          Next: Configure Training
        </Button>
      </div>
    </div>
  );
};

export default ModelSelectionPage;

