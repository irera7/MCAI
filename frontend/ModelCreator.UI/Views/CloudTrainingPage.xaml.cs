using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// صفحه Cloud Training
    /// Complete implementation with API integration
    /// </summary>
    public partial class CloudTrainingPage : Page
    {
        private readonly HttpClient _httpClient;

        public CloudTrainingPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient { BaseAddress = new Uri("http://127.0.0.1:8181") };
            LoadProjects();
        }

        /// <summary>
        /// لود کردن پروژه‌های موجود
        /// </summary>
        private async void LoadProjects()
        {
            try
            {
                var response = await _httpClient.GetAsync("/api/project/list");
                
                if (response.IsSuccessStatusCode)
                {
                    var jsonString = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<ProjectsResponse>(
                        jsonString,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );

                    if (result?.Projects != null && result.Projects.Count > 0)
                    {
                        ProjectComboBox.ItemsSource = result.Projects;
                        ProjectComboBox.DisplayMemberPath = "Name";
                        ProjectComboBox.SelectedValuePath = "Id";
                    }
                }
            }
            catch
            {
                // Silently fail - user can still enter project name manually
            }
        }

        /// <summary>
        /// شروع cloud training
        /// </summary>
        private async void StartTrainingButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Validation
                if (ProjectComboBox.SelectedItem == null && string.IsNullOrWhiteSpace(ProjectComboBox.Text))
                {
                    MessageBox.Show(
                        "Please select or enter a project name",
                        "Validation Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Warning
                    );
                    return;
                }

                // تشخیص provider
                string provider = "aws";
                if (AzureRadio.IsChecked == true) provider = "azure";
                else if (GCPRadio.IsChecked == true) provider = "gcp";

                // دریافت تنظیمات
                string region = (RegionComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "us-east-1";
                string instanceType = (InstanceTypeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "ml.p3.2xlarge";

                // Disable button
                StartTrainingButton.IsEnabled = false;
                StartTrainingButton.Content = "⏳ Launching...";

                // ساخت درخواست
                var cloudConfig = new
                {
                    project_id = ProjectComboBox.SelectedValue?.ToString() ?? ProjectComboBox.Text,
                    provider = provider,
                    region = region,
                    instance_type = instanceType,
                    spot_instance = SpotInstanceCheckBox.IsChecked ?? false,
                    auto_shutdown = AutoShutdownCheckBox.IsChecked ?? true
                };

                var json = JsonSerializer.Serialize(cloudConfig);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync("/api/cloud/training/start", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseText = await response.Content.ReadAsStringAsync();
                    var result = JsonSerializer.Deserialize<CloudTrainingResponse>(
                        responseText,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true }
                    );

                    MessageBox.Show(
                        $"✅ Cloud training launched successfully!\n\n" +
                        $"Provider: {provider.ToUpper()}\n" +
                        $"Region: {region}\n" +
                        $"Instance: {instanceType}\n" +
                        $"Job ID: {result?.JobId}\n\n" +
                        "You can monitor the training progress from the cloud provider's console.",
                        "Success",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information
                    );

                    // Show job details
                    if (result != null)
                    {
                        JobStatusPanel.Visibility = Visibility.Visible;
                        JobIdText.Text = $"Job ID: {result.JobId}";
                        JobStatusText.Text = $"Status: {result.Status}";
                        EstimatedCostText.Text = $"Estimated Cost: ${result.EstimatedCost:F2}/hour";
                    }
                }
                else
                {
                    var errorText = await response.Content.ReadAsStringAsync();
                    MessageBox.Show(
                        $"Failed to start cloud training:\n\n{errorText}\n\n" +
                        "Note: Cloud training requires proper credentials and configuration.\n" +
                        "Please check your cloud provider settings.",
                        "Error",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error
                    );
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error starting cloud training:\n\n{ex.Message}\n\n" +
                    "Make sure:\n" +
                    "1. Backend server is running\n" +
                    "2. Cloud credentials are configured\n" +
                    "3. You have necessary permissions",
                    "Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
            finally
            {
                StartTrainingButton.IsEnabled = true;
                StartTrainingButton.Content = "🚀 Start Cloud Training";
            }
        }

        /// <summary>
        /// نمایش cost estimation
        /// </summary>
        private void InstanceTypeComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (CostEstimateText == null) return;

            var instanceType = (InstanceTypeComboBox.SelectedItem as ComboBoxItem)?.Content.ToString() ?? "";
            
            // تخمین هزینه ساده (واقعی باید از API بیاید)
            double costPerHour = 0;
            if (instanceType.Contains("p3.2xlarge")) costPerHour = 3.06;
            else if (instanceType.Contains("p3.8xlarge")) costPerHour = 12.24;
            else if (instanceType.Contains("p3.16xlarge")) costPerHour = 24.48;
            else if (instanceType.Contains("g4dn.xlarge")) costPerHour = 0.526;
            else if (instanceType.Contains("Standard_NC6")) costPerHour = 0.90;
            else if (instanceType.Contains("n1-standard-4")) costPerHour = 0.19;

            if (SpotInstanceCheckBox?.IsChecked == true)
            {
                costPerHour *= 0.3; // Spot instances ~70% cheaper
            }

            CostEstimateText.Text = $"💰 Estimated Cost: ${costPerHour:F2}/hour";
        }

        private void SpotInstanceCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            InstanceTypeComboBox_SelectionChanged(sender, null!);
        }

        // ============================================
        // Data Models
        // ============================================

        private class ProjectsResponse
        {
            public System.Collections.Generic.List<ProjectInfo>? Projects { get; set; }
        }

        private class ProjectInfo
        {
            public string? Id { get; set; }
            public string? Name { get; set; }
        }

        private class CloudTrainingResponse
        {
            public string? JobId { get; set; }
            public string? Status { get; set; }
            public double EstimatedCost { get; set; }
        }
    }
}
