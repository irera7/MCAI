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
    /// Interaction logic for ModelComparisonPage.xaml
    /// صفحه مقایسه مدل‌های مختلف
    /// </summary>
    public partial class ModelComparisonPage : Page
    {
        private readonly HttpClient _httpClient;
        private ObservableCollection<ProjectModel> _availableProjects = new();
        private List<ProjectModel> _selectedProjects = new();

        public ModelComparisonPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:8181") };
            
            ProjectsListBox.ItemsSource = _availableProjects;
            LoadProjects();
        }

        /// <summary>
        /// لود کردن پروژه‌های تکمیل شده
        /// </summary>
        private async void LoadProjects()
        {
            try
            {
                LoadingPanel.Visibility = Visibility.Visible;
                ContentPanel.Visibility = Visibility.Collapsed;
                ErrorPanel.Visibility = Visibility.Collapsed;

                var response = await _httpClient.GetAsync("/api/comparison/projects");

                if (response.IsSuccessStatusCode)
                {
                    var jsonString = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<ProjectsResponse>(
                        jsonString,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );

                    _availableProjects.Clear();

                    if (result?.Projects != null && result.Projects.Count > 0)
                    {
                        foreach (var project in result.Projects)
                        {
                            _availableProjects.Add(project);
                        }

                        LoadingPanel.Visibility = Visibility.Collapsed;
                        ContentPanel.Visibility = Visibility.Visible;
                        
                        StatusText.Text = $"{result.Total} trained models available";
                    }
                    else
                    {
                        ShowError("❌ No trained models found!\n\nComplete training of at least 2 models to use comparison.");
                    }
                }
                else
                {
                    ShowError($"Failed to load projects: {response.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                ShowError($"Error: {ex.Message}\n\nMake sure backend is running.");
            }
        }

        /// <summary>
        /// هندلر تغییر selection
        /// </summary>
        private void ProjectsListBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            _selectedProjects = ProjectsListBox.SelectedItems.Cast<ProjectModel>().ToList();
            
            SelectedCountText.Text = $"{_selectedProjects.Count} projects selected";
            CompareButton.IsEnabled = _selectedProjects.Count >= 2;

            if (_selectedProjects.Count < 2)
            {
                ValidationText.Text = "⚠️ Select at least 2 projects to compare";
                ValidationText.Foreground = System.Windows.Media.Brushes.Orange;
            }
            else
            {
                ValidationText.Text = $"✅ Ready to compare {_selectedProjects.Count} projects";
                ValidationText.Foreground = System.Windows.Media.Brushes.Green;
            }
        }

        /// <summary>
        /// مقایسه پروژه‌های انتخاب شده
        /// </summary>
        private async void CompareButton_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedProjects.Count < 2)
            {
                MessageBox.Show(
                    "Please select at least 2 projects to compare.",
                    "Selection Required",
                    MessageBoxButton.OK,
                    MessageBoxImage.Warning
                );
                return;
            }

            try
            {
                CompareButton.IsEnabled = false;
                CompareButton.Content = "⏳ Comparing...";

                var projectIds = _selectedProjects.Select(p => p.ProjectId).ToList();
                var json = JsonSerializer.Serialize(projectIds);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync("/api/comparison/compare", content);
                var responseText = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var result = JsonSerializer.Deserialize<ComparisonResponse>(
                        responseText,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );

                    // نمایش نتایج
                    ShowComparisonResults(result);
                }
                else
                {
                    MessageBox.Show(
                        $"Comparison failed:\n\n{responseText}",
                        "Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error
                    );
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error during comparison:\n\n{ex.Message}",
                    "Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
            finally
            {
                CompareButton.IsEnabled = true;
                CompareButton.Content = "📊 Compare Selected";
            }
        }

        /// <summary>
        /// نمایش نتایج مقایسه
        /// </summary>
        private void ShowComparisonResults(ComparisonResponse? result)
        {
            if (result == null || result.Comparison == null) return;

            // پاک کردن جدول قبلی
            ComparisonGrid.Children.Clear();
            ComparisonGrid.RowDefinitions.Clear();

            // Header
            ComparisonGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            
            var headers = new[] { "Project", "Model", "Accuracy", "Loss", "Epochs", "Duration", "Batch Size", "LR" };
            for (int col = 0; col < headers.Length; col++)
            {
                var header = new TextBlock
                {
                    Text = headers[col],
                    FontWeight = FontWeights.Bold,
                    Padding = new Thickness(10),
                    Background = System.Windows.Media.Brushes.LightGray
                };
                Grid.SetRow(header, 0);
                Grid.SetColumn(header, col);
                ComparisonGrid.Children.Add(header);
            }

            // Data rows
            int rowIndex = 1;
            foreach (var project in result.Comparison)
            {
                ComparisonGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

                var cells = new[]
                {
                    project.ProjectName ?? "Unknown",
                    project.ModelArchitecture ?? "Unknown",
                    $"{project.BestAccuracy:F2}%",
                    $"{project.BestLoss:F4}",
                    project.TotalEpochs.ToString(),
                    $"{project.TrainingDuration:F1}s",
                    project.BatchSize.ToString(),
                    project.LearningRate.ToString("F5")
                };

                for (int col = 0; col < cells.Length; col++)
                {
                    var cell = new TextBlock
                    {
                        Text = cells[col],
                        Padding = new Thickness(10),
                        VerticalAlignment = VerticalAlignment.Center
                    };
                    
                    // Highlight best accuracy
                    if (col == 2 && project.BestAccuracy == result.Statistics?.BestModel?.BestAccuracy)
                    {
                        cell.Background = System.Windows.Media.Brushes.LightGreen;
                        cell.FontWeight = FontWeights.Bold;
                    }

                    Grid.SetRow(cell, rowIndex);
                    Grid.SetColumn(cell, col);
                    ComparisonGrid.Children.Add(cell);
                }

                rowIndex++;
            }

            // نمایش آمار
            if (result.Statistics != null)
            {
                StatsPanel.Visibility = Visibility.Visible;
                
                BestModelText.Text = $"🏆 Best: {result.Statistics.BestModel?.ProjectName} ({result.Statistics.BestModel?.BestAccuracy:F2}%)";
                AvgAccuracyText.Text = $"📊 Average Accuracy: {result.Statistics.AverageAccuracy:F2}%";
                StdAccuracyText.Text = $"📉 Std Dev: {result.Statistics.AccuracyStd:F2}%";
                FastestText.Text = $"⚡ Fastest: {result.Statistics.FastestTraining?.ProjectName} ({result.Statistics.FastestTraining?.TrainingDuration:F1}s)";
            }

            ResultsPanel.Visibility = Visibility.Visible;
        }

        /// <summary>
        /// Export به CSV
        /// </summary>
        private async void ExportCSVButton_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedProjects.Count < 1)
            {
                MessageBox.Show("Please select projects first.", "No Selection", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            try
            {
                var projectIds = string.Join(",", _selectedProjects.Select(p => p.ProjectId));
                var url = $"/api/comparison/export/csv?project_ids={projectIds}";
                
                var response = await _httpClient.GetAsync(url);
                
                if (response.IsSuccessStatusCode)
                {
                    var csvData = await response.Content.ReadAsByteArrayAsync();
                    
                    // ذخیره فایل
                    var dialog = new Microsoft.Win32.SaveFileDialog
                    {
                        FileName = "model_comparison",
                        DefaultExt = ".csv",
                        Filter = "CSV files (*.csv)|*.csv"
                    };

                    if (dialog.ShowDialog() == true)
                    {
                        System.IO.File.WriteAllBytes(dialog.FileName, csvData);
                        MessageBox.Show($"✅ Comparison exported to:\n{dialog.FileName}", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
                    }
                }
                else
                {
                    MessageBox.Show("Export failed!", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Refresh لیست
        /// </summary>
        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            LoadProjects();
        }

        /// <summary>
        /// Clear Results
        /// </summary>
        private void ClearButton_Click(object sender, RoutedEventArgs e)
        {
            ResultsPanel.Visibility = Visibility.Collapsed;
            ProjectsListBox.SelectedItems.Clear();
        }

        /// <summary>
        /// نمایش خطا
        /// </summary>
        private void ShowError(string message)
        {
            LoadingPanel.Visibility = Visibility.Collapsed;
            ContentPanel.Visibility = Visibility.Collapsed;
            ErrorPanel.Visibility = Visibility.Visible;
            ErrorText.Text = message;
        }

        // ============================================
        // Data Models
        // ============================================

        public class ProjectModel
        {
            public string ProjectId { get; set; } = "";
            public string ProjectName { get; set; } = "";
            public string ModelArchitecture { get; set; } = "";
            public string Modality { get; set; } = "";
            public double BestAccuracy { get; set; }
            public double BestLoss { get; set; }
            public int TotalEpochs { get; set; }
            public double TrainingDuration { get; set; }
            public int BatchSize { get; set; }
            public double LearningRate { get; set; }

            public string DisplayText => $"{ProjectName} - {ModelArchitecture} ({BestAccuracy:F2}%)";
        }

        public class ProjectsResponse
        {
            public string Status { get; set; } = "";
            public List<ProjectModel> Projects { get; set; } = new();
            public int Total { get; set; }
        }

        public class ComparisonResponse
        {
            public string Status { get; set; } = "";
            public List<ProjectModel> Comparison { get; set; } = new();
            public ComparisonStats? Statistics { get; set; }
            public int TotalCompared { get; set; }
        }

        public class ComparisonStats
        {
            public ProjectModel? BestModel { get; set; }
            public ProjectModel? FastestTraining { get; set; }
            public double AverageAccuracy { get; set; }
            public double AccuracyStd { get; set; }
        }
    }
}
