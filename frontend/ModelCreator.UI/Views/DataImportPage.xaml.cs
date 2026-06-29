using Microsoft.Win32;
using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace ModelCreator.UI.Views
{
    /// <summary>
    /// Data Import Page - Import and label training data
    /// </summary>
    public partial class DataImportPage : Page
    {
        public class DataItem : INotifyPropertyChanged
        {
            private string? _label;

            public string FileName { get; set; } = string.Empty;
            public string FilePath { get; set; } = string.Empty;
            
            public string? Label
            {
                get => _label;
                set
                {
                    if (_label != value)
                    {
                        _label = value;
                        OnPropertyChanged(nameof(Label));
                    }
                }
            }

            public event PropertyChangedEventHandler? PropertyChanged;

            protected void OnPropertyChanged(string propertyName)
            {
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
            }
        }

        public class LabelItem : INotifyPropertyChanged
        {
            private string _name = string.Empty;
            private int _count;

            public string Name
            {
                get => _name;
                set
                {
                    if (_name != value)
                    {
                        _name = value;
                        OnPropertyChanged(nameof(Name));
                    }
                }
            }

            public int Count
            {
                get => _count;
                set
                {
                    if (_count != value)
                    {
                        _count = value;
                        OnPropertyChanged(nameof(Count));
                    }
                }
            }

            public event PropertyChangedEventHandler? PropertyChanged;

            protected void OnPropertyChanged(string propertyName)
            {
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
            }
        }

        private ObservableCollection<DataItem> dataItems = new ObservableCollection<DataItem>();
        private ObservableCollection<string> labels = new ObservableCollection<string>();
        private ObservableCollection<LabelItem> labelItems = new ObservableCollection<LabelItem>();
        private string projectId;
        private string modality;

        public ObservableCollection<string> Labels => labels;

        public DataImportPage(string projectId, string projectName, string modality)
        {
            InitializeComponent();
            this.projectId = projectId;
            this.modality = modality;
            
            // Set DataContext to this page so bindings work
            this.DataContext = this;
            
            ProjectDescText.Text = $"پروژه: {projectName} | نوع: {GetModalityDisplay(modality)}";
            
            DataListBox.ItemsSource = dataItems;
            LabelsListBox.ItemsSource = labelItems;
            
            // Load existing data from project directory
            LoadExistingData();
            
            // Add default labels only if none were loaded
            if (labels.Count == 0)
            {
                AddDefaultLabels();
            }
            
            UpdateStatistics();
            
            // Show instruction message only if no data exists
            if (dataItems.Count == 0)
            {
                MessageBox.Show(
                    "راهنما:\n\n" +
                    "1. ابتدا لیبل‌های مورد نیاز را در سمت راست اضافه کنید\n" +
                    "2. سپس فایل‌ها را Drag & Drop کنید یا با دکمه Browse اضافه کنید\n" +
                    "3. برای هر فایل از منوی کشویی یک لیبل انتخاب کنید\n" +
                    "4. حداقل 2 لیبل و 50% داده‌های لیبل‌گذاری شده نیاز است",
                    "راهنمای Import داده",
                    MessageBoxButton.OK,
                    MessageBoxImage.Information
                );
            }
            else
            {
                MessageBox.Show(
                    $"✅ پروژه موجود بارگذاری شد!\n\n" +
                    $"📊 داده‌های موجود:\n" +
                    $"  • {dataItems.Count} فایل\n" +
                    $"  • {labels.Count} لیبل\n\n" +
                    "می‌توانید داده بیشتر اضافه کنید یا به مرحله بعد بروید.",
                    "بارگذاری پروژه",
                    MessageBoxButton.OK,
                    MessageBoxImage.Information
                );
            }
        }

        private string GetModalityDisplay(string modality)
        {
            return modality switch
            {
                "image" => "Image Classification",
                "text" => "Text Classification",
                "audio" => "Audio Classification",
                "video" => "Video Classification",
                "tabular" => "Tabular Data",
                "timeseries" => "Time Series",
                "medical" => "Medical Data",
                "genomic" => "Genomic Data",
                _ => modality
            };
        }

        private void LoadExistingData()
        {
            try
            {
                // Get project directory - use absolute path
                string solutionDir = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", ".."));
                string projectsDir = Path.Combine(solutionDir, "projects");
                string projectDir = Path.Combine(projectsDir, projectId);
                string dataDir = Path.Combine(projectDir, "data");
                
                System.Diagnostics.Debug.WriteLine($"Loading existing data from: {dataDir}");
                
                // Check if data directory exists
                if (!Directory.Exists(dataDir))
                {
                    System.Diagnostics.Debug.WriteLine("Data directory does not exist");
                    return;
                }
                
                // Load labels from labels.json if exists
                string labelsFile = Path.Combine(projectDir, "labels.json");
                if (File.Exists(labelsFile))
                {
                    try
                    {
                        string json = File.ReadAllText(labelsFile, System.Text.Encoding.UTF8);
                        var labelMapping = System.Text.Json.JsonSerializer.Deserialize<System.Collections.Generic.Dictionary<string, int>>(json);
                        
                        if (labelMapping != null)
                        {
                            foreach (var labelName in labelMapping.Keys.OrderBy(k => labelMapping[k]))
                            {
                                AddLabel(labelName);
                            }
                            System.Diagnostics.Debug.WriteLine($"Loaded {labels.Count} labels from labels.json");
                        }
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Error loading labels.json: {ex.Message}");
                    }
                }
                
                // Load files from data directory
                var extensions = GetFileExtensions();
                int loadedCount = 0;
                
                // Check for subdirectories (one per label)
                var subdirs = Directory.GetDirectories(dataDir);
                
                if (subdirs.Length > 0)
                {
                    // Load from subdirectories
                    foreach (var subdir in subdirs)
                    {
                        string labelName = Path.GetFileName(subdir);
                        
                        // Add label if not already exists
                        if (!labels.Contains(labelName))
                        {
                            AddLabel(labelName);
                        }
                        
                        // Load files from this label directory
                        var files = Directory.GetFiles(subdir)
                            .Where(f => extensions.Any(ext => f.EndsWith(ext, StringComparison.OrdinalIgnoreCase)))
                            .ToList();
                        
                        foreach (var file in files)
                        {
                            dataItems.Add(new DataItem
                            {
                                FileName = Path.GetFileName(file),
                                FilePath = file,
                                Label = labelName
                            });
                            loadedCount++;
                        }
                        
                        System.Diagnostics.Debug.WriteLine($"Loaded {files.Count} files from {labelName}/");
                    }
                }
                else
                {
                    // Load files from root data directory
                    var files = Directory.GetFiles(dataDir)
                        .Where(f => extensions.Any(ext => f.EndsWith(ext, StringComparison.OrdinalIgnoreCase)))
                        .ToList();
                    
                    foreach (var file in files)
                    {
                        dataItems.Add(new DataItem
                        {
                            FileName = Path.GetFileName(file),
                            FilePath = file,
                            Label = null  // Will need to be labeled
                        });
                        loadedCount++;
                    }
                    
                    System.Diagnostics.Debug.WriteLine($"Loaded {files.Count} files from root directory");
                }
                
                System.Diagnostics.Debug.WriteLine($"=== Load Summary ===");
                System.Diagnostics.Debug.WriteLine($"Total labels: {labels.Count}");
                System.Diagnostics.Debug.WriteLine($"Total files: {loadedCount}");
                System.Diagnostics.Debug.WriteLine($"Labeled files: {dataItems.Count(d => !string.IsNullOrEmpty(d.Label))}");
                
                UpdateLabelCounts();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading existing data: {ex.Message}");
                MessageBox.Show(
                    $"خطا در بارگذاری داده‌های موجود:\n\n{ex.Message}\n\nپروژه خالی بارگذاری می‌شود.",
                    "خطا در بارگذاری",
                    MessageBoxButton.OK,
                    MessageBoxImage.Warning
                );
            }
        }

        private void AddDefaultLabels()
        {
            // Add example labels based on modality
            switch (modality)
            {
                case "image":
                    AddLabel("Class_A");
                    AddLabel("Class_B");
                    break;
                case "text":
                    AddLabel("Positive");
                    AddLabel("Negative");
                    break;
                default:
                    AddLabel("Label_1");
                    AddLabel("Label_2");
                    break;
            }
        }

        private void AddLabel(string labelName)
        {
            if (!string.IsNullOrWhiteSpace(labelName) && !labels.Contains(labelName))
            {
                labels.Add(labelName);
                labelItems.Add(new LabelItem { Name = labelName, Count = 0 });
            }
        }

        private void AddLabel_Click(object sender, RoutedEventArgs e)
        {
            string newLabel = NewLabelTextBox.Text.Trim();
            if (!string.IsNullOrWhiteSpace(newLabel))
            {
                if (labels.Contains(newLabel))
                {
                    MessageBox.Show("این لیبل قبلاً اضافه شده است!", "لیبل تکراری", 
                        MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }
                
                AddLabel(newLabel);
                NewLabelTextBox.Clear();
                NewLabelTextBox.Focus();
                UpdateStatistics();
                
                MessageBox.Show(
                    $"لیبل '{newLabel}' با موفقیت اضافه شد!\n\nحالا می‌توانید در لیست فایل‌ها، این لیبل را به فایل‌ها اختصاص دهید.",
                    "موفق",
                    MessageBoxButton.OK,
                    MessageBoxImage.Information
                );
            }
            else
            {
                MessageBox.Show("لطفاً نام لیبل را وارد کنید.", "خطا", 
                    MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }

        private void RemoveLabel_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is LabelItem labelItem)
            {
                if (labelItem.Count > 0)
                {
                    var result = MessageBox.Show(
                        $"Label '{labelItem.Name}' is assigned to {labelItem.Count} samples. Remove anyway?",
                        "Confirm Removal", MessageBoxButton.YesNo, MessageBoxImage.Warning);
                    
                    if (result != MessageBoxResult.Yes)
                        return;
                }
                
                labels.Remove(labelItem.Name);
                labelItems.Remove(labelItem);
                
                // Clear label from data items
                foreach (var item in dataItems.Where(d => d.Label == labelItem.Name))
                {
                    item.Label = null;
                }
                
                UpdateStatistics();
                UpdateLabelCounts();
            }
        }

        private void BrowseFiles_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Multiselect = true,
                Filter = GetFileFilter()
            };

            if (openFileDialog.ShowDialog() == true)
            {
                foreach (string filename in openFileDialog.FileNames)
                {
                    AddFile(filename);
                }
            }
        }

        private void BrowseFolder_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new Microsoft.Win32.OpenFileDialog
            {
                Title = "Select any file in the folder (folder will be imported)",
                CheckFileExists = false,
                CheckPathExists = true
            };
            
            if (dialog.ShowDialog() == true && !string.IsNullOrEmpty(dialog.FileName))
            {
                var folderPath = System.IO.Path.GetDirectoryName(dialog.FileName);
                if (!string.IsNullOrEmpty(folderPath))
                {
                    ImportFolder(folderPath);
                }
            }
        }

        private void ImportCSV_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Title = "انتخاب فایل CSV برای لیبل‌گذاری خودکار",
                Filter = "CSV files|*.csv|All files|*.*",
                Multiselect = false
            };

            if (openFileDialog.ShowDialog() == true)
            {
                try
                {
                    ImportLabelsFromCSV(openFileDialog.FileName);
                }
                catch (Exception ex)
                {
                    MessageBox.Show(
                        $"خطا در خواندن فایل CSV:\n\n{ex.Message}\n\n" +
                        "فرمت مورد انتظار:\n" +
                        "filename,label\n" +
                        "Image_1.jpg,Class_A\n" +
                        "Image_2.jpg,Class_B",
                        "خطا در Import CSV",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error
                    );
                }
            }
        }

        private void ImportFolder(string folderPath)
        {
            try
            {
                var extensions = GetFileExtensions();
                var files = Directory.GetFiles(folderPath, "*.*", SearchOption.AllDirectories)
                    .Where(f => extensions.Any(ext => f.EndsWith(ext, StringComparison.OrdinalIgnoreCase)));
                
                int count = 0;
                foreach (var file in files)
                {
                    AddFile(file);
                    count++;
                }
                
                MessageBox.Show(
                    $"{count} فایل با موفقیت import شد!\n\nحالا برای هر فایل از منوی کشویی یک لیبل انتخاب کنید.", 
                    "Import کامل شد", 
                    MessageBoxButton.OK, 
                    MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error importing folder: {ex.Message}", "Import Error", 
                    MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void ImportLabelsFromCSV(string csvFilePath)
        {
            // Ask user to select the images directory
            var folderDialog = new Microsoft.Win32.OpenFileDialog
            {
                Title = "پوشه تصاویر را انتخاب کنید (یک فایل از داخل پوشه را انتخاب کنید)",
                CheckFileExists = false,
                CheckPathExists = true
            };
            
            if (folderDialog.ShowDialog() != true || string.IsNullOrEmpty(folderDialog.FileName))
            {
                MessageBox.Show("لطفاً پوشه تصاویر را انتخاب کنید.", "لغو شد", 
                    MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }
            
            var imageFolder = System.IO.Path.GetDirectoryName(folderDialog.FileName);
            if (string.IsNullOrEmpty(imageFolder))
            {
                throw new Exception("پوشه نامعتبر است.");
            }
            
            System.Diagnostics.Debug.WriteLine($"CSV File: {csvFilePath}");
            System.Diagnostics.Debug.WriteLine($"Image Folder: {imageFolder}");
            
            // Read CSV file with proper encoding
            var lines = File.ReadAllLines(csvFilePath, System.Text.Encoding.UTF8);
            if (lines.Length == 0)
            {
                throw new Exception("فایل CSV خالی است!");
            }
            
            System.Diagnostics.Debug.WriteLine($"Total lines in CSV: {lines.Length}");
            
            // Parse CSV
            var csvData = new System.Collections.Generic.List<(string filename, string label)>();
            bool hasHeader = false;
            
            // Check if first line is header
            var firstLine = lines[0].ToLower();
            System.Diagnostics.Debug.WriteLine($"First line: {firstLine}");
            
            if (firstLine.Contains("filename") || firstLine.Contains("file") || 
                firstLine.Contains("label") || firstLine.Contains("class"))
            {
                hasHeader = true;
                System.Diagnostics.Debug.WriteLine("Header detected, skipping first line");
            }
            
            int startIndex = hasHeader ? 1 : 0;
            int successCount = 0;
            int errorCount = 0;
            var newLabels = new System.Collections.Generic.HashSet<string>();
            
            System.Diagnostics.Debug.WriteLine($"Starting to parse from line {startIndex}");
            
            for (int i = startIndex; i < lines.Length; i++)
            {
                var line = lines[i].Trim();
                if (string.IsNullOrEmpty(line))
                {
                    System.Diagnostics.Debug.WriteLine($"Skipping empty line {i + 1}");
                    continue;
                }
                
                // Split by comma (handle quoted values if needed)
                var parts = line.Split(',');
                if (parts.Length < 2)
                {
                    System.Diagnostics.Debug.WriteLine($"Skipping invalid line {i + 1}: {line} (only {parts.Length} parts)");
                    errorCount++;
                    continue;
                }
                
                string filename = parts[0].Trim().Trim('"');
                string label = parts[1].Trim().Trim('"');
                
                if (string.IsNullOrEmpty(filename) || string.IsNullOrEmpty(label))
                {
                    System.Diagnostics.Debug.WriteLine($"Skipping line {i + 1}: empty filename or label");
                    errorCount++;
                    continue;
                }
                
                csvData.Add((filename, label));
                newLabels.Add(label);
                successCount++;
                
                // Debug first few entries
                if (i < startIndex + 5)
                {
                    System.Diagnostics.Debug.WriteLine($"Parsed line {i + 1}: {filename} -> {label}");
                }
            }
            
            System.Diagnostics.Debug.WriteLine($"Parsed {csvData.Count} entries from CSV (success: {successCount}, errors: {errorCount})");
            System.Diagnostics.Debug.WriteLine($"Found {newLabels.Count} unique labels: {string.Join(", ", newLabels.Take(10))}");
            
            // Add new labels to the labels list
            int addedLabels = 0;
            foreach (var label in newLabels)
            {
                if (!labels.Contains(label))
                {
                    AddLabel(label);
                    addedLabels++;
                    System.Diagnostics.Debug.WriteLine($"Added new label: {label}");
                }
            }
            
            System.Diagnostics.Debug.WriteLine($"Total labels after import: {labels.Count} (added: {addedLabels})");
            
            // Now import files and assign labels
            int filesAdded = 0;
            int labelsAssigned = 0;
            var missingFiles = new System.Collections.Generic.List<string>();
            
            foreach (var (filename, label) in csvData)
            {
                // Try to find the file in the selected folder
                var possiblePaths = new[]
                {
                    Path.Combine(imageFolder, filename),
                    Path.Combine(imageFolder, Path.GetFileName(filename)),
                };
                
                string? foundPath = null;
                foreach (var path in possiblePaths)
                {
                    if (File.Exists(path))
                    {
                        foundPath = path;
                        break;
                    }
                }
                
                // Also search subdirectories
                if (foundPath == null)
                {
                    try
                    {
                        var allFiles = Directory.GetFiles(imageFolder, filename, SearchOption.AllDirectories);
                        if (allFiles.Length > 0)
                        {
                            foundPath = allFiles[0];
                        }
                    }
                    catch
                    {
                        // Ignore search errors
                    }
                }
                
                if (foundPath != null)
                {
                    // Check if file already exists in list
                    var existingItem = dataItems.FirstOrDefault(d => d.FilePath == foundPath);
                    
                    if (existingItem != null)
                    {
                        // Update label of existing item
                        existingItem.Label = label;
                        labelsAssigned++;
                        System.Diagnostics.Debug.WriteLine($"Updated existing item: {filename} -> {label}");
                    }
                    else
                    {
                        // Add new file with label
                        dataItems.Add(new DataItem
                        {
                            FileName = Path.GetFileName(foundPath),
                            FilePath = foundPath,
                            Label = label
                        });
                        filesAdded++;
                        labelsAssigned++;
                        
                        // Debug first few files
                        if (filesAdded <= 5)
                        {
                            System.Diagnostics.Debug.WriteLine($"Added new file: {filename} ({foundPath}) -> {label}");
                        }
                    }
                }
                else
                {
                    missingFiles.Add(filename);
                    
                    // Debug first few missing files
                    if (missingFiles.Count <= 5)
                    {
                        System.Diagnostics.Debug.WriteLine($"File not found: {filename}");
                    }
                }
            }
            
            System.Diagnostics.Debug.WriteLine($"=== Import Summary ===");
            System.Diagnostics.Debug.WriteLine($"Files added: {filesAdded}");
            System.Diagnostics.Debug.WriteLine($"Labels assigned: {labelsAssigned}");
            System.Diagnostics.Debug.WriteLine($"Missing files: {missingFiles.Count}");
            System.Diagnostics.Debug.WriteLine($"Total items in dataItems: {dataItems.Count}");
            
            // IMPORTANT: Update UI
            UpdateStatistics();
            UpdateLabelCounts();
            
            // Show summary
            string message = $"✅ Import از CSV کامل شد!\n\n";
            message += $"📊 آمار:\n";
            message += $"  • تعداد کل در CSV: {csvData.Count} ردیف\n";
            message += $"  • {addedLabels} لیبل جدید اضافه شد\n";
            message += $"  • {filesAdded} فایل جدید اضافه شد\n";
            message += $"  • {labelsAssigned} فایل لیبل‌گذاری شد\n";
            message += $"\n📂 وضعیت فعلی:\n";
            message += $"  • کل فایل‌ها در لیست: {dataItems.Count}\n";
            message += $"  • فایل‌های لیبل‌شده: {dataItems.Count(d => !string.IsNullOrEmpty(d.Label))}\n";
            message += $"  • کل لیبل‌ها: {labels.Count}\n";
            
            if (missingFiles.Count > 0)
            {
                message += $"\n⚠️ {missingFiles.Count} فایل در پوشه انتخابی پیدا نشد!\n";
                message += $"\nاین فایل‌ها ممکن است:\n";
                message += $"  • در پوشه دیگری باشند\n";
                message += $"  • نام‌شان تغییر کرده باشد\n";
                message += $"  • حذف شده باشند\n";
                
                if (missingFiles.Count <= 10)
                {
                    message += $"\nفایل‌های گم شده:\n";
                    foreach (var file in missingFiles)
                    {
                        message += $"  • {file}\n";
                    }
                }
                else
                {
                    message += $"\nنمونه از فایل‌های گم شده:\n";
                    for (int i = 0; i < 5; i++)
                    {
                        message += $"  • {missingFiles[i]}\n";
                    }
                    message += $"  ... و {missingFiles.Count - 5} فایل دیگر\n";
                }
            }
            
            if (filesAdded == 0 && labelsAssigned == 0)
            {
                message += $"\n❌ هیچ فایلی پیدا نشد!\n\n";
                message += $"احتمالاً:\n";
                message += $"  • پوشه اشتباه انتخاب شده است\n";
                message += $"  • نام فایل‌ها در CSV با فایل‌های واقعی مطابقت ندارند\n\n";
                message += $"لطفاً:\n";
                message += $"  1. پوشه‌ای که فایل‌های تصویر در آن هستند را انتخاب کنید\n";
                message += $"  2. مطمئن شوید نام فایل‌ها دقیقاً مطابق CSV است\n";
            }
            
            MessageBox.Show(message, "Import از CSV", 
                MessageBoxButton.OK, 
                filesAdded == 0 ? MessageBoxImage.Warning : 
                (missingFiles.Count > 0 ? MessageBoxImage.Warning : MessageBoxImage.Information));
        }

        private string GetFileFilter()
        {
            return modality switch
            {
                "image" => "Image files|*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff|All files|*.*",
                "audio" => "Audio files|*.wav;*.mp3;*.flac;*.ogg;*.m4a|All files|*.*",
                "video" => "Video files|*.mp4;*.avi;*.mov;*.wmv;*.mkv|All files|*.*",
                "text" => "Text files|*.txt;*.csv;*.json|All files|*.*",
                "tabular" => "Data files|*.csv;*.xlsx;*.xls|All files|*.*",
                "timeseries" => "Data files|*.csv;*.json|All files|*.*",
                "medical" => "Medical files|*.dcm;*.nii;*.nii.gz;*.png;*.jpg|All files|*.*",
                "genomic" => "Sequence files|*.fasta;*.fa;*.fastq;*.txt|All files|*.*",
                _ => "All files|*.*"
            };
        }

        private string[] GetFileExtensions()
        {
            return modality switch
            {
                "image" => new[] { ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff" },
                "audio" => new[] { ".wav", ".mp3", ".flac", ".ogg", ".m4a" },
                "video" => new[] { ".mp4", ".avi", ".mov", ".wmv", ".mkv" },
                "text" => new[] { ".txt", ".csv", ".json" },
                "tabular" => new[] { ".csv", ".xlsx", ".xls" },
                "timeseries" => new[] { ".csv", ".json" },
                "medical" => new[] { ".dcm", ".nii", ".nii.gz", ".png", ".jpg" },
                "genomic" => new[] { ".fasta", ".fa", ".fastq", ".txt" },
                _ => new[] { "*.*" }
            };
        }

        private void AddFile(string filePath)
        {
            if (!dataItems.Any(d => d.FilePath == filePath))
            {
                dataItems.Add(new DataItem
                {
                    FileName = Path.GetFileName(filePath),
                    FilePath = filePath,
                    Label = null
                });
                UpdateStatistics();
            }
        }

        private void RemoveItem_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is DataItem item)
            {
                dataItems.Remove(item);
                UpdateStatistics();
            }
        }

        private void LabelComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (sender is ComboBox comboBox && comboBox.Tag is DataItem item)
            {
                // Debug: Check what's happening
                System.Diagnostics.Debug.WriteLine($"Label changed for {item.FileName} to {item.Label}");
                System.Diagnostics.Debug.WriteLine($"Total items in list: {dataItems.Count}");
                
                // Label is already updated via binding, just update statistics
                UpdateStatistics();
                
                // Also update the label count in the labels list
                UpdateLabelCounts();
                
                // Debug: Check after update
                System.Diagnostics.Debug.WriteLine($"After update - Total items: {dataItems.Count}");
            }
        }

        private void UpdateLabelCounts()
        {
            // Update count for each label
            foreach (var labelItem in labelItems)
            {
                labelItem.Count = dataItems.Count(d => d.Label == labelItem.Name);
            }
            
            // Don't refresh the entire ListBox - INotifyPropertyChanged will handle it!
            // LabelsListBox.Items.Refresh();  // This was causing the bug!
        }

        private void ClearAll_Click(object sender, RoutedEventArgs e)
        {
            if (dataItems.Count == 0)
                return;
            
            var result = MessageBox.Show("Remove all imported data?", "Confirm Clear", 
                MessageBoxButton.YesNo, MessageBoxImage.Question);
            
            if (result == MessageBoxResult.Yes)
            {
                dataItems.Clear();
                UpdateStatistics();
            }
        }

        private void DropZone_Drop(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
                
                foreach (string path in files)
                {
                    if (Directory.Exists(path))
                    {
                        ImportFolder(path);
                    }
                    else if (File.Exists(path))
                    {
                        AddFile(path);
                    }
                }
            }
        }

        private void DropZone_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effects = DragDropEffects.Copy;
            }
            else
            {
                e.Effects = DragDropEffects.None;
            }
        }

        private void DropZone_DragLeave(object sender, DragEventArgs e)
        {
            // Visual feedback when drag leaves
        }

        private void UpdateStatistics()
        {
            int total = dataItems.Count;
            int labeled = dataItems.Count(d => !string.IsNullOrEmpty(d.Label));
            int unlabeled = total - labeled;
            
            TotalSamplesText.Text = total.ToString();
            LabeledSamplesText.Text = labeled.ToString();
            UnlabeledSamplesText.Text = unlabeled.ToString();
            DataCountText.Text = $"{total} فایل import شده";
            
            // Update label counts - INotifyPropertyChanged will handle the UI update!
            foreach (var labelItem in labelItems)
            {
                labelItem.Count = dataItems.Count(d => d.Label == labelItem.Name);
            }
            
            // DON'T refresh - this causes items to disappear!
            // Since we're using ObservableCollection and INotifyPropertyChanged,
            // the UI will automatically update when properties change.
            // LabelsListBox.Items.Refresh();
            // DataListBox.Items.Refresh();
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            NavigationService?.GoBack();
        }

        private void Next_Click(object sender, RoutedEventArgs e)
        {
            // Validate data
            if (dataItems.Count == 0)
            {
                MessageBox.Show(
                    "لطفاً ابتدا فایل‌های خود را import کنید.\n\nاز دکمه‌های 'Browse Files' یا 'Browse Folder' استفاده کنید یا فایل‌ها را Drag & Drop کنید.", 
                    "داده‌ای وجود ندارد", 
                    MessageBoxButton.OK, 
                    MessageBoxImage.Warning);
                return;
            }
            
            if (labels.Count < 2)
            {
                MessageBox.Show(
                    "لطفاً حداقل 2 لیبل ایجاد کنید.\n\nمثال: 'Class_A' و 'Class_B'\n\nاز بخش 'Class Labels' در سمت راست استفاده کنید.", 
                    "لیبل کافی نیست", 
                    MessageBoxButton.OK, 
                    MessageBoxImage.Warning);
                return;
            }
            
            int labeled = dataItems.Count(d => !string.IsNullOrEmpty(d.Label));
            if (labeled == 0)
            {
                MessageBox.Show(
                    "هیچ فایلی لیبل‌گذاری نشده است!\n\nنحوه لیبل‌گذاری:\n1. در لیست فایل‌ها، منوی کشویی هر فایل را باز کنید\n2. یک لیبل انتخاب کنید\n3. برای همه فایل‌ها این کار را تکرار کنید",
                    "لیبل‌گذاری نشده",
                    MessageBoxButton.OK,
                    MessageBoxImage.Warning);
                return;
            }
            
            if (labeled < dataItems.Count * 0.5)
            {
                var result = MessageBox.Show(
                    $"فقط {labeled} از {dataItems.Count} فایل ({(labeled*100.0/dataItems.Count):F0}%) لیبل‌گذاری شده است.\n\n" +
                    "برای نتایج بهتر، حداقل 80% فایل‌ها باید لیبل داشته باشند.\n\n" +
                    "آیا می‌خواهید با این وضعیت ادامه دهید؟",
                    "لیبل‌گذاری ناقص", 
                    MessageBoxButton.YesNo, 
                    MessageBoxImage.Question);
                
                if (result != MessageBoxResult.Yes)
                    return;
            }
            
            // Save data to project directory
            try
            {
                SaveDataToProject();
                
                // Navigate to model selection
                NavigationService?.Navigate(new ModelSelectionPage(projectId, modality, labels.ToList()));
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"خطا در ذخیره داده‌ها:\n{ex.Message}\n\nلطفاً دوباره تلاش کنید یا پوشه project را بررسی کنید.",
                    "خطا در ذخیره",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error);
            }
        }

        private void SaveDataToProject()
        {
            // Get project directory - use absolute path
            // Assuming the backend projects directory is at: D:\Project\ModelCreator\projects
            string solutionDir = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", ".."));
            string projectsDir = Path.Combine(solutionDir, "projects");
            string projectDir = Path.Combine(projectsDir, projectId);
            string dataDir = Path.Combine(projectDir, "data");
            
            System.Diagnostics.Debug.WriteLine($"Solution directory: {solutionDir}");
            System.Diagnostics.Debug.WriteLine($"Projects directory: {projectsDir}");
            System.Diagnostics.Debug.WriteLine($"Project directory: {projectDir}");
            System.Diagnostics.Debug.WriteLine($"Data directory: {dataDir}");
            
            // Verify projects directory exists
            if (!Directory.Exists(projectsDir))
            {
                throw new Exception($"Projects directory not found: {projectsDir}\n\nPlease make sure the backend is set up correctly.");
            }
            
            // Verify project directory exists
            if (!Directory.Exists(projectDir))
            {
                throw new Exception($"Project directory not found: {projectDir}\n\nPlease create the project first.");
            }
            
            // Create data directory if it doesn't exist
            Directory.CreateDirectory(dataDir);
            
            // Create label mapping (label_name -> label_id)
            var labelMapping = new System.Collections.Generic.Dictionary<string, int>();
            for (int i = 0; i < labels.Count; i++)
            {
                labelMapping[labels[i]] = i;
            }
            
            // Save labels.json
            string labelsJson = System.Text.Json.JsonSerializer.Serialize(labelMapping, new System.Text.Json.JsonSerializerOptions
            {
                WriteIndented = true,
                Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            });
            File.WriteAllText(Path.Combine(projectDir, "labels.json"), labelsJson);
            
            // Create subdirectories for each label and copy files
            foreach (var label in labels)
            {
                string labelDir = Path.Combine(dataDir, label);
                Directory.CreateDirectory(labelDir);
            }
            
            // Copy labeled files to their respective directories
            int copiedCount = 0;
            int skippedCount = 0;
            int errorCount = 0;
            System.Text.StringBuilder errors = new System.Text.StringBuilder();
            
            foreach (var item in dataItems.Where(d => !string.IsNullOrEmpty(d.Label)))
            {
                if (item.Label == null) continue;
                
                try
                {
                    string destDir = Path.Combine(dataDir, item.Label);
                    string destPath = Path.Combine(destDir, item.FileName);
                    
                    // Check if file already exists in destination
                    if (File.Exists(destPath))
                    {
                        // File already exists - check if it's the same file
                        if (item.FilePath == destPath)
                        {
                            // Same file, skip
                            skippedCount++;
                            System.Diagnostics.Debug.WriteLine($"Skipped (already in place): {item.FileName}");
                        }
                        else
                        {
                            // Different source, check if we should overwrite
                            var sourceInfo = new FileInfo(item.FilePath);
                            var destInfo = new FileInfo(destPath);
                            
                            // Only copy if source is newer or different size
                            if (sourceInfo.LastWriteTime > destInfo.LastWriteTime || 
                                sourceInfo.Length != destInfo.Length)
                            {
                                File.Copy(item.FilePath, destPath, overwrite: true);
                                copiedCount++;
                                System.Diagnostics.Debug.WriteLine($"Updated: {item.FileName}");
                            }
                            else
                            {
                                skippedCount++;
                                System.Diagnostics.Debug.WriteLine($"Skipped (same): {item.FileName}");
                            }
                        }
                    }
                    else
                    {
                        // File doesn't exist, copy it
                        File.Copy(item.FilePath, destPath, overwrite: false);
                        copiedCount++;
                        System.Diagnostics.Debug.WriteLine($"Copied: {item.FileName} -> {destPath}");
                    }
                }
                catch (Exception ex)
                {
                    errorCount++;
                    errors.AppendLine($"- {item.FileName}: {ex.Message}");
                    System.Diagnostics.Debug.WriteLine($"Error copying {item.FileName}: {ex.Message}");
                }
            }
            
            System.Diagnostics.Debug.WriteLine($"=== Save Summary ===");
            System.Diagnostics.Debug.WriteLine($"Copied: {copiedCount} files");
            System.Diagnostics.Debug.WriteLine($"Skipped: {skippedCount} files (already exist)");
            System.Diagnostics.Debug.WriteLine($"Errors: {errorCount}");
            System.Diagnostics.Debug.WriteLine($"Data saved to: {dataDir}");
            System.Diagnostics.Debug.WriteLine($"Label mapping: {labelsJson}");
            
            // Show success message
            int totalProcessed = copiedCount + skippedCount;
            if (totalProcessed > 0)
            {
                string message = "";
                
                if (copiedCount > 0 && skippedCount > 0)
                {
                    message = $"✅ ذخیره‌سازی کامل شد!\n\n";
                    message += $"📊 خلاصه:\n";
                    message += $"  • {copiedCount} فایل جدید کپی شد\n";
                    message += $"  • {skippedCount} فایل قبلاً موجود بود\n";
                    message += $"  • کل: {dataItems.Count(d => !string.IsNullOrEmpty(d.Label))} فایل\n\n";
                    message += $"📂 مسیر: {dataDir}\n\n";
                }
                else if (copiedCount > 0)
                {
                    message = $"✅ {copiedCount} فایل با موفقیت ذخیره شد!\n\n";
                    message += $"مسیر: {dataDir}\n\n";
                }
                else if (skippedCount > 0)
                {
                    message = $"ℹ️ همه فایل‌ها ({skippedCount}) قبلاً در پروژه موجود بودند.\n\n";
                    message += $"تغییری در فایل‌ها ایجاد نشد.\n\n";
                }
                
                if (errorCount > 0)
                {
                    message += $"⚠️ {errorCount} فایل با خطا مواجه شد:\n{errors}";
                }
                else
                {
                    message += "حالا می‌توانید به مرحله انتخاب مدل بروید.";
                }
                
                MessageBox.Show(message, "ذخیره‌سازی", 
                    MessageBoxButton.OK, 
                    errorCount > 0 ? MessageBoxImage.Warning : MessageBoxImage.Information);
            }
            else
            {
                throw new Exception("هیچ فایلی برای ذخیره وجود ندارد! لطفاً فایل‌ها را لیبل‌گذاری کنید.");
            }
        }
    }
}

