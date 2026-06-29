using ModelCreator.UI.Services;
using System.Windows;
using System.Windows.Controls;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Interaction logic for CreateProjectPage.xaml
    /// Create new project page
    /// </summary>
    public partial class CreateProjectPage : Page
    {
        private readonly IProjectService? _projectService;

        public CreateProjectPage()
        {
            InitializeComponent();
            
            try
            {
                _projectService = App.GetService<IProjectService>();
            }
            catch
            {
                // Service not available
            }
        }

        /// <summary>
        /// Create new project
        /// </summary>
        private async void CreateProject_Click(object sender, RoutedEventArgs e)
        {
            var name = ProjectNameTextBox.Text.Trim();
            if (string.IsNullOrEmpty(name))
            {
                MessageBox.Show("Please enter a project name.", "Validation Error", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (_projectService == null)
            {
                MessageBox.Show("Backend service is not available. Please ensure the backend is running on http://127.0.0.1:8181", 
                    "Service Error", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            var modalityItem = ModalityComboBox.SelectedItem as ComboBoxItem;
            var modality = modalityItem?.Tag?.ToString() ?? "image";
            var description = DescriptionTextBox.Text.Trim();

            try
            {
                var project = await _projectService.CreateProject(name, modality, description);
                
                MessageBox.Show($"Project '{project.Name}' created successfully!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
                
                // Navigate to data import page
                NavigationService?.Navigate(new DataImportPage(project.Id, project.Name, modality));
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error creating project: {ex.Message}\n\nPlease ensure the backend is running on http://127.0.0.1:8181", 
                    "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Cancel and go back
        /// </summary>
        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.GoBack();
        }
    }
}

