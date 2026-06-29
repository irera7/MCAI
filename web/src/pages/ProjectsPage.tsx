import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Space, Tag, Input, Select, Card, Typography, App, Grid, List, Dropdown } from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  SearchOutlined,
  EyeOutlined,
  MoreOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { projectApi } from '../api/endpoints';
import { Project } from '../types/project.types';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Search } = Input;
const { useBreakpoint } = Grid;

const ProjectsPage: React.FC = () => {
  const { message, modal } = App.useApp();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const screens = useBreakpoint();
  const isMobile = !screens.md;
  const [searchText, setSearchText] = React.useState('');
  const [modalityFilter, setModalityFilter] = React.useState<string>('all');

  // Fetch projects
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectApi.list();
      console.log('Projects fetched:', response.data);  // Debug log
      return response.data;
    },
    refetchInterval: 5000,  // Auto-refresh every 5 seconds
  });

  // Delete project mutation
  const deleteMutation = useMutation({
    mutationFn: (projectId: string) => projectApi.delete(projectId),
    onSuccess: () => {
      message.success('Project deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
    onError: (error: any) => {
      message.error(`Failed to delete project: ${error.detail || error.message}`);
    },
  });

  const handleDelete = (projectId: string, projectName: string) => {
    modal.confirm({
      title: 'Delete Project',
      content: `Are you sure you want to delete "${projectName}"? This action cannot be undone.`,
      okText: 'Delete',
      okType: 'danger',
      onOk: () => deleteMutation.mutate(projectId),
    });
  };

  const handleView = (projectId: string) => {
    navigate(`/training/${projectId}`);
  };

  const getModalityColor = (modality: string): string => {
    const colors: Record<string, string> = {
      image: 'blue',
      text: 'gold',
      audio: 'cyan',
      video: 'magenta',
      tabular: 'green',
      timeseries: 'red',
      medical: 'purple',
      genomic: 'geekblue',
    };
    return colors[modality] || 'default';
  };

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      idle: 'default',
      training: 'processing',
      completed: 'success',
      error: 'error',
    };
    return colors[status] || 'default';
  };

  const columns: ColumnsType<Project> = [
    {
      title: 'Project Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
      ellipsis: true,
    },
    {
      title: 'Modality',
      dataIndex: 'modality',
      key: 'modality',
      render: (modality: string) => (
        <Tag color={getModalityColor(modality)}>{modality.toUpperCase()}</Tag>
      ),
      responsive: ['sm'],
      filters: [
        { text: 'Image', value: 'image' },
        { text: 'Text', value: 'text' },
        { text: 'Audio', value: 'audio' },
        { text: 'Video', value: 'video' },
        { text: 'Tabular', value: 'tabular' },
        { text: 'TimeSeries', value: 'timeseries' },
        { text: 'Medical', value: 'medical' },
        { text: 'Genomic', value: 'genomic' },
      ],
      onFilter: (value, record) => record.modality === value,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status || 'idle')}>
          {(status || 'idle').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Model',
      dataIndex: 'model_name',
      key: 'model_name',
      render: (model: string) => model || '-',
      responsive: ['lg'],
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
      sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
      responsive: ['md'],
    },
    {
      title: 'Actions',
      key: 'actions',
      width: isMobile ? 80 : 250,
      render: (_, record) => isMobile ? (
        <Dropdown
          menu={{
            items: [
              { key: 'view', label: 'View', icon: <EyeOutlined />, onClick: () => handleView(record.id) },
              { key: 'train', label: 'Train', icon: <PlayCircleOutlined />, onClick: () => navigate(`/training/${record.id}`) },
              { key: 'delete', label: 'Delete', icon: <DeleteOutlined />, danger: true, onClick: () => handleDelete(record.id, record.name) },
            ]
          }}
          trigger={['click']}
        >
          <Button icon={<MoreOutlined />} />
        </Dropdown>
      ) : (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record.id)}
          >
            View
          </Button>
          <Button
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => navigate(`/training/${record.id}`)}
          >
            Train
          </Button>
          <Button
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id, record.name)}
            loading={deleteMutation.isPending}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  const filteredData = React.useMemo(() => {
    if (!data?.projects) return [];
    let filtered = data.projects;
    
    if (modalityFilter !== 'all') {
      filtered = filtered.filter((p) => p.modality === modalityFilter);
    }
    
    if (searchText) {
      filtered = filtered.filter((p) =>
        p.name.toLowerCase().includes(searchText.toLowerCase())
      );
    }
    
    return filtered;
  }, [data, modalityFilter, searchText]);

  if (error) {
    return (
      <Card style={{ margin: isMobile ? 12 : 24 }}>
        <Title level={4}>Error Loading Projects</Title>
        <p>{(error as any).detail || 'Failed to load projects'}</p>
        <Button onClick={() => queryClient.invalidateQueries({ queryKey: ['projects'] })}>
          Retry
        </Button>
      </Card>
    );
  }

  // Mobile card view for projects
  const renderMobileProjectCard = (project: Project) => (
    <Card
      key={project.id}
      style={{ marginBottom: 12 }}
      size="small"
      onClick={() => handleView(project.id)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <Text strong style={{ fontSize: 14 }}>{project.name}</Text>
          <div style={{ marginTop: 8 }}>
            <Tag color={getModalityColor(project.modality)} style={{ marginRight: 4 }}>
              {project.modality.toUpperCase()}
            </Tag>
            <Tag color={getStatusColor(project.status || 'idle')}>
              {(project.status || 'idle').toUpperCase()}
            </Tag>
          </div>
          <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 8 }}>
            {new Date(project.created_at).toLocaleDateString()}
          </Text>
        </div>
        <Dropdown
          menu={{
            items: [
              { key: 'view', label: 'View', icon: <EyeOutlined />, onClick: (e) => { e.domEvent.stopPropagation(); handleView(project.id); } },
              { key: 'train', label: 'Train', icon: <PlayCircleOutlined />, onClick: (e) => { e.domEvent.stopPropagation(); navigate(`/training/${project.id}`); } },
              { key: 'delete', label: 'Delete', icon: <DeleteOutlined />, danger: true, onClick: (e) => { e.domEvent.stopPropagation(); handleDelete(project.id, project.name); } },
            ]
          }}
          trigger={['click']}
        >
          <Button icon={<MoreOutlined />} onClick={(e) => e.stopPropagation()} />
        </Dropdown>
      </div>
    </Card>
  );

  return (
    <div style={{ padding: isMobile ? 12 : 24 }}>
      <div style={{ marginBottom: isMobile ? 16 : 24 }}>
        <Title level={isMobile ? 3 : 2}>Projects</Title>
        <Space style={{ marginBottom: 16, width: '100%' }} wrap direction={isMobile ? 'vertical' : 'horizontal'}>
          <Search
            placeholder="Search projects..."
            allowClear
            style={{ width: isMobile ? '100%' : 300 }}
            onChange={(e) => setSearchText(e.target.value)}
            prefix={<SearchOutlined />}
          />
          <div style={{ display: 'flex', gap: 8, width: isMobile ? '100%' : 'auto' }}>
            <Select
              value={modalityFilter}
              onChange={setModalityFilter}
              style={{ width: isMobile ? 'calc(100% - 88px)' : 200 }}
            >
              <Select.Option value="all">All Modalities</Select.Option>
              <Select.Option value="image">Image</Select.Option>
              <Select.Option value="text">Text</Select.Option>
              <Select.Option value="audio">Audio</Select.Option>
              <Select.Option value="video">Video</Select.Option>
              <Select.Option value="tabular">Tabular</Select.Option>
              <Select.Option value="timeseries">TimeSeries</Select.Option>
              <Select.Option value="medical">Medical</Select.Option>
              <Select.Option value="genomic">Genomic</Select.Option>
            </Select>
            <Button icon={<ReloadOutlined />} onClick={() => refetch()} />
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/')}
            style={{ width: isMobile ? '100%' : 'auto' }}
          >
            {isMobile ? 'New Project' : 'Create New Project'}
          </Button>
        </Space>
      </div>

      {isMobile ? (
        // Mobile: Card List View
        <div>
          {isLoading ? (
            <Card loading style={{ marginBottom: 12 }} />
          ) : filteredData.length === 0 ? (
            <Card>
              <Text type="secondary">No projects found</Text>
            </Card>
          ) : (
            filteredData.map(renderMobileProjectCard)
          )}
        </div>
      ) : (
        // Desktop: Table View
        <Card>
          <Table
            columns={columns}
            dataSource={filteredData}
            rowKey="id"
            loading={isLoading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `Total ${total} projects`,
            }}
            scroll={{ x: 800 }}
          />
        </Card>
      )}
    </div>
  );
};

export default ProjectsPage;

