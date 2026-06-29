using ModelCreator.UI.Services;
using System;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Training Configuration Page - Set hyperparameters
    /// </summary>
    public partial class TrainingConfigPage : Page
    {
        private string projectId;
        private string modality;
        private System.Collections.Generic.List<string> labels;
        private string modelId;
        private readonly IApiService? _apiService;

        public TrainingConfigPage(string projectId, string modality, System.Collections.Generic.List<string> labels, string modelId)
        {
            InitializeComponent();
            this.projectId = projectId;
            this.modality = modality;
            this.labels = labels;
            this.modelId = modelId;
            
            // Try to get API service
            _apiService = App.GetService<IApiService>();
            
            LoadConfiguration();
            CheckSystemResources();
        }

        private void LoadConfiguration()
        {
            // Set default values
            UpdateSummary();
        }

        private async void CheckSystemResources()
        {
            try
            {
                GPUInfoText.Text = "🔍 در حال بررسی GPU...";
                MemoryInfoText.Text = "🔍 در حال بررسی RAM...";
                
                if (_apiService == null)
                {
                    GPUInfoText.Text = "⚠️ خطا: Backend در دسترس نیست";
                    GPUInfoText.Foreground = (System.Windows.Media.Brush)FindResource("SecondaryBrush");
                    MemoryInfoText.Text = "لطفاً Backend را روی http://127.0.0.1:8181 اجرا کنید";
                    MixedPrecisionCheckBox.IsEnabled = false;
                    return;
                }
                
                var systemInfo = await _apiService.GetSystemInfoAsync();
                
                if (systemInfo != null && systemInfo.ContainsKey("gpu_available"))
                {
                    // Safe conversion from JSON values
                    bool gpuAvailable = GetBoolValue(systemInfo, "gpu_available");
                    int gpuCount = GetIntValue(systemInfo, "gpu_count");
                    
                    if (gpuAvailable && systemInfo.ContainsKey("gpu_name"))
                    {
                        string gpuName = GetStringValue(systemInfo, "gpu_name");
                        double gpuMemory = GetDoubleValue(systemInfo, "gpu_memory_total");
                        
                        GPUInfoText.Text = $"✅ GPU: {gpuName}";
                        GPUInfoText.Foreground = (System.Windows.Media.Brush)FindResource("AccentBrush");
                        
                        if (gpuMemory > 0)
                        {
                            MemoryInfoText.Text = $"💾 GPU Memory: {gpuMemory:F1} GB | RAM: موجود";
                        }
                        else
                        {
                            MemoryInfoText.Text = "💾 RAM: موجود";
                        }
                        
                        MixedPrecisionCheckBox.IsEnabled = true;
                        
                        MessageBox.Show(
                            $"GPU شناسایی شد! ✅\n\n" +
                            $"نام: {gpuName}\n" +
                            $"تعداد: {gpuCount}\n" +
                            $"حافظه: {gpuMemory:F1} GB\n\n" +
                            "آموزش با GPU سریع‌تر خواهد بود.",
                            "GPU موجود است",
                            MessageBoxButton.OK,
                            MessageBoxImage.Information
                        );
                    }
                    else
                    {
                        GPUInfoText.Text = "⚠️ GPU: موجود نیست (آموزش با CPU)";
                        GPUInfoText.Foreground = (System.Windows.Media.Brush)FindResource("SecondaryBrush");
                        MemoryInfoText.Text = "💾 RAM: موجود (آموزش کندتر خواهد بود)";
                        MixedPrecisionCheckBox.IsEnabled = false;
                        
                        MessageBox.Show(
                            "GPU یافت نشد ❌\n\n" +
                            "دلایل احتمالی:\n" +
                            "1. GPU NVIDIA ندارید\n" +
                            "2. درایورهای NVIDIA نصب نیستند\n" +
                            "3. PyTorch بدون CUDA نصب شده\n" +
                            "4. CUDA Toolkit نصب نیست\n\n" +
                            "آموزش با CPU انجام می‌شود (کندتر است)\n\n" +
                            "برای راهنمای نصب GPU_TROUBLESHOOTING_FA.md را ببینید.",
                            "GPU موجود نیست",
                            MessageBoxButton.OK,
                            MessageBoxImage.Warning
                        );
                    }
                }
                else
                {
                    GPUInfoText.Text = "⚠️ خطا: اطلاعات سیستم دریافت نشد";
                    MemoryInfoText.Text = "Backend ممکن است درست کار نکند";
                    MixedPrecisionCheckBox.IsEnabled = false;
                }
            }
            catch (Exception ex)
            {
                GPUInfoText.Text = "❌ خطا در بررسی GPU";
                GPUInfoText.Foreground = (System.Windows.Media.Brush)FindResource("SecondaryBrush");
                MemoryInfoText.Text = $"خطا: {ex.Message}";
                MixedPrecisionCheckBox.IsEnabled = false;
                
                MessageBox.Show(
                    $"خطا در دریافت اطلاعات سیستم:\n\n{ex.Message}\n\n" +
                    "لطفاً مطمئن شوید:\n" +
                    "1. Backend روی http://127.0.0.1:8181 در حال اجرا است\n" +
                    "2. PyTorch به درستی نصب شده است\n\n" +
                    "برای تست GPU در Backend:\n" +
                    "cd backend\n" +
                    "python test_gpu.py",
                    "خطا در بررسی GPU",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
        }
        
        // Helper methods for safe JSON conversion
        private bool GetBoolValue(System.Collections.Generic.Dictionary<string, object> dict, string key)
        {
            if (!dict.ContainsKey(key)) return false;
            var value = dict[key];
            if (value is bool b) return b;
            if (value is System.Text.Json.JsonElement je && je.ValueKind == System.Text.Json.JsonValueKind.True) return true;
            if (value is System.Text.Json.JsonElement je2 && je2.ValueKind == System.Text.Json.JsonValueKind.False) return false;
            return Convert.ToBoolean(value);
        }
        
        private int GetIntValue(System.Collections.Generic.Dictionary<string, object> dict, string key)
        {
            if (!dict.ContainsKey(key)) return 0;
            var value = dict[key];
            if (value is int i) return i;
            if (value is System.Text.Json.JsonElement je && je.ValueKind == System.Text.Json.JsonValueKind.Number)
                return je.GetInt32();
            return Convert.ToInt32(value);
        }
        
        private double GetDoubleValue(System.Collections.Generic.Dictionary<string, object> dict, string key)
        {
            if (!dict.ContainsKey(key)) return 0;
            var value = dict[key];
            if (value is double d) return d;
            if (value is System.Text.Json.JsonElement je && je.ValueKind == System.Text.Json.JsonValueKind.Number)
                return je.GetDouble();
            return Convert.ToDouble(value);
        }
        
        private string GetStringValue(System.Collections.Generic.Dictionary<string, object> dict, string key)
        {
            if (!dict.ContainsKey(key)) return "Unknown";
            var value = dict[key];
            if (value is string s) return s;
            if (value is System.Text.Json.JsonElement je && je.ValueKind == System.Text.Json.JsonValueKind.String)
                return je.GetString() ?? "Unknown";
            return value?.ToString() ?? "Unknown";
        }
        
        private class Logger
        {
            public void Info(string message)
            {
                System.Diagnostics.Debug.WriteLine($"[INFO] {message}");
            }
        }
        private static readonly Logger logger = new Logger();

        private void EpochsSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (EpochsTextBox != null)
            {
                EpochsTextBox.Text = ((int)EpochsSlider.Value).ToString();
                UpdateSummary();
            }
        }

        private void EpochsTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (int.TryParse(EpochsTextBox.Text, out int value))
            {
                if (value >= 10 && value <= 200)
                {
                    EpochsSlider.Value = value;
                }
            }
        }

        private void DropoutSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (DropoutTextBox != null)
            {
                DropoutTextBox.Text = DropoutSlider.Value.ToString("0.00");
            }
        }

        private void UpdateSummary()
        {
            if (SummaryEpochs == null) return;
            
            SummaryEpochs.Text = EpochsTextBox.Text;
            
            string batchSize = BatchSizeComboBox.SelectedIndex switch
            {
                0 => "8",
                1 => "16",
                2 => "32",
                3 => "64",
                4 => "128",
                _ => "32"
            };
            SummaryBatchSize.Text = batchSize;
            
            string lr = LearningRateComboBox.SelectedIndex switch
            {
                0 => "0.0001",
                1 => "0.0005",
                2 => "0.001",
                3 => "0.005",
                4 => "0.01",
                _ => "0.001"
            };
            SummaryLR.Text = lr;
            
            string optimizer = OptimizerComboBox.SelectedIndex switch
            {
                0 => "Adam",
                1 => "AdamW",
                2 => "SGD",
                3 => "RMSprop",
                _ => "Adam"
            };
            SummaryOptimizer.Text = optimizer;
            
            SummaryAugmentation.Text = DataAugmentationCheckBox.IsChecked == true ? "Enabled" : "Disabled";
            
            // Estimate training time
            int epochs = int.TryParse(EpochsTextBox.Text, out int e) ? e : 50;
            EstimatedTimeText.Text = EstimateTrainingTime(epochs, batchSize);
        }

        private string EstimateTrainingTime(int epochs, string batchSize)
        {
            // Very rough estimate
            int batchSizeInt = int.Parse(batchSize);
            double baseTime = 0.5; // minutes per epoch for batch size 32
            double scaleFactor = 32.0 / batchSizeInt;
            double totalMinutes = epochs * baseTime * scaleFactor;
            
            if (totalMinutes < 60)
            {
                return $"~{(int)totalMinutes}-{(int)(totalMinutes * 1.3)} minutes";
            }
            else
            {
                double hours = totalMinutes / 60.0;
                return $"~{hours:F1}-{(hours * 1.3):F1} hours";
            }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.GoBack();
        }

        private async void StartTraining_Click(object sender, RoutedEventArgs e)
        {
            // Validate splits
            if (!ValidateSplits())
            {
                MessageBox.Show("تقسیم‌بندی داده باید جمعاً 100% باشد!", "خطا در تقسیم‌بندی",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            
            try
            {
                // Disable button and show progress
                var button = sender as System.Windows.Controls.Button;
                if (button != null)
                {
                    button.IsEnabled = false;
                    button.Content = "⏳ در حال بررسی داده‌ها...";
                }
                
                // Check data stats before starting training
                if (_apiService != null)
                {
                    try
                    {
                        var dataStats = await _apiService.GetAsync<System.Collections.Generic.Dictionary<string, object>>(
                            $"/api/data/stats/{projectId}"
                        );
                        
                        if (dataStats != null)
                        {
                            bool readyForTraining = false;
                            if (dataStats.ContainsKey("ready_for_training"))
                            {
                                var value = dataStats["ready_for_training"];
                                if (value is System.Text.Json.JsonElement je)
                                {
                                    readyForTraining = je.GetBoolean();
                                }
                                else if (value is bool b)
                                {
                                    readyForTraining = b;
                                }
                            }
                            
                            int totalFiles = 0;
                            if (dataStats.ContainsKey("total_files"))
                            {
                                var value = dataStats["total_files"];
                                if (value is System.Text.Json.JsonElement je)
                                {
                                    totalFiles = je.GetInt32();
                                }
                                else if (value is int i)
                                {
                                    totalFiles = i;
                                }
                            }
                            
                            // Show warnings if any
                            if (dataStats.ContainsKey("warnings"))
                            {
                                var warnings = dataStats["warnings"];
                                if (warnings is System.Text.Json.JsonElement je && je.ValueKind == System.Text.Json.JsonValueKind.Array)
                                {
                                    var warningsList = System.Text.Json.JsonSerializer.Deserialize<System.Collections.Generic.List<string>>(
                                        je.GetRawText()
                                    );
                                    
                                    if (warningsList != null && warningsList.Count > 0)
                                    {
                                        var warningMessage = "⚠️ هشدارها:\n\n" + string.Join("\n", warningsList);
                                        
                                        if (!readyForTraining)
                                        {
                                            if (button != null)
                                            {
                                                button.IsEnabled = true;
                                                button.Content = "▶️ شروع آموزش";
                                            }
                                            
                                            MessageBox.Show(
                                                warningMessage + "\n\n❌ لطفاً ابتدا داده‌ها را آپلود کنید.",
                                                "داده کافی موجود نیست",
                                                MessageBoxButton.OK,
                                                MessageBoxImage.Warning
                                            );
                                            return;
                                        }
                                        else
                                        {
                                            // Show warnings but allow training to continue
                                            var result = MessageBox.Show(
                                                warningMessage + "\n\nآیا می‌خواهید ادامه دهید؟",
                                                "هشدار",
                                                MessageBoxButton.YesNo,
                                                MessageBoxImage.Warning
                                            );
                                            
                                            if (result != MessageBoxResult.Yes)
                                            {
                                                if (button != null)
                                                {
                                                    button.IsEnabled = true;
                                                    button.Content = "▶️ شروع آموزش";
                                                }
                                                return;
                                            }
                                        }
                                    }
                                }
                            }
                            
                            // Show data summary
                            if (totalFiles > 0 && readyForTraining)
                            {
                                MessageBox.Show(
                                    $"✅ آماده برای آموزش!\n\n" +
                                    $"تعداد کل تصاویر: {totalFiles}\n\n" +
                                    "آموزش شروع می‌شود...",
                                    "بررسی داده",
                                    MessageBoxButton.OK,
                                    MessageBoxImage.Information
                                );
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Warning: Could not check data stats: {ex.Message}");
                        // Continue anyway if stats check fails
                    }
                }
                
                if (button != null)
                {
                    button.Content = "⏳ در حال شروع آموزش...";
                }
                
                // Prepare training configuration
                var config = new System.Collections.Generic.Dictionary<string, object>
                {
                    ["epochs"] = int.Parse(EpochsTextBox.Text),
                    ["batch_size"] = GetBatchSize(),
                    ["learning_rate"] = GetLearningRate(),
                    ["optimizer"] = GetOptimizer(),
                    ["dropout"] = double.Parse(DropoutTextBox.Text),
                    ["weight_decay"] = GetWeightDecay(),
                    ["data_augmentation"] = DataAugmentationCheckBox.IsChecked == true,
                    ["early_stopping"] = EarlyStoppingCheckBox.IsChecked == true,
                    ["mixed_precision"] = MixedPrecisionCheckBox.IsChecked == true,
                    ["train_split"] = double.Parse(TrainSplitTextBox.Text) / 100.0,
                    ["val_split"] = double.Parse(ValSplitTextBox.Text) / 100.0,
                    ["test_split"] = double.Parse(TestSplitTextBox.Text) / 100.0,
                    ["model_id"] = modelId,
                    ["modality"] = modality
                };
                
                // Start training
                if (_apiService != null)
                {
                    var response = await _apiService.StartTrainingAsync(projectId, config);
                    
                    // Check if training started successfully
                    if (response != null && response.ContainsKey("message"))
                    {
                        // Give backend a moment to initialize WebSocket
                        await System.Threading.Tasks.Task.Delay(1000);
                        
                        // Navigate to training dashboard (pass project ID only, name will be "My Model")
                        NavigationService?.Navigate(new TrainingDashboardPage(projectId));
                    }
                    else
                    {
                        if (button != null)
                        {
                            button.IsEnabled = true;
                            button.Content = "▶️ شروع آموزش";
                        }
                        MessageBox.Show("خطا در دریافت پاسخ از سرور", "خطا",
                            MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }
                else
                {
                    if (button != null)
                    {
                        button.IsEnabled = true;
                        button.Content = "▶️ شروع آموزش";
                    }
                    MessageBox.Show("سرویس API در دسترس نیست", "خطا",
                        MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
            catch (Exception ex)
            {
                var button = sender as System.Windows.Controls.Button;
                if (button != null)
                {
                    button.IsEnabled = true;
                    button.Content = "▶️ شروع آموزش";
                }
                
                var errorMessage = "خطا در شروع آموزش:\n\n" + ex.Message + "\n\n";
                
                if (ex.Message.Contains("Unable to connect") || ex.Message.Contains("No connection"))
                {
                    errorMessage += "⚠️ Backend در دسترس نیست!\n\n" +
                                  "لطفاً مطمئن شوید Backend در حال اجرا است:\n" +
                                  "cd backend\n" +
                                  "python main.py";
                }
                else if (ex.Message.Contains("No images found") || ex.Message.Contains("Data directory not found"))
                {
                    errorMessage += "💡 راهنما:\n" +
                                  "1. به صفحه Data Upload برگردید\n" +
                                  "2. تصاویر خود را آپلود کنید\n" +
                                  "3. حداقل 10 تصویر برای هر کلاس نیاز است";
                }
                
                MessageBox.Show(errorMessage, "خطای آموزش",
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private bool ValidateSplits()
        {
            if (double.TryParse(TrainSplitTextBox.Text, out double train) &&
                double.TryParse(ValSplitTextBox.Text, out double val) &&
                double.TryParse(TestSplitTextBox.Text, out double test))
            {
                double sum = train + val + test;
                return Math.Abs(sum - 100.0) < 0.01;
            }
            return false;
        }

        private int GetBatchSize()
        {
            return BatchSizeComboBox.SelectedIndex switch
            {
                0 => 8,
                1 => 16,
                2 => 32,
                3 => 64,
                4 => 128,
                _ => 32
            };
        }

        private double GetLearningRate()
        {
            return LearningRateComboBox.SelectedIndex switch
            {
                0 => 0.0001,
                1 => 0.0005,
                2 => 0.001,
                3 => 0.005,
                4 => 0.01,
                _ => 0.001
            };
        }

        private string GetOptimizer()
        {
            return OptimizerComboBox.SelectedIndex switch
            {
                0 => "adam",
                1 => "adamw",
                2 => "sgd",
                3 => "rmsprop",
                _ => "adam"
            };
        }

        private double GetWeightDecay()
        {
            return WeightDecayComboBox.SelectedIndex switch
            {
                0 => 0.0,
                1 => 0.00001,
                2 => 0.0001,
                3 => 0.001,
                _ => 0.0001
            };
        }
    }
}

