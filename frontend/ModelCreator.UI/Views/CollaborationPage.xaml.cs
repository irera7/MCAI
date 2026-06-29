using System;
using System.Windows;
using System.Windows.Controls;

namespace ModelCreator.UI.Views
{
    public partial class CollaborationPage : Page
    {
        public CollaborationPage()
        {
            InitializeComponent();
            LoadData();
        }

        private void LoadData()
        {
            // Sample data
            UsersDataGrid.ItemsSource = new[]
            {
                new { Username = "john_doe", Email = "john@example.com", Role = "Admin" },
                new { Username = "jane_smith", Email = "jane@example.com", Role = "Editor" }
            };

            TeamsDataGrid.ItemsSource = new[]
            {
                new { TeamName = "ML Team", Members = 5, Owner = "john_doe" },
                new { TeamName = "Data Science", Members = 3, Owner = "jane_smith" }
            };
        }

        private void AddUserButton_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Add User dialog (to be implemented)", "Add User", 
                MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void CreateTeamButton_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Create Team dialog (to be implemented)", "Create Team", 
                MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void AddMemberButton_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Add Member dialog (to be implemented)", "Add Member", 
                MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }
}

