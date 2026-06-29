// Project-related Types

export type Modality = 
  | 'image' 
  | 'text' 
  | 'audio' 
  | 'video' 
  | 'tabular' 
  | 'timeseries' 
  | 'medical' 
  | 'genomic';

export interface Project {
  id: string;
  name: string;
  modality: Modality;
  description?: string;
  created_at: string;
  updated_at?: string;
  status?: 'idle' | 'training' | 'completed' | 'error';
  model_name?: string;
  num_classes?: number;
}

export interface ProjectCreate {
  name: string;
  modality: Modality;
  description?: string;
}

export interface ProjectList {
  projects: Project[];
  total: number;
}

