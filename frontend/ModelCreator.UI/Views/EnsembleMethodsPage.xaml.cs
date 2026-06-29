using ModelCreator.UI.Services;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Interaction logic for EnsembleMethodsPage.xaml
    /// صفحه ترکیب چند مدل برای accuracy بهتر
    /// </summary>
    public partial class EnsembleMethodsPage : Page
    {
        private readonly HttpClient _httpClient;
        private ObservableCollection<AvailableModel> _availableModels = new();
        private List<AvailableModel> _selectedModels = new();

        public EnsembleMethodsPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:8181") };
            
            ModelsListBox.ItemsSource = _availableModels;
            LoadAvailableModels();
        }

        /// <summary>
        /// لود کردن مدل‌های موجود از backend
        /// </summary>
        private async void LoadAvailableModels()
        {
            try {
                LoadingPanel.Visibility = Visibility.Visible;
                ModelsPanel.Visibility = Visibility.Collapsed;
                ErrorPanel.Visibility = Visibility.Collapsed;

                var response = await _httpClient.GetAsync("/api/ensemble/available-models");

                if (response.IsSuccessStatusCode)
                {
                    var jsonString = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<AvailableModelsResponse>(
                        jsonString,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );

                    _availableModels.Clear();

                    if (result?.Models != null && result.Models.Count > 0)
                    {
                        foreach (var model in result.Models)
                        {
                            _availableModels.Add(model);
                        }

                        LoadingPanel.Visibility = Visibility.Collapsed;
                        ModelsPanel.Visibility = Visibility.Visible;
                        
                        StatusText.Text = $"{result.Total} trained models available for ensemble";
                    }
                    else
                    {
                        // هیچ مدل آموزش‌دیده‌ای وجود ندارد
                        LoadingPanel.Visibility = Visibility.Collapsed;
                        ErrorPanel.Visibility = Visibility.Visible;
                        ErrorText.Text = "❌ No trained models found!\n\nPlease train at least 2 models before creating an ensemble.";
                    }
                }
                else
                {
                    ShowError($"Failed to load models: {response.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                ShowError($"Error loading models: {ex.Message}\n\nMake sure backend is running.");
            }
        }

        /// <summary>
        /// هندلر تغییر selection در لیست مدل‌ها
        /// </summary>
        private void ModelsListBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            _selectedModels = ModelsListBox.SelectedItems.Cast<AvailableModel>().ToList();
            
            // Update UI
            SelectedCountText.Text = $"{_selectedModels.Count} models selected";
            CreateEnsembleButton.IsEnabled = _selectedModels.Count >= 2;

            if (_selectedModels.Count < 2)
            {
                ValidationText.Text = "⚠️ Select at least 2 models";
                ValidationText.Foreground = System.Windows.Media.Brushes.Orange;
            }
            else
            {
                // بررسی num_classes یکسان
                var numClassesList = _selectedModels.Select(m => m.NumClasses).Distinct().ToList();
                if (numClassesList.Count > 1)
                {
                    ValidationText.Text = $"⚠️ Models must have same number of classes. Found: {string.Join(", ", numClassesList)}";
                    ValidationText.Foreground = System.Windows.Media.Brushes.Red;
                    CreateEnsembleButton.IsEnabled = false;
                }
                else
                {
                    ValidationText.Text = $"✅ {_selectedModels.Count} compatible models selected";
                    ValidationText.Foreground = System.Windows.Media.Brushes.Green;
                }
            }
        }

        /// <summary>
        /// ایجاد ensemble
        /// </summary>
        private async void CreateEnsembleButton_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedModels.Count < 2)
            {
                MessageBox.Show(
                    "Please select at least 2 models for ensemble.",
                    "Invalid Selection",
                    MessageBoxButton.OK,
                    MessageBoxImage.Warning
                );
                return;
            }

            // دریافت نام ensemble
            var ensembleName = EnsembleNameTextBox.Text.Trim();
            if (string.IsNullOrEmpty(ensembleName))
            {
                MessageBox.Show(
                    "Please enter a name for the ensemble.",
                    "Name Required",
                    MessageBoxButton.OK,
                    MessageBoxImage.Warning
                );
                return;
            }

            // تعیین نوع ensemble
            string ensembleType = "voting";
            if (StackingRadio.IsChecked == true) ensembleType = "stacking";
            else if (BaggingRadio.IsChecked == true) ensembleType = "bagging";

            // تعیین voting type
            string votingType = "soft";
            if (HardVotingRadio.IsChecked == true) votingType = "hard";

            try
            {
                CreateEnsembleButton.IsEnabled = false;
                CreateEnsembleButton.Content = "⏳ Creating...";

                var request = new
                {
                    project_ids = _selectedModels.Select(m => m.ProjectId).ToList(),
                    ensemble_type = ensembleType,
                    voting_type = votingType,
                    weights = (List<float>?)null,
                    ensemble_name = ensembleName
                };

                var json = JsonSerializer.Serialize(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync("/api/ensemble/create", content);
                var responseText = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    MessageBox.Show(
                        $"✅ Ensemble \"{ensembleName}\" created successfully!\n\n" +
                        $"Type: {ensembleType}\n" +
                        $"Models: {_selectedModels.Count}\n" +
                        $"Combined Accuracy: ~{_selectedModels.Average(m => m.Accuracy):F2}%",
                        "Success",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information
                    );

                    // Reset form
                    EnsembleNameTextBox.Clear();
                    ModelsListBox.SelectedItems.Clear();
                }
                else
                {
                    var errorObj = JsonSerializer.Deserialize<ErrorResponse>(
                        responseText,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );
                    
                    MessageBox.Show(
                        $"Failed to create ensemble:\n\n{errorObj?.Detail ?? responseText}",
                        "Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error
                    );
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error creating ensemble:\n\n{ex.Message}",
                    "Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
            finally
            {
                CreateEnsembleButton.IsEnabled = true;
                CreateEnsembleButton.Content = "🎯 Create Ensemble";
            }
        }

        /// <summary>
        /// Refresh لیست مدل‌ها
        /// </summary>
        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            LoadAvailableModels();
        }

        /// <summary>
        /// نمایش خطا
        /// </summary>
        private void ShowError(string message)
        {
            LoadingPanel.Visibility = Visibility.Collapsed;
            ModelsPanel.Visibility = Visibility.Collapsed;
            ErrorPanel.Visibility = Visibility.Visible;
            ErrorText.Text = message;
        }

        // ============================================
        // Data Models
        // ============================================

        public class AvailableModel
        {
            public string ProjectId { get; set; } = "";
            public string ProjectName { get; set; } = "";
            public string Architecture { get; set; } = "";
            public double Accuracy { get; set; }
            public int NumClasses { get; set; }
            public string Modality { get; set; } = "";
            public string CreatedAt { get; set; } = "";

            public string DisplayText => $"{ProjectName} - {Architecture} (Acc: {Accuracy:F2}%, Classes: {NumClasses})";
        }

        public class AvailableModelsResponse
        {
            public string Status { get; set; } = "";
            public List<AvailableModel> Models { get; set; } = new();
            public int Total { get; set; }
        }

        public class ErrorResponse
        {
            public string Detail { get; set; } = "";
        }
    }
}
