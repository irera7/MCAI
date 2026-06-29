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
    /// صفحه ایجاد پروژه Medical Data Classification
    /// Complete implementation with API integration for MRI, ECG, EEG
    /// </summary>
    public partial class MedicalProjectPage : Page
    {
        private readonly HttpClient _httpClient;
        private string[]? _uploadedFiles;
        private string? _projectId;
        private string _currentDataType = "mri";

        public MedicalProjectPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient 
            { 
                BaseAddress = new Uri("http://127.0.0.1:8181"),
                Timeout = TimeSpan.FromMinutes(10)
            };
        }

        /// <summary>
        /// هندلر تغییر نوع داده
        /// </summary>
        private void DataTypeComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var selected = (DataTypeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "";

            if (selected.Contains("MRI"))
            {
                _currentDataType = "mri";
                MRI_CNNRadio.Visibility = Visibility.Visible;
                MRI_CNNRadio.IsChecked = true;
                ECG_CNNRadio.Visibility = Visibility.Collapsed;
            }
            else if (selected.Contains("ECG"))
            {
                _currentDataType = "ecg";
                MRI_CNNRadio.Visibility = Visibility.Collapsed;
                ECG_CNNRadio.Visibility = Visibility.Visible;
                ECG_CNNRadio.IsChecked = true;
            }
            else if (selected.Contains("EEG"))
            {
                _currentDataType = "eeg";
                MRI_CNNRadio.Visibility = Visibility.Collapsed;
                ECG_CNNRadio.Visibility = Visibility.Visible;
                ECG_CNNRadio.IsChecked = true;
            }
        }

        /// <summary>
        /// آپلود فایل‌های پزشکی
        /// </summary>
        private async void UploadDataButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                string filter;
                if (_currentDataType == "mri")
                {
                    filter = "DICOM Files (*.dcm;*.dicom)|*.dcm;*.dicom|NIfTI Files (*.nii;*.nii.gz)|*.nii;*.nii.gz|All Files (*.*)|*.*";
                }
                else // ECG or EEG
                {
                    filter = "Signal Files (*.csv;*.txt;*.dat)|*.csv;*.txt;*.dat|All Files (*.*)|*.*";
                }

                var dialog = new OpenFileDialog
                {
                    Title = $"Select {_currentDataType.ToUpper()} Files",
                    Filter = filter,
                    Multiselect = true
                };

                if (dialog.ShowDialog() == true)
                {
                    _uploadedFiles = dialog.FileNames;
                    
                    // نمایش وضعیت
                    DataStatusTextBlock.Text = $"📄 {_uploadedFiles.Length} files selected";
                    DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Blue;

                    // آپلود به backend
                    var uploadButton = sender as Button;
                    if (uploadButton != null)
                    {
                        uploadButton.IsEnabled = false;
                        uploadButton.Content = "⏳ Uploading...";
                    }

                    var success = await UploadMedicalFilesToBackend(_uploadedFiles);

                    if (success)
                    {
                        DataStatusTextBlock.Text = $"✅ Uploaded {_uploadedFiles.Length} {_currentDataType.ToUpper()} files";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Green;

                        string formatInfo = _currentDataType == "mri" 
                            ? "DICOM files (.dcm) or NIfTI files (.nii)" 
                            : "CSV or TXT files with signal data";

                        MessageBox.Show(
                            $"Successfully uploaded {_uploadedFiles.Length} medical files!\n\n" +
                            $"Data Type: {_currentDataType.ToUpper()}\n" +
                            $"Format: {formatInfo}\n\n" +
                            "Files are ready for training.",
                            "Upload Successful",
                            MessageBoxButton.OK,
                            MessageBoxImage.Information
                        );
                    }
                    else
                    {
                        DataStatusTextBlock.Text = "❌ Upload failed";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                        _uploadedFiles = null;
                    }

                    if (uploadButton != null)
                    {
                        uploadButton.IsEnabled = true;
                        uploadButton.Content = "📁 Upload Medical Files";
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error uploading medical files:\n\n{ex.Message}",
                    "Upload Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
                
                DataStatusTextBlock.Text = "❌ Error";
                DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                _uploadedFiles = null;
            }
        }

        /// <summary>
        /// آپلود فایل‌های medical به backend
        /// </summary>
        private async Task<bool> UploadMedicalFilesToBackend(string[] filePaths)
        {
            try
            {
                using var content = new MultipartFormDataContent();
                
                // اضافه کردن data type
                content.Add(new StringContent(_currentDataType), "data_type");
                content.Add(new StringContent("class1"), "class_name"); // فعلاً یک کلاس پیش‌فرض

                // اضافه کردن تمام فایل‌ها
                foreach (var filePath in filePaths)
                {
                    var fileContent = new ByteArrayContent(File.ReadAllBytes(filePath));
                    fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/octet-stream");
                    content.Add(fileContent, "files", Path.GetFileName(filePath));
                }

                var response = await _httpClient.PostAsync("/api/medical/upload", content);
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// شروع training
        /// </summary>
        private async void StartTrainingButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // اعتبارسنجی
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

                if (_uploadedFiles == null || _uploadedFiles.Length == 0)
                {
                    MessageBox.Show(
                        "Please upload medical data files first",
                        "Validation Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Warning
                    );
                    return;
                }

                // تشخیص مدل
                string modelType = _currentDataType == "mri" ? "mri_cnn" : "ecg_cnn";

                // دریافت پارامترها
                int epochs = GetEpochs();
                int batchSize = GetBatchSize();

                // Disable button
                var button = sender as Button;
                if (button != null)
                {
                    button.IsEnabled = false;
                    button.Content = "⏳ Creating Project...";
                }

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
                if (button != null)
                {
                    button.Content = "⏳ Starting Training...";
                }

                var trainingStarted = await StartTraining(_projectId, modelType, epochs, batchSize);

                if (trainingStarted)
                {
                    MessageBox.Show(
                        $"✅ Medical classification project created!\n\n" +
                        $"Project: {ProjectNameTextBox.Text}\n" +
                        $"Data Type: {_currentDataType.ToUpper()}\n" +
                        $"Model: {modelType.ToUpper()}\n" +
                        $"Files: {_uploadedFiles.Length}\n" +
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
                    $"Error starting training:\n\n{ex.Message}\n\n" +
                    "Make sure the backend server is running.",
                    "Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
            finally
            {
                var button = sender as Button;
                if (button != null)
                {
                    button.IsEnabled = true;
                    button.Content = "Start Training";
                }
            }
        }

        /// <summary>
        /// ایجاد پروژه
        /// </summary>
        private async Task<string?> CreateProject()
        {
            try
            {
                var projectData = new
                {
                    name = ProjectNameTextBox.Text,
                    modality = "medical",
                    data_type = _currentDataType,
                    num_files = _uploadedFiles?.Length ?? 0
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
        private async Task<bool> StartTraining(string projectId, string modelType, int epochs, int batchSize)
        {
            try
            {
                var trainingConfig = new
                {
                    project_id = projectId,
                    modality = "medical",
                    model_id = modelType,
                    data_type = _currentDataType,
                    epochs = epochs,
                    batch_size = batchSize,
                    learning_rate = 0.001
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

        private int GetEpochs()
        {
            var selected = (EpochsComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "50";
            return int.Parse(selected);
        }

        private int GetBatchSize()
        {
            var selected = (BatchSizeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "32";
            return int.Parse(selected);
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
