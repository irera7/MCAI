using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Debug page for testing Training Dashboard API
    /// </summary>
    public partial class DashboardDebugPage : Page
    {
        private readonly HttpClient _httpClient = new HttpClient();
        private string _projectId;

        public DashboardDebugPage(string projectId = "53569a3d-1248-4b5d-8e8b-be8b75556767")
        {
            InitializeComponent();
            _projectId = projectId;
            _httpClient.BaseAddress = new Uri("http://127.0.0.1:8181");
            
            ProjectIdTextBox.Text = _projectId;
        }

        private async void TestButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                _projectId = ProjectIdTextBox.Text;
                StatusTextBlock.Text = "⏳ در حال دریافت...";
                ResponseTextBox.Text = "";

                var response = await _httpClient.GetAsync($"/api/training/status/{_projectId}");
                var content = await response.Content.ReadAsStringAsync();

                StatusTextBlock.Text = $"✅ Status: {response.StatusCode}";
                
                // Pretty print JSON
                try
                {
                    var jsonDoc = JsonDocument.Parse(content);
                    var prettyJson = JsonSerializer.Serialize(jsonDoc, new JsonSerializerOptions 
                    { 
                        WriteIndented = true 
                    });
                    ResponseTextBox.Text = prettyJson;
                    
                    // Parse specific fields
                    var root = jsonDoc.RootElement;
                    if (root.TryGetProperty("status", out var statusProp))
                    {
                        StatusValueText.Text = statusProp.GetString();
                    }
                    if (root.TryGetProperty("current_epoch", out var epochProp))
                    {
                        EpochValueText.Text = epochProp.ToString();
                    }
                    if (root.TryGetProperty("train_loss", out var lossProp))
                    {
                        LossValueText.Text = lossProp.GetDouble().ToString("F4");
                    }
                    if (root.TryGetProperty("train_acc", out var accProp))
                    {
                        AccValueText.Text = $"{accProp.GetDouble() * 100:F2}%";
                    }
                }
                catch
                {
                    ResponseTextBox.Text = content;
                }
            }
            catch (Exception ex)
            {
                StatusTextBlock.Text = $"❌ خطا: {ex.Message}";
                ResponseTextBox.Text = ex.ToString();
            }
        }

        private void CopyButton_Click(object sender, RoutedEventArgs e)
        {
            Clipboard.SetText(ResponseTextBox.Text);
            MessageBox.Show("کپی شد!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void BackButton_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.GoBack();
        }
    }
}

