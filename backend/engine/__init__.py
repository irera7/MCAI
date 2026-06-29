"""
ModelCreator Training Engine
Core components for real model training
"""

__version__ = "1.1.0"
__author__ = "ModelCreator Team"

from .data_loader import ImageDataLoader, create_data_loaders
from .text_data_loader import TextDataLoader, create_text_loaders
from .audio_data_loader import AudioDataLoader, create_audio_loaders
from .model_builder import ModelBuilder
from .trainer import Trainer
from .callbacks import EarlyStopping, ModelCheckpoint, ProgressCallback, TensorBoardCallback
from .hyperparameter_optimizer import HyperparameterOptimizer, optimize_hyperparameters
from .model_comparison import ModelComparison, TrainingRun, compare_models
from .ensemble import (
    VotingEnsemble, StackingEnsemble, BaggingEnsemble,
    create_voting_ensemble, evaluate_ensemble, quick_ensemble
)
from .cloud_training import CloudTrainer, AWSTrainer, AzureTrainer, GCPTrainer, create_cloud_trainer
from .collaboration import CollaborationManager, User, Team, UserRole, Permission

__all__ = [
    'ImageDataLoader',
    'create_data_loaders',
    'TextDataLoader',
    'create_text_loaders',
    'AudioDataLoader',
    'create_audio_loaders',
    'ModelBuilder',
    'Trainer',
    'EarlyStopping',
    'ModelCheckpoint',
    'ProgressCallback',
    'TensorBoardCallback',
    'HyperparameterOptimizer',
    'optimize_hyperparameters',
    'ModelComparison',
    'TrainingRun',
    'compare_models',
    'VotingEnsemble',
    'StackingEnsemble',
    'BaggingEnsemble',
    'create_voting_ensemble',
    'evaluate_ensemble',
    'quick_ensemble',
    'CloudTrainer',
    'AWSTrainer',
    'AzureTrainer',
    'GCPTrainer',
    'create_cloud_trainer',
    'CollaborationManager',
    'User',
    'Team',
    'UserRole',
    'Permission',
]

