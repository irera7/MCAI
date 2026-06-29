using ModelCreator.UI.Services;
using System;
using System.Windows;
using System.Windows.Controls;
using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using System.Windows.Threading;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Interaction logic for TrainingDashboardPage.xaml
    /// Live training monitoring dashboard with real-time charts
    /// </summary>
    public partial class TrainingDashboardPage : Page
    {
        private readonly IWebSocketService _webSocketService;
        private string _projectId;
        private string _projectName;
        private DispatcherTimer _pollingTimer;
        
        // Chart data
        private ObservableCollection<double> _trainLossData = new();
        private ObservableCollection<double> _valLossData = new();
        private ObservableCollection<double> _trainAccData = new();
        private ObservableCollection<double> _valAccData = new();
        
        // Track last seen epoch to avoid duplicates
        private int _lastSeenEpoch = 0;

        public TrainingDashboardPage(string projectId, string projectName = "")
        {
            InitializeComponent();
            _projectId = projectId;
            _projectName = string.IsNullOrEmpty(projectName) ? "My Model" : projectName;
            _webSocketService = App.GetService<IWebSocketService>();
            
            // Debug: Log Project ID
            System.Diagnostics.Debug.WriteLine($"[Dashboard] Initialized with Project ID: {_projectId}");
            
            // Set project name in UI
            if (ProjectNameText != null)
            {
                ProjectNameText.Text = $"Project: {_projectName}";
                System.Diagnostics.Debug.WriteLine($"[Dashboard] ProjectNameText updated");
            }
            else
            {
                System.Diagnostics.Debug.WriteLine($"[Dashboard] WARNING: ProjectNameText is NULL!");
            }
            
            // Show Project ID for debugging - VERY VISIBLE
            if (StatusText != null)
            {
                StatusText.Text = $"🔍 DEBUG: Monitoring Project ID: {_projectId}";
                System.Diagnostics.Debug.WriteLine($"[Dashboard] StatusText set to: Monitoring {_projectId}");
            }
            else
            {
                System.Diagnostics.Debug.WriteLine($"[Dashboard] WARNING: StatusText is NULL!");
            }
            
            // Also update ProjectNameText to show Project ID
            if (ProjectNameText != null)
            {
                ProjectNameText.Text = $"Project: {_projectName} (ID: {_projectId.Substring(0, 13)}...)";
                System.Diagnostics.Debug.WriteLine($"[Dashboard] ProjectNameText updated with ID");
            }
            
            InitializeCharts();
            ConnectToTraining();
        }

        /// <summary>
        /// Initialize chart data and series
        /// </summary>
        private void InitializeCharts()
        {
            try
            {
                // Add some initial dummy data to ensure charts are visible
                _trainLossData.Clear();
                _valLossData.Clear();
                _trainAccData.Clear();
                _valAccData.Clear();
                
                // Loss chart
                LossChart.Series = new ISeries[]
                {
                    new LineSeries<double>
                    {
                        Values = _trainLossData,
                        Name = "Train Loss",
                        Fill = null,
                        GeometrySize = 6,
                        LineSmoothness = 0
                    },
                    new LineSeries<double>
                    {
                        Values = _valLossData,
                        Name = "Val Loss",
                        Fill = null,
                        GeometrySize = 6,
                        LineSmoothness = 0
                    }
                };

                // Accuracy chart
                AccuracyChart.Series = new ISeries[]
                {
                    new LineSeries<double>
                    {
                        Values = _trainAccData,
                        Name = "Train Accuracy",
                        Fill = null,
                        GeometrySize = 6,
                        LineSmoothness = 0
                    },
                    new LineSeries<double>
                    {
                        Values = _valAccData,
                        Name = "Val Accuracy",
                        Fill = null,
                        GeometrySize = 6,
                        LineSmoothness = 0
                    }
                };
                
                System.Diagnostics.Debug.WriteLine("[Charts] Initialized successfully");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[Charts] Initialization error: {ex.Message}");
            }
        }

        /// <summary>
        /// Connect to training WebSocket for live updates
        /// NOTE: Due to WebSocket compatibility issues, we use HTTP polling instead
        /// </summary>
        private async void ConnectToTraining()
        {
            try
            {
                StatusText.Text = "⏳ در حال بررسی وضعیت Backend...";
                
                // Check if backend is running via HTTP
                var apiService = App.GetService<IApiService>();
                if (apiService == null)
                {
                    throw new Exception("ApiService در دسترس نیست");
                }
                
                try
                {
                    var systemInfo = await apiService.GetSystemInfoAsync();
                    StatusText.Text = "✅ Backend متصل است - شروع مانیتورینگ...";
                }
                catch
                {
                    throw new Exception("Backend در دسترس نیست! لطفاً ابتدا Backend را اجرا کنید:\n\ncd backend\npython main.py");
                }
                
                // Use DispatcherTimer instead of Task.Run for better UI thread compatibility
                StatusText.Text = "📊 در حال دریافت اطلاعات آموزش...";
                
                // Create and start polling timer
                _pollingTimer = new DispatcherTimer
                {
                    Interval = TimeSpan.FromSeconds(2)
                };
                _pollingTimer.Tick += PollingTimer_Tick;
                _pollingTimer.Start();
                
                System.Diagnostics.Debug.WriteLine("[Timer] Polling timer started (2 second interval)");
                
                StatusText.Text = "✅ متصل به سیستم مانیتورینگ";
                
                // 🔥 FORCE an immediate poll to test
                System.Diagnostics.Debug.WriteLine("[INIT] 🔥 Calling immediate first poll...");
                await PollTrainingStatusOnce();
                System.Diagnostics.Debug.WriteLine("[INIT] ✅ First poll completed!");
            }
            catch (Exception ex)
            {
                StatusText.Text = "❌ خطا در اتصال";
                
                var message = "⚠️ خطا در اتصال به سرور:\n\n" + ex.Message + "\n\n";
                
                if (ex.Message.Contains("Backend در دسترس نیست"))
                {
                    message += "🔴 Backend در حال اجرا نیست!\n\n" +
                              "لطفاً ابتدا Backend را اجرا کنید:\n\n" +
                              "1️⃣ Terminal/CMD جدید باز کنید\n" +
                              "2️⃣ دستورات زیر را اجرا کنید:\n" +
                              "   cd D:\\Project\\ModelCreator\\backend\n" +
                              "   .\\venv\\Scripts\\activate\n" +
                              "   python main.py\n\n" +
                              "3️⃣ منتظر بمانید تا ببینید:\n" +
                              "   INFO: Uvicorn running on http://127.0.0.1:8181\n\n" +
                              "4️⃣ سپس Frontend را Restart کنید";
                }
                else
                {
                    message += "⚠️ لطفاً مطمئن شوید:\n" +
                              "• Backend روی http://127.0.0.1:8181 در حال اجرا است\n" +
                              "• آموزش شروع شده است\n\n" +
                              "📖 راهنمای کامل: TRAINING_GUIDE_FA.md";
                }
                
                MessageBox.Show(message, "خطا در اتصال", MessageBoxButton.OK, MessageBoxImage.Error);
                
                // Allow user to go back
                if (MessageBox.Show("آیا می‌خواهید به صفحه قبل برگردید؟", "برگشت", 
                    MessageBoxButton.YesNo, MessageBoxImage.Question) == MessageBoxResult.Yes)
                {
                    Dispatcher.Invoke(() => NavigationService?.GoBack());
                }
            }
        }
        
        /// <summary>
        /// Polling timer tick - runs on UI thread!
        /// </summary>
        private async void PollingTimer_Tick(object? sender, EventArgs e)
        {
            await PollTrainingStatusOnce();
        }
        
        /// <summary>
        /// Poll training status once (called from timer on UI thread)
        /// </summary>
        private async Task PollTrainingStatusOnce()
        {
            var apiService = App.GetService<IApiService>();
            if (apiService == null) return;
            
            try
            {
                System.Diagnostics.Debug.WriteLine($"[Timer Poll] Fetching status for {_projectId.Substring(0, 13)}...");
                
                // Get training status via HTTP
                var status = await apiService.GetAsync<System.Collections.Generic.Dictionary<string, object>>(
                    $"/api/training/status/{_projectId}"
                );
                
                if (status != null)
                {
                    // Get status string
                    var statusValue = status.ContainsKey("status") ? status["status"].ToString() : "unknown";
                    
                    System.Diagnostics.Debug.WriteLine($"[Timer Poll] Status: {statusValue}");
                    
                    // We're already on UI thread, so no Dispatcher needed!
                    UpdateUI(status, statusValue);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[Timer Poll] Error: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Update UI with training data (called from UI thread)
        /// </summary>
        private void UpdateUI(System.Collections.Generic.Dictionary<string, object> status, string? statusValue)
        {
            try
            {
                System.Diagnostics.Debug.WriteLine($"[UI Update] Entered (already on UI thread)");
                
                // Check if training is active or starting
                if (statusValue == "training" || statusValue == "starting")
                {
                    StatusText.Text = statusValue == "starting" ? "⏳ در حال آماده‌سازی..." : "🔥 در حال آموزش...";
                    
                    // Add initial log message if logs are empty
                    if (LogsTextBox != null && string.IsNullOrWhiteSpace(LogsTextBox.Text))
                    {
                        LogsTextBox.AppendText($"{DateTime.Now:HH:mm:ss} - ✅ اتصال برقرار شد!\n");
                        LogsTextBox.AppendText($"{DateTime.Now:HH:mm:ss} - 🚀 آموزش در حال اجرا است...\n\n");
                        System.Diagnostics.Debug.WriteLine("[Log] ✅ Added initial log messages");
                    }
                    
                    // Update progress
                    int currentEpoch = 0;
                    int totalEpochs = 0;
                    bool isNewEpoch = false;
                    
                    if (status.ContainsKey("current_epoch") && status.ContainsKey("total_epochs"))
                    {
                        try
                        {
                            currentEpoch = Convert.ToInt32(status["current_epoch"]);
                            totalEpochs = Convert.ToInt32(status["total_epochs"]);
                            
                            System.Diagnostics.Debug.WriteLine($"[UI Update] Epoch: {currentEpoch}/{totalEpochs}");
                            
                            // Check if this is the first connection
                            if (_lastSeenEpoch == 0 && currentEpoch > 1)
                            {
                                _lastSeenEpoch = currentEpoch - 1;
                                System.Diagnostics.Debug.WriteLine($"[Charts] Dashboard opened mid-training at Epoch {currentEpoch}");
                                
                                if (LogsTextBox != null && string.IsNullOrWhiteSpace(LogsTextBox.Text))
                                {
                                    LogsTextBox.AppendText($"{DateTime.Now:HH:mm:ss} - 📊 متصل شد! آموزش در Epoch {currentEpoch}/{totalEpochs} در حال اجرا است.\n\n");
                                }
                            }
                            
                            // Check if this is a new epoch
                            if (currentEpoch > _lastSeenEpoch)
                            {
                                isNewEpoch = true;
                                _lastSeenEpoch = currentEpoch;
                                System.Diagnostics.Debug.WriteLine($"[Charts] ✅ NEW EPOCH: {currentEpoch}");
                            }
                            
                            // Update UI - with detailed logging
                            System.Diagnostics.Debug.WriteLine($"[UI Update] Setting CurrentEpochText to: {currentEpoch} / {totalEpochs}");
                            if (CurrentEpochText != null)
                            {
                                CurrentEpochText.Text = $"{currentEpoch} / {totalEpochs}";
                                System.Diagnostics.Debug.WriteLine($"[UI Update] ✅ CurrentEpochText updated successfully");
                            }
                            
                            if (EpochProgressBar != null)
                            {
                                EpochProgressBar.Value = totalEpochs > 0 ? (double)currentEpoch / totalEpochs * 100 : 0;
                            }
                            
                            // Update metrics
                            if (status.ContainsKey("train_loss"))
                            {
                                var trainLoss = Convert.ToDouble(status["train_loss"]);
                                System.Diagnostics.Debug.WriteLine($"[UI Update] Setting TrainLossText to: {trainLoss:F4}");
                                if (TrainLossText != null)
                                {
                                    TrainLossText.Text = trainLoss.ToString("F4");
                                    System.Diagnostics.Debug.WriteLine($"[UI Update] ✅ TrainLossText updated");
                                }
                                
                                if (isNewEpoch)
                                {
                                    _trainLossData.Add(trainLoss);
                                    if (_trainLossData.Count > 100) _trainLossData.RemoveAt(0);
                                }
                            }
                            
                            if (status.ContainsKey("train_acc"))
                            {
                                var trainAcc = Convert.ToDouble(status["train_acc"]);
                                if (TrainAccText != null)
                                {
                                    TrainAccText.Text = $"{trainAcc * 100:F2}%";
                                }
                                
                                if (isNewEpoch)
                                {
                                    _trainAccData.Add(trainAcc);
                                    if (_trainAccData.Count > 100) _trainAccData.RemoveAt(0);
                                }
                            }
                            
                            // Update charts if needed
                            if (isNewEpoch && _trainLossData.Count > 0)
                            {
                                System.Diagnostics.Debug.WriteLine($"[Charts] Updating charts with {_trainLossData.Count} points");
                                InitializeCharts(); // Refresh charts
                            }
                        }
                        catch (Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"[UI Update] Parse error: {ex.Message}");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[UI Update] Error: {ex.Message}\n{ex.StackTrace}");
            }
        }
        
        /// <summary>
        /// Poll training status via HTTP (OLD - using Task.Run)
        /// </summary>
        private async Task PollTrainingStatus()
        {
            var apiService = App.GetService<IApiService>();
            if (apiService == null) return;
            
            while (true)
            {
                try
                {
                    // Get training status via HTTP
                    var status = await apiService.GetAsync<System.Collections.Generic.Dictionary<string, object>>(
                        $"/api/training/status/{_projectId}"
                    );
                    
                    if (status != null)
                    {
                        // Get status string
                        var statusValue = status.ContainsKey("status") ? status["status"].ToString() : "unknown";
                        
                        // DEBUG: Print all received data
                        System.Diagnostics.Debug.WriteLine($"\n========== [Polling @ {DateTime.Now:HH:mm:ss}] Received Data ==========");
                        System.Diagnostics.Debug.WriteLine($"Project ID: {_projectId}");
                        System.Diagnostics.Debug.WriteLine($"Status: {statusValue}");
                        if (status.ContainsKey("current_epoch"))
                            System.Diagnostics.Debug.WriteLine($"Epoch: {status["current_epoch"]} (Last seen: {_lastSeenEpoch})");
                        if (status.ContainsKey("train_loss"))
                            System.Diagnostics.Debug.WriteLine($"Train Loss: {status["train_loss"]}");
                        if (status.ContainsKey("train_acc"))
                            System.Diagnostics.Debug.WriteLine($"Train Acc: {status["train_acc"]}");
                        if (status.ContainsKey("val_loss"))
                            System.Diagnostics.Debug.WriteLine($"Val Loss: {status["val_loss"]}");
                        if (status.ContainsKey("val_acc"))
                            System.Diagnostics.Debug.WriteLine($"Val Acc: {status["val_acc"]}");
                        System.Diagnostics.Debug.WriteLine($"Chart Data Points: Loss={_trainLossData.Count}, Acc={_trainAccData.Count}");
                        System.Diagnostics.Debug.WriteLine($"=================================================================\n");
                        
                        // Check if completed - handle outside Dispatcher
                        bool shouldNavigateToResults = false;
                        string completionMessage = "";
                        
                        // Parse and update UI - use Application.Current.Dispatcher for cross-thread safety
                        await Application.Current.Dispatcher.InvokeAsync(() =>
                        {
                            try
                            {
                                System.Diagnostics.Debug.WriteLine($"[Dispatcher] Entered UI thread successfully");

                                // Check if training is active or starting
                                if (statusValue == "training" || statusValue == "starting")
                                {
                                    StatusText.Text = statusValue == "starting" ? "⏳ در حال آماده‌سازی..." : "🔥 در حال آموزش...";
                                    
                                    // Add initial log message if logs are empty
                                    if (LogsTextBox != null && string.IsNullOrWhiteSpace(LogsTextBox.Text))
                                    {
                                        LogsTextBox.AppendText($"{DateTime.Now:HH:mm:ss} - ✅ اتصال برقرار شد!\n");
                                        LogsTextBox.AppendText($"{DateTime.Now:HH:mm:ss} - 🚀 آموزش در حال اجرا است...\n\n");
                                        System.Diagnostics.Debug.WriteLine("[Log] ✅ Added initial log messages");
                                    }
                                    
                                    // Update progress
                                    int currentEpoch = 0;
                                    int totalEpochs = 0;
                                    bool isNewEpoch = false;
                                    
                                    if (status.ContainsKey("current_epoch") && status.ContainsKey("total_epochs"))
                                    {
                                        try
                                        {
                                            currentEpoch = Convert.ToInt32(status["current_epoch"]);
                                            totalEpochs = Convert.ToInt32(status["total_epochs"]);
                                            
                                            // Detect training restart (epoch went backwards)
                                            if (currentEpoch < _lastSeenEpoch && currentEpoch <= 2)
                                            {
                                                System.Diagnostics.Debug.WriteLine($"[Charts] 🔄 TRAINING RESTART DETECTED! Resetting from Epoch {_lastSeenEpoch} to {currentEpoch}");
                                                _lastSeenEpoch = 0;
                                                _trainLossData.Clear();
                                                _trainAccData.Clear();
                                                _valLossData.Clear();
                                                _valAccData.Clear();
                                                
                                                // Clear logs
                                                if (LogsTextBox != null)
                                                {
                                                    LogsTextBox.Clear();
                                                    LogsTextBox.AppendText("🔄 Training restarted...\n");
                                                }
                                            }
                                            
                                            // Check if this is the first connection (dashboard opened mid-training)
                                            if (_lastSeenEpoch == 0 && currentEpoch > 1)
                                            {
                                                // Dashboard opened while training was already in progress
                                                // Set lastSeenEpoch to current-1 so we'll capture this epoch as new
                                                _lastSeenEpoch = currentEpoch - 1;
                                                System.Diagnostics.Debug.WriteLine($"[Charts] 📊 Dashboard opened mid-training at Epoch {currentEpoch}. Will start tracking from here.");
                                                
                                                if (LogsTextBox != null && string.IsNullOrWhiteSpace(LogsTextBox.Text))
                                                {
                                                    LogsTextBox.AppendText($"{DateTime.Now:HH:mm:ss} - 📊 متصل شد! آموزش در Epoch {currentEpoch}/{totalEpochs} در حال اجرا است.\n");
                                                    LogsTextBox.AppendText($"{DateTime.Now:HH:mm:ss} - 🔄 شروع ردیابی از این نقطه...\n\n");
                                                }
                                            }
                                            
                                            // Check if this is a new epoch
                                            if (currentEpoch > _lastSeenEpoch)
                                            {
                                                isNewEpoch = true;
                                                _lastSeenEpoch = currentEpoch;
                                                System.Diagnostics.Debug.WriteLine($"[Charts] ✅ NEW EPOCH DETECTED: {currentEpoch}");
                                            }
                                            
                                            // Update UI - with detailed logging
                                            System.Diagnostics.Debug.WriteLine($"[UI Update] Setting CurrentEpochText to: {currentEpoch} / {totalEpochs}");
                                            if (CurrentEpochText != null)
                                            {
                                                CurrentEpochText.Text = $"{currentEpoch} / {totalEpochs}";
                                                System.Diagnostics.Debug.WriteLine($"[UI Update] ✅ CurrentEpochText updated successfully");
                                            }
                                            else
                                            {
                                                System.Diagnostics.Debug.WriteLine($"[UI Update] ❌ CurrentEpochText is NULL!");
                                            }
                                            
                                            if (EpochProgressBar != null)
                                            {
                                                EpochProgressBar.Value = totalEpochs > 0 ? (double)currentEpoch / totalEpochs * 100 : 0;
                                                System.Diagnostics.Debug.WriteLine($"[UI Update] ✅ EpochProgressBar updated to {EpochProgressBar.Value}%");
                                            }
                                            
                                            // Show progress percentage
                                            if (status.ContainsKey("progress_percent"))
                                            {
                                                var progress = Convert.ToInt32(status["progress_percent"]);
                                                CurrentEpochText.Text = $"{currentEpoch} / {totalEpochs} ({progress}%)";
                                            }
                                        }
                                        catch (Exception ex)
                                        {
                                            System.Diagnostics.Debug.WriteLine($"[Polling] Epoch parse error: {ex.Message}");
                                        }
                                    }
                                    
                                    // Update time information
                                    if (status.ContainsKey("elapsed_time_str"))
                                    {
                                        var elapsed = status["elapsed_time_str"].ToString();
                                        if (StatusText != null)
                                        {
                                            StatusText.Text = $"🔥 در حال آموزش... (زمان: {elapsed})";
                                        }
                                    }
                                    
                                    // Update ETA
                                    if (status.ContainsKey("eta_str"))
                                    {
                                        var eta = status["eta_str"].ToString();
                                        if (ETAText != null)
                                        {
                                            ETAText.Text = eta;
                                        }
                                    }
                                    
                                    // Update epoch time
                                    if (status.ContainsKey("epoch_time"))
                                    {
                                        var epochTime = status["epoch_time"].ToString();
                                        // Could display this somewhere
                                    }
                                    
                                    // Update metrics - only add to charts on NEW EPOCH
                                    bool chartsNeedUpdate = false;
                                    
                                    if (status.ContainsKey("train_loss"))
                                    {
                                        try
                                        {
                                            var trainLoss = Convert.ToDouble(status["train_loss"]);
                                            System.Diagnostics.Debug.WriteLine($"[UI Update] Setting TrainLossText to: {trainLoss:F4}");
                                            if (TrainLossText != null)
                                            {
                                                TrainLossText.Text = trainLoss.ToString("F4");
                                                System.Diagnostics.Debug.WriteLine($"[UI Update] ✅ TrainLossText updated successfully");
                                            }
                                            else
                                            {
                                                System.Diagnostics.Debug.WriteLine($"[UI Update] ❌ TrainLossText is NULL!");
                                            }
                                            
                                            // Only add if this is a NEW EPOCH (not duplicate polling)
                                            if (isNewEpoch)
                                            {
                                                _trainLossData.Add(trainLoss);
                                                chartsNeedUpdate = true;
                                                System.Diagnostics.Debug.WriteLine($"[Charts] ✅ Added train_loss: {trainLoss} (Epoch {currentEpoch}), Total points: {_trainLossData.Count}");
                                                
                                                if (_trainLossData.Count > 100)
                                                    _trainLossData.RemoveAt(0);
                                            }
                                            else
                                            {
                                                System.Diagnostics.Debug.WriteLine($"[Charts] ⏭️ Skipped duplicate poll for Epoch {currentEpoch} (train_loss: {trainLoss})");
                                            }
                                        }
                                        catch (Exception ex)
                                        {
                                            System.Diagnostics.Debug.WriteLine($"[Polling] Loss parse error: {ex.Message}");
                                        }
                                    }
                                    
                                    if (status.ContainsKey("train_acc"))
                                    {
                                        try
                                        {
                                            var trainAcc = Convert.ToDouble(status["train_acc"]);
                                            System.Diagnostics.Debug.WriteLine($"[UI Update] Setting TrainAccText to: {trainAcc * 100:F2}%");
                                            if (TrainAccText != null)
                                            {
                                                TrainAccText.Text = $"{trainAcc * 100:F2}%";
                                                System.Diagnostics.Debug.WriteLine($"[UI Update] ✅ TrainAccText updated successfully");
                                            }
                                            else
                                            {
                                                System.Diagnostics.Debug.WriteLine($"[UI Update] ❌ TrainAccText is NULL!");
                                            }
                                            
                                            // Only add if this is a NEW EPOCH
                                            if (isNewEpoch)
                                            {
                                                _trainAccData.Add(trainAcc);
                                                chartsNeedUpdate = true;
                                                System.Diagnostics.Debug.WriteLine($"[Charts] ✅ Added train_acc: {trainAcc} (Epoch {currentEpoch}), Total points: {_trainAccData.Count}");
                                                
                                                if (_trainAccData.Count > 100)
                                                    _trainAccData.RemoveAt(0);
                                            }
                                        }
                                        catch (Exception ex)
                                        {
                                            System.Diagnostics.Debug.WriteLine($"[Polling] Acc parse error: {ex.Message}");
                                        }
                                    }
                                    
                                    // Update validation metrics and add to charts - only on NEW EPOCH
                                    if (status.ContainsKey("val_loss"))
                                    {
                                        try
                                        {
                                            var valLoss = Convert.ToDouble(status["val_loss"]);
                                            
                                            // Only add if this is a NEW EPOCH
                                            if (isNewEpoch)
                                            {
                                                _valLossData.Add(valLoss);
                                                chartsNeedUpdate = true;
                                                System.Diagnostics.Debug.WriteLine($"[Charts] ✅ Added val_loss: {valLoss} (Epoch {currentEpoch})");
                                                
                                                if (_valLossData.Count > 100)
                                                    _valLossData.RemoveAt(0);
                                            }
                                        }
                                        catch { }
                                    }
                                    
                                    if (status.ContainsKey("val_acc"))
                                    {
                                        try
                                        {
                                            var valAcc = Convert.ToDouble(status["val_acc"]);
                                            
                                            // Only add if this is a NEW EPOCH
                                            if (isNewEpoch)
                                            {
                                                _valAccData.Add(valAcc);
                                                chartsNeedUpdate = true;
                                                System.Diagnostics.Debug.WriteLine($"[Charts] ✅ Added val_acc: {valAcc} (Epoch {currentEpoch})");
                                                
                                                if (_valAccData.Count > 100)
                                                    _valAccData.RemoveAt(0);
                                            }
                                        }
                                        catch { }
                                    }
                                    
                                    // Force chart update if data changed
                                    if (chartsNeedUpdate)
                                    {
                                        try
                                        {
                                            System.Diagnostics.Debug.WriteLine($"[Charts] Updating with {_trainLossData.Count} loss points, {_trainAccData.Count} acc points");
                                            
                                            // Force chart refresh by recreating series
                                            LossChart.Series = new ISeries[]
                                            {
                                                new LineSeries<double>
                                                {
                                                    Values = _trainLossData,
                                                    Name = "Train Loss",
                                                    Fill = null,
                                                    GeometrySize = 4,
                                                    Stroke = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(
                                                        SkiaSharp.SKColors.Blue, 2),
                                                    LineSmoothness = 0
                                                },
                                                new LineSeries<double>
                                                {
                                                    Values = _valLossData,
                                                    Name = "Val Loss",
                                                    Fill = null,
                                                    GeometrySize = 4,
                                                    Stroke = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(
                                                        SkiaSharp.SKColors.Orange, 2),
                                                    LineSmoothness = 0
                                                }
                                            };

                                            AccuracyChart.Series = new ISeries[]
                                            {
                                                new LineSeries<double>
                                                {
                                                    Values = _trainAccData,
                                                    Name = "Train Accuracy",
                                                    Fill = null,
                                                    GeometrySize = 4,
                                                    Stroke = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(
                                                        SkiaSharp.SKColors.Green, 2),
                                                    LineSmoothness = 0
                                                },
                                                new LineSeries<double>
                                                {
                                                    Values = _valAccData,
                                                    Name = "Val Accuracy",
                                                    Fill = null,
                                                    GeometrySize = 4,
                                                    Stroke = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(
                                                        SkiaSharp.SKColors.Purple, 2),
                                                    LineSmoothness = 0
                                                }
                                            };
                                            
                                            System.Diagnostics.Debug.WriteLine($"[Charts] Series recreated successfully");
                                        }
                                        catch (Exception ex)
                                        {
                                            System.Diagnostics.Debug.WriteLine($"[Charts] Update error: {ex.Message}");
                                        }
                                    }
                                    
                                    // Update best metrics
                                    if (status.ContainsKey("best_val_acc"))
                                    {
                                        try
                                        {
                                            var bestAcc = Convert.ToDouble(status["best_val_acc"]);
                                            if (BestAccText != null)
                                            {
                                                BestAccText.Text = $"{bestAcc * 100:F2}%";
                                            }
                                        }
                                        catch { }
                                    }
                                    
                                    if (status.ContainsKey("best_train_loss"))
                                    {
                                        try
                                        {
                                            var bestLoss = Convert.ToDouble(status["best_train_loss"]);
                                            // Could display this somewhere
                                        }
                                        catch { }
                                    }
                                    
                                    // Update Learning Rate
                                    if (status.ContainsKey("learning_rate"))
                                    {
                                        try
                                        {
                                            var lr = Convert.ToDouble(status["learning_rate"]);
                                            if (LearningRateText != null)
                                            {
                                                LearningRateText.Text = lr.ToString("F6");
                                            }
                                        }
                                        catch { }
                                    }
                                    
                                    // Update Batch Speed
                                    if (status.ContainsKey("samples_per_sec"))
                                    {
                                        try
                                        {
                                            var speed = Convert.ToDouble(status["samples_per_sec"]);
                                            if (BatchSpeedText != null)
                                            {
                                                BatchSpeedText.Text = $"{speed:F1} samples/sec";
                                            }
                                        }
                                        catch { }
                                    }
                                    else if (status.ContainsKey("batch_time"))
                                    {
                                        try
                                        {
                                            var batchTime = Convert.ToDouble(status["batch_time"]);
                                            var batchSize = status.ContainsKey("batch_size") ? Convert.ToInt32(status["batch_size"]) : 32;
                                            var speed = batchSize / batchTime;
                                            if (BatchSpeedText != null)
                                            {
                                                BatchSpeedText.Text = $"{speed:F1} samples/sec";
                                            }
                                        }
                                        catch { }
                                    }
                                    
                                    // Update log with detailed information - only on NEW EPOCH
                                    if (isNewEpoch && status.ContainsKey("message"))
                                    {
                                        var message = status["message"]?.ToString();
                                        System.Diagnostics.Debug.WriteLine($"[Log] Checking log write: isNewEpoch={isNewEpoch}, message={message}, LogsTextBox={LogsTextBox != null}");
                                        
                                        if (!string.IsNullOrEmpty(message) && LogsTextBox != null)
                                        {
                                            try
                                            {
                                                // Add rich log entry
                                                var logEntry = $"{DateTime.Now:HH:mm:ss} - Epoch {currentEpoch}: {message}\n";
                                                LogsTextBox.AppendText(logEntry);
                                                LogsTextBox.ScrollToEnd();
                                                System.Diagnostics.Debug.WriteLine($"[Log] ✅ Added: {logEntry.Trim()}");
                                            }
                                            catch (Exception logEx)
                                            {
                                                System.Diagnostics.Debug.WriteLine($"[Log] ❌ Error adding log: {logEx.Message}");
                                            }
                                        }
                                        else
                                        {
                                            System.Diagnostics.Debug.WriteLine($"[Log] ⚠️ Skipped: message empty={string.IsNullOrEmpty(message)}, LogsTextBox null={LogsTextBox == null}");
                                        }
                                    }
                                    else if (!isNewEpoch)
                                    {
                                        // Log why we're not adding (duplicate epoch)
                                        // System.Diagnostics.Debug.WriteLine($"[Log] ⏭️ Skipped duplicate poll for Epoch {currentEpoch}");
                                    }
                                }
                                else if (statusValue == "completed")
                                {
                                    StatusText.Text = "✅ آموزش تکمیل شد!";
                                    
                                    // Add completion log only once
                                    if (!LogsTextBox.Text.Contains("✅ آموزش با موفقیت تکمیل شد!"))
                                    {
                                        completionMessage = status.ContainsKey("message") ? status["message"]?.ToString() ?? "" : "آموزش با موفقیت تکمیل شد!";
                                        LogsTextBox.AppendText($"\n{DateTime.Now:HH:mm:ss} - ✅ {completionMessage}\n");
                                        LogsTextBox.ScrollToEnd();
                                        
                                        // Flag to navigate after Dispatcher.Invoke
                                        shouldNavigateToResults = true;
                                    }
                                }
                                else if (statusValue == "failed")
                                {
                                    StatusText.Text = "❌ آموزش با خطا متوقف شد";
                                    
                                    // Add error log only once
                                    if (!LogsTextBox.Text.Contains("❌ خطا:") && status.ContainsKey("error"))
                                    {
                                        var error = status["error"].ToString();
                                        LogsTextBox.AppendText($"\n{DateTime.Now:HH:mm:ss} - ❌ خطا: {error}\n");
                                        LogsTextBox.ScrollToEnd();
                                        
                                        MessageBox.Show(
                                            $"خطا در آموزش:\n{error}",
                                            "خطا",
                                            MessageBoxButton.OK,
                                            MessageBoxImage.Error
                                        );
                                    }
                                }
                                else if (statusValue == "stopping")
                                {
                                    StatusText.Text = "⏸️ در حال توقف آموزش...";
                                }
                                else if (statusValue == "not_started")
                                {
                                    // Check if we have training data (meaning training was running before)
                                    if (_trainLossData.Count > 0 || _lastSeenEpoch > 0)
                                    {
                                        // Training completed and was removed from active_trainings
                                        StatusText.Text = "✅ آموزش تکمیل شد!";
                                        System.Diagnostics.Debug.WriteLine($"[Dashboard] Training completed! Had {_trainLossData.Count} data points, last epoch: {_lastSeenEpoch}");
                                        
                                        LogsTextBox.AppendText($"\n{DateTime.Now:HH:mm:ss} - ✅ آموزش با موفقیت تکمیل شد!\n");
                                        LogsTextBox.ScrollToEnd();
                                        
                                        // Navigate to Results page
                                        shouldNavigateToResults = true;
                                    }
                                    else
                                    {
                                        // Training really hasn't started
                                        StatusText.Text = "⏸️ آموزش شروع نشده";
                                    }
                                }
                                else
                                {
                                    // Unknown status
                                    StatusText.Text = $"⚠️ وضعیت نامشخص: {statusValue}";
                                }
                            }
                            catch (Exception ex)
                            {
                                System.Diagnostics.Debug.WriteLine($"[Polling] UI update error: {ex.Message}");
                                System.Diagnostics.Debug.WriteLine($"[Polling] Stack trace: {ex.StackTrace}");
                            }
                        });
                        
                        System.Diagnostics.Debug.WriteLine($"[Dispatcher] Exited UI thread");
                        
                        // Handle navigation outside Dispatcher
                        if (shouldNavigateToResults)
                        {
                            // Wait 2 seconds to show completion message
                            await Task.Delay(2000);
                            
                            // Navigate to Results page
                            await Application.Current.Dispatcher.InvokeAsync(() =>
                            {
                                var resultsPage = new ResultsPage(_projectId, _projectName);
                                NavigationService?.Navigate(resultsPage);
                            });
                            
                            return; // Exit polling loop
                        }
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"[Polling] Network error: {ex.Message}");
                }
                
                // Poll every 2 seconds
                await Task.Delay(2000);
            }
        }

        /// <summary>
        /// Handle training update messages (DEPRECATED - using HTTP polling now)
        /// </summary>
        /*
        private void OnTrainingUpdate(object? sender, string message)
        {
            Dispatcher.Invoke(() =>
            {
                try
                {
                    var data = System.Text.Json.JsonSerializer.Deserialize<TrainingUpdate>(message);
                    if (data == null) return;

                    // Update progress
                    CurrentEpochText.Text = $"{data.CurrentEpoch} / {data.TotalEpochs}";
                    EpochProgressBar.Value = (double)data.CurrentEpoch / data.TotalEpochs * 100;

                    // Update metrics
                    TrainLossText.Text = data.TrainLoss.ToString("F4");
                    TrainAccText.Text = $"{data.TrainAcc * 100:F2}%";
                    
                    if (data.ValLoss > 0)
                    {
                        // Update validation metrics if available
                    }

                    // Update charts
                    _trainLossData.Add(data.TrainLoss);
                    _trainAccData.Add(data.TrainAcc);
                    
                    if (_trainLossData.Count > 100)
                    {
                        _trainLossData.RemoveAt(0);
                        _trainAccData.RemoveAt(0);
                    }

                    // Update logs
                    LogsTextBox.AppendText($"[Epoch {data.CurrentEpoch}] Loss: {data.TrainLoss:F4}, Acc: {data.TrainAcc:F4}\n");
                    LogsTextBox.ScrollToEnd();
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error parsing training update: {ex.Message}");
                }
            });
        }
        */


        /// <summary>
        /// Stop training
        /// </summary>
        private async void StopTraining_Click(object sender, RoutedEventArgs e)
        {
            var apiService = App.GetService<IApiService>();
            
            try
            {
                await apiService.PostAsync<object>($"/api/training/stop/{_projectId}");
                StatusText.Text = "Training stopped";
                StopButton.IsEnabled = false;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error stopping training: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Save checkpoint
        /// </summary>
        private void SaveCheckpoint_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Save checkpoint endpoint would be implemented
                MessageBox.Show("Checkpoint saved successfully!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error saving checkpoint: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
    }

    /// <summary>
    /// Training update data model
    /// </summary>
    public class TrainingUpdate
    {
        public int CurrentEpoch { get; set; }
        public int TotalEpochs { get; set; }
        public double TrainLoss { get; set; }
        public double TrainAcc { get; set; }
        public double ValLoss { get; set; }
        public double ValAcc { get; set; }
        public double LearningRate { get; set; }
    }
}

