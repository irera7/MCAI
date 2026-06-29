using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using ModelCreator.UI.Services;
using System.Collections.ObjectModel;
using System.Windows;

namespace ModelCreator.UI.ViewModels
{
    /// <summary>
    /// View model for home page
    /// </summary>
    public partial class HomeViewModel : ObservableObject
    {
        private readonly IProjectService _projectService;

        [ObservableProperty]
        private ObservableCollection<ProjectInfo> _recentProjects = new();

        [ObservableProperty]
        private bool _isLoading;

        public HomeViewModel(IProjectService projectService)
        {
            _projectService = projectService;
            // Load projects in background - don't block UI startup
            Task.Run(async () =>
            {
                try
                {
                    await LoadRecentProjectsAsync();
                }
                catch
                {
                    // Silently fail if backend is not available
                }
            });
        }

        /// <summary>
        /// Load recent projects
        /// </summary>
        private async Task LoadRecentProjectsAsync()
        {
            IsLoading = true;
            try
            {
                var projects = await _projectService.GetRecentProjects();
                
                // Update UI on UI thread
                Application.Current.Dispatcher.Invoke(() =>
                {
                    RecentProjects = new ObservableCollection<ProjectInfo>(projects.Take(5));
                });
            }
            catch (Exception ex)
            {
                // Only show error if user explicitly tries to load projects
                System.Diagnostics.Debug.WriteLine($"Error loading projects: {ex.Message}");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private void CreateNewProject()
        {
            // Navigate to project creation
            var window = Application.Current.MainWindow as MainWindow;
            window?.MainFrame.Navigate(new Uri("Views/CreateProjectPage.xaml", UriKind.Relative));
        }

        [RelayCommand]
        private void LoadProject()
        {
            // Navigate to project loading
            var window = Application.Current.MainWindow as MainWindow;
            window?.MainFrame.Navigate(new Uri("Views/ProjectsPage.xaml", UriKind.Relative));
        }
    }
}

