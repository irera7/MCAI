"""
Create sample audio dataset for testing
Generates simple sine wave audio files for testing audio classification
"""

import os
import numpy as np
import soundfile as sf
from pathlib import Path
import json

def generate_sine_wave(frequency: float, duration: float, sample_rate: int = 22050) -> np.ndarray:
    """
    Generate a sine wave audio signal
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        Audio waveform as numpy array
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    return audio.astype(np.float32)

def create_sample_audio_dataset(
    project_name: str = "audio-test",
    num_samples_per_class: int = 10,
    duration: float = 3.0,
    sample_rate: int = 22050
):
    """
    Create a sample audio dataset with different frequency classes
    
    Args:
        project_name: Name of the project
        num_samples_per_class: Number of audio files per class
        duration: Duration of each audio file in seconds
        sample_rate: Audio sample rate
    """
    project_dir = Path(f"../projects/{project_name}")
    data_dir = project_dir / "data"
    
    # Clear existing data
    if project_dir.exists():
        import shutil
        shutil.rmtree(project_dir)
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Define classes with different frequency ranges
    classes = {
        "low_tone": 220,    # A3 note (low)
        "mid_tone": 440,    # A4 note (middle)
        "high_tone": 880    # A5 note (high)
    }
    
    label_map = {name: idx for idx, name in enumerate(classes.keys())}
    
    # Create labels.json
    with open(project_dir / "labels.json", "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)
    
    print(f"Creating sample audio dataset: {project_name}")
    print(f"Classes: {list(classes.keys())}")
    print(f"Samples per class: {num_samples_per_class}")
    print(f"Duration: {duration}s, Sample rate: {sample_rate}Hz")
    print()
    
    # Generate audio files
    total_created = 0
    for class_name, base_frequency in classes.items():
        class_dir = data_dir / class_name
        class_dir.mkdir(exist_ok=True)
        
        for i in range(num_samples_per_class):
            # Add slight frequency variation to make samples more diverse
            frequency_variation = np.random.uniform(-20, 20)
            frequency = base_frequency + frequency_variation
            
            # Generate audio
            audio = generate_sine_wave(frequency, duration, sample_rate)
            
            # Add slight noise
            noise = np.random.normal(0, 0.02, audio.shape)
            audio = audio + noise
            
            # Save as WAV file
            filename = class_dir / f"sample_{i:03d}.wav"
            sf.write(filename, audio, sample_rate)
            total_created += 1
        
        print(f"✅ Created {num_samples_per_class} samples for '{class_name}'")
    
    # Create project.json
    project_info = {
        "name": project_name,
        "modality": "audio",
        "created_at": "2025-11-30",
        "description": "Sample audio classification dataset with sine waves",
        "sample_rate": sample_rate,
        "duration": duration
    }
    
    with open(project_dir / "project.json", "w", encoding="utf-8") as f:
        json.dump(project_info, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"✅ Created {total_created} audio files total")
    print(f"📂 Dataset location: {project_dir}")
    print(f"📊 Labels: {label_map}")
    print()
    print("Dataset structure:")
    print(f"{project_dir}/")
    print(f"├── data/")
    for class_name in classes.keys():
        print(f"│   ├── {class_name}/")
        print(f"│   │   ├── sample_000.wav")
        print(f"│   │   ├── ...")
        print(f"│   │   └── sample_{num_samples_per_class-1:03d}.wav")
    print(f"├── labels.json")
    print(f"└── project.json")
    print()
    print("✅ Ready for training!")

if __name__ == "__main__":
    # Check if soundfile is available
    try:
        import soundfile
        print("✅ soundfile library is available\n")
    except ImportError:
        print("❌ soundfile library is not installed!")
        print("Install it with: pip install soundfile")
        exit(1)
    
    # Check if librosa is available (needed for data loader)
    try:
        import librosa
        print("✅ librosa library is available\n")
    except ImportError:
        print("❌ librosa library is not installed!")
        print("Install it with: pip install librosa")
        exit(1)
    
    # Create dataset
    create_sample_audio_dataset(
        project_name="audio-test",
        num_samples_per_class=10,
        duration=3.0
    )

