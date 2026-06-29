using ModelCreator.UI.Services;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Interaction logic for ProjectsPage.xaml
    /// Projects list page
    /// </summary>
    public partial class ProjectsPage : Page
    {
        private readonly IProjectService? _projectService;

        public ProjectsPage()
        {
            InitializeComponent();
            
            try
            {
                _projectService = App.GetService<IProjectService>();
                LoadProjects();
            }
            catch
            {
                EmptyStateText.Text = "Backend service not available. Please start the backend server.";
                EmptyStateText.Visibility = Visibility.Visible;
                ProjectsList.Visibility = Visibility.Collapsed;
            }
        }

        /// <summary>
        /// Load all projects
        /// </summary>
        private async void LoadProjects()
        {
            if (_projectService == null) return;
            
            try
            {
                var projects = await _projectService.GetRecentProjects();
                
                if (projects.Count == 0)
                {
                    EmptyStateText.Visibility = Visibility.Visible;
                    ProjectsList.Visibility = Visibility.Collapsed;
                }
                else
                {
                    ProjectsList.ItemsSource = projects;
                    EmptyStateText.Visibility = Visibility.Collapsed;
                    ProjectsList.Visibility = Visibility.Visible;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading projects: {ex.Message}\n\nPlease ensure the backend is running.", 
                    "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                
                EmptyStateText.Text = "Could not load projects. Backend may not be running.";
                EmptyStateText.Visibility = Visibility.Visible;
                ProjectsList.Visibility = Visibility.Collapsed;
            }
        }

        /// <summary>
        /// Create new project
        /// </summary>
        private void NewProject_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new CreateProjectPage());
        }

        /// <summary>
        /// Open project
        /// </summary>
        private async void Project_Click(object sender, MouseButtonEventArgs e)
        {
            if (sender is Border border && border.DataContext is ProjectInfo project)
            {
                try
                {
                    var window = Window.GetWindow(this) as MainWindow;
                    
                    // Check if project is currently training
                    if (project.IsTraining)
                    {
                        // Navigate to Training Dashboard
                        window?.MainFrame.Navigate(new TrainingDashboardPage(
                            project.Id,
                            project.Name
                        ));
                        return;
                    }
                    
                    // Check training status by calling API
                    var apiService = App.GetService<IApiService>();
                    if (apiService != null)
                    {
                        try
                        {
                            var status = await apiService.GetAsync<System.Collections.Generic.Dictionary<string, object>>(
                                $"/api/training/status/{project.Id}"
                            );
                            
                            if (status != null && status.ContainsKey("status"))
                            {
                                var trainingStatus = status["status"].ToString();
                                
                                // If training is active, go to dashboard
                                if (trainingStatus == "training" || trainingStatus == "starting")
                                {
                                    window?.MainFrame.Navigate(new TrainingDashboardPage(
                                        project.Id,
                                        project.Name
                                    ));
                                    return;
                                }
                                
                                // If training completed, go to results
                                if (trainingStatus == "completed")
                                {
                                    window?.MainFrame.Navigate(new ResultsPage(project.Id, project.Name));
                                    return;
                                }
                            }
                        }
                        catch
                        {
                            // If API call fails, continue with normal navigation
                        }
                    }
                    
                    // Default: navigate to Data Import page
                    window?.MainFrame.Navigate(new DataImportPage(
                        project.Id, 
                        project.Name, 
                        project.Modality
                    ));
                }
                catch (Exception ex)
                {
                    MessageBox.Show(
                        $"خطا در باز کردن پروژه:\n\n{ex.Message}\n\nلطفاً مطمئن شوید Backend در حال اجرا است.",
                        "خطا",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error
                    );
                }
            }
        }

        /// <summary>
        /// Delete project
        /// </summary>
        private async void DeleteProject_Click(object sender, RoutedEventArgs e)
        {
            // Stop event from bubbling to Project_Click
            e.Handled = true;
            
            if (_projectService == null)
            {
                MessageBox.Show("Backend service not available.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }
            
            if (sender is Button button && button.DataContext is ProjectInfo project)
            {
                var result = MessageBox.Show(
                    $"Are you sure you want to delete '{project.Name}'?", 
                    "Confirm Delete", 
                    MessageBoxButton.YesNo, 
                    MessageBoxImage.Warning
                );

                if (result == MessageBoxResult.Yes)
                {
                    try
                    {
                        await _projectService.DeleteProject(project.Id);
                        LoadProjects(); // Refresh list
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Error deleting project: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }
            }
        }
        
        /// <summary>
        /// Open Playground for trained project
        /// </summary>
        private void Playground_Click(object sender, RoutedEventArgs e)
        {
            // Stop event from bubbling to Project_Click
            e.Handled = true;
            
            if (sender is Button button && button.DataContext is ProjectInfo project)
            {
                try
                {
                    var window = Window.GetWindow(this) as MainWindow;
                    window?.MainFrame.Navigate(new InferencePlaygroundPage(project.Id));
                }
                catch (Exception ex)
                {
                    MessageBox.Show(
                        $"خطا در باز کردن Playground:\n\n{ex.Message}",
                        "خطا",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error
                    );
                }
            }
        }
    }
}

