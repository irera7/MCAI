using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using ModelCreator.UI.Services;
using System.Collections.ObjectModel;

namespace ModelCreator.UI.ViewModels
{
    /// <summary>
    /// View model for project management
    /// </summary>
    public partial class ProjectViewModel : ObservableObject
    {
        private readonly IProjectService _projectService;

        [ObservableProperty]
        private string _projectName = string.Empty;

        [ObservableProperty]
        private string _projectDescription = string.Empty;

        [ObservableProperty]
        private string _selectedModality = "image";

        [ObservableProperty]
        private ObservableCollection<string> _availableModalities = new()
        {
            "image", "text", "audio", "video", 
            "tabular", "timeseries", "medical", "genomic"
        };

        public ProjectViewModel(IProjectService projectService)
        {
            _projectService = projectService;
        }

        [RelayCommand]
        private async Task CreateProject()
        {
            if (string.IsNullOrWhiteSpace(ProjectName))
            {
                System.Windows.MessageBox.Show("Please enter a project name.", "Validation Error");
                return;
            }

            try
            {
                var project = await _projectService.CreateProject(ProjectName, SelectedModality, ProjectDescription);
                // Navigate to next step
            }
            catch (Exception ex)
            {
                System.Windows.MessageBox.Show($"Error creating project: {ex.Message}", "Error");
            }
        }
    }
}

