# Models package
# Central registry for all model types

from . import image
from . import text
from . import audio
from . import video
from . import tabular
from . import timeseries
from . import medical
from . import genomic

__all__ = [
    'image',
    'text',
    'audio',
    'video',
    'tabular',
    'timeseries',
    'medical',
    'genomic'
]

# Model type registry
MODEL_REGISTRY = {
    'image': image,
    'text': text,
    'audio': audio,
    'video': video,
    'tabular': tabular,
    'timeseries': timeseries,
    'medical': medical,
    'genomic': genomic
}

def get_model_module(modality: str):
    """
    Get model module for a specific modality
    
    Args:
        modality: Data modality type
        
    Returns:
        Model module
    """
    if modality not in MODEL_REGISTRY:
        raise ValueError(f"Unknown modality: {modality}")
    return MODEL_REGISTRY[modality]

