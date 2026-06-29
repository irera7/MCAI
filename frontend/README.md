# AI Model Builder - Frontend

.NET WPF frontend for the AI Model Builder application.

## Prerequisites

- .NET 8.0 SDK or later
- Visual Studio 2022 (recommended) or Visual Studio Code

## Building the Project

1. Open the solution in Visual Studio:
```bash
start ModelCreator.sln
```

Or build from command line:
```bash
dotnet build
```

2. Run the application:
```bash
dotnet run --project ModelCreator.UI
```

## Project Structure

```
frontend/
├── ModelCreator.sln
└── ModelCreator.UI/
    ├── App.xaml                # Application entry point
    ├── MainWindow.xaml         # Main window
    ├── ViewModels/             # MVVM ViewModels
    ├── Views/                  # XAML pages
    ├── Services/               # Services (API, WebSocket, Project)
    ├── Models/                 # Data models
    ├── Controls/               # Custom controls
    └── Themes/                 # Light/Dark themes
```

## Features

- Modern MVVM architecture with CommunityToolkit.Mvvm
- Dependency injection
- HTTP/WebSocket communication with backend
- Dark/Light theme support
- Project management UI
- Real-time training dashboard (to be implemented)

## Backend Connection

The frontend connects to the Python backend running at `http://127.0.0.1:8181` by default. Ensure the backend is running before starting the frontend.

