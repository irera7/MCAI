# ModelCreator Web Application

A React + TypeScript web application for the ModelCreator AI training platform.

## 🚀 Current Status

**Phase 1-2 Complete**: Infrastructure and routing setup ✅
- ✅ React 18 + TypeScript + Vite setup
- ✅ Ant Design UI library integration  
- ✅ API service layer with Axios
- ✅ React Router with layout
- ✅ Theme system (Dark/Light mode)
- ✅ HomePage with all modality cards

## 📋 Tech Stack

- **Frontend**: React 18 + TypeScript
- **UI Library**: Ant Design 5.x
- **State Management**: React Context + React Query
- **Routing**: React Router v6
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Build Tool**: Vite
- **WebSocket**: socket.io-client

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🌐 Development

The app runs on `http://localhost:3000` and proxies API requests to the backend at `http://127.0.0.1:8181`.

### Prerequisites

1. Backend server must be running at `http://127.0.0.1:8181`
2. Node.js 16+ installed
3. npm or yarn package manager

### Project Structure

```
web/
├── src/
│   ├── api/              # API service layer
│   │   ├── client.ts     # Axios client with interceptors
│   │   └── endpoints.ts  # API endpoint definitions
│   ├── components/       # Reusable UI components
│   ├── pages/            # Page components
│   │   └── HomePage.tsx  # Main landing page
│   ├── contexts/         # React contexts
│   │   └── ThemeContext.tsx  # Theme management
│   ├── hooks/            # Custom hooks
│   ├── types/            # TypeScript interfaces
│   │   ├── api.types.ts
│   │   ├── project.types.ts
│   │   ├── training.types.ts
│   │   └── model.types.ts
│   ├── utils/            # Helper functions
│   ├── theme.ts          # Ant Design theme config
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
├── public/
├── package.json
└── vite.config.ts
```

## 📦 Available API Endpoints

All endpoints are defined in `src/api/endpoints.ts`:

### Project Management
- `projectApi.list()` - GET /api/project/list
- `projectApi.create(data)` - POST /api/project/create
- `projectApi.get(id)` - GET /api/project/{id}
- `projectApi.delete(id)` - DELETE /api/project/{id}

### Data Management
- `dataApi.upload(projectId, formData, onProgress)` - POST /api/data/upload/{projectId}
- `dataApi.getInfo(projectId)` - GET /api/data/info/{projectId}

### Training
- `trainingApi.start(projectId, config)` - POST /api/training/start/{projectId}
- `trainingApi.stop(projectId)` - POST /api/training/stop/{projectId}
- `trainingApi.status(projectId)` - GET /api/training/status/{projectId}
- `trainingApi.metrics(projectId)` - GET /api/training/metrics/{projectId}

### Inference
- `inferenceApi.predict(projectId, formData)` - POST /api/inference/predict/{projectId}

### AutoML
- `automlApi.start(config)` - POST /api/automl/start
- `automlApi.status(projectId)` - GET /api/automl/status/{projectId}
- `automlApi.apply(projectId)` - POST /api/automl/apply/{projectId}

### Model Serving
- `servingApi.load(modelId, device)` - POST /api/serve/load/{modelId}
- `servingApi.unload(modelId)` - DELETE /api/serve/unload/{modelId}
- `servingApi.listModels()` - GET /api/serve/models
- `servingApi.predict(modelId, formData)` - POST /api/serve/predict/{modelId}

### Ensemble & Comparison
- `ensembleApi.create(data)` - POST /api/ensemble/create
- `comparisonApi.compare(projectIds)` - POST /api/comparison/compare

## 🎨 Features Implemented

### ✅ Completed
1. **Infrastructure**
   - React + TypeScript + Vite setup
   - Ant Design UI integration
   - API client with error handling
   - Type-safe API endpoints

2. **Layout & Navigation**
   - Responsive layout with header, sider, content
   - Dark/Light theme toggle
   - Navigation menu with routes
   - Theme persistence in localStorage

3. **HomePage**
   - Hero section with gradient
   - 8 modality cards (Image, Text, Audio, Video, Tabular, TimeSeries, Medical, Genomic)
   - 4 advanced feature cards
   - Getting started guide
   - Navigation to respective pages

### 🚧 To Be Implemented

The following pages need full implementation (currently showing placeholders):

#### Core Pages (Priority 1)
1. **ProjectsPage** - List all projects with filters
2. **ImageProjectPage** - Image classification project creation
3. **TextProjectPage** - Text classification project creation
4. **AudioProjectPage** - Audio classification project creation
5. **VideoProjectPage** - Video classification project creation
6. **TabularProjectPage** - Tabular data project with feature engineering
7. **TimeSeriesProjectPage** - Time series project with preprocessing
8. **MedicalProjectPage** - Medical imaging project
9. **GenomicProjectPage** - Genomic analysis project

#### Training Pages (Priority 2)
10. **TrainingConfigPage** - Configure training parameters
11. **TrainingDashboardPage** - Real-time training monitoring with charts
12. **ResultsPage** - Display final metrics and confusion matrix

#### Advanced Pages (Priority 3)
13. **AutoMLPage** - Hyperparameter optimization interface
14. **ModelServingPage** - Load/unload models and test inference
15. **EnsembleMethodsPage** - Create ensemble models
16. **ModelComparisonPage** - Compare multiple trained models
17. **CloudTrainingPage** - Cloud training configuration
18. **InferencePlaygroundPage** - Test trained models

#### Reusable Components (Priority 4)
- FileUploader component (drag-and-drop)
- MetricsChart component (Recharts)
- ProgressCard component
- ModelCard component
- StatisticsPanel component
- LoadingSpinner component
- ErrorBoundary component

## 🔧 Environment Variables

Create a `.env` file (or use the provided `.env.example`):

```env
VITE_API_BASE_URL=http://127.0.0.1:8181
VITE_WS_URL=ws://127.0.0.1:8181
```

## 📝 Development Notes

### API Integration Pattern

Example of using the API with React Query:

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { projectApi } from '../api/endpoints';

// Fetch projects
const { data, isLoading, error } = useQuery({
  queryKey: ['projects'],
  queryFn: async () => {
    const response = await projectApi.list();
    return response.data;
  },
});

// Create project
const mutation = useMutation({
  mutationFn: (data: ProjectCreate) => projectApi.create(data),
  onSuccess: () => {
    // Refetch projects or show success message
  },
});
```

### File Upload Pattern

```typescript
const handleUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('class_name', className);
  
  try {
    const response = await dataApi.upload(projectId, formData, (progress) => {
      setUploadProgress(progress);
    });
    console.log('Upload success:', response.data);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

## 🚀 Deployment

### Development
```bash
npm run dev
```
Access at: `http://localhost:3000`

### Production Build
```bash
npm run build
```
Output in `dist/` folder

### Serve from Backend
After building, copy the `dist/` folder contents to the backend's static files folder, or configure FastAPI to serve the built files.

## 🎯 Next Steps

To continue development:

1. **Implement ProjectsPage** - Show list of projects with table
2. **Create project pages** - One for each modality with file upload
3. **Build TrainingDashboardPage** - Real-time metrics with Recharts
4. **Add AutoMLPage** - Full hyperparameter optimization UI
5. **Implement ModelServingPage** - Model management and testing
6. **Create reusable components** - FileUploader, Charts, etc.
7. **Add comprehensive error handling**
8. **Write unit tests**

## 📚 Resources

- [React Documentation](https://react.dev/)
- [Ant Design Components](https://ant.design/components/overview/)
- [React Query Guide](https://tanstack.com/query/latest)
- [Vite Guide](https://vitejs.dev/guide/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 🤝 Contributing

This web application mirrors the functionality of the ModelCreator WPF desktop application. When implementing new features, refer to the desktop app's UI and behavior for consistency.

## 📄 License

Proprietary - Part of the ModelCreator project

---

**Current Version**: 0.1.0 (Infrastructure Complete)
**Last Updated**: December 2, 2025

