using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// صفحه Video Classification Project
    /// Complete implementation with API integration
    /// </summary>
    public partial class VideoProjectPage : Page
    {
        private readonly HttpClient _httpClient;
        private string[]? _uploadedVideoFiles;
        private string? _projectId;

        public VideoProjectPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient 
            { 
                BaseAddress = new Uri("http://127.0.0.1:8181"),
                Timeout = TimeSpan.FromMinutes(15) // برای آپلود ویدئوهای بزرگ
            };
        }

        /// <summary>
        /// آپلود فایل‌های video
        /// </summary>
        private async void UploadDataButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var dialog = new OpenFileDialog
                {
                    Title = "Select Video Files",
                    Filter = "Video Files (*.mp4;*.avi;*.mov;*.mkv)|*.mp4;*.avi;*.mov;*.mkv|All Files (*.*)|*.*",
                    Multiselect = true
                };

                if (dialog.ShowDialog() == true)
                {
                    _uploadedVideoFiles = dialog.FileNames;
                    
                    DataStatusTextBlock.Text = $"📹 {_uploadedVideoFiles.Length} videos selected";
                    DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Blue;
                    
                    UploadDataButton.IsEnabled = false;
                    UploadDataButton.Content = "⏳ Uploading...";

                    var success = await UploadVideoFilesToBackend(_uploadedVideoFiles);

                    if (success)
                    {
                        DataStatusTextBlock.Text = $"✅ Uploaded {_uploadedVideoFiles.Length} video files";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Green;

                        MessageBox.Show(
                            $"Successfully uploaded {_uploadedVideoFiles.Length} video files!\n\n" +
                            "Supported formats: MP4, AVI, MOV, MKV\n" +
                            "Videos will be processed into frames for training.",
                            "Upload Successful",
                            MessageBoxButton.OK,
                            MessageBoxImage.Information
                        );
                    }
                    else
                    {
                        DataStatusTextBlock.Text = "❌ Upload failed";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                        _uploadedVideoFiles = null;
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error uploading video files:\n\n{ex.Message}",
                    "Upload Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
                
                DataStatusTextBlock.Text = "❌ Error";
                DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                _uploadedVideoFiles = null;
            }
            finally
            {
                UploadDataButton.IsEnabled = true;
                UploadDataButton.Content = "📁 Upload Video Files";
            }
        }

        private async Task<bool> UploadVideoFilesToBackend(string[] filePaths)
        {
            try
            {
                using var content = new MultipartFormDataContent();
                
                foreach (var filePath in filePaths)
                {
                    var fileContent = new ByteArrayContent(File.ReadAllBytes(filePath));
                    fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("video/mp4");
                    content.Add(fileContent, "files", Path.GetFileName(filePath));
                }

                var response = await _httpClient.PostAsync("/api/data/upload/video", content);
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        private async void CreateProjectButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(ProjectNameTextBox.Text))
                {
                    MessageBox.Show("Please enter a project name", "Validation Error", 
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                if (_uploadedVideoFiles == null || _uploadedVideoFiles.Length == 0)
                {
                    MessageBox.Show("Please upload video files first", "Validation Error", 
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                string modelType = CNN3DRadio.IsChecked == true ? "cnn3d" : "r2plus1d";
                int numFrames = GetNumFrames();
                int frameSize = GetFrameSize();
                int batchSize = GetBatchSize();
                double learningRate = GetLearningRate();
                int epochs = GetEpochs();

                CreateProjectButton.IsEnabled = false;
                CreateProjectButton.Content = "⏳ Creating...";

                _projectId = await CreateProject();
                if (string.IsNullOrEmpty(_projectId))
                {
                    MessageBox.Show("Failed to create project", "Error", 
                        MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }

                CreateProjectButton.Content = "⏳ Starting Training...";
                var trainingStarted = await StartTraining(_projectId, modelType, numFrames, 
                    frameSize, batchSize, learningRate, epochs);

                if (trainingStarted)
                {
                    MessageBox.Show(
                        $"✅ Video classification project created!\n\n" +
                        $"Project: {ProjectNameTextBox.Text}\n" +
                        $"Model: {modelType.ToUpper()}\n" +
                        $"Videos: {_uploadedVideoFiles.Length}\n" +
                        $"Frames per video: {numFrames}\n" +
                        $"Epochs: {epochs}\n\n" +
                        "Training started!",
                        "Success",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information
                    );

                    var window = Window.GetWindow(this) as MainWindow;
                    window?.MainFrame.Navigate(new TrainingDashboardPage(_projectId, ProjectNameTextBox.Text));
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                CreateProjectButton.IsEnabled = true;
                CreateProjectButton.Content = "✅ Create Video Project";
            }
        }

        private async Task<string?> CreateProject()
        {
            try
            {
                var projectData = new
                {
                    name = ProjectNameTextBox.Text,
                    description = DescriptionTextBox.Text,
                    modality = "video",
                    num_files = _uploadedVideoFiles?.Length ?? 0
                };

                var json = JsonSerializer.Serialize(projectData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync("/api/project/create", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseText = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<ProjectCreateResponse>(
                        responseText,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );
                    return result?.ProjectId;
                }
                return null;
            }
            catch { return null; }
        }

        private async Task<bool> StartTraining(string projectId, string model, int numFrames, 
            int frameSize, int batchSize, double learningRate, int epochs)
        {
            try
            {
                var trainingConfig = new
                {
                    project_id = projectId,
                    modality = "video",
                    model_id = model,
                    num_frames = numFrames,
                    frame_size = frameSize,
                    epochs = epochs,
                    batch_size = batchSize,
                    learning_rate = learningRate
                };

                var json = JsonSerializer.Serialize(trainingConfig);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync($"/api/training/start/{projectId}", content);
                return response.IsSuccessStatusCode;
            }
            catch { return false; }
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new HomePage());
        }

        private int GetNumFrames() =>
            int.Parse((FramesComboBox.SelectedItem as ComboBoxItem)?.Content.ToString()?.Split(' ')[0] ?? "16");
        
        private int GetFrameSize() =>
            int.Parse((FrameSizeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString()?.Split('x')[0] ?? "112");
        
        private int GetBatchSize() =>
            int.Parse((BatchSizeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "4");
        
        private double GetLearningRate() =>
            double.TryParse(LearningRateTextBox.Text, out double lr) ? lr : 0.0001;
        
        private int GetEpochs() =>
            int.TryParse(EpochsTextBox.Text, out int epochs) ? epochs : 20;

        private class ProjectCreateResponse
        {
            public string? ProjectId { get; set; }
            public string? Status { get; set; }
        }
    }
}
