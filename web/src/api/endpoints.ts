import apiClient from './client';
import {
  Project,
  ProjectCreate,
  ProjectList,
} from '../types/project.types';
import {
  TrainingConfig,
  TrainingStatus,
  TrainingMetrics,
} from '../types/training.types';
import {
  Model,
  ModelInfo,
  InferenceResult,
  AutoMLConfig,
  AutoMLResult,
} from '../types/model.types';

// ============================================
// Project Management
// ============================================

export const projectApi = {
  list: () => apiClient.get<ProjectList>('/api/project/list'),
  
  create: (data: ProjectCreate) => 
    apiClient.post<Project>('/api/project/create', data),
  
  get: (projectId: string) => 
    apiClient.get<Project>(`/api/project/${projectId}`),
  
  update: (projectId: string, updates: Partial<Project>) =>
    apiClient.put<Project>(`/api/project/${projectId}`, updates),
  
  delete: (projectId: string) => 
    apiClient.delete(`/api/project/delete/${projectId}`),
};

// ============================================
// Data Management
// ============================================

export const dataApi = {
  upload: (projectId: string, formData: FormData, onProgress?: (progress: number) => void) =>
    apiClient.post(`/api/data/upload/${projectId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentage);
        }
      },
    }),
  
  getInfo: (projectId: string) =>
    apiClient.get(`/api/data/info/${projectId}`),
};

// ============================================
// Training
// ============================================

export const trainingApi = {
  start: (projectId: string, config: TrainingConfig) =>
    apiClient.post(`/api/training/start/${projectId}`, config),
  
  stop: (projectId: string) =>
    apiClient.post(`/api/training/stop/${projectId}`),
  
  resume: (projectId: string) =>
    apiClient.post(`/api/training/resume/${projectId}`),
  
  status: (projectId: string) =>
    apiClient.get<TrainingStatus>(`/api/training/status/${projectId}`),
  
  metrics: (projectId: string) =>
    apiClient.get<TrainingMetrics>(`/api/training/metrics/${projectId}`),
  
  tensorboard: {
    info: (projectId: string) =>
      apiClient.get(`/api/training/tensorboard/${projectId}`),
    launch: (projectId: string) =>
      apiClient.post(`/api/training/tensorboard/launch/${projectId}`),
  },
};

// ============================================
// Inference
// ============================================

export const inferenceApi = {
  predict: (projectId: string, formData: FormData) =>
    apiClient.post<InferenceResult>(`/api/inference/predict/${projectId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// ============================================
// Model Export
// ============================================

export const exportApi = {
  exportModel: (projectId: string, format: 'pytorch' | 'onnx' | 'torchscript') =>
    apiClient.post(`/api/export/${projectId}`, { format }),
  
  listExports: (projectId: string) =>
    apiClient.get(`/api/export/list/${projectId}`),
};

// ============================================
// AutoML
// ============================================

export const automlApi = {
  start: (config: AutoMLConfig) =>
    apiClient.post<AutoMLResult>('/api/automl/start', config),
  
  status: (projectId: string) =>
    apiClient.get(`/api/automl/status/${projectId}`),
  
  history: (projectId: string) =>
    apiClient.get(`/api/automl/history/${projectId}`),
  
  apply: (projectId: string) =>
    apiClient.post(`/api/automl/apply/${projectId}`),
  
  deleteResults: (projectId: string) =>
    apiClient.delete(`/api/automl/results/${projectId}`),
};

// ============================================
// Model Serving
// ============================================

export const servingApi = {
  register: (data: { model_id: string; model_path: string; model_type: string; metadata?: any }) =>
    apiClient.post('/api/serve/register', data),
  
  load: (modelId: string, device: 'cuda' | 'cpu' = 'cuda') =>
    apiClient.post(`/api/serve/load/${modelId}?device=${device}`),
  
  unload: (modelId: string) =>
    apiClient.delete(`/api/serve/unload/${modelId}`),
  
  listModels: () =>
    apiClient.get<{ loaded_models: ModelInfo[] }>('/api/serve/models'),
  
  getModel: (modelId: string) =>
    apiClient.get<ModelInfo>(`/api/serve/models/${modelId}`),
  
  predict: (modelId: string, formData: FormData) =>
    apiClient.post<InferenceResult>(`/api/serve/predict/${modelId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  health: () =>
    apiClient.get('/api/serve/health'),
  
  stats: () =>
    apiClient.get('/api/serve/stats'),
};

// ============================================
// Ensemble Methods
// ============================================

export const ensembleApi = {
  create: (data: {
    ensemble_name: string;
    model_ids: string[];
    method: 'voting' | 'stacking' | 'bagging';
    voting_type?: 'hard' | 'soft' | 'weighted';
  }) => apiClient.post('/api/ensemble/create', data),
  
  list: () =>
    apiClient.get('/api/ensemble/list'),
  
  get: (ensembleId: string) =>
    apiClient.get(`/api/ensemble/info/${ensembleId}`),
  
  availableModels: () =>
    apiClient.get('/api/ensemble/available-models'),
  
  delete: (ensembleId: string) =>
    apiClient.delete(`/api/ensemble/${ensembleId}`),
};

// ============================================
// Model Comparison
// ============================================

export const comparisonApi = {
  listProjects: () =>
    apiClient.get('/api/comparison/projects'),
  
  compare: (projectIds: string[]) =>
    apiClient.post('/api/comparison/compare', { project_ids: projectIds }),
  
  getDetails: (projectId: string) =>
    apiClient.get(`/api/comparison/project/${projectId}/details`),
  
  exportCsv: (projectIds: string[]) =>
    apiClient.get('/api/comparison/export/csv', {
      params: { project_ids: projectIds.join(',') },
      responseType: 'blob',
    }),
  
  statistics: () =>
    apiClient.get('/api/comparison/statistics'),
};

// ============================================
// System
// ============================================

export const systemApi = {
  info: () =>
    apiClient.get('/api/system/info'),
  
  devices: () =>
    apiClient.get('/api/system/devices'),
  
  health: () =>
    apiClient.get('/api/system/health'),
  
  models: (modality: string) =>
    apiClient.get<{ models: Model[] }>(`/api/system/models/list/${modality}`),
};

// ============================================
// Cloud Training
// ============================================

export const cloudApi = {
  start: (config: {
    project_id: string;
    provider: string;
    instance_type: string;
    region: string;
    use_spot: boolean;
    estimated_epochs: number;
    batch_size?: number;
    learning_rate?: number;
  }) => apiClient.post('/api/cloud/start', config),
  
  status: (jobId: string) =>
    apiClient.get(`/api/cloud/status/${jobId}`),
  
  stop: (jobId: string) =>
    apiClient.post(`/api/cloud/stop/${jobId}`),
  
  listJobs: () =>
    apiClient.get('/api/cloud/jobs'),
  
  download: (jobId: string, localPath?: string) =>
    apiClient.post(`/api/cloud/download/${jobId}`, { local_path: localPath }),
  
  health: () =>
    apiClient.get('/api/cloud/health'),
};

