using System;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;
using ModelCreator.UI.Services;
using System.IO;
using System.Linq;

namespace ModelCreator.UI.Views
{
    public partial class TabularProjectPage : Page
    {
        private readonly ApiService _apiService;
        private string? _uploadedDataPath;
        private int _rowCount = 0;
        private int _featureCount = 0;
        private int _numericCount = 0;
        private int _categoricalCount = 0;

        public TabularProjectPage()
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
                    Title = "Select Tabular Data File",
                    Filter = "Data Files (*.csv;*.xlsx;*.xls)|*.csv;*.xlsx;*.xls|All Files (*.*)|*.*"
                };

                if (dialog.ShowDialog() == true)
                {
                    _uploadedDataPath = dialog.FileName;
                    DataStatusTextBlock.Text = $"✅ Loaded: {Path.GetFileName(_uploadedDataPath)}";
                    DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Green;
                    
                    // Analyze data (simple CSV parsing for preview)
                    AnalyzeData(_uploadedDataPath);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void AnalyzeData(string filePath)
        {
            try
            {
                if (filePath.EndsWith(".csv", StringComparison.OrdinalIgnoreCase))
                {
                    var lines = File.ReadAllLines(filePath);
                    if (lines.Length > 0)
                    {
                        _rowCount = lines.Length - 1; // Exclude header
                        var headers = lines[0].Split(',');
                        _featureCount = headers.Length - 1; // Exclude target
                        
                        // Simple heuristic: assume numeric if all values are numbers
                        _numericCount = 0;
                        _categoricalCount = 0;
                        
                        if (lines.Length > 1)
                        {
                            var firstDataLine = lines[1].Split(',');
                            for (int i = 0; i < firstDataLine.Length - 1; i++)
                            {
                                if (double.TryParse(firstDataLine[i], out _))
                                    _numericCount++;
                                else
                                    _categoricalCount++;
                            }
                        }
                        
                        // Update UI
                        RowCountText.Text = _rowCount.ToString();
                        FeatureCountText.Text = _featureCount.ToString();
                        NumericCountText.Text = _numericCount.ToString();
                        CategoricalCountText.Text = _categoricalCount.ToString();
                        DataStatsPanel.Visibility = Visibility.Visible;
                    }
                }
                else
                {
                    // For Excel files, show placeholder
                    DataStatsPanel.Visibility = Visibility.Visible;
                    RowCountText.Text = "?";
                    FeatureCountText.Text = "?";
                    NumericCountText.Text = "?";
                    CategoricalCountText.Text = "?";
                }
            }
            catch (Exception ex)
            {
                // If analysis fails, just hide stats panel
                DataStatsPanel.Visibility = Visibility.Collapsed;
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

                string model = XGBoostRadio.IsChecked == true ? "XGBoost" : "LightGBM";
                string taskType = ((ComboBoxItem)TaskTypeComboBox.SelectedItem)?.Content?.ToString() ?? "Classification";
                
                // Get preprocessing options
                var scalingMethod = ((ComboBoxItem)ScalingComboBox.SelectedItem)?.Content?.ToString() ?? "Standard Scaling";
                var missingValue = ((ComboBoxItem)MissingValueComboBox.SelectedItem)?.Content?.ToString() ?? "Mean Imputation";
                var encoding = ((ComboBoxItem)EncodingComboBox.SelectedItem)?.Content?.ToString() ?? "One-Hot Encoding";
                var featureSelection = FeatureSelectionCheckBox.IsChecked == true;
                var topFeatures = featureSelection ? TopFeaturesTextBox.Text : "all";
                
                // Get training config
                var nEstimators = NEstimatorsTextBox.Text;
                var maxDepth = MaxDepthTextBox.Text;
                var learningRate = LearningRateTextBox.Text;
                var subsample = SubsampleTextBox.Text;
                var trainSplit = TrainValSplitSlider.Value / 100.0;
                var earlyStopping = EarlyStoppingCheckBox.IsChecked == true;

                var message = $"✅ Tabular Project Created!\n\n" +
                    $"📊 Project: {ProjectNameTextBox.Text}\n" +
                    $"🤖 Model: {model}\n" +
                    $"🎯 Task: {taskType}\n\n" +
                    $"⚙️ Preprocessing:\n" +
                    $"  • Scaling: {scalingMethod.Split('(')[0].Trim()}\n" +
                    $"  • Missing Values: {missingValue}\n" +
                    $"  • Encoding: {encoding.Split(' ')[0]}\n" +
                    $"  • Feature Selection: {(featureSelection ? $"Top {topFeatures}" : "All features")}\n\n" +
                    $"🎯 Training Config:\n" +
                    $"  • Trees: {nEstimators}\n" +
                    $"  • Max Depth: {maxDepth}\n" +
                    $"  • Learning Rate: {learningRate}\n" +
                    $"  • Train/Val Split: {trainSplit:P0} / {(1 - trainSplit):P0}\n" +
                    $"  • Early Stopping: {(earlyStopping ? "Yes" : "No")}\n\n" +
                    $"Ready to start training!";

                MessageBox.Show(message, "Project Created", MessageBoxButton.OK, MessageBoxImage.Information);

                // Navigate to training dashboard (or go back)
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
