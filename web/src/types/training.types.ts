// Training Configuration and Status Types

export interface TrainingConfig {
  epochs: number;
  batch_size: number;
  learning_rate: number;
  optimizer: string;
  device?: string;
  train_split?: number;
  val_split?: number;
  test_split?: number;
  use_augmentation?: boolean;
  dropout?: number;
  weight_decay?: number;
  early_stopping?: boolean;
  early_stopping_patience?: number;
  mixed_precision?: boolean;
  training_mode?: string;
  model_id?: string | null;
}

export interface TrainingStatus {
  status: 'idle' | 'training' | 'completed' | 'stopped' | 'error';
  current_epoch: number;
  total_epochs: number;
  train_loss: number;
  train_acc: number;
  val_loss: number;
  val_acc: number;
  best_val_acc: number;
  eta_seconds?: number;
  progress_percentage: number;
}

export interface TrainingHistory {
  epochs: number[];
  train_loss: number[];
  train_acc: number[];
  val_loss: number[];
  val_acc: number[];
}

export interface TrainingMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix?: number[][];
}

