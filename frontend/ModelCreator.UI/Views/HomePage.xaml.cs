using System.Windows;
using System.Windows.Controls;
using System;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Interaction logic for HomePage.xaml
    /// Home page with quick actions and features overview
    /// </summary>
    public partial class HomePage : Page
    {
        public HomePage()
        {
            InitializeComponent();
        }

        // ============================================
        // Data Type Navigation Methods
        // ============================================

        /// <summary>
        /// Navigate to Image Classification project
        /// </summary>
        private void ImageProject_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new CreateProjectPage());
        }

        /// <summary>
        /// Navigate to Text Classification project
        /// </summary>
        private void TextProject_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new TextProjectPage());
        }

        /// <summary>
        /// Navigate to Audio Classification project
        /// </summary>
        private void AudioProject_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new AudioProjectPage());
        }

        /// <summary>
        /// Navigate to Video Classification project
        /// </summary>
        private void VideoProject_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new VideoProjectPage());
        }

        /// <summary>
        /// Navigate to Tabular Data project
        /// </summary>
        private void TabularProject_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new TabularProjectPage());
        }

        /// <summary>
        /// Navigate to Time Series project
        /// </summary>
        private void TimeSeriesProject_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new TimeSeriesProjectPage());
        }

        /// <summary>
        /// Navigate to Medical project
        /// انتقال به پروژه پزشکی
        /// </summary>
        private void MedicalProject_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var window = Window.GetWindow(this) as MainWindow;
                if (window == null)
                {
                    MessageBox.Show("خطا: پنجره اصلی پیدا نشد.\nError: Main window not found.", 
                        "Navigation Error", 
                        MessageBoxButton.OK, 
                        MessageBoxImage.Error);
                    return;
                }

                if (window.MainFrame == null)
                {
                    MessageBox.Show("خطا: Frame اصلی پیدا نشد.\nError: Main frame not found.", 
                        "Navigation Error", 
                        MessageBoxButton.OK, 
                        MessageBoxImage.Error);
                    return;
                }

                var medicalPage = new MedicalProjectPage();
                window.MainFrame.Navigate(medicalPage);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"خطا در باز کردن صفحه پزشکی:\n{ex.Message}\n\nStack Trace:\n{ex.StackTrace}", 
                    "Error", 
                    MessageBoxButton.OK, 
                    MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Navigate to Genomic project
        /// انتقال به پروژه ژنومی
        /// </summary>
        private void GenomicProject_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var window = Window.GetWindow(this) as MainWindow;
                if (window == null)
                {
                    MessageBox.Show("خطا: پنجره اصلی پیدا نشد.\nError: Main window not found.", 
                        "Navigation Error", 
                        MessageBoxButton.OK, 
                        MessageBoxImage.Error);
                    return;
                }

                if (window.MainFrame == null)
                {
                    MessageBox.Show("خطا: Frame اصلی پیدا نشد.\nError: Main frame not found.", 
                        "Navigation Error", 
                        MessageBoxButton.OK, 
                        MessageBoxImage.Error);
                    return;
                }

                var genomicPage = new GenomicProjectPage();
                window.MainFrame.Navigate(genomicPage);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"خطا در باز کردن صفحه ژنومیک:\n{ex.Message}\n\nStack Trace:\n{ex.StackTrace}", 
                    "Error", 
                    MessageBoxButton.OK, 
                    MessageBoxImage.Error);
            }
        }

        /// <summary>
        /// Navigate to Model Comparison
        /// </summary>
        private void ModelComparison_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new ModelComparisonPage());
        }

        /// <summary>
        /// Navigate to Ensemble Methods
        /// </summary>
        private void EnsembleMethods_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new EnsembleMethodsPage());
        }

        /// <summary>
        /// Navigate to Cloud Training
        /// </summary>
        private void CloudTraining_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new CloudTrainingPage());
        }

        /// <summary>
        /// Navigate to Collaboration
        /// </summary>
        private void Collaboration_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new CollaborationPage());
        }

        // ============================================
        // Additional Feature Navigation Methods
        // ============================================

        /// <summary>
        /// Navigate to AutoML
        /// </summary>
        private void AutoML_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new AutoMLPage());
        }

        /// <summary>
        /// Navigate to Model Serving
        /// </summary>
        private void ModelServing_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new ModelServingPage());
        }

        /// <summary>
        /// Navigate to Data Preview
        /// </summary>
        private void DataPreview_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new DataPreviewPage());
        }

        /// <summary>
        /// Navigate to Real-time Inference
        /// </summary>
        private void Inference_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Real-time Inference API در بکند در حال اجرا است.\n\nEndpoint: http://localhost:8000/api/realtime/", 
                "Real-time API", 
                MessageBoxButton.OK, 
                MessageBoxImage.Information);
        }

        /// <summary>
        /// Navigate to Dashboard Debug Tool
        /// </summary>
        private void DashboardDebug_Click(object sender, RoutedEventArgs e)
        {
            var window = Window.GetWindow(this) as MainWindow;
            window?.MainFrame.Navigate(new DashboardDebugPage());
        }
    }
}
