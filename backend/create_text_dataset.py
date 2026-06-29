"""
Create sample text classification dataset for testing
Creates IMDB-style sentiment classification (positive/negative)
"""

import pandas as pd
from pathlib import Path
import json

def create_sample_text_dataset(output_dir='../projects/text-sentiment-test'):
    """
    Create a small sample text dataset for testing
    
    Format: CSV with 'text' and 'label' columns
    """
    output_dir = Path(output_dir)
    data_dir = output_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("Creating Sample Text Dataset")
    print("=" * 70)
    
    # Sample data - Sentiment analysis
    train_data = [
        # Positive reviews
        ("This movie is absolutely fantastic! I loved every minute of it.", "positive"),
        ("Great performance by the actors. Highly recommended!", "positive"),
        ("One of the best films I've seen this year. Amazing!", "positive"),
        ("Wonderful storyline and beautiful cinematography.", "positive"),
        ("I enjoyed this movie very much. Worth watching!", "positive"),
        ("Excellent direction and amazing visual effects.", "positive"),
        ("A masterpiece! This film exceeded all my expectations.", "positive"),
        ("Brilliant acting and engaging plot. Loved it!", "positive"),
        ("This is a must-watch movie. Absolutely brilliant!", "positive"),
        ("Outstanding performance. One of my favorites now.", "positive"),
        ("Fantastic movie with great music and visuals.", "positive"),
        ("Simply amazing! The best movie experience ever.", "positive"),
        ("I highly recommend this film. Truly exceptional.", "positive"),
        ("Wonderful movie that touched my heart deeply.", "positive"),
        ("Incredible storyline and superb acting throughout.", "positive"),
        ("This movie is a gem. Don't miss it!", "positive"),
        ("Absolutely loved the screenplay and direction.", "positive"),
        ("Best movie I've watched in years. Perfect!", "positive"),
        ("Amazing cinematography and powerful message.", "positive"),
        ("Truly exceptional film with great performances.", "positive"),
        
        # Negative reviews
        ("This movie was terrible. Complete waste of time.", "negative"),
        ("Very disappointing. Poor acting and weak plot.", "negative"),
        ("I didn't enjoy this film at all. Boring!", "negative"),
        ("Awful movie with a confusing storyline.", "negative"),
        ("Not worth watching. Very disappointing experience.", "negative"),
        ("Terrible acting and poor direction throughout.", "negative"),
        ("This was the worst movie I've seen in years.", "negative"),
        ("Boring plot and unconvincing performances.", "negative"),
        ("I regret watching this. Complete disaster!", "negative"),
        ("Poor quality film with no redeeming features.", "negative"),
        ("Disappointing movie that failed to deliver.", "negative"),
        ("Waste of money. The plot made no sense.", "negative"),
        ("Terrible screenplay and mediocre acting.", "negative"),
        ("Not recommended. Very boring and predictable.", "negative"),
        ("Poor execution of a potentially good idea.", "negative"),
        ("This film was a huge disappointment overall.", "negative"),
        ("Bad acting and a confusing, messy plot.", "negative"),
        ("I couldn't finish watching. Too boring!", "negative"),
        ("Worst movie experience. Complete waste of time.", "negative"),
        ("Disappointing on all fronts. Not worth it.", "negative"),
    ]
    
    # Validation data
    val_data = [
        ("Good movie but could have been better.", "positive"),
        ("Enjoyed most of it. Pretty entertaining overall.", "positive"),
        ("Nice film with some great moments.", "positive"),
        ("Pretty good but not amazing. Worth a watch.", "positive"),
        ("Decent movie with good acting performances.", "positive"),
        ("Not great but not terrible either. Average film.", "negative"),
        ("Mediocre at best. Expected more from this.", "negative"),
        ("Somewhat disappointing but had good parts.", "negative"),
        ("Below average movie. Not recommended.", "negative"),
        ("Could have been better. Disappointed overall.", "negative"),
    ]
    
    # Test data
    test_data = [
        ("Absolutely wonderful! A true cinematic experience.", "positive"),
        ("Great movie that I'll watch again for sure.", "positive"),
        ("Excellent work by everyone involved. Loved it!", "positive"),
        ("This movie exceeded my high expectations.", "positive"),
        ("Perfect blend of action and emotion. Fantastic!", "positive"),
        ("Terrible film that wasted a great concept.", "negative"),
        ("Very poor execution. Not worth the time.", "negative"),
        ("Disappointing and forgettable. Skip this one.", "negative"),
        ("Bad movie with no redeeming qualities.", "negative"),
        ("Regret watching this. Total waste of time.", "negative"),
    ]
    
    # Create DataFrames
    train_df = pd.DataFrame(train_data, columns=['text', 'label'])
    val_df = pd.DataFrame(val_data, columns=['text', 'label'])
    test_df = pd.DataFrame(test_data, columns=['text', 'label'])
    
    # Save to CSV
    train_df.to_csv(data_dir / 'train.csv', index=False)
    val_df.to_csv(data_dir / 'val.csv', index=False)
    test_df.to_csv(data_dir / 'test.csv', index=False)
    
    # Create labels.json
    labels = {"positive": 0, "negative": 1}
    with open(output_dir / 'labels.json', 'w') as f:
        json.dump(labels, f, indent=2)
    
    # Create project.json
    project_info = {
        "id": "text-sentiment-test",
        "name": "Text Sentiment Classification",
        "modality": "text",
        "description": "Binary sentiment classification (positive/negative)",
        "created_at": "2025-11-30",
        "num_classes": 2,
        "total_samples": len(train_data) + len(val_data) + len(test_data)
    }
    
    with open(output_dir / 'project.json', 'w') as f:
        json.dump(project_info, f, indent=2)
    
    # Print summary
    print("\n✅ Sample Text Dataset Created!")
    print("=" * 70)
    print(f"\nLocation: {output_dir.absolute()}")
    print(f"\nDataset Statistics:")
    print(f"  Train samples: {len(train_data)}")
    print(f"  Val samples:   {len(val_data)}")
    print(f"  Test samples:  {len(test_data)}")
    print(f"  Total:         {len(train_data) + len(val_data) + len(test_data)}")
    print(f"\nClasses:")
    print(f"  positive: {sum(1 for _, label in train_data if label == 'positive')} train samples")
    print(f"  negative: {sum(1 for _, label in train_data if label == 'negative')} train samples")
    
    print("\n" + "=" * 70)
    print("Test Script:")
    print("=" * 70)
    print("""
# Test the text data loader
cd D:\\Project\\ModelCreator\\backend
.\\venv\\Scripts\\activate

python -c "
from engine import create_text_loaders

config = {
    'batch_size': 4,
    'num_workers': 0,
    'max_length': 128,
    'train_split': 0.8
}

train_loader, val_loader, test_loader = create_text_loaders(
    '../projects/text-sentiment-test',
    config
)

# Test loading a batch
for texts, labels in train_loader:
    print(f'Batch shape: {texts.shape}')
    print(f'Labels: {labels}')
    break
"
    """)
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. Test the TextDataLoader with this dataset")
    print("2. Train an LSTM model")
    print("3. Evaluate on test set")
    print("4. Compare with BERT model")
    print("=" * 70)


if __name__ == "__main__":
    create_sample_text_dataset()

