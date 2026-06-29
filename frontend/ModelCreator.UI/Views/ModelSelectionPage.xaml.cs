using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Model Selection Page - Choose model architecture
    /// </summary>
    public partial class ModelSelectionPage : Page
    {
        public class ModelInfo : INotifyPropertyChanged
        {
            public string Id { get; set; } = string.Empty;
            public string Name { get; set; } = string.Empty;
            public string Description { get; set; } = string.Empty;
            public string Category { get; set; } = string.Empty;
            public string Icon { get; set; } = string.Empty;
            public bool IsRecommended { get; set; }
            public int Speed { get; set; }  // 1-5 rating
            public int Accuracy { get; set; }  // 1-5 rating
            public int Memory { get; set; }  // 1-5 rating (lower is better)
            public string TrainingTime { get; set; } = string.Empty;
            public string Parameters { get; set; } = string.Empty;
            
            private bool isSelected;
            public bool IsSelected 
            { 
                get => isSelected;
                set
                {
                    if (isSelected != value)
                    {
                        isSelected = value;
                        OnPropertyChanged(nameof(IsSelected));
                    }
                }
            }

            public event PropertyChangedEventHandler? PropertyChanged;
            protected void OnPropertyChanged(string propertyName)
            {
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
            }
        }

        private ObservableCollection<ModelInfo> models = new ObservableCollection<ModelInfo>();
        private string projectId;
        private string modality;
        private List<string> labels;
        private ModelInfo? selectedModel;

        public ModelSelectionPage(string projectId, string modality, List<string> labels)
        {
            InitializeComponent();
            this.projectId = projectId;
            this.modality = modality;
            this.labels = labels;
            
            LoadModels();
            ModelsGrid.ItemsSource = models;
        }

        private void LoadModels()
        {
            models.Clear();
            
            switch (modality)
            {
                case "image":
                    LoadImageModels();
                    break;
                case "text":
                    LoadTextModels();
                    break;
                case "audio":
                    LoadAudioModels();
                    break;
                case "video":
                    LoadVideoModels();
                    break;
                case "tabular":
                    LoadTabularModels();
                    break;
                case "timeseries":
                    LoadTimeSeriesModels();
                    break;
                case "medical":
                    LoadMedicalModels();
                    break;
                case "genomic":
                    LoadGenomicModels();
                    break;
            }
        }

        private void LoadImageModels()
        {
            models.Add(new ModelInfo
            {
                Id = "simple_cnn",
                Name = "Simple CNN",
                Category = "Convolutional Neural Network",
                Description = "Fast and lightweight CNN perfect for quick prototyping and simple image classification tasks.",
                Icon = "🏃",
                IsRecommended = false,
                Speed = 5,
                Accuracy = 3,
                Memory = 2,
                TrainingTime = "~5-10 min",
                Parameters = "~500K"
            });
            
            models.Add(new ModelInfo
            {
                Id = "mobilenet_v3",
                Name = "MobileNetV3",
                Category = "Efficient Architecture",
                Description = "Optimized for mobile deployment. Excellent balance of speed, accuracy, and model size.",
                Icon = "📱",
                IsRecommended = true,
                Speed = 4,
                Accuracy = 4,
                Memory = 2,
                TrainingTime = "~15-20 min",
                Parameters = "~5.4M"
            });
            
            models.Add(new ModelInfo
            {
                Id = "resnet50",
                Name = "ResNet-50",
                Category = "Deep Residual Network",
                Description = "Industry-standard architecture with excellent accuracy. Best for complex image classification.",
                Icon = "🎯",
                IsRecommended = false,
                Speed = 2,
                Accuracy = 5,
                Memory = 4,
                TrainingTime = "~30-45 min",
                Parameters = "~25M"
            });
            
            models.Add(new ModelInfo
            {
                Id = "vision_transformer",
                Name = "Vision Transformer",
                Category = "Transformer-based",
                Description = "State-of-the-art transformer architecture. Requires more data but achieves top accuracy.",
                Icon = "✨",
                IsRecommended = false,
                Speed = 1,
                Accuracy = 5,
                Memory = 5,
                TrainingTime = "~1-2 hours",
                Parameters = "~86M"
            });
        }

        private void LoadTextModels()
        {
            models.Add(new ModelInfo
            {
                Id = "tfidf_classifier",
                Name = "TF-IDF + Classifier",
                Category = "Classical ML",
                Description = "Fast traditional approach using TF-IDF features. Great for quick results with small datasets.",
                Icon = "📝",
                IsRecommended = false,
                Speed = 5,
                Accuracy = 3,
                Memory = 1,
                TrainingTime = "~1-2 min",
                Parameters = "~100K"
            });
            
            models.Add(new ModelInfo
            {
                Id = "lstm",
                Name = "LSTM Network",
                Category = "Recurrent Neural Network",
                Description = "Effective for sequence understanding. Good balance of performance and speed.",
                Icon = "🔄",
                IsRecommended = true,
                Speed = 3,
                Accuracy = 4,
                Memory = 3,
                TrainingTime = "~10-15 min",
                Parameters = "~2M"
            });
            
            models.Add(new ModelInfo
            {
                Id = "bert_small",
                Name = "BERT-Small",
                Category = "Transformer",
                Description = "Contextual language model. Best accuracy for text classification tasks.",
                Icon = "🤖",
                IsRecommended = false,
                Speed = 2,
                Accuracy = 5,
                Memory = 4,
                TrainingTime = "~20-30 min",
                Parameters = "~30M"
            });
        }

        private void LoadAudioModels()
        {
            models.Add(new ModelInfo
            {
                Id = "spectrogram_cnn",
                Name = "Spectrogram CNN",
                Category = "2D Convolutional",
                Description = "Converts audio to spectrograms and uses CNN. Excellent for most audio tasks.",
                Icon = "🎵",
                IsRecommended = true,
                Speed = 4,
                Accuracy = 4,
                Memory = 3,
                TrainingTime = "~15-20 min",
                Parameters = "~3M"
            });
            
            models.Add(new ModelInfo
            {
                Id = "audio_transformer",
                Name = "Audio Transformer",
                Category = "Transformer-based",
                Description = "Advanced architecture for complex audio patterns. Best for large datasets.",
                Icon = "🎼",
                IsRecommended = false,
                Speed = 2,
                Accuracy = 5,
                Memory = 4,
                TrainingTime = "~30-45 min",
                Parameters = "~12M"
            });
        }

        private void LoadVideoModels()
        {
            models.Add(new ModelInfo
            {
                Id = "3d_cnn",
                Name = "3D CNN",
                Category = "Spatiotemporal",
                Description = "Processes video frames spatially and temporally. Good for action recognition.",
                Icon = "🎬",
                IsRecommended = true,
                Speed = 2,
                Accuracy = 4,
                Memory = 5,
                TrainingTime = "~1-2 hours",
                Parameters = "~10M"
            });
        }

        private void LoadTabularModels()
        {
            models.Add(new ModelInfo
            {
                Id = "mlp",
                Name = "Multi-Layer Perceptron",
                Category = "Neural Network",
                Description = "Simple and fast neural network. Good starting point for tabular data.",
                Icon = "📊",
                IsRecommended = false,
                Speed = 5,
                Accuracy = 3,
                Memory = 1,
                TrainingTime = "~2-5 min",
                Parameters = "~50K"
            });
            
            models.Add(new ModelInfo
            {
                Id = "xgboost",
                Name = "XGBoost",
                Category = "Gradient Boosting",
                Description = "Industry-standard for tabular data. Excellent accuracy with minimal tuning.",
                Icon = "🚀",
                IsRecommended = true,
                Speed = 4,
                Accuracy = 5,
                Memory = 2,
                TrainingTime = "~5-10 min",
                Parameters = "Variable"
            });
            
            models.Add(new ModelInfo
            {
                Id = "random_forest",
                Name = "Random Forest",
                Category = "Ensemble Learning",
                Description = "Reliable and interpretable. Great for feature importance analysis.",
                Icon = "🌲",
                IsRecommended = false,
                Speed = 3,
                Accuracy = 4,
                Memory = 2,
                TrainingTime = "~3-8 min",
                Parameters = "Variable"
            });
        }

        private void LoadTimeSeriesModels()
        {
            models.Add(new ModelInfo
            {
                Id = "lstm_ts",
                Name = "LSTM",
                Category = "Recurrent Network",
                Description = "Specialized for sequential data. Captures temporal dependencies effectively.",
                Icon = "📈",
                IsRecommended = true,
                Speed = 3,
                Accuracy = 4,
                Memory = 3,
                TrainingTime = "~15-20 min",
                Parameters = "~1.5M"
            });
            
            models.Add(new ModelInfo
            {
                Id = "temporal_cnn",
                Name = "Temporal CNN",
                Category = "Convolutional",
                Description = "Fast and efficient for time series. Good for pattern recognition.",
                Icon = "⚡",
                IsRecommended = false,
                Speed = 4,
                Accuracy = 3,
                Memory = 2,
                TrainingTime = "~10-15 min",
                Parameters = "~800K"
            });
            
            models.Add(new ModelInfo
            {
                Id = "transformer_ts",
                Name = "Transformer",
                Category = "Attention-based",
                Description = "State-of-the-art for complex time series. Handles long sequences well.",
                Icon = "🔮",
                IsRecommended = false,
                Speed = 2,
                Accuracy = 5,
                Memory = 4,
                TrainingTime = "~30-40 min",
                Parameters = "~8M"
            });
        }

        private void LoadMedicalModels()
        {
            models.Add(new ModelInfo
            {
                Id = "medical_cnn",
                Name = "Medical CNN",
                Category = "2D Convolutional",
                Description = "Optimized for medical images (MRI, CT scans). Includes preprocessing steps.",
                Icon = "🏥",
                IsRecommended = true,
                Speed = 3,
                Accuracy = 4,
                Memory = 3,
                TrainingTime = "~20-30 min",
                Parameters = "~5M"
            });
            
            models.Add(new ModelInfo
            {
                Id = "signal_cnn",
                Name = "Signal 1D CNN",
                Category = "1D Convolutional",
                Description = "For ECG, EEG signals. Specialized for time-series medical data.",
                Icon = "💓",
                IsRecommended = false,
                Speed = 4,
                Accuracy = 4,
                Memory = 2,
                TrainingTime = "~15-20 min",
                Parameters = "~2M"
            });
        }

        private void LoadGenomicModels()
        {
            models.Add(new ModelInfo
            {
                Id = "dna_cnn",
                Name = "DNA CNN",
                Category = "1D Convolutional",
                Description = "Specialized for DNA sequence analysis. One-hot encoding built-in.",
                Icon = "🧬",
                IsRecommended = true,
                Speed = 3,
                Accuracy = 4,
                Memory = 3,
                TrainingTime = "~15-25 min",
                Parameters = "~3M"
            });
            
            models.Add(new ModelInfo
            {
                Id = "sequence_embedding",
                Name = "Sequence Embedding",
                Category = "Embedding + LSTM",
                Description = "Learns sequence representations. Good for variable-length sequences.",
                Icon = "🔬",
                IsRecommended = false,
                Speed = 2,
                Accuracy = 4,
                Memory = 4,
                TrainingTime = "~20-30 min",
                Parameters = "~5M"
            });
        }

        private void ModelCard_Click(object sender, MouseButtonEventArgs e)
        {
            if (sender is Border border && border.Tag is ModelInfo model)
            {
                // Deselect previous
                if (selectedModel != null)
                {
                    selectedModel.IsSelected = false;
                }
                
                // Select new
                selectedModel = model;
                selectedModel.IsSelected = true;
                NextButton.IsEnabled = true;
            }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.GoBack();
        }

        private void Next_Click(object sender, RoutedEventArgs e)
        {
            if (selectedModel == null)
            {
                MessageBox.Show("Please select a model architecture.", "No Model Selected",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            
            // Navigate to training configuration
            NavigationService?.Navigate(new TrainingConfigPage(projectId, modality, labels, selectedModel.Id));
        }
    }
}

