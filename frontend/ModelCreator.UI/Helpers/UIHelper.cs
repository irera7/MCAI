using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Animation;

namespace ModelCreator.UI.Helpers
{
    /// <summary>
    /// UI Helper برای Loading states, Tooltips و Validation
    /// </summary>
    public static class UIHelper
    {
        // ============================================
        // Loading States
        // ============================================
        
        /// <summary>
        /// نمایش loading indicator
        /// </summary>
        public static void ShowLoading(ContentControl loadingPanel, string message = "Loading...")
        {
            if (loadingPanel != null)
            {
                loadingPanel.Content = CreateLoadingContent(message);
                loadingPanel.Visibility = Visibility.Visible;
                
                // Fade in animation
                var fadeIn = new DoubleAnimation(0, 1, TimeSpan.FromMilliseconds(300));
                loadingPanel.BeginAnimation(UIElement.OpacityProperty, fadeIn);
            }
        }
        
        /// <summary>
        /// مخفی کردن loading indicator
        /// </summary>
        public static void HideLoading(ContentControl loadingPanel)
        {
            if (loadingPanel != null)
            {
                // Fade out animation
                var fadeOut = new DoubleAnimation(1, 0, TimeSpan.FromMilliseconds(300));
                fadeOut.Completed += (s, e) => loadingPanel.Visibility = Visibility.Collapsed;
                loadingPanel.BeginAnimation(UIElement.OpacityProperty, fadeOut);
            }
        }
        
        private static StackPanel CreateLoadingContent(string message)
        {
            var panel = new StackPanel
            {
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center
            };
            
            // Spinner
            var spinner = new TextBlock
            {
                Text = "⏳",
                FontSize = 48,
                HorizontalAlignment = HorizontalAlignment.Center,
                Margin = new Thickness(0, 0, 0, 10)
            };
            
            // Rotate animation
            var rotate = new DoubleAnimation(0, 360, TimeSpan.FromSeconds(2))
            {
                RepeatBehavior = RepeatBehavior.Forever
            };
            var rotateTransform = new RotateTransform();
            spinner.RenderTransform = rotateTransform;
            spinner.RenderTransformOrigin = new Point(0.5, 0.5);
            rotateTransform.BeginAnimation(RotateTransform.AngleProperty, rotate);
            
            // Message
            var messageText = new TextBlock
            {
                Text = message,
                FontSize = 16,
                HorizontalAlignment = HorizontalAlignment.Center,
                Foreground = Brushes.Gray
            };
            
            panel.Children.Add(spinner);
            panel.Children.Add(messageText);
            
            return panel;
        }
        
        // ============================================
        // Validation Messages
        // ============================================
        
        /// <summary>
        /// نمایش validation error
        /// </summary>
        public static void ShowValidationError(TextBlock errorText, string message)
        {
            if (errorText != null)
            {
                errorText.Text = $"⚠️ {message}";
                errorText.Foreground = Brushes.Red;
                errorText.Visibility = Visibility.Visible;
                
                // Shake animation
                var shake = CreateShakeAnimation();
                errorText.RenderTransform = new TranslateTransform();
                errorText.RenderTransform.BeginAnimation(TranslateTransform.XProperty, shake);
            }
        }
        
        /// <summary>
        /// نمایش validation success
        /// </summary>
        public static void ShowValidationSuccess(TextBlock errorText, string message)
        {
            if (errorText != null)
            {
                errorText.Text = $"✅ {message}";
                errorText.Foreground = Brushes.Green;
                errorText.Visibility = Visibility.Visible;
            }
        }
        
        /// <summary>
        /// پاک کردن validation message
        /// </summary>
        public static void ClearValidation(TextBlock errorText)
        {
            if (errorText != null)
            {
                errorText.Visibility = Visibility.Collapsed;
            }
        }
        
        private static DoubleAnimationUsingKeyFrames CreateShakeAnimation()
        {
            var animation = new DoubleAnimationUsingKeyFrames();
            animation.KeyFrames.Add(new EasingDoubleKeyFrame(0, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(0))));
            animation.KeyFrames.Add(new EasingDoubleKeyFrame(10, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(50))));
            animation.KeyFrames.Add(new EasingDoubleKeyFrame(-10, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(100))));
            animation.KeyFrames.Add(new EasingDoubleKeyFrame(10, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(150))));
            animation.KeyFrames.Add(new EasingDoubleKeyFrame(0, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(200))));
            return animation;
        }
        
        // ============================================
        // Tooltips
        // ============================================
        
        /// <summary>
        /// اضافه کردن tooltip به یک control
        /// </summary>
        public static void AddTooltip(FrameworkElement element, string tooltipText, string description = "")
        {
            if (element == null || string.IsNullOrEmpty(tooltipText))
                return;
            
            var tooltipPanel = new StackPanel { MaxWidth = 300 };
            
            // Title
            tooltipPanel.Children.Add(new TextBlock
            {
                Text = tooltipText,
                FontWeight = FontWeights.Bold,
                FontSize = 13,
                Margin = new Thickness(0, 0, 0, 5),
                TextWrapping = TextWrapping.Wrap
            });
            
            // Description
            if (!string.IsNullOrEmpty(description))
            {
                tooltipPanel.Children.Add(new TextBlock
                {
                    Text = description,
                    FontSize = 11,
                    Foreground = Brushes.Gray,
                    TextWrapping = TextWrapping.Wrap
                });
            }
            
            var tooltip = new ToolTip
            {
                Content = tooltipPanel,
                Placement = System.Windows.Controls.Primitives.PlacementMode.Mouse,
                HasDropShadow = true
            };
            
            element.ToolTip = tooltip;
        }
        
        // ============================================
        // Progress Indicators
        // ============================================
        
        /// <summary>
        /// به‌روزرسانی progress bar با animation
        /// </summary>
        public static void UpdateProgress(ProgressBar progressBar, double newValue, double duration = 500)
        {
            if (progressBar == null)
                return;
            
            var animation = new DoubleAnimation
            {
                From = progressBar.Value,
                To = newValue,
                Duration = TimeSpan.FromMilliseconds(duration),
                EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
            };
            
            progressBar.BeginAnimation(ProgressBar.ValueProperty, animation);
        }
        
        // ============================================
        // Button States
        // ============================================
        
        /// <summary>
        /// تنظیم وضعیت loading برای button
        /// </summary>
        public static void SetButtonLoading(Button button, bool isLoading, string loadingText = "⏳ Loading...", string normalText = "Submit")
        {
            if (button == null)
                return;
            
            button.IsEnabled = !isLoading;
            button.Content = isLoading ? loadingText : normalText;
            button.Cursor = isLoading ? System.Windows.Input.Cursors.Wait : System.Windows.Input.Cursors.Hand;
        }
        
        // ============================================
        // Error Dialogs
        // ============================================
        
        /// <summary>
        /// نمایش error dialog با جزئیات بیشتر
        /// </summary>
        public static void ShowErrorDialog(string title, string message, string details = "")
        {
            var messageText = message;
            if (!string.IsNullOrEmpty(details))
            {
                messageText += $"\n\nDetails:\n{details}";
            }
            
            MessageBox.Show(
                messageText,
                title,
                MessageBoxButton.OK,
                MessageBoxImage.Error
            );
        }
        
        /// <summary>
        /// نمایش success dialog
        /// </summary>
        public static void ShowSuccessDialog(string title, string message)
        {
            MessageBox.Show(
                message,
                title,
                MessageBoxButton.OK,
                MessageBoxImage.Information
            );
        }
        
        /// <summary>
        /// نمایش confirmation dialog
        /// </summary>
        public static bool ShowConfirmDialog(string title, string message)
        {
            var result = MessageBox.Show(
                message,
                title,
                MessageBoxButton.YesNo,
                MessageBoxImage.Question
            );
            
            return result == MessageBoxResult.Yes;
        }
        
        // ============================================
        // Input Validation
        // ============================================
        
        /// <summary>
        /// Validate کردن required field
        /// </summary>
        public static bool ValidateRequired(TextBox textBox, string fieldName, TextBlock errorDisplay)
        {
            if (string.IsNullOrWhiteSpace(textBox?.Text))
            {
                ShowValidationError(errorDisplay, $"{fieldName} is required");
                textBox?.Focus();
                return false;
            }
            
            ClearValidation(errorDisplay);
            return true;
        }
        
        /// <summary>
        /// Validate کردن number
        /// </summary>
        public static bool ValidateNumber(TextBox textBox, string fieldName, TextBlock errorDisplay, double? min = null, double? max = null)
        {
            if (!double.TryParse(textBox?.Text, out double value))
            {
                ShowValidationError(errorDisplay, $"{fieldName} must be a valid number");
                textBox?.Focus();
                return false;
            }
            
            if (min.HasValue && value < min.Value)
            {
                ShowValidationError(errorDisplay, $"{fieldName} must be at least {min.Value}");
                textBox?.Focus();
                return false;
            }
            
            if (max.HasValue && value > max.Value)
            {
                ShowValidationError(errorDisplay, $"{fieldName} must be at most {max.Value}");
                textBox?.Focus();
                return false;
            }
            
            ClearValidation(errorDisplay);
            return true;
        }
        
        /// <summary>
        /// Validate کردن email
        /// </summary>
        public static bool ValidateEmail(TextBox textBox, TextBlock errorDisplay)
        {
            var email = textBox?.Text ?? "";
            if (string.IsNullOrWhiteSpace(email) || !email.Contains("@") || !email.Contains("."))
            {
                ShowValidationError(errorDisplay, "Please enter a valid email address");
                textBox?.Focus();
                return false;
            }
            
            ClearValidation(errorDisplay);
            return true;
        }
    }
}

