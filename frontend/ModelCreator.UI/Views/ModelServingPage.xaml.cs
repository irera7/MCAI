using System;
using System.Collections.ObjectModel;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.IO;
using System.Linq;
using System.Collections.Generic;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Model Serving Page - Deploy and manage trained models for inference
    /// </summary>
    public partial class ModelServingPage : Page
    {
        private readonly HttpClient _httpClient;
        private ObservableCollection<AvailableModel> _availableModels;
        private ObservableCollection<LoadedModel> _loadedModels;
        private string? _selectedTestFilePath;

        public ModelServingPage()
        {
            InitializeComponent();
            
            _httpClient = new HttpClient 
            { 
                BaseAddress = new Uri("http://127.0.0.1:8181"),
                Timeout = TimeSpan.FromMinutes(5)
            };
            
            _availableModels = new ObservableCollection<AvailableModel>();
            _loadedModels = new ObservableCollection<LoadedModel>();
            
            AvailableModelsListView.ItemsSource = _availableModels;
            LoadedModelsGrid.ItemsSource = _loadedModels;
            TestModelComboBox.ItemsSource = _loadedModels;
            
            LoadAvailableModels();
            LoadLoadedModels();
        }

        private async void LoadAvailableModels()
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

                    _availableModels.Clear();
                    
                    if (result?.Projects != null)
                    {
                        foreach (var project in result.Projects)
                        {
                            // Check if project has trained models
                            var projectDir = Path.Combine("..", "projects", project.Id, "checkpoints");
                            if (Directory.Exists(projectDir))
                            {
                                var modelFiles = Directory.GetFiles(projectDir, "best_model.pt");
                                if (modelFiles.Length > 0)
                                {
                                    var fileInfo = new FileInfo(modelFiles[0]);
                                    _availableModels.Add(new AvailableModel
                                    {
                                        Name = project.Name ?? "Unknown",
                                        ProjectId = project.Id ?? "",
                                        Modality = project.Modality ?? "unknown",
                                        ModelPath = modelFiles[0],
                                        Size = $"{fileInfo.Length / (1024 * 1024):F1} MB"
                                    });
                                }
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading models:\n\n{ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void LoadLoadedModels()
        {
            try
            {
                var response = await _httpClient.GetAsync("/api/serve/models");
                
                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<LoadedModelsResponse>(
                        json,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );

                    _loadedModels.Clear();
                    
                    if (result?.LoadedModels != null)
                    {
                        foreach (var model in result.LoadedModels)
                        {
                            _loadedModels.Add(new LoadedModel
                            {
                                ModelId = model.ModelId ?? "",
                                ModelType = model.ModelType ?? "unknown",
                                Device = model.Device ?? "cpu",
                                MemoryMB = model.MemoryMB,
                                RequestCount = model.RequestCount,
                                AvgLatency = $"{model.AvgLatency:F1}"
                            });
                        }
                    }
                    
                    LoadedCountText.Text = $"{_loadedModels.Count} models";
                    UnloadAllButton.IsEnabled = _loadedModels.Count > 0;
                }
            }
            catch (Exception ex)
            {
                // Server might not be running or no models loaded
                _loadedModels.Clear();
                LoadedCountText.Text = "0 models";
                UnloadAllButton.IsEnabled = false;
            }
        }

        private void AvailableModelsListView_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            LoadModelButton.IsEnabled = AvailableModelsListView.SelectedItem != null;
        }

        private async void LoadModelButton_Click(object sender, RoutedEventArgs e)
        {
            if (AvailableModelsListView.SelectedItem is not AvailableModel selectedModel)
                return;

            try
            {
                LoadModelButton.IsEnabled = false;
                LoadModelButton.Content = "⏳ Loading...";

                var device = DeviceComboBox.SelectedIndex == 0 ? "cuda" : "cpu";
                
                // Register model first
                var registerData = new
                {
                    model_id = selectedModel.ProjectId,
                    model_path = selectedModel.ModelPath,
                    model_type = selectedModel.Modality,
                    metadata = new { name = selectedModel.Name }
                };

                var registerJson = JsonSerializer.Serialize(registerData);
                var registerContent = new StringContent(registerJson, Encoding.UTF8, "application/json");
                
                var registerResponse = await _httpClient.PostAsync("/api/serve/register", registerContent);
                
                if (!registerResponse.IsSuccessStatusCode)
                {
                    var error = await registerResponse.Content.ReadAsStringAsync();
                    throw new Exception($"Registration failed: {error}");
                }

                // Load model
                var loadResponse = await _httpClient.PostAsync(
                    $"/api/serve/load/{selectedModel.ProjectId}?device={device}", 
                    null
                );

                if (loadResponse.IsSuccessStatusCode)
                {
                    MessageBox.Show(
                        $"✅ Model loaded successfully!\n\nModel ID: {selectedModel.ProjectId}\nDevice: {device}",
                        "Success",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information
                    );
                    
                    LoadLoadedModels(); // Refresh loaded models list
                }
                else
                {
                    var error = await loadResponse.Content.ReadAsStringAsync();
                    MessageBox.Show($"Failed to load model:\n\n{error}", "Error", 
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
                LoadModelButton.IsEnabled = true;
                LoadModelButton.Content = "⬆️ Load Selected Model";
            }
        }

        private async void UnloadModelButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is string modelId)
            {
                try
                {
                    var response = await _httpClient.DeleteAsync($"/api/serve/unload/{modelId}");
                    
                    if (response.IsSuccessStatusCode)
                    {
                        MessageBox.Show($"Model '{modelId}' unloaded successfully", "Success", 
                            MessageBoxButton.OK, MessageBoxImage.Information);
                        LoadLoadedModels(); // Refresh
                    }
                    else
                    {
                        var error = await response.Content.ReadAsStringAsync();
                        MessageBox.Show($"Failed to unload:\n\n{error}", "Error", 
                            MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error:\n\n{ex.Message}", "Error", 
                        MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private async void UnloadAllButton_Click(object sender, RoutedEventArgs e)
        {
            var result = MessageBox.Show(
                "Are you sure you want to unload all models?",
                "Confirm Unload All",
                MessageBoxButton.YesNo,
                MessageBoxImage.Question
            );

            if (result == MessageBoxResult.Yes)
            {
                try
                {
                    foreach (var model in _loadedModels.ToList())
                    {
                        await _httpClient.DeleteAsync($"/api/serve/unload/{model.ModelId}");
                    }
                    
                    MessageBox.Show("All models unloaded successfully", "Success", 
                        MessageBoxButton.OK, MessageBoxImage.Information);
                    LoadLoadedModels(); // Refresh
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error:\n\n{ex.Message}", "Error", 
                        MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void RefreshModelsButton_Click(object sender, RoutedEventArgs e)
        {
            LoadAvailableModels();
        }

        private void RefreshLoadedButton_Click(object sender, RoutedEventArgs e)
        {
            LoadLoadedModels();
        }

        private void BrowseTestFileButton_Click(object sender, RoutedEventArgs e)
        {
            var openDialog = new Microsoft.Win32.OpenFileDialog
            {
                Filter = "All Files (*.*)|*.*|Images (*.jpg;*.png)|*.jpg;*.png|Audio (*.wav;*.mp3)|*.wav;*.mp3",
                Title = "Select Test File"
            };

            if (openDialog.ShowDialog() == true)
            {
                _selectedTestFilePath = openDialog.FileName;
                TestFilePathTextBox.Text = Path.GetFileName(openDialog.FileName);
                RunInferenceButton.IsEnabled = TestModelComboBox.SelectedItem != null;
            }
        }

        private async void RunInferenceButton_Click(object sender, RoutedEventArgs e)
        {
            if (TestModelComboBox.SelectedItem is not LoadedModel selectedModel)
            {
                MessageBox.Show("Please select a model", "Validation Error", 
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (string.IsNullOrEmpty(_selectedTestFilePath) || !File.Exists(_selectedTestFilePath))
            {
                MessageBox.Show("Please select a valid test file", "Validation Error", 
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            try
            {
                RunInferenceButton.IsEnabled = false;
                RunInferenceButton.Content = "⏳ Running...";
                InferenceResultText.Text = "Processing...";

                var stopwatch = System.Diagnostics.Stopwatch.StartNew();

                // Create multipart form data
                using var formData = new MultipartFormDataContent();
                var fileBytes = await File.ReadAllBytesAsync(_selectedTestFilePath);
                var fileContent = new ByteArrayContent(fileBytes);
                fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/octet-stream");
                formData.Add(fileContent, "file", Path.GetFileName(_selectedTestFilePath));

                var response = await _httpClient.PostAsync(
                    $"/api/serve/predict/{selectedModel.ModelId}",
                    formData
                );

                stopwatch.Stop();
                LatencyText.Text = $"{stopwatch.ElapsedMilliseconds} ms";

                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<InferenceResult>(
                        json,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );

                    if (result != null)
                    {
                        InferenceResultText.Text = $"Prediction: {result.PredictedClass}\n" +
                                                   $"Class ID: {result.ClassId}\n" +
                                                   $"Confidence: {result.Confidence:P2}";
                        
                        ConfidenceText.Text = $"{result.Confidence:P2}";
                        ConfidenceText.Foreground = result.Confidence > 0.8 
                            ? System.Windows.Media.Brushes.Green 
                            : System.Windows.Media.Brushes.Orange;
                    }
                }
                else
                {
                    var error = await response.Content.ReadAsStringAsync();
                    InferenceResultText.Text = $"Error: {error}";
                    ConfidenceText.Text = "-";
                }
            }
            catch (Exception ex)
            {
                InferenceResultText.Text = $"Error: {ex.Message}";
                LatencyText.Text = "-";
                ConfidenceText.Text = "-";
                MessageBox.Show($"Inference error:\n\n{ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                RunInferenceButton.IsEnabled = true;
                RunInferenceButton.Content = "▶️ Run Inference";
            }
        }

        // Data Models
        public class AvailableModel
        {
            public string Name { get; set; } = "";
            public string ProjectId { get; set; } = "";
            public string Modality { get; set; } = "";
            public string ModelPath { get; set; } = "";
            public string Size { get; set; } = "";
        }

        public class LoadedModel
        {
            public string ModelId { get; set; } = "";
            public string ModelType { get; set; } = "";
            public string Device { get; set; } = "";
            public int MemoryMB { get; set; }
            public int RequestCount { get; set; }
            public string AvgLatency { get; set; } = "";
        }

        private class ProjectsResponse
        {
            public List<ProjectInfo>? Projects { get; set; }
        }

        private class ProjectInfo
        {
            public string? Id { get; set; }
            public string? Name { get; set; }
            public string? Modality { get; set; }
        }

        private class LoadedModelsResponse
        {
            public List<LoadedModelInfo>? LoadedModels { get; set; }
        }

        private class LoadedModelInfo
        {
            public string? ModelId { get; set; }
            public string? ModelType { get; set; }
            public string? Device { get; set; }
            public int MemoryMB { get; set; }
            public int RequestCount { get; set; }
            public double AvgLatency { get; set; }
        }

        private class InferenceResult
        {
            public string PredictedClass { get; set; } = "";
            public int ClassId { get; set; }
            public double Confidence { get; set; }
        }
    }
}
