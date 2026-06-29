import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider, Layout, Menu, Button, Space, Typography, App as AntApp, Drawer, Grid } from 'antd';
import {
  HomeOutlined,
  FolderOutlined,
  CloudServerOutlined,
  RobotOutlined,
  FundOutlined,
  AppstoreOutlined,
  BulbOutlined,
  MoonOutlined,
  SunOutlined,
  MenuOutlined,
  CloseOutlined,
} from '@ant-design/icons';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { lightTheme, darkTheme } from './theme';
import HomePage from './pages/HomePage';
import ProjectsPage from './pages/ProjectsPage';
import ImageProjectPage from './pages/ImageProjectPage';
import TextProjectPage from './pages/TextProjectPage';
import AudioProjectPage from './pages/AudioProjectPage';
import VideoProjectPage from './pages/VideoProjectPage';
import TabularProjectPage from './pages/TabularProjectPage';
import TimeSeriesProjectPage from './pages/TimeSeriesProjectPage';
import MedicalProjectPage from './pages/MedicalProjectPage';
import GenomicProjectPage from './pages/GenomicProjectPage';
import ModelSelectionPage from './pages/ModelSelectionPage';
import TrainingConfigPage from './pages/TrainingConfigPage';
import TrainingDashboardPage from './pages/TrainingDashboardPage';
import ResultsPage from './pages/ResultsPage';
import AutoMLPage from './pages/AutoMLPage';
import ModelServingPage from './pages/ModelServingPage';
import ModelComparisonPage from './pages/ModelComparisonPage';
import EnsembleMethodsPage from './pages/EnsembleMethodsPage';
import InferencePlaygroundPage from './pages/InferencePlaygroundPage';
import CloudTrainingPage from './pages/CloudTrainingPage';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;
const { useBreakpoint } = Grid;

// Create Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const screens = useBreakpoint();
  const [drawerVisible, setDrawerVisible] = useState(false);
  
  // Determine if mobile view (xs or sm)
  const isMobile = !screens.md;

  // Close drawer on route change
  useEffect(() => {
    setDrawerVisible(false);
  }, [location.pathname]);

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Home',
    },
    {
      key: '/projects',
      icon: <FolderOutlined />,
      label: 'Projects',
    },
    {
      key: 'features',
      label: 'Features',
      type: 'group' as const,
    },
    {
      key: '/automl',
      icon: <RobotOutlined />,
      label: 'AutoML',
    },
    {
      key: '/serving',
      icon: <CloudServerOutlined />,
      label: 'Model Serving',
    },
    {
      key: '/comparison',
      icon: <FundOutlined />,
      label: 'Comparison',
    },
    {
      key: '/ensemble',
      icon: <AppstoreOutlined />,
      label: 'Ensemble',
    },
    {
      key: '/cloud',
      icon: <CloudServerOutlined />,
      label: 'Cloud Training',
    },
    {
      key: '/inference',
      icon: <BulbOutlined />,
      label: 'Inference',
    },
  ];

  const handleMenuClick = (key: string) => {
    navigate(key);
    setDrawerVisible(false);
  };

  const renderMenu = () => (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      items={menuItems}
      onClick={({ key }) => handleMenuClick(key)}
      style={{ height: '100%', borderRight: 0 }}
    />
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header 
        className="app-header"
        style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between', 
          padding: isMobile ? '0 12px' : '0 24px',
          position: 'sticky',
          top: 0,
          zIndex: 1000,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {isMobile && (
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setDrawerVisible(true)}
              style={{ color: 'white', marginRight: 12, fontSize: 18 }}
            />
          )}
          <Title 
            level={isMobile ? 5 : 3} 
            style={{ 
              color: 'white', 
              margin: 0, 
              marginRight: isMobile ? 0 : 32,
              whiteSpace: 'nowrap',
            }}
          >
            🚀 {isMobile ? 'AI Builder' : 'AI Model Builder'}
          </Title>
        </div>
        <Space>
          <Button
            type="text"
            icon={theme === 'light' ? <MoonOutlined /> : <SunOutlined />}
            onClick={toggleTheme}
            style={{ color: 'white' }}
          >
            {!isMobile && (theme === 'light' ? 'Dark' : 'Light')}
          </Button>
        </Space>
      </Header>
      <Layout>
        {/* Desktop Sidebar */}
        {!isMobile && (
          <Sider 
            width={250} 
            theme={theme === 'dark' ? 'dark' : 'light'}
            style={{
              overflow: 'auto',
              height: 'calc(100vh - 64px)',
              position: 'sticky',
              top: 64,
              left: 0,
            }}
          >
            {renderMenu()}
          </Sider>
        )}
        
        {/* Mobile Drawer */}
        <Drawer
          title={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span>🚀 AI Model Builder</span>
            </div>
          }
          placement="left"
          onClose={() => setDrawerVisible(false)}
          open={drawerVisible}
          width={280}
          styles={{ body: { padding: 0 } }}
          closeIcon={<CloseOutlined />}
        >
          {renderMenu()}
        </Drawer>
        
        <Layout 
          style={{ 
            padding: isMobile ? '12px' : '0 24px 24px',
            minHeight: 'calc(100vh - 64px)',
          }}
        >
          <Content
            className="main-content"
            style={{
              margin: 0,
              minHeight: 280,
              overflow: 'auto',
            }}
          >
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              
              {/* Project creation routes */}
              <Route path="/project/new/image" element={<ImageProjectPage />} />
              <Route path="/project/new/text" element={<TextProjectPage />} />
              <Route path="/project/new/audio" element={<AudioProjectPage />} />
              <Route path="/project/new/video" element={<VideoProjectPage />} />
              <Route path="/project/new/tabular" element={<TabularProjectPage />} />
              <Route path="/project/new/timeseries" element={<TimeSeriesProjectPage />} />
              <Route path="/project/new/medical" element={<MedicalProjectPage />} />
              <Route path="/project/new/genomic" element={<GenomicProjectPage />} />
              
              {/* Model selection and training config */}
              <Route path="/project/:projectId/model-selection/:modality" element={<ModelSelectionPage />} />
              <Route path="/project/:projectId/training-config/:modality" element={<TrainingConfigPage />} />
              
              {/* Training routes */}
              <Route path="/training/:projectId" element={<TrainingDashboardPage />} />
              <Route path="/results/:projectId" element={<ResultsPage />} />
              
              {/* Feature routes */}
              <Route path="/automl" element={<AutoMLPage />} />
              <Route path="/serving" element={<ModelServingPage />} />
              <Route path="/comparison" element={<ModelComparisonPage />} />
              <Route path="/ensemble" element={<EnsembleMethodsPage />} />
              <Route path="/cloud" element={<CloudTrainingPage />} />
              <Route path="/inference" element={<InferencePlaygroundPage />} />
              
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </QueryClientProvider>
  );
};

const AppContent: React.FC = () => {
  const { theme } = useTheme();
  
  return (
    <ConfigProvider theme={theme === 'light' ? lightTheme : darkTheme}>
      <BrowserRouter>
        <AntApp>
          <AppLayout />
        </AntApp>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
