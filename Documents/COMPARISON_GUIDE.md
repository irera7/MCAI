# 📊 Model Comparison - Complete Guide

**Compare Multiple Training Runs**  
**Status:** ✅ Complete  
**Date:** 30 November 2025

## Quick Start

```python
from engine import ModelComparison

# Create comparison object
comparison = ModelComparison('projects/my-project')

# Save a training run
comparison.save_run(
    run_id='run1',
    project_id='my-project',
    model_name='resnet18',
    modality='image',
    hyperparameters={'lr': 0.001, 'batch_size': 32},
    history={'val_acc': [70, 75, 80, 85, 87]},
    duration=300.0
)

# Compare all runs
df = comparison.compare_runs()
print(df)

# Get best model
best = comparison.get_best_run('val_acc')
print(f"Best: {best.model_name}")

# Generate report
report = comparison.generate_report('report.txt')

# Plot comparison
comparison.plot_comparison('val_acc', save_path='plot.png')
```

## Features

✅ Save training runs automatically  
✅ Compare multiple models  
✅ Find best model by any metric  
✅ Generate detailed reports  
✅ Export to CSV  
✅ Plot comparisons  
✅ با کامنت فارسی کامل  

## Complete! 🎉

