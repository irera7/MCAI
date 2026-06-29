using System.Windows;

namespace ModelCreator.UI.Services
{
    /// <summary>
    /// Theme service interface
    /// </summary>
    public interface IThemeService
    {
        void SetTheme(string themeName);
        void ToggleTheme();
        string CurrentTheme { get; }
    }

    /// <summary>
    /// Theme service for managing application themes
    /// </summary>
    public class ThemeService : IThemeService
    {
        private string _currentTheme = "Light";

        public string CurrentTheme => _currentTheme;

        /// <summary>
        /// Set application theme
        /// </summary>
        public void SetTheme(string themeName)
        {
            _currentTheme = themeName;

            // Theme colors
            var resources = Application.Current.Resources;
            
            if (themeName == "Dark")
            {
                // Dark theme colors
                resources["BackgroundBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#121212"));
                resources["SurfaceBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#1E1E1E"));
                resources["TextPrimaryBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#FFFFFF"));
                resources["TextSecondaryBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#B0B0B0"));
                resources["BorderBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#333333"));
            }
            else
            {
                // Light theme colors (default)
                resources["BackgroundBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#FAFAFA"));
                resources["SurfaceBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#FFFFFF"));
                resources["TextPrimaryBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#212121"));
                resources["TextSecondaryBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#757575"));
                resources["BorderBrush"] = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#E0E0E0"));
            }
        }

        /// <summary>
        /// Toggle between light and dark themes
        /// </summary>
        public void ToggleTheme()
        {
            SetTheme(_currentTheme == "Light" ? "Dark" : "Light");
        }
    }
}

