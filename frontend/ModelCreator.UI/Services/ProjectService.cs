using System.Collections.ObjectModel;

namespace ModelCreator.UI.Services
{
    /// <summary>
    /// Project information model
    /// </summary>
    public class ProjectInfo
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Modality { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string ModelType { get; set; } = string.Empty;
        public string CreatedAt { get; set; } = string.Empty;
        public string UpdatedAt { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        
        // Training status fields
        public string? TrainingStatus { get; set; }  // training, completed, not_started
        public int? CurrentEpoch { get; set; }
        public int? TotalEpochs { get; set; }
        public int? TrainingProgress { get; set; }  // percentage 0-100
        public double? TrainLoss { get; set; }
        public double? TrainAccuracy { get; set; }
        
        // Helper property for display
        public string DisplayStatus
        {
            get
            {
                if (TrainingStatus == "training")
                    return $"🔥 Training: Epoch {CurrentEpoch}/{TotalEpochs} ({TrainingProgress}%)";
                else if (TrainingStatus == "completed" || Status == "trained")
                    return $"✅ Trained (Acc: {TrainAccuracy * 100:F1}%)";
                else
                    return Status;
            }
        }
        
        public bool IsTraining => TrainingStatus == "training";
        public bool IsTrained => TrainingStatus == "completed" || Status == "trained";
    }

    /// <summary>
    /// Project service interface
    /// </summary>
    public interface IProjectService
    {
        Task<ProjectInfo> CreateProject(string name, string modality, string description);
        Task<ProjectInfo> LoadProject(string projectId);
        Task<List<ProjectInfo>> GetRecentProjects();
        Task<bool> DeleteProject(string projectId);
    }

    /// <summary>
    /// Project service for managing projects
    /// </summary>
    public class ProjectService : IProjectService
    {
        private readonly IApiService _apiService;

        public ProjectService(IApiService apiService)
        {
            _apiService = apiService;
        }

        /// <summary>
        /// Create a new project
        /// </summary>
        public async Task<ProjectInfo> CreateProject(string name, string modality, string description)
        {
            var request = new
            {
                name,
                modality,
                description
            };

            var project = await _apiService.PostAsync<ProjectInfo>("/api/project/create", request);
            return project ?? throw new Exception("Failed to create project");
        }

        /// <summary>
        /// Load existing project
        /// </summary>
        public async Task<ProjectInfo> LoadProject(string projectId)
        {
            var project = await _apiService.GetAsync<ProjectInfo>($"/api/project/load/{projectId}");
            return project ?? throw new Exception("Project not found");
        }

        /// <summary>
        /// Get list of recent projects
        /// </summary>
        public async Task<List<ProjectInfo>> GetRecentProjects()
        {
            var projects = await _apiService.GetAsync<List<ProjectInfo>>("/api/project/list");
            return projects ?? new List<ProjectInfo>();
        }

        /// <summary>
        /// Delete a project
        /// </summary>
        public async Task<bool> DeleteProject(string projectId)
        {
            return await _apiService.DeleteAsync($"/api/project/delete/{projectId}");
        }
    }
}

