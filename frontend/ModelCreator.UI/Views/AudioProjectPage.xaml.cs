using System;
using System.IO;
using System.Linq;
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
    /// صفحه ایجاد پروژه Audio Classification
    /// Complete implementation with API integration
    /// </summary>
    public partial class AudioProjectPage : Page
    {
        private readonly HttpClient _httpClient;
        private string[]? _uploadedAudioFiles;
        private string? _projectId;

        public AudioProjectPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient 
            { 
                BaseAddress = new Uri("http://127.0.0.1:8181"),
                Timeout = TimeSpan.FromMinutes(5) // برای آپلود فایل‌های بزرگ
            };
        }

        /// <summary>
        /// آپلود فایل‌های audio
        /// </summary>
        private async void UploadDataButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var dialog = new OpenFileDialog
                {
                    Title = "Select Audio Files",
                    Filter = "Audio Files (*.wav;*.mp3;*.flac)|*.wav;*.mp3;*.flac|All Files (*.*)|*.*",
                    Multiselect = true
                };

                if (dialog.ShowDialog() == true)
                {
                    _uploadedAudioFiles = dialog.FileNames;
                    
                    // نمایش وضعیت
                    DataStatusTextBlock.Text = $"📄 {_uploadedAudioFiles.Length} files selected";
                    DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Blue;
                    
                    // آپلود به backend
                    UploadDataButton.IsEnabled = false;
                    UploadDataButton.Content = "⏳ Uploading...";

                    var success = await UploadAudioFilesToBackend(_uploadedAudioFiles);

                    if (success)
                    {
                        DataStatusTextBlock.Text = $"✅ Uploaded {_uploadedAudioFiles.Length} audio files";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Green;

                        MessageBox.Show(
                            $"Successfully uploaded {_uploadedAudioFiles.Length} audio files!\n\n" +
                            "Supported formats: WAV, MP3, FLAC\n" +
                            "Recommended sample rate: 16kHz or 22kHz\n\n" +
                            "Make sure your files are organized by class folders or named with class labels.",
                            "Upload Successful",
                            MessageBoxButton.OK,
                            MessageBoxImage.Information
                        );
                    }
                    else
                    {
                        DataStatusTextBlock.Text = "❌ Upload failed";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                        _uploadedAudioFiles = null;
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error uploading audio files:\n\n{ex.Message}",
                    "Upload Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
                
                DataStatusTextBlock.Text = "❌ Error";
                DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                _uploadedAudioFiles = null;
            }
            finally
            {
                UploadDataButton.IsEnabled = true;
                UploadDataButton.Content = "📁 Upload Audio Files";
            }
        }

        /// <summary>
        /// آپلود فایل‌های audio به backend
        /// </summary>
        private async Task<bool> UploadAudioFilesToBackend(string[] filePaths)
        {
            try
            {
                using var content = new MultipartFormDataContent();
                
                // اضافه کردن تمام فایل‌ها
                foreach (var filePath in filePaths)
                {
                    var fileContent = new ByteArrayContent(File.ReadAllBytes(filePath));
                    fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/mpeg");
                    content.Add(fileContent, "files", Path.GetFileName(filePath));
                }

                var response = await _httpClient.PostAsync("/api/data/upload/audio", content);
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// ایجاد پروژه audio و شروع training
        /// </summary>
        private async void CreateProjectButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // اعتبارسنجی ورودی
                if (string.IsNullOrWhiteSpace(ProjectNameTextBox.Text))
                {
                    MessageBox.Show(
                        "Please enter a project name",
                        "Validation Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Warning
                    );
                    return;
                }

                if (_uploadedAudioFiles == null || _uploadedAudioFiles.Length == 0)
                {
                    MessageBox.Show(
                        "Please upload audio files first",
                        "Validation Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Warning
                    );
                    return;
                }

                // دریافت پارامترها
                int sampleRate = GetSampleRate();
                int duration = GetDuration();
                int nMels = GetNMels();
                int batchSize = GetBatchSize();
                double learningRate = GetLearningRate();
                int epochs = GetEpochs();
                double dropout = GetDropout();

                // Disable button
                CreateProjectButton.IsEnabled = false;
                CreateProjectButton.Content = "⏳ Creating Project...";

                // Step 1: ایجاد پروژه
                _projectId = await CreateProject();

                if (string.IsNullOrEmpty(_projectId))
                {
                    MessageBox.Show(
                        "Failed to create project",
                        "Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error
                    );
                    return;
                }

                // Step 2: شروع training
                CreateProjectButton.Content = "⏳ Starting Training...";

                var trainingStarted = await StartTraining(
                    _projectId,
                    "spectrogram_cnn",
                    sampleRate,
                    duration,
                    nMels,
                    batchSize,
                    learningRate,
                    epochs,
                    dropout
                );

                if (trainingStarted)
                {
                    MessageBox.Show(
                        $"✅ Audio classification project created!\n\n" +
                        $"Project: {ProjectNameTextBox.Text}\n" +
                        $"Model: Spectrogram CNN\n" +
                        $"Audio Files: {_uploadedAudioFiles.Length}\n" +
                        $"Sample Rate: {sampleRate} Hz\n" +
                        $"Epochs: {epochs}\n\n" +
                        "Training started! Navigate to Training Dashboard to monitor progress.",
                        "Success",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information
                    );

                    // Navigate to training dashboard
                    var window = Window.GetWindow(this) as MainWindow;
                    window?.MainFrame.Navigate(new TrainingDashboardPage(_projectId, ProjectNameTextBox.Text));
                }
                else
                {
                    MessageBox.Show(
                        "Failed to start training",
                        "Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error
                    );
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error creating project:\n\n{ex.Message}\n\n" +
                    "Make sure the backend server is running.",
                    "Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
            finally
            {
                CreateProjectButton.IsEnabled = true;
                CreateProjectButton.Content = "✅ Create Audio Project";
            }
        }

        /// <summary>
        /// ایجاد پروژه در backend
        /// </summary>
        private async Task<string?> CreateProject()
        {
            try
            {
                var audioType = (AudioTypeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "Other";
                
                var projectData = new
                {
                    name = ProjectNameTextBox.Text,
                    description = DescriptionTextBox.Text,
                    modality = "audio",
                    audio_type = audioType,
                    num_files = _uploadedAudioFiles?.Length ?? 0
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
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// شروع training
        /// </summary>
        private async Task<bool> StartTraining(
            string projectId,
            string model,
            int sampleRate,
            int duration,
            int nMels,
            int batchSize,
            double learningRate,
            int epochs,
            double dropout)
        {
            try
            {
                var trainingConfig = new
                {
                    project_id = projectId,
                    modality = "audio",
                    model_id = model,
                    epochs = epochs,
                    batch_size = batchSize,
                    learning_rate = learningRate,
                    sample_rate = sampleRate,
                    duration = duration,
                    n_mels = nMels,
                    dropout = dropout
                };

                var json = JsonSerializer.Serialize(trainingConfig);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync($"/api/training/start/{projectId}", content);
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Cancel button
        /// </summary>
        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            var result = MessageBox.Show(
                "Are you sure you want to cancel?\nAny unsaved changes will be lost.",
                "Confirm Cancel",
                MessageBoxButton.YesNo,
                MessageBoxImage.Question
            );

            if (result == MessageBoxResult.Yes)
            {
                var window = Window.GetWindow(this) as MainWindow;
                window?.MainFrame.Navigate(new HomePage());
            }
        }

        // ============================================
        // Helper Methods
        // ============================================

        private int GetSampleRate()
        {
            var selected = (SampleRateComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "22050";
            return int.Parse(selected.Split(' ')[0]);
        }

        private int GetDuration()
        {
            var selected = (DurationComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "3";
            return int.Parse(selected.Split(' ')[0]);
        }

        private int GetNMels()
        {
            var selected = (NMelsComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "128";
            return int.Parse(selected);
        }

        private int GetBatchSize()
        {
            var selected = (BatchSizeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "32";
            return int.Parse(selected);
        }

        private double GetLearningRate()
        {
            if (double.TryParse(LearningRateTextBox.Text, out double lr))
                return lr;
            return 0.001;
        }

        private int GetEpochs()
        {
            if (int.TryParse(EpochsTextBox.Text, out int epochs))
                return epochs;
            return 30;
        }

        private double GetDropout()
        {
            var selected = (DropoutComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "0.3";
            return double.Parse(selected);
        }

        // ============================================
        // Data Models
        // ============================================

        private class ProjectCreateResponse
        {
            public string? ProjectId { get; set; }
            public string? Status { get; set; }
        }
    }
}
