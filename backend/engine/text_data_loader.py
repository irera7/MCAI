"""
Text Data Loader Module
Handles loading and preprocessing of text datasets for classification
"""

import torch
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import pandas as pd
from collections import Counter
import re


class TextDataset(Dataset):
    """
    Dataset for text classification
    
    Expected structure:
    data_dir/
        train.csv  (or train.txt, train.json)
        - text, label columns
    
    OR:
    data_dir/
        class_1/
            text1.txt
            text2.txt
        class_2/
            text3.txt
            text4.txt
    """
    
    def __init__(
        self,
        data_dir: str,
        label_map: Dict[str, int],
        vocab: Optional[Dict[str, int]] = None,
        max_length: int = 512,
        split: str = 'train'
    ):
        """
        Args:
            data_dir: Root directory containing text data
            label_map: Mapping from class name to class ID
            vocab: Vocabulary mapping (word -> id)
            max_length: Maximum sequence length
            split: 'train', 'val', or 'test'
        """
        self.data_dir = Path(data_dir)
        self.label_map = label_map
        self.vocab = vocab or {'<PAD>': 0, '<UNK>': 1, '<SOS>': 2, '<EOS>': 3}
        self.max_length = max_length
        self.split = split
        
        self.samples = self._load_samples()
        
        # Build vocabulary if not provided
        if len(self.vocab) <= 4:  # Only special tokens
            self._build_vocab()
    
    def _load_samples(self) -> List[Tuple[str, int]]:
        """Load all text samples and their labels"""
        samples = []
        
        print(f"Loading {self.split} samples from: {self.data_dir}")
        
        # Try loading from CSV/JSON files
        csv_file = self.data_dir / f"{self.split}.csv"
        json_file = self.data_dir / f"{self.split}.json"
        txt_file = self.data_dir / f"{self.split}.txt"
        
        if csv_file.exists():
            samples = self._load_from_csv(csv_file)
        elif json_file.exists():
            samples = self._load_from_json(json_file)
        elif txt_file.exists():
            samples = self._load_from_txt(txt_file)
        else:
            # Try loading from directory structure
            samples = self._load_from_dirs()
        
        print(f"Loaded {len(samples)} {self.split} samples")
        return samples
    
    def _load_from_csv(self, file_path: Path) -> List[Tuple[str, int]]:
        """Load from CSV file (text, label columns)"""
        df = pd.read_csv(file_path)
        
        # Detect columns
        text_col = 'text' if 'text' in df.columns else df.columns[0]
        label_col = 'label' if 'label' in df.columns else df.columns[1]
        
        samples = []
        for _, row in df.iterrows():
            text = str(row[text_col])
            label_name = str(row[label_col])
            
            # Map label to ID
            if label_name in self.label_map:
                label_id = self.label_map[label_name]
            else:
                # Try to parse as integer
                try:
                    label_id = int(label_name)
                except:
                    continue
            
            samples.append((text, label_id))
        
        return samples
    
    def _load_from_json(self, file_path: Path) -> List[Tuple[str, int]]:
        """Load from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        samples = []
        for item in data:
            text = item.get('text', '')
            label_name = item.get('label', '')
            
            if label_name in self.label_map:
                label_id = self.label_map[label_name]
                samples.append((text, label_id))
        
        return samples
    
    def _load_from_txt(self, file_path: Path) -> List[Tuple[str, int]]:
        """Load from TXT file (tab-separated: text\tlabel)"""
        samples = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    text = parts[0]
                    label_name = parts[1]
                    
                    if label_name in self.label_map:
                        label_id = self.label_map[label_name]
                        samples.append((text, label_id))
        
        return samples
    
    def _load_from_dirs(self) -> List[Tuple[str, int]]:
        """Load from directory structure (one dir per class)"""
        samples = []
        
        for label_name, label_id in self.label_map.items():
            label_dir = self.data_dir / label_name
            
            if label_dir.exists() and label_dir.is_dir():
                for txt_file in label_dir.glob('*.txt'):
                    try:
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            text = f.read().strip()
                        
                        if text:
                            samples.append((text, label_id))
                    except Exception as e:
                        print(f"Error reading {txt_file}: {e}")
        
        return samples
    
    def _build_vocab(self, min_freq: int = 2, max_vocab_size: int = 50000):
        """Build vocabulary from training samples"""
        print("Building vocabulary...")
        
        word_freq = Counter()
        
        for text, _ in self.samples:
            tokens = self._tokenize(text)
            word_freq.update(tokens)
        
        # Add most common words to vocab
        vocab_size = len(self.vocab)
        for word, freq in word_freq.most_common(max_vocab_size):
            if freq >= min_freq:
                self.vocab[word] = vocab_size
                vocab_size += 1
        
        print(f"Vocabulary size: {len(self.vocab)}")
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Convert to lowercase and split
        text = text.lower()
        # Remove special characters except spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Split and filter
        tokens = text.split()
        return tokens
    
    def _text_to_indices(self, text: str) -> List[int]:
        """Convert text to token indices"""
        tokens = self._tokenize(text)
        indices = [self.vocab.get(token, self.vocab['<UNK>']) for token in tokens]
        return indices
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """Get a sample"""
        text, label = self.samples[idx]
        
        # Convert text to indices
        indices = self._text_to_indices(text)
        
        # Truncate or pad
        if len(indices) > self.max_length:
            indices = indices[:self.max_length]
        else:
            indices = indices + [self.vocab['<PAD>']] * (self.max_length - len(indices))
        
        return torch.tensor(indices, dtype=torch.long), label


class TextDataLoader:
    """
    DataLoader factory for text datasets
    Handles train/val/test splitting
    """
    
    def __init__(self, project_dir: str, config: dict):
        """
        Args:
            project_dir: Project directory containing data/ subdirectory
            config: Training configuration
        """
        self.project_dir = Path(project_dir)
        self.data_dir = self.project_dir / "data"
        self.config = config
        
        # Load label mapping
        self.label_map = self._load_label_map()
        self.num_classes = len(self.label_map)
        
        # Shared vocabulary
        self.vocab = None
    
    def _load_label_map(self) -> Dict[str, int]:
        """Load or create label mapping"""
        label_file = self.project_dir / "labels.json"
        
        if label_file.exists():
            with open(label_file, 'r', encoding='utf-8') as f:
                label_map = json.load(f)
            print(f"Loaded {len(label_map)} classes: {list(label_map.keys())}")
            return label_map
        
        # Auto-detect labels
        label_map = {}
        
        # Try from CSV
        csv_file = self.data_dir / "train.csv"
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            label_col = 'label' if 'label' in df.columns else df.columns[1]
            unique_labels = df[label_col].unique()
            label_map = {str(label): idx for idx, label in enumerate(sorted(unique_labels))}
        
        # Try from directories
        elif self.data_dir.exists():
            for idx, label_dir in enumerate(sorted(self.data_dir.iterdir())):
                if label_dir.is_dir():
                    label_map[label_dir.name] = idx
        
        # Save label map
        if label_map:
            with open(label_file, 'w', encoding='utf-8') as f:
                json.dump(label_map, f, ensure_ascii=False, indent=2)
            print(f"Created label map with {len(label_map)} classes")
        
        return label_map
    
    def create_loaders(self) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Create train, validation, and test data loaders
        
        Returns:
            (train_loader, val_loader, test_loader)
        """
        batch_size = self.config.get('batch_size', 32)
        # Set num_workers=0 on Windows to avoid DataLoader worker crashes
        num_workers = self.config.get('num_workers', 0)
        max_length = self.config.get('max_length', 512)
        
        # Create train dataset (builds vocabulary)
        train_dataset = TextDataset(
            str(self.data_dir),
            self.label_map,
            max_length=max_length,
            split='train'
        )
        
        # Share vocabulary with val and test
        self.vocab = train_dataset.vocab
        
        val_dataset = TextDataset(
            str(self.data_dir),
            self.label_map,
            vocab=self.vocab,
            max_length=max_length,
            split='val'
        )
        
        test_dataset = TextDataset(
            str(self.data_dir),
            self.label_map,
            vocab=self.vocab,
            max_length=max_length,
            split='test'
        )
        
        # If no validation data, split from train
        if len(val_dataset) == 0:
            train_size = int(len(train_dataset) * self.config.get('train_split', 0.8))
            val_size = len(train_dataset) - train_size
            
            from torch.utils.data import random_split
            train_dataset, val_dataset = random_split(
                train_dataset,
                [train_size, val_size],
                generator=torch.Generator().manual_seed(42)
            )
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers
        )
        
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers
        )
        
        print(f"\nCreated text data loaders:")
        print(f"  Train: {len(train_dataset)} samples")
        print(f"  Val:   {len(val_dataset)} samples")
        print(f"  Test:  {len(test_dataset)} samples")
        print(f"  Vocab size: {len(self.vocab)}")
        
        return train_loader, val_loader, test_loader


def create_text_loaders(project_dir: str, config: dict) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Convenience function to create text data loaders
    
    Args:
        project_dir: Project directory
        config: Training configuration
        
    Returns:
        (train_loader, val_loader, test_loader)
    """
    loader = TextDataLoader(project_dir, config)
    return loader.create_loaders()


# Test code
if __name__ == "__main__":
    # Example usage
    test_config = {
        'batch_size': 16,
        'num_workers': 0,
        'max_length': 256,
        'train_split': 0.8
    }
    
    # Test with sample project
    print("Testing TextDataLoader...")
    print("Create sample data in: projects/test-text-project/data/")
    print("Format options:")
    print("  1. train.csv with 'text' and 'label' columns")
    print("  2. class folders with .txt files")
    print("  3. train.txt with tab-separated text\\tlabel")

