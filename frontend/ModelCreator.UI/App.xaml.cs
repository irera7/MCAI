using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using ModelCreator.UI.Services;
using ModelCreator.UI.ViewModels;
using System.Windows;

namespace ModelCreator.UI
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// Main application entry point with dependency injection setup
    /// </summary>
    public partial class App : Application
    {
        private readonly IHost _host;

        public App()
        {
            // Configure dependency injection and services
            _host = Host.CreateDefaultBuilder()
                .ConfigureServices((context, services) =>
                {
                    // Register services
                    services.AddSingleton<IApiService, ApiService>();
                    services.AddSingleton<IWebSocketService, WebSocketService>();
                    services.AddSingleton<IProjectService, ProjectService>();
                    services.AddSingleton<IThemeService, ThemeService>();
                    
                    // Register ViewModels
                    services.AddTransient<MainViewModel>();
                    services.AddTransient<HomeViewModel>();
                    services.AddTransient<ProjectViewModel>();
                    services.AddTransient<DataImportViewModel>();
                    services.AddTransient<ModelSelectionViewModel>();
                    services.AddTransient<TrainingConfigViewModel>();
                    services.AddTransient<TrainingDashboardViewModel>();
                    services.AddTransient<InferenceViewModel>();
                    
                    // Register Windows
                    services.AddSingleton<MainWindow>();
                })
                .Build();
        }

        protected override async void OnStartup(StartupEventArgs e)
        {
            // Setup unhandled exception handlers
            AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;
            DispatcherUnhandledException += App_DispatcherUnhandledException;
            
            await _host.StartAsync();

            try
            {
                // Get main window and show it
                var mainWindow = _host.Services.GetRequiredService<MainWindow>();
                mainWindow.Show();
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"خطا در راه‌اندازی برنامه:\n\n{ex.Message}\n\nلطفاً مطمئن شوید که Backend روی http://127.0.0.1:8181 در حال اجرا است.",
                    "خطای راه‌اندازی",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
                Shutdown();
            }

            base.OnStartup(e);
        }

        private void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            if (e.ExceptionObject is Exception ex)
            {
                MessageBox.Show(
                    $"خطای غیرمنتظره:\n\n{ex.Message}",
                    "خطا",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error
                );
            }
        }

        private void App_DispatcherUnhandledException(object sender, System.Windows.Threading.DispatcherUnhandledExceptionEventArgs e)
        {
            MessageBox.Show(
                $"خطا در برنامه:\n\n{e.Exception.Message}\n\nبرنامه ممکن است ناپایدار شود.",
                "خطا",
                MessageBoxButton.OK,
                MessageBoxImage.Error
            );
            e.Handled = true;
        }

        protected override async void OnExit(ExitEventArgs e)
        {
            using (_host)
            {
                await _host.StopAsync();
            }

            base.OnExit(e);
        }

        /// <summary>
        /// Get service from dependency injection container
        /// </summary>
        public static T GetService<T>() where T : class
        {
            return ((App)Current)._host.Services.GetRequiredService<T>();
        }
    }
}

