using ModelCreator.UI.Services;
using Microsoft.Win32;
using System.Collections.ObjectModel;
using System.IO;
using System.Net.Http;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Interaction logic for InferencePlaygroundPage.xaml
    /// Test trained models with new data
    /// </summary>
    public partial class InferencePlaygroundPage : Page
    {
        private readonly IApiService _apiService;
        private string _projectId;
        private string? _selectedFilePath;

        public InferencePlaygroundPage(string projectId)
        {
            InitializeComponent();
            _projectId = projectId;
            _apiService = App.GetService<IApiService>();
        }

        /// <summary>
        /// Handle file drop
        /// </summary>
        private void InputArea_Drop(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
                if (files.Length > 0)
                {
                    LoadFile(files[0]);
                }
            }
        }

        /// <summary>
        /// Handle drag enter
        /// </summary>
        private void InputArea_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effects = DragDropEffects.Copy;
            }
        }

        /// <summary>
        /// Handle drag leave
        /// </summary>
        private void InputArea_DragLeave(object sender, DragEventArgs e)
        {
            // Reset visual state if needed
        }

        /// <summary>
        /// Browse for files
        /// </summary>
        private void BrowseFiles_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Title = "Select File",
                Filter = "All Files (*.*)|*.*|Images (*.jpg;*.png)|*.jpg;*.png|Text Files (*.txt)|*.txt|Audio Files (*.wav;*.mp3)|*.wav;*.mp3"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                LoadFile(openFileDialog.FileName);
            }
        }

        /// <summary>
        /// Load and preview file
        /// </summary>
        private void LoadFile(string filePath)
        {
            _selectedFilePath = filePath;
            var extension = Path.GetExtension(filePath).ToLower();

            // Hide all previews
            PreviewImage.Visibility = Visibility.Collapsed;
            PreviewText.Visibility = Visibility.Collapsed;
            PreviewPlaceholder.Visibility = Visibility.Collapsed;

            try
            {
                // Preview based on file type
                if (extension == ".jpg" || extension == ".jpeg" || extension == ".png" || extension == ".bmp")
                {
                    // Show image preview
                    var bitmap = new BitmapImage();
                    bitmap.BeginInit();
                    bitmap.UriSource = new Uri(filePath);
                    bitmap.CacheOption = BitmapCacheOption.OnLoad;
                    bitmap.EndInit();
                    
                    PreviewImage.Source = bitmap;
                    PreviewImage.Visibility = Visibility.Visible;
                }
                else if (extension == ".txt")
                {
                    // Show text preview
                    var text = File.ReadAllText(filePath);
                    if (text.Length > 500)
                    {
                        text = text.Substring(0, 500) + "...";
                    }
                    PreviewText.Text = text;
                    PreviewText.Visibility = Visibility.Visible;
                }
                else
                {
                    // Show file info
                    var fileInfo = new FileInfo(filePath);
                    PreviewText.Text = $"File: {fileInfo.Name}\nSize: {fileInfo.Length / 1024} KB\nType: {extension}";
                    PreviewText.Visibility = Visibility.Visible;
                }

                PredictButton.IsEnabled = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading file: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Run prediction
        /// </summary>
        private async void Predict_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(_selectedFilePath))
            {
                MessageBox.Show("Please select a file first.", "No File Selected", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            try
            {
                PredictButton.IsEnabled = false;
                PredictButton.Content = "⏳ Predicting...";

                // Call actual inference API
                var result = await RunInference(_selectedFilePath);
                
                if (result != null)
                {
                    // Display results
                    DisplayResults(result);
                }
                else
                {
                    MessageBox.Show("No prediction result returned.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }

                PredictButton.Content = "🚀 Run Prediction";
                PredictButton.IsEnabled = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error during prediction: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                PredictButton.Content = "🚀 Run Prediction";
                PredictButton.IsEnabled = true;
            }
        }
        
        /// <summary>
        /// Run inference via API
        /// </summary>
        private async Task<PredictionResult?> RunInference(string filePath)
        {
            try
            {
                // Create multipart form data
                using var content = new MultipartFormDataContent();
                using var fileStream = File.OpenRead(filePath);
                using var streamContent = new StreamContent(fileStream);
                
                content.Add(streamContent, "file", Path.GetFileName(filePath));
                
                // Call inference API
                var response = await _apiService.PostMultipartAsync<Dictionary<string, object>>(
                    $"/api/inference/predict/{_projectId}",
                    content
                );
                
                if (response == null) return null;
                
                // Parse response
                var result = new PredictionResult();
                
                // Initialize top predictions
                result.TopPredictions = new ObservableCollection<TopPrediction>();
                
                // Parse inference_time (using JsonElement methods)
                if (response.ContainsKey("inference_time"))
                {
                    var inferenceTimeObj = response["inference_time"];
                    if (inferenceTimeObj is System.Text.Json.JsonElement inferenceTimeElem)
                    {
                        result.InferenceTime = inferenceTimeElem.GetDouble();
                    }
                    else if (inferenceTimeObj is double inferenceTimeDouble)
                    {
                        result.InferenceTime = inferenceTimeDouble;
                    }
                }
                
                // Parse top predictions
                if (response.ContainsKey("predictions"))
                {
                    var predictionsObj = response["predictions"];
                    
                    if (predictionsObj is System.Text.Json.JsonElement predictions)
                    {
                        if (predictions.ValueKind == System.Text.Json.JsonValueKind.Array)
                        {
                            foreach (var pred in predictions.EnumerateArray())
                            {
                                try
                                {
                                    var className = pred.GetProperty("class_name").GetString() ?? "Unknown";
                                    var confidence = pred.GetProperty("confidence").GetDouble();
                                    
                                    result.TopPredictions.Add(new TopPrediction
                                    {
                                        Label = className,
                                        Probability = confidence
                                    });
                                    
                                    // Set predicted class from first item
                                    if (result.TopPredictions.Count == 1)
                                    {
                                        result.PredictedClass = className;
                                        result.Confidence = confidence;
                                    }
                                }
                                catch (Exception ex)
                                {
                                    System.Diagnostics.Debug.WriteLine($"Error parsing prediction: {ex.Message}");
                                }
                            }
                        }
                    }
                }
                
                return result;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Inference error: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Display prediction results
        /// </summary>
        private void DisplayResults(PredictionResult result)
        {
            if (PredictedClassText != null)
            {
                PredictedClassText.Text = result.PredictedClass;
            }
            
            if (ConfidenceBar != null)
            {
                ConfidenceBar.Value = result.Confidence * 100;
            }
            
            if (ConfidenceText != null)
            {
                ConfidenceText.Text = $"Confidence: {result.Confidence:P1}";
            }
            
            if (InferenceTimeText != null)
            {
                InferenceTimeText.Text = $"{result.InferenceTime:F3}s";
            }

            if (TopPredictionsList != null)
            {
                TopPredictionsList.ItemsSource = result.TopPredictions;
            }
        }
    }

    /// <summary>
    /// Prediction result model
    /// </summary>
    public class PredictionResult
    {
        public string PredictedClass { get; set; } = "";
        public double Confidence { get; set; }
        public double InferenceTime { get; set; }
        public ObservableCollection<TopPrediction> TopPredictions { get; set; } = new();
    }

    /// <summary>
    /// Top prediction model
    /// </summary>
    public class TopPrediction
    {
        public string Label { get; set; } = "";
        public double Probability { get; set; }
    }
}

