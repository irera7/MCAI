using System;
using System.Collections.ObjectModel;
using System.Data;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Data Preview Page - Explore dataset before training
    /// </summary>
    public partial class DataPreviewPage : Page
    {
        private ObservableCollection<ClassDistribution> _classDistributions;
        private ObservableCollection<FeatureInfo> _featureInfos;

        public DataPreviewPage()
        {
            InitializeComponent();
            _classDistributions = new ObservableCollection<ClassDistribution>();
            _featureInfos = new ObservableCollection<FeatureInfo>();
            ClassDistributionList.ItemsSource = _classDistributions;
            FeatureInfoGrid.ItemsSource = _featureInfos;
        }

        private void LoadFileButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var dialog = new OpenFileDialog
                {
                    Title = "Select Data File",
                    Filter = "CSV Files (*.csv)|*.csv|All Files (*.*)|*.*"
                };

                if (dialog.ShowDialog() == true)
                {
                    FileNameText.Text = Path.GetFileName(dialog.FileName);
                    LoadAndAnalyzeData(dialog.FileName);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading file:\n\n{ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void LoadAndAnalyzeData(string filePath)
        {
            try
            {
                // برای سادگی، فقط CSV را پشتیبانی می‌کنیم
                var lines = File.ReadAllLines(filePath);
                if (lines.Length == 0)
                {
                    MessageBox.Show("File is empty!", "Error", 
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                // خواندن header
                var headers = lines[0].Split(',');
                var dataLines = lines.Skip(1).ToArray();

                // ساخت DataTable
                var dataTable = new DataTable();
                foreach (var header in headers)
                {
                    dataTable.Columns.Add(header.Trim());
                }

                // خواندن اول 10 سطر
                var previewRows = Math.Min(10, dataLines.Length);
                for (int i = 0; i < previewRows; i++)
                {
                    var values = dataLines[i].Split(',');
                    if (values.Length == headers.Length)
                    {
                        dataTable.Rows.Add(values);
                    }
                }

                // نمایش data
                DataPreviewGrid.ItemsSource = dataTable.DefaultView;

                // محاسبه آمار
                CalculateStatistics(lines, headers);

                // نمایش panels
                StatsPanel.Visibility = Visibility.Visible;
                TablePanel.Visibility = Visibility.Visible;
                FeaturesPanel.Visibility = Visibility.Visible;

                // اگر ستون target داریم، class distribution نمایش بده
                if (headers.Contains("target") || headers.Contains("label"))
                {
                    CalculateClassDistribution(dataLines, headers);
                    DistributionPanel.Visibility = Visibility.Visible;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error analyzing data:\n\n{ex.Message}", "Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void CalculateStatistics(string[] lines, string[] headers)
        {
            var dataLines = lines.Skip(1).ToArray();
            
            TotalSamplesText.Text = dataLines.Length.ToString();
            FeaturesText.Text = headers.Length.ToString();
            
            // محاسبه missing values
            int missingCount = 0;
            foreach (var line in dataLines)
            {
                var values = line.Split(',');
                missingCount += values.Count(v => string.IsNullOrWhiteSpace(v) || v == "NaN" || v == "NA");
            }
            MissingValuesText.Text = missingCount.ToString();

            // محاسبه feature info
            _featureInfos.Clear();
            
            for (int i = 0; i < headers.Length; i++)
            {
                var featureName = headers[i].Trim();
                var values = dataLines.Select(l => l.Split(',')[i]).ToList();
                
                // تشخیص نوع
                var isNumeric = values.Take(100).All(v => 
                    string.IsNullOrWhiteSpace(v) || double.TryParse(v, out _)
                );
                
                var missing = values.Count(v => string.IsNullOrWhiteSpace(v));
                var unique = values.Distinct().Count();
                
                var mean = "-";
                var std = "-";
                
                if (isNumeric)
                {
                    var numericValues = values
                        .Where(v => double.TryParse(v, out _))
                        .Select(double.Parse)
                        .ToList();
                    
                    if (numericValues.Any())
                    {
                        mean = numericValues.Average().ToString("F2");
                        var avg = numericValues.Average();
                        var sumOfSquares = numericValues.Sum(v => (v - avg) * (v - avg));
                        std = Math.Sqrt(sumOfSquares / numericValues.Count).ToString("F2");
                    }
                }
                
                _featureInfos.Add(new FeatureInfo
                {
                    Name = featureName,
                    Type = isNumeric ? "Numeric" : "Categorical",
                    Missing = missing.ToString(),
                    Unique = unique.ToString(),
                    Mean = mean,
                    Std = std
                });
            }
        }

        private void CalculateClassDistribution(string[] dataLines, string[] headers)
        {
            try
            {
                // پیدا کردن ستون target
                int targetIndex = Array.IndexOf(headers, "target");
                if (targetIndex == -1)
                    targetIndex = Array.IndexOf(headers, "label");
                
                if (targetIndex == -1)
                    return;

                // شمارش classes
                var classCounts = dataLines
                    .Select(l => l.Split(',')[targetIndex])
                    .GroupBy(c => c)
                    .ToDictionary(g => g.Key, g => g.Count());

                ClassesText.Text = classCounts.Count.ToString();

                // محاسبه درصد
                var total = dataLines.Length;
                _classDistributions.Clear();
                
                foreach (var kvp in classCounts.OrderByDescending(x => x.Value))
                {
                    _classDistributions.Add(new ClassDistribution
                    {
                        ClassName = kvp.Key,
                        Count = kvp.Value,
                        Percentage = (kvp.Value * 100.0) / total
                    });
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error calculating class distribution: {ex.Message}");
            }
        }

        // Data Models
        public class ClassDistribution
        {
            public string ClassName { get; set; } = "";
            public int Count { get; set; }
            public double Percentage { get; set; }
        }

        public class FeatureInfo
        {
            public string Name { get; set; } = "";
            public string Type { get; set; } = "";
            public string Missing { get; set; } = "";
            public string Unique { get; set; } = "";
            public string Mean { get; set; } = "";
            public string Std { get; set; } = "";
        }
    }
}

