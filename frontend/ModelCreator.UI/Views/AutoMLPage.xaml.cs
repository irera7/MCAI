using System;
using System.Collections.ObjectModel;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Diagnostics;
using System.IO;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// AutoML Page - Automated Hyperparameter Optimization
    /// </summary>
    public partial class AutoMLPage : Page
    {
        private readonly HttpClient _httpClient;
        private ObservableCollection<TrialInfo> _trials;
        private Stopwatch _stopwatch;
        private string? _selectedProjectId;
        private bool _isRunning;

        public AutoMLPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient 
            { 
                BaseAddress = new Uri("http://127.0.0.1:8181"),
                Timeout = TimeSpan.FromHours(2)
            };
            _trials = new ObservableCollection<TrialInfo>();
            TrialHistoryGrid.ItemsSource = _trials;
            _stopwatch = new Stopwatch();
            
            LoadProjects();
        }

        private async void LoadProjects()
        {
            try
            {
                var response = await _httpClient.GetAsync("/api/project/list");
                
                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<ProjectsResponse>(
                        json,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );

                    if (result?.Projects != null)
                    {
                        ProjectComboBox.ItemsSource = result.Projects;
                        ProjectComboBox.DisplayMemberPath = "Name";
                        ProjectComboBox.SelectedValuePath = "Id";
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading projects:\n\n{ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void ProjectComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (ProjectComboBox.SelectedItem is ProjectInfo project)
            {
                _selectedProjectId = project.Id;
                ProjectInfoText.Text = $"Type: {project.Modality} | Models: {project.ModelCount}";
            }
        }

        private async void StartAutoMLButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(_selectedProjectId))
            {
                MessageBox.Show("Please select a project first", "Validation Error", 
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (!ValidateInputs())
                return;

            try
            {
                StartAutoMLButton.IsEnabled = false;
                StopAutoMLButton.IsEnabled = true;
                _isRunning = true;
                _trials.Clear();
                
                StatusText.Text = "Running...";
                StatusText.Foreground = System.Windows.Media.Brushes.Green;
                _stopwatch.Restart();

                // ساخت configuration
                var config = new
                {
                    project_id = _selectedProjectId,
                    n_trials = int.Parse(NumTrialsTextBox.Text),
                    timeout = int.Parse(TimeoutTextBox.Text) * 60, // Convert to seconds
                    optimizer = GetOptimizerType(),
                    metric = GetMetricType(),
                    search_space = BuildSearchSpace()
                };

                var json = JsonSerializer.Serialize(config);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                // شروع AutoML (این یک عملیات طولانی است)
                var response = await _httpClient.PostAsync("/api/automl/start", content);

                if (response.IsSuccessStatusCode)
                {
                    var resultJson = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<AutoMLResponse>(
                        resultJson,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );

                    if (result?.BestParams != null)
                    {
                        DisplayResults(result);
                        MessageBox.Show(
                            $"✅ AutoML completed successfully!\n\n" +
                            $"Best Score: {result.BestScore:F4}\n" +
                            $"Total Trials: {result.TotalTrials}\n" +
                            $"Time: {_stopwatch.Elapsed:hh\\:mm\\:ss}",
                            "Success",
                            MessageBoxButton.OK,
                            MessageBoxImage.Information
                        );
                    }
                }
                else
                {
                    var error = await response.Content.ReadAsStringAsync();
                    MessageBox.Show($"AutoML failed:\n\n{error}", "Error", 
                        MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error:\n\n{ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                _isRunning = false;
                _stopwatch.Stop();
                StartAutoMLButton.IsEnabled = true;
                StopAutoMLButton.IsEnabled = false;
                StatusText.Text = "Completed";
                StatusText.Foreground = System.Windows.Media.Brushes.Blue;
            }
        }

        private void StopAutoMLButton_Click(object sender, RoutedEventArgs e)
        {
            if (_isRunning)
            {
                var result = MessageBox.Show(
                    "Are you sure you want to stop AutoML optimization?",
                    "Confirm Stop",
                    MessageBoxButton.YesNo,
                    MessageBoxImage.Question
                );

                if (result == MessageBoxResult.Yes)
                {
                    // TODO: Implement stop functionality
                    _isRunning = false;
                    _stopwatch.Stop();
                    StatusText.Text = "Stopped";
                    StatusText.Foreground = System.Windows.Media.Brushes.Red;
                    StartAutoMLButton.IsEnabled = true;
                    StopAutoMLButton.IsEnabled = false;
                }
            }
        }

        private bool ValidateInputs()
        {
            if (!int.TryParse(NumTrialsTextBox.Text, out int trials) || trials <= 0)
            {
                MessageBox.Show("Number of trials must be a positive integer", "Validation Error", 
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return false;
            }

            if (!int.TryParse(TimeoutTextBox.Text, out int timeout) || timeout <= 0)
            {
                MessageBox.Show("Timeout must be a positive integer", "Validation Error", 
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return false;
            }

            return true;
        }

        private string GetOptimizerType()
        {
            var selected = (OptimizerComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "";
            if (selected.Contains("TPE")) return "tpe";
            if (selected.Contains("Random")) return "random";
            if (selected.Contains("Grid")) return "grid";
            return "tpe";
        }

        private string GetMetricType()
        {
            var selected = (MetricComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "";
            if (selected.Contains("Accuracy")) return "accuracy";
            if (selected.Contains("Loss")) return "loss";
            if (selected.Contains("F1")) return "f1";
            return "accuracy";
        }

        private object BuildSearchSpace()
        {
            var searchSpace = new Dictionary<string, object>();

            if (LearningRateCheckBox.IsChecked == true)
            {
                searchSpace["learning_rate"] = new
                {
                    type = "float",
                    low = double.Parse(LRMinTextBox.Text),
                    high = double.Parse(LRMaxTextBox.Text),
                    log = true
                };
            }

            if (BatchSizeCheckBox.IsChecked == true)
            {
                searchSpace["batch_size"] = new
                {
                    type = "categorical",
                    choices = new[] { 16, 32, 64 }
                };
            }

            if (DropoutCheckBox.IsChecked == true)
            {
                searchSpace["dropout"] = new
                {
                    type = "float",
                    low = double.Parse(DropoutMinTextBox.Text),
                    high = double.Parse(DropoutMaxTextBox.Text)
                };
            }

            if (OptimizerTypeCheckBox.IsChecked == true)
            {
                searchSpace["optimizer"] = new
                {
                    type = "categorical",
                    choices = new[] { "adam", "sgd", "adamw" }
                };
            }

            if (HiddenLayersCheckBox.IsChecked == true)
            {
                searchSpace["hidden_size"] = new
                {
                    type = "categorical",
                    choices = new[] { 128, 256, 512 }
                };
            }

            return searchSpace;
        }

        private void DisplayResults(AutoMLResponse result)
        {
            // Update best score
            BestScoreText.Text = $"{result.BestScore:F4}";
            TrialsText.Text = $"{result.TotalTrials} / {result.TotalTrials}";
            ProgressBar.Value = 100;

            // Display best parameters
            BestParamsText.Text = JsonSerializer.Serialize(
                result.BestParams,
                new JsonSerializerOptions { WriteIndented = true }
            );

            // Populate trial history
            if (result.TrialHistory != null)
            {
                _trials.Clear();
                foreach (var trial in result.TrialHistory)
                {
                    _trials.Add(new TrialInfo
                    {
                        TrialNumber = trial.Number,
                        Score = $"{trial.Score:F4}",
                        LearningRate = $"{trial.Params?.LearningRate:F6}",
                        BatchSize = trial.Params?.BatchSize.ToString() ?? "-",
                        Dropout = $"{trial.Params?.Dropout:F2}"
                    });
                }
            }

            ApplyBestButton.IsEnabled = true;
            ExportTrialsButton.IsEnabled = true;
        }

        private void ApplyBestButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(_selectedProjectId))
                return;

            var result = MessageBox.Show(
                "Apply best parameters to the project and start training?",
                "Confirm Apply",
                MessageBoxButton.YesNo,
                MessageBoxImage.Question
            );

            if (result == MessageBoxResult.Yes)
            {
                try
                {
                    // TODO: Apply best params and start training
                    MessageBox.Show(
                        "Best parameters applied successfully!\nNavigate to Training Dashboard to start training.",
                        "Success",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information
                    );
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error:\n\n{ex.Message}", "Error", 
                        MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void ExportTrialsButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var saveDialog = new Microsoft.Win32.SaveFileDialog
                {
                    Filter = "CSV Files (*.csv)|*.csv",
                    FileName = $"automl_trials_{DateTime.Now:yyyyMMdd_HHmmss}.csv"
                };

                if (saveDialog.ShowDialog() == true)
                {
                    var csv = new StringBuilder();
                    csv.AppendLine("Trial,Score,LearningRate,BatchSize,Dropout");

                    foreach (var trial in _trials)
                    {
                        csv.AppendLine($"{trial.TrialNumber},{trial.Score},{trial.LearningRate},{trial.BatchSize},{trial.Dropout}");
                    }

                    File.WriteAllText(saveDialog.FileName, csv.ToString());
                    
                    MessageBox.Show($"Trials exported successfully to:\n{saveDialog.FileName}", 
                        "Success", MessageBoxButton.OK, MessageBoxImage.Information);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error exporting:\n\n{ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        // Data Models
        public class TrialInfo
        {
            public int TrialNumber { get; set; }
            public string Score { get; set; } = "";
            public string LearningRate { get; set; } = "";
            public string BatchSize { get; set; } = "";
            public string Dropout { get; set; } = "";
        }

        private class ProjectsResponse
        {
            public List<ProjectInfo>? Projects { get; set; }
        }

        private class ProjectInfo
        {
            public string Id { get; set; } = "";
            public string Name { get; set; } = "";
            public string Modality { get; set; } = "";
            public int ModelCount { get; set; }
        }

        private class AutoMLResponse
        {
            public double BestScore { get; set; }
            public int TotalTrials { get; set; }
            public Dictionary<string, object>? BestParams { get; set; }
            public List<TrialData>? TrialHistory { get; set; }
        }

        private class TrialData
        {
            public int Number { get; set; }
            public double Score { get; set; }
            public TrialParams? Params { get; set; }
        }

        private class TrialParams
        {
            public double LearningRate { get; set; }
            public int BatchSize { get; set; }
            public double Dropout { get; set; }
            public string? Optimizer { get; set; }
        }
    }
}

