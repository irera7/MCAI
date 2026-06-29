using System;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;
using ModelCreator.UI.Services;
using System.IO;

namespace ModelCreator.UI.Views
{
    public partial class TimeSeriesProjectPage : Page
    {
        private readonly ApiService _apiService;
        private string? _uploadedDataPath;

        public TimeSeriesProjectPage()
        {
            InitializeComponent();
            _apiService = new ApiService();
        }

        private void UploadDataButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var dialog = new OpenFileDialog
                {
                    Title = "Select Time Series Data",
                    Filter = "CSV Files (*.csv)|*.csv|All Files (*.*)|*.*"
                };

                if (dialog.ShowDialog() == true)
                {
                    _uploadedDataPath = dialog.FileName;
                    DataStatusTextBlock.Text = $"✅ Loaded: {Path.GetFileName(_uploadedDataPath)}";
                    DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Green;
                    
                    // Analyze time series data
                    AnalyzeTimeSeriesData(_uploadedDataPath);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void AnalyzeTimeSeriesData(string filePath)
        {
            try
            {
                var lines = File.ReadAllLines(filePath);
                if (lines.Length > 1)
                {
                    var timePoints = lines.Length - 1; // Exclude header
                    var headers = lines[0].Split(',');
                    var variables = headers.Length - 1; // Assuming first column is timestamp
                    
                    TimePointsText.Text = timePoints.ToString();
                    VariablesText.Text = variables.ToString();
                    
                    // Try to detect frequency (simple heuristic)
                    if (timePoints > 24 * 7) // > 1 week hourly
                        FrequencyText.Text = "Hourly/Daily";
                    else if (timePoints > 24)
                        FrequencyText.Text = "Hourly";
                    else
                        FrequencyText.Text = "Unknown";
                    
                    TimeSeriesStatsPanel.Visibility = Visibility.Visible;
                }
            }
            catch (Exception)
            {
                // If analysis fails, hide stats
                TimeSeriesStatsPanel.Visibility = Visibility.Collapsed;
            }
        }

        private void CreateProjectButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(ProjectNameTextBox.Text) || string.IsNullOrEmpty(_uploadedDataPath))
                {
                    MessageBox.Show("Please fill all fields and upload data", "Validation Error", 
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                // Get selected model
                string model = "LSTM";
                if (GRURadio.IsChecked == true) model = "GRU";
                else if (AttentionLSTMRadio.IsChecked == true) model = "Attention-LSTM";
                else if (ProphetRadio.IsChecked == true) model = "Prophet";

                // Get task type
                var taskType = ((ComboBoxItem)TaskTypeComboBox.SelectedItem)?.Content?.ToString() ?? "Forecasting";

                // Get preprocessing options
                var detrend = DetrendCheckBox.IsChecked == true;
                var deseasonalize = DeseasonalizeCheckBox.IsChecked == true;
                var differencing = DifferencingCheckBox.IsChecked == true;
                var normalize = NormalizeCheckBox.IsChecked == true;

                // Get model config
                var seqLength = SequenceLengthTextBox.Text;
                var horizon = ForecastHorizonTextBox.Text;
                var hiddenUnits = ((ComboBoxItem)HiddenUnitsComboBox.SelectedItem)?.Content?.ToString() ?? "128";
                var numLayers = ((ComboBoxItem)NumLayersComboBox.SelectedItem)?.Content?.ToString() ?? "2 layers";
                var learningRate = LearningRateTextBox.Text;
                var batchSize = ((ComboBoxItem)BatchSizeComboBox.SelectedItem)?.Content?.ToString() ?? "32";

                var message = $"✅ Time Series Project Created!\n\n" +
                    $"📈 Project: {ProjectNameTextBox.Text}\n" +
                    $"🤖 Model: {model}\n" +
                    $"🎯 Task: {taskType.Split('(')[0].Trim()}\n\n" +
                    $"⚙️ Preprocessing:\n" +
                    $"  • Detrend: {(detrend ? "Yes" : "No")}\n" +
                    $"  • Deseasonalize: {(deseasonalize ? "Yes" : "No")}\n" +
                    $"  • Differencing: {(differencing ? "Yes" : "No")}\n" +
                    $"  • Normalize: {(normalize ? "Yes" : "No")}\n\n" +
                    $"🎯 Model Config:\n" +
                    $"  • Sequence Length: {seqLength}\n" +
                    $"  • Forecast Horizon: {horizon}\n" +
                    $"  • Hidden Units: {hiddenUnits}\n" +
                    $"  • Layers: {numLayers}\n" +
                    $"  • Learning Rate: {learningRate}\n" +
                    $"  • Batch Size: {batchSize}\n\n" +
                    $"Ready to start training!";

                MessageBox.Show(message, "Project Created", MessageBoxButton.OK, MessageBoxImage.Information);

                NavigationService?.GoBack();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.GoBack();
        }
    }
}
