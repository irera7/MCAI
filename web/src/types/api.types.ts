// API Request/Response Types

export interface ApiResponse<T = any> {
  status: string;
  message?: string;
  data?: T;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

