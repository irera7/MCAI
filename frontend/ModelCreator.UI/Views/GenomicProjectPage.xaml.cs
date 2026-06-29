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
    /// صفحه ایجاد پروژه Genomic Sequence Analysis
    /// Complete implementation with API integration for DNA/RNA
    /// </summary>
    public partial class GenomicProjectPage : Page
    {
        private readonly HttpClient _httpClient;
        private string[]? _uploadedFastaFiles;
        private string? _projectId;

        public GenomicProjectPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient 
            { 
                BaseAddress = new Uri("http://127.0.0.1:8181"),
                Timeout = TimeSpan.FromMinutes(10)
            };
        }

        /// <summary>
        /// آپلود فایل‌های FASTA
        /// </summary>
        private async void UploadDataButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var dialog = new OpenFileDialog
                {
                    Title = "Select FASTA Files",
                    Filter = "FASTA Files (*.fasta;*.fa;*.fna;*.ffn;*.faa;*.frn)|*.fasta;*.fa;*.fna;*.ffn;*.faa;*.frn|All Files (*.*)|*.*",
                    Multiselect = true
                };

                if (dialog.ShowDialog() == true)
                {
                    _uploadedFastaFiles = dialog.FileNames;
                    
                    // نمایش وضعیت
                    DataStatusTextBlock.Text = $"📄 {_uploadedFastaFiles.Length} FASTA files selected";
                    DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Blue;

                    // آپلود به backend
                    var uploadButton = sender as Button;
                    if (uploadButton != null)
                    {
                        uploadButton.IsEnabled = false;
                        uploadButton.Content = "⏳ Uploading...";
                    }

                    var success = await UploadFastaFilesToBackend(_uploadedFastaFiles);

                    if (success)
                    {
                        DataStatusTextBlock.Text = $"✅ Uploaded {_uploadedFastaFiles.Length} FASTA files";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Green;

                        MessageBox.Show(
                            $"Successfully uploaded {_uploadedFastaFiles.Length} FASTA files!\n\n" +
                            "Supported formats: .fasta, .fa, .fna, .ffn\n" +
                            "Your sequences are ready for processing.",
                            "Upload Successful",
                            MessageBoxButton.OK,
                            MessageBoxImage.Information
                        );
                    }
                    else
                    {
                        DataStatusTextBlock.Text = "❌ Upload failed";
                        DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                        _uploadedFastaFiles = null;
                    }

                    if (uploadButton != null)
                    {
                        uploadButton.IsEnabled = true;
                        uploadButton.Content = "📁 Upload FASTA Files";
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error uploading FASTA files:\n\n{ex.Message}",
                    "Upload Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
                
                DataStatusTextBlock.Text = "❌ Error";
                DataStatusTextBlock.Foreground = System.Windows.Media.Brushes.Red;
                _uploadedFastaFiles = null;
            }
        }

        /// <summary>
        /// آپلود فایل‌های FASTA به backend
        /// </summary>
        private async Task<bool> UploadFastaFilesToBackend(string[] filePaths)
        {
            try
            {
                using var content = new MultipartFormDataContent();
                
                // تشخیص نوع sequence
                var sequenceType = (SequenceTypeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "DNA";
                string seqType = sequenceType.Contains("DNA") ? "dna" : "rna";
                
                content.Add(new StringContent(seqType), "sequence_type");
                content.Add(new StringContent("class1"), "class_name"); // فعلاً یک کلاس پیش‌فرض

                // اضافه کردن تمام فایل‌ها
                foreach (var filePath in filePaths)
                {
                    var fileContent = new ByteArrayContent(File.ReadAllBytes(filePath));
                    fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("text/plain");
                    content.Add(fileContent, "files", Path.GetFileName(filePath));
                }

                var response = await _httpClient.PostAsync("/api/genomic/upload", content);
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

                if (_uploadedFastaFiles == null || _uploadedFastaFiles.Length == 0)
                {
                    MessageBox.Show(
                        "Please upload FASTA files first",
                        "Validation Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Warning
                    );
                    return;
                }

                // تشخیص مدل
                string modelType = DNA_CNNRadio.IsChecked == true ? "dna_cnn" : "sequence_embedding";

                // دریافت پارامترها
                int sequenceLength = GetSequenceLength();
                string encodingType = GetEncodingType();
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

                var trainingStarted = await StartTraining(
                    _projectId, 
                    modelType, 
                    sequenceLength, 
                    encodingType, 
                    epochs, 
                    batchSize
                );

                if (trainingStarted)
                {
                    var seqType = (SequenceTypeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "DNA";
                    
                    MessageBox.Show(
                        $"✅ Genomic analysis project created!\n\n" +
                        $"Project: {ProjectNameTextBox.Text}\n" +
                        $"Sequence Type: {seqType}\n" +
                        $"Model: {modelType.ToUpper()}\n" +
                        $"Files: {_uploadedFastaFiles.Length}\n" +
                        $"Sequence Length: {sequenceLength}\n" +
                        $"Encoding: {encodingType}\n" +
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
                var seqType = (SequenceTypeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "DNA";
                
                var projectData = new
                {
                    name = ProjectNameTextBox.Text,
                    modality = "genomic",
                    sequence_type = seqType.Contains("DNA") ? "dna" : "rna",
                    num_files = _uploadedFastaFiles?.Length ?? 0
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
            string modelType, 
            int sequenceLength, 
            string encodingType, 
            int epochs, 
            int batchSize)
        {
            try
            {
                var trainingConfig = new
                {
                    project_id = projectId,
                    modality = "genomic",
                    model_id = modelType,
                    sequence_length = sequenceLength,
                    encoding_type = encodingType,
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

        private int GetSequenceLength()
        {
            var selected = (SequenceLengthComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "1000";
            return int.Parse(selected);
        }

        private string GetEncodingType()
        {
            var selected = (EncodingTypeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "One-hot";
            return selected.Contains("One-hot") ? "onehot" : "index";
        }

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
