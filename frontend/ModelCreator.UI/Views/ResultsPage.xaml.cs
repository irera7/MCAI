using ModelCreator.UI.Services;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Results Page - View training results and export model
    /// </summary>
    public partial class ResultsPage : Page
    {
        public class ClassMetric
        {
            public string ClassName { get; set; } = string.Empty;
            public double Precision { get; set; }
            public double Recall { get; set; }
            public double F1Score { get; set; }
            public int SampleCount { get; set; }
        }

        private string projectId;
        private readonly IApiService? _apiService;
        private Dictionary<string, object>? trainingResults;
        private string projectName = "";

        public ResultsPage(string projectId, Dictionary<string, object>? results = null)
        {
            InitializeComponent();
            this.projectId = projectId;
            this.projectName = "";
            this.trainingResults = results;
            
            _apiService = App.GetService<IApiService>();
            
            LoadResults();
        }
        
        public ResultsPage(string projectId, string projectName, Dictionary<string, object>? results = null)
        {
            InitializeComponent();
            this.projectId = projectId;
            this.projectName = projectName;
            this.trainingResults = results;
            
            _apiService = App.GetService<IApiService>();
            
            LoadResults();
        }

        private async void LoadResults()
        {
            try
            {
                // If results not provided, fetch from API
                if (trainingResults == null && _apiService != null)
                {
                    trainingResults = await _apiService.GetTrainingResultsAsync(projectId);
                }
                
                if (trainingResults != null)
                {
                    DisplayResults();
                }
                else
                {
                    // Use mock data for demonstration
                    DisplayMockResults();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading results: {ex.Message}", "Error",
                    MessageBoxButton.OK, MessageBoxImage.Error);
                DisplayMockResults();
            }
        }

        private void DisplayResults()
        {
            // Display final metrics
            if (trainingResults != null && trainingResults.ContainsKey("final_accuracy"))
            {
                var accuracyObj = trainingResults["final_accuracy"];
                double accuracy = 0;
                
                if (accuracyObj is System.Text.Json.JsonElement accuracyElem)
                {
                    accuracy = accuracyElem.GetDouble();
                }
                else
                {
                    accuracy = Convert.ToDouble(accuracyObj);
                }
                
                if (FinalAccuracyText != null)
                {
                    FinalAccuracyText.Text = $"{accuracy:P2}";
                }
            }
            
            if (trainingResults != null && trainingResults.ContainsKey("final_loss"))
            {
                var lossObj = trainingResults["final_loss"];
                double loss = 0;
                
                if (lossObj is System.Text.Json.JsonElement lossElem)
                {
                    loss = lossElem.GetDouble();
                }
                else
                {
                    loss = Convert.ToDouble(lossObj);
                }
                
                if (FinalLossText != null)
                {
                    FinalLossText.Text = $"{loss:F4}";
                }
            }
            
            if (trainingResults != null && trainingResults.ContainsKey("training_time"))
            {
                var timeObj = trainingResults["training_time"];
                double timeSeconds = 0;
                
                if (timeObj is System.Text.Json.JsonElement timeElem)
                {
                    timeSeconds = timeElem.GetDouble();
                }
                else
                {
                    timeSeconds = Convert.ToDouble(timeObj);
                }
                
                if (TrainingTimeText != null)
                {
                    TrainingTimeText.Text = FormatTime(timeSeconds);
                }
            }
            
            if (trainingResults != null && trainingResults.ContainsKey("epochs_trained"))
            {
                var epochsObj = trainingResults["epochs_trained"];
                int epochs = 0;
                
                if (epochsObj is System.Text.Json.JsonElement epochsElem)
                {
                    epochs = epochsElem.GetInt32();
                }
                else
                {
                    epochs = Convert.ToInt32(epochsObj);
                }
                
                if (EpochsTrainedText != null)
                {
                    EpochsTrainedText.Text = epochs.ToString();
                }
            }
            
            // Display per-class metrics
            if (trainingResults != null && trainingResults.ContainsKey("class_metrics"))
            {
                try
                {
                    var classMetrics = new ObservableCollection<ClassMetric>();
                    
                    // Try to handle different JSON formats
                    var metricsObj = trainingResults["class_metrics"];
                    
                    if (metricsObj is System.Text.Json.JsonElement jsonElement && jsonElement.ValueKind == System.Text.Json.JsonValueKind.Array)
                    {
                        // Handle JsonElement array
                        foreach (var item in jsonElement.EnumerateArray())
                        {
                            try
                            {
                                classMetrics.Add(new ClassMetric
                                {
                                    ClassName = item.GetProperty("class_name").GetString() ?? "Unknown",
                                    Precision = item.GetProperty("precision").GetDouble(),
                                    Recall = item.GetProperty("recall").GetDouble(),
                                    F1Score = item.GetProperty("f1_score").GetDouble(),
                                    SampleCount = item.GetProperty("sample_count").GetInt32()
                                });
                            }
                            catch (Exception ex)
                            {
                                System.Diagnostics.Debug.WriteLine($"Error parsing class metric: {ex.Message}");
                            }
                        }
                    }
                    else if (metricsObj is List<Dictionary<string, object>> metricsList)
                    {
                        // Handle List<Dictionary<string, object>>
                        foreach (var metric in metricsList)
                        {
                            var className = metric.ContainsKey("class_name") ? metric["class_name"]?.ToString() : null;
                            if (!string.IsNullOrEmpty(className))
                            {
                                classMetrics.Add(new ClassMetric
                                {
                                    ClassName = className,
                                    Precision = Convert.ToDouble(metric["precision"]),
                                    Recall = Convert.ToDouble(metric["recall"]),
                                    F1Score = Convert.ToDouble(metric["f1_score"]),
                                    SampleCount = Convert.ToInt32(metric["sample_count"])
                                });
                            }
                        }
                    }
                    
                    if (ClassMetricsGrid != null && classMetrics.Count > 0)
                    {
                        ClassMetricsGrid.ItemsSource = classMetrics;
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error loading class metrics: {ex.Message}");
                    // Fall back to displaying just overall metrics
                }
            }
        }

        private void DisplayMockResults()
        {
            // Mock data for demonstration
            FinalAccuracyText.Text = "95.67%";
            FinalLossText.Text = "0.1234";
            TrainingTimeText.Text = "18m 42s";
            EpochsTrainedText.Text = "50";
            
            var mockMetrics = new ObservableCollection<ClassMetric>
            {
                new ClassMetric { ClassName = "Class_A", Precision = 0.96, Recall = 0.94, F1Score = 0.95, SampleCount = 120 },
                new ClassMetric { ClassName = "Class_B", Precision = 0.93, Recall = 0.97, F1Score = 0.95, SampleCount = 115 },
                new ClassMetric { ClassName = "Class_C", Precision = 0.98, Recall = 0.95, F1Score = 0.96, SampleCount = 110 }
            };
            
            ClassMetricsGrid.ItemsSource = mockMetrics;
        }

        private string FormatTime(double seconds)
        {
            TimeSpan time = TimeSpan.FromSeconds(seconds);
            if (time.TotalHours >= 1)
            {
                return $"{(int)time.TotalHours}h {time.Minutes}m";
            }
            else if (time.TotalMinutes >= 1)
            {
                return $"{(int)time.TotalMinutes}m {time.Seconds}s";
            }
            else
            {
                return $"{(int)time.TotalSeconds}s";
            }
        }

        private void BrowseExportPath_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new Microsoft.Win32.SaveFileDialog
            {
                Title = "Select export folder",
                FileName = "ModelExport",
                DefaultExt = ".folder",
                Filter = "Folder|*.folder"
            };
            
            if (dialog.ShowDialog() == true)
            {
                ExportPathTextBox.Text = System.IO.Path.GetDirectoryName(dialog.FileName) ?? Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
            }
        }

        private async void Export_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(ExportPathTextBox.Text) || 
                ExportPathTextBox.Text == "Select export folder...")
            {
                MessageBox.Show("Please select an export location.", "Export Location Required",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            
            // Check if at least one format is selected
            if (!ExportPyTorchCheckBox.IsChecked.GetValueOrDefault() &&
                !ExportONNXCheckBox.IsChecked.GetValueOrDefault() &&
                !ExportTFLiteCheckBox.IsChecked.GetValueOrDefault())
            {
                MessageBox.Show("Please select at least one export format.", "No Format Selected",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            
            try
            {
                ExportButton.IsEnabled = false;
                ExportButton.Content = "⏳ Exporting...";
                
                var formats = new List<string>();
                if (ExportPyTorchCheckBox.IsChecked.GetValueOrDefault()) formats.Add("pytorch");
                if (ExportONNXCheckBox.IsChecked.GetValueOrDefault()) formats.Add("onnx");
                if (ExportTFLiteCheckBox.IsChecked.GetValueOrDefault()) formats.Add("tflite");
                
                if (_apiService != null)
                {
                    var exportRequest = new Dictionary<string, object>
                    {
                        ["project_id"] = projectId,
                        ["formats"] = formats,
                        ["export_path"] = ExportPathTextBox.Text,
                        ["include_metadata"] = IncludeMetadataCheckBox.IsChecked.GetValueOrDefault()
                    };
                    
                    var result = await _apiService.ExportModelAsync(exportRequest);
                    
                    MessageBox.Show(
                        $"Model exported successfully!\n\nLocation: {ExportPathTextBox.Text}",
                        "Export Complete",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information);
                }
                else
                {
                    // Mock success for demo
                    await Task.Delay(2000); // Simulate export
                    MessageBox.Show(
                        $"Model exported successfully!\n\nFormats: {string.Join(", ", formats)}\nLocation: {ExportPathTextBox.Text}",
                        "Export Complete",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error exporting model: {ex.Message}", "Export Error",
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                ExportButton.IsEnabled = true;
                ExportButton.Content = "📦 Export Model";
            }
        }

        private void TestInPlayground_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.Navigate(new InferencePlaygroundPage(projectId));
        }

        private void ViewDashboard_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.Navigate(new TrainingDashboardPage(projectId));
        }

        private void BackToHome_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.Navigate(new HomePage());
        }
    }
}

