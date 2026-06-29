using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Windows.Input;

namespace ModelCreator.UI.ViewModels
{
    /// <summary>
    /// Main view model for the application
    /// </summary>
    public partial class MainViewModel : ObservableObject
    {
        [ObservableProperty]
        private string _title = "AI Model Builder";

        [ObservableProperty]
        private string _currentPage = "Home";

        public MainViewModel()
        {
            // Initialize
        }

        [RelayCommand]
        private void NavigateHome()
        {
            CurrentPage = "Home";
        }

        [RelayCommand]
        private void NavigateProjects()
        {
            CurrentPage = "Projects";
        }
    }
}

