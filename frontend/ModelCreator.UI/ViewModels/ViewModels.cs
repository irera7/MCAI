using CommunityToolkit.Mvvm.ComponentModel;

namespace ModelCreator.UI.ViewModels
{
    /// <summary>
    /// View model for data import
    /// </summary>
    public partial class DataImportViewModel : ObservableObject
    {
        [ObservableProperty]
        private string _projectId = string.Empty;

        public DataImportViewModel()
        {
        }
    }

    /// <summary>
    /// View model for model selection
    /// </summary>
    public partial class ModelSelectionViewModel : ObservableObject
    {
        [ObservableProperty]
        private string _selectedModel = string.Empty;

        public ModelSelectionViewModel()
        {
        }
    }

    /// <summary>
    /// View model for training configuration
    /// </summary>
    public partial class TrainingConfigViewModel : ObservableObject
    {
        [ObservableProperty]
        private int _epochs = 50;

        [ObservableProperty]
        private int _batchSize = 32;

        [ObservableProperty]
        private double _learningRate = 0.001;

        public TrainingConfigViewModel()
        {
        }
    }

    /// <summary>
    /// View model for training dashboard
    /// </summary>
    public partial class TrainingDashboardViewModel : ObservableObject
    {
        [ObservableProperty]
        private int _currentEpoch;

        [ObservableProperty]
        private double _currentLoss;

        [ObservableProperty]
        private double _currentAccuracy;

        public TrainingDashboardViewModel()
        {
        }
    }

    /// <summary>
    /// View model for inference playground
    /// </summary>
    public partial class InferenceViewModel : ObservableObject
    {
        [ObservableProperty]
        private string _predictionResult = string.Empty;

        public InferenceViewModel()
        {
        }
    }
}

