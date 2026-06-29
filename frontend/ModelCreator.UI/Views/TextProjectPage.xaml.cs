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
    /// صفحه ایجاد پروژه Text Classification
    /// Complete implementation with API integration
    /// </summary>
    public partial class TextProjectPage : Page
    {
        private readonly HttpClient _httpClient;
        private string? _uploadedDataPath;
        private string? _projectId;

        public TextProjectPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:8181") };
        }

        /// <summary>
        /// آپلود داده‌های text
        /// </summary>
        private async void UploadDataButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var dialog = new OpenFileDialog
                {
                    Title = "Select Text Data File",
                    Filter = "CSV Files (*.csv)|*.csv|JSON Files (*.json)|*.json|Text Files (*.txt)|*.txt|All Files (*.*)|*.*",
                    Multiselect = false
                };

                if (dialog.ShowDialog() == true)
                {
                    _uploadedDataPath = dialog.FileName;
                    string fileName = Path.GetFileName(_uploadedDataPath);
                    
                    // نمایش وضعیت
                    DataStatusTextBlock.Text = $"📄 {fileName}";
                    DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Blue;
                    
                    // آپلود به backend
                    UploadDataButton.IsEnabled = false;
                    UploadDataButton.Content = "⏳ Uploading...";

                    var success = await UploadDataToBackend(_uploadedDataPath);

                    if (success)
                    {
                        DataStatusTextBlock.Text = $"✅ Uploaded: {fileName}";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Green;

                        MessageBox.Show(
                            $"Data file uploaded successfully: {fileName}\n\n" +
                            "Format requirements:\n" +
                            "• CSV: must have 'text' and 'label' columns\n" +
                            "• JSON: array of objects with 'text' and 'label' fields\n" +
                            "• TXT: one document per file in class folders",
                            "Upload Successful",
                            MessageBoxButton.OK,
                            MessageBoxImage.Information
                        );
                    }
                    else
                    {
                        DataStatusTextBlock.Text = "❌ Upload failed";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                        _uploadedDataPath = null;
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error uploading data:\n\n{ex.Message}",
                    "Upload Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
                
                DataStatusTextBlock.Text = "❌ Error";
                DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                _uploadedDataPath = null;
            }
            finally
            {
                UploadDataButton.IsEnabled = true;
                UploadDataButton.Content = "📁 Upload Text Data";
            }
        }

        /// <summary>
        /// آپلود داده به backend
        /// </summary>
        private async Task<bool> UploadDataToBackend(string filePath)
        {
            try
            {
                using var content = new MultipartFormDataContent();
                
                // اضافه کردن فایل
                var fileContent = new ByteArrayContent(File.ReadAllBytes(filePath));
                fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/octet-stream");
                content.Add(fileContent, "file", Path.GetFileName(filePath));

                var response = await _httpClient.PostAsync("/api/data/upload/text", content);
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// ایجاد پروژه text و شروع training
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

                if (string.IsNullOrEmpty(_uploadedDataPath))
                {
                    MessageBox.Show(
                        "Please upload text data first",
                        "Validation Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Warning
                    );
                    return;
                }

                // تشخیص مدل انتخابی
                string selectedModel = "lstm";
                if (GRURadio.IsChecked == true) selectedModel = "gru";
                else if (TransformerRadio.IsChecked == true) selectedModel = "transformer";
                else if (BERTRadio.IsChecked == true) selectedModel = "bert";

                // دریافت پارامترها
                int maxLength = GetMaxLength();
                int batchSize = GetBatchSize();
                double learningRate = GetLearningRate();
                int epochs = GetEpochs();
                int hiddenDim = GetHiddenDim();
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
                    selectedModel,
                    maxLength,
                    batchSize,
                    learningRate,
                    epochs,
                    hiddenDim,
                    dropout
                );

                if (trainingStarted)
                {
                    MessageBox.Show(
                        $"✅ Text classification project created!\n\n" +
                        $"Project: {ProjectNameTextBox.Text}\n" +
                        $"Model: {selectedModel.ToUpper()}\n" +
                        $"Epochs: {epochs}\n" +
                        $"Batch Size: {batchSize}\n\n" +
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
                CreateProjectButton.Content = "✅ Create Text Project";
            }
        }

        /// <summary>
        /// ایجاد پروژه در backend
        /// </summary>
        private async Task<string?> CreateProject()
        {
            try
            {
                var projectData = new
                {
                    name = ProjectNameTextBox.Text,
                    description = DescriptionTextBox.Text,
                    modality = "text",
                    data_path = _uploadedDataPath
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
            int maxLength,
            int batchSize,
            double learningRate,
            int epochs,
            int hiddenDim,
            double dropout)
        {
            try
            {
                var trainingConfig = new
                {
                    project_id = projectId,
                    modality = "text",
                    model_id = model,
                    epochs = epochs,
                    batch_size = batchSize,
                    learning_rate = learningRate,
                    max_length = maxLength,
                    hidden_dim = hiddenDim,
                    dropout = dropout,
                    num_layers = 2,
                    bidirectional = true
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

        private int GetMaxLength()
        {
            var selected = (MaxLengthComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "256";
            return int.Parse(selected.Split(' ')[0]);
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
            return 20;
        }

        private int GetHiddenDim()
        {
            var selected = (HiddenDimComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "256";
            return int.Parse(selected);
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
