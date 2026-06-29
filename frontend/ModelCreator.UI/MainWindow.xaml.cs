using ModelCreator.UI.ViewModels;
using ModelCreator.UI.Views;
using ModelCreator.UI.Services;
using System.Windows;
using System.Windows.Controls;

namespace ModelCreator.UI
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// Main application window with navigation
    /// </summary>
    public partial class MainWindow : Window
    {
        private readonly IThemeService _themeService;
        private ContextMenu? _dataTypesMenu;
        private ContextMenu? _featuresMenu;

        public MainWindow(MainViewModel viewModel, IThemeService themeService)
        {
            InitializeComponent();
            DataContext = viewModel;
            _themeService = themeService;

            // Navigate to home page on startup
            MainFrame.Navigate(new HomePage());

            // Initialize context menus
            InitializeMenus();
        }

        /// <summary>
        /// Initialize dropdown menus
        /// </summary>
        private void InitializeMenus()
        {
            // Data Types Menu
            _dataTypesMenu = new ContextMenu();
            _dataTypesMenu.Items.Add(CreateMenuItem("📷 Image Classification", () => MainFrame.Navigate(new CreateProjectPage())));
            _dataTypesMenu.Items.Add(CreateMenuItem("📝 Text Classification", () => MainFrame.Navigate(new TextProjectPage())));
            _dataTypesMenu.Items.Add(CreateMenuItem("🎵 Audio Classification", () => MainFrame.Navigate(new AudioProjectPage())));
            _dataTypesMenu.Items.Add(CreateMenuItem("🎬 Video Classification", () => MainFrame.Navigate(new VideoProjectPage())));
            _dataTypesMenu.Items.Add(CreateMenuItem("📊 Tabular Data", () => MainFrame.Navigate(new TabularProjectPage())));
            _dataTypesMenu.Items.Add(CreateMenuItem("📈 Time Series", () => MainFrame.Navigate(new TimeSeriesProjectPage())));
            _dataTypesMenu.Items.Add(CreateMenuItem("🏥 Medical Imaging", () => MainFrame.Navigate(new MedicalProjectPage())));
            _dataTypesMenu.Items.Add(CreateMenuItem("🧬 Genomic Analysis", () => MainFrame.Navigate(new GenomicProjectPage())));

            // Features Menu
            _featuresMenu = new ContextMenu();
            _featuresMenu.Items.Add(CreateMenuItem("📊 Model Comparison", () => MainFrame.Navigate(new ModelComparisonPage())));
            _featuresMenu.Items.Add(CreateMenuItem("🔗 Ensemble Methods", () => MainFrame.Navigate(new EnsembleMethodsPage())));
            _featuresMenu.Items.Add(CreateMenuItem("☁️ Cloud Training", () => MainFrame.Navigate(new CloudTrainingPage())));
            _featuresMenu.Items.Add(CreateMenuItem("👥 Collaboration", () => MainFrame.Navigate(new CollaborationPage())));
            _featuresMenu.Items.Add(new Separator());
            _featuresMenu.Items.Add(CreateMenuItem("🤖 AutoML (في Training)", () => 
                MessageBox.Show("AutoML با Optuna در صفحه Training موجود است.", "AutoML", MessageBoxButton.OK, MessageBoxImage.Information)));
            _featuresMenu.Items.Add(CreateMenuItem("⚡ Real-time API", () => 
                MessageBox.Show("Real-time API: http://localhost:8000/api/realtime/", "API", MessageBoxButton.OK, MessageBoxImage.Information)));
        }

        /// <summary>
        /// Create menu item with action
        /// </summary>
        private MenuItem CreateMenuItem(string header, System.Action action)
        {
            var menuItem = new MenuItem { Header = header };
            menuItem.Click += (s, e) => action();
            return menuItem;
        }

        /// <summary>
        /// Navigate to home page
        /// </summary>
        private void HomeButton_Click(object sender, RoutedEventArgs e)
        {
            MainFrame.Navigate(new HomePage());
        }

        /// <summary>
        /// Navigate to projects page
        /// </summary>
        private void ProjectsButton_Click(object sender, RoutedEventArgs e)
        {
            MainFrame.Navigate(new ProjectsPage());
        }

        /// <summary>
        /// Show Data Types dropdown menu
        /// </summary>
        private void DataTypesMenu_Click(object sender, RoutedEventArgs e)
        {
            if (_dataTypesMenu != null && sender is Button button)
            {
                _dataTypesMenu.PlacementTarget = button;
                _dataTypesMenu.Placement = System.Windows.Controls.Primitives.PlacementMode.Bottom;
                _dataTypesMenu.IsOpen = true;
            }
        }

        /// <summary>
        /// Show Features dropdown menu
        /// </summary>
        private void FeaturesMenu_Click(object sender, RoutedEventArgs e)
        {
            if (_featuresMenu != null && sender is Button button)
            {
                _featuresMenu.PlacementTarget = button;
                _featuresMenu.Placement = System.Windows.Controls.Primitives.PlacementMode.Bottom;
                _featuresMenu.IsOpen = true;
            }
        }

        /// <summary>
        /// Navigate to help page
        /// </summary>
        private void HelpButton_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Help documentation coming soon!", "Help", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        /// <summary>
        /// Navigate to Debug Dashboard page
        /// صفحه Debug برای تست Training Dashboard
        /// </summary>
        private void DebugButton_Click(object sender, RoutedEventArgs e)
        {
            MainFrame.Navigate(new DashboardDebugPage());
        }

        /// <summary>
        /// Toggle between light and dark themes
        /// </summary>
        private void ThemeToggle_Click(object sender, RoutedEventArgs e)
        {
            _themeService.ToggleTheme();
        }
    }
}

