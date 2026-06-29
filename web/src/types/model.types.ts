// Model Definition Types

export interface Model {
  id: string;
  name: string;
  modality: string;
  description?: string;
  parameters?: number;
  pretrained?: boolean;
}

export interface ModelInfo {
  model_id: string;
  model_type: string;
  device: string;
  memory_mb: number;
  request_count: number;
  avg_latency: number;
}

export interface InferenceResult {
  predicted_class: string;
  class_id: number;
  confidence: number;
  probabilities?: Record<string, number>;
  latency_ms?: number;
}

export interface AutoMLConfig {
  project_id: string;
  n_trials: number;
  timeout?: number;
  optimizer: 'tpe' | 'random' | 'grid';
  metric: 'accuracy' | 'loss' | 'f1';
  search_space: Record<string, any>;
}

export interface AutoMLResult {
  status: string;
  best_score: number;
  total_trials: number;
  best_params: Record<string, any>;
  trial_history: TrialData[];
  optimization_time: number;
}

export interface TrialData {
  number: number;
  score: number;
  params: Record<string, any>;
}

