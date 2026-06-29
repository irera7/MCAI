using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;

namespace ModelCreator.UI.Services
{
    /// <summary>
    /// API service interface
    /// </summary>
    public interface IApiService
    {
        Task<T?> GetAsync<T>(string endpoint);
        Task<T?> PostAsync<T>(string endpoint, object? data = null);
        Task<T?> PostMultipartAsync<T>(string endpoint, MultipartFormDataContent content);
        Task<bool> DeleteAsync(string endpoint);
        string BaseUrl { get; set; }
        
        // Extended methods for specific operations
        Task<Dictionary<string, object>> GetSystemInfoAsync();
        Task<Dictionary<string, object>> StartTrainingAsync(string projectId, Dictionary<string, object> config);
        Task<Dictionary<string, object>> GetTrainingResultsAsync(string projectId);
        Task<Dictionary<string, object>> ExportModelAsync(Dictionary<string, object> exportRequest);
    }

    /// <summary>
    /// HTTP API service for communicating with backend
    /// </summary>
    public class ApiService : IApiService
    {
        private readonly HttpClient _httpClient;
        
        public string BaseUrl { get; set; } = "http://127.0.0.1:8181";

        public ApiService()
        {
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(30)
            };
            
            // Disable proxy to avoid 502 Bad Gateway
            var handler = new HttpClientHandler
            {
                UseProxy = false,
                Proxy = null
            };
            
            _httpClient = new HttpClient(handler)
            {
                Timeout = TimeSpan.FromSeconds(30)
            };
        }

        /// <summary>
        /// Send GET request
        /// </summary>
        public async Task<T?> GetAsync<T>(string endpoint)
        {
            try
            {
                var url = $"{BaseUrl}{endpoint}";
                System.Diagnostics.Debug.WriteLine($"GET: {url}");
                
                var response = await _httpClient.GetAsync(url);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadFromJsonAsync<T>();
            }
            catch (HttpRequestException ex)
            {
                System.Diagnostics.Debug.WriteLine($"GET Error: {ex.Message}");
                throw new Exception($"API request failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Send POST request
        /// </summary>
        public async Task<T?> PostAsync<T>(string endpoint, object? data = null)
        {
            try
            {
                var url = $"{BaseUrl}{endpoint}";
                System.Diagnostics.Debug.WriteLine($"POST: {url}");
                
                var response = await _httpClient.PostAsJsonAsync(url, data);
                
                // If not successful, try to read error details
                if (!response.IsSuccessStatusCode)
                {
                    string errorContent = "";
                    try
                    {
                        errorContent = await response.Content.ReadAsStringAsync();
                        System.Diagnostics.Debug.WriteLine($"Error Response: {errorContent}");
                        
                        // Try to parse as JSON to get detail field
                        try
                        {
                            var errorJson = JsonSerializer.Deserialize<Dictionary<string, object>>(errorContent);
                            if (errorJson != null && errorJson.ContainsKey("detail"))
                            {
                                var detail = errorJson["detail"].ToString();
                                throw new Exception(detail);
                            }
                        }
                        catch (JsonException)
                        {
                            // If not JSON, use raw content
                            if (!string.IsNullOrEmpty(errorContent))
                            {
                                throw new Exception(errorContent);
                            }
                        }
                    }
                    catch (Exception ex) when (ex is not HttpRequestException)
                    {
                        throw;
                    }
                    
                    // If we couldn't parse error details, use status code
                    throw new HttpRequestException($"HTTP {(int)response.StatusCode}: {response.ReasonPhrase}");
                }
                
                return await response.Content.ReadFromJsonAsync<T>();
            }
            catch (HttpRequestException ex)
            {
                System.Diagnostics.Debug.WriteLine($"POST Error: {ex.Message}");
                throw new Exception($"API request failed: {ex.Message}", ex);
            }
        }
        
        /// <summary>
        /// Send POST request with multipart form data (for file uploads)
        /// </summary>
        public async Task<T?> PostMultipartAsync<T>(string endpoint, MultipartFormDataContent content)
        {
            try
            {
                var url = $"{BaseUrl}{endpoint}";
                System.Diagnostics.Debug.WriteLine($"POST (Multipart): {url}");
                
                var response = await _httpClient.PostAsync(url, content);
                response.EnsureSuccessStatusCode();
                
                return await response.Content.ReadFromJsonAsync<T>();
            }
            catch (HttpRequestException ex)
            {
                System.Diagnostics.Debug.WriteLine($"POST Multipart Error: {ex.Message}");
                throw new Exception($"API request failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Send DELETE request
        /// </summary>
        public async Task<bool> DeleteAsync(string endpoint)
        {
            try
            {
                var url = $"{BaseUrl}{endpoint}";
                System.Diagnostics.Debug.WriteLine($"DELETE: {url}");
                
                var response = await _httpClient.DeleteAsync(url);
                response.EnsureSuccessStatusCode();
                return true;
            }
            catch (HttpRequestException ex)
            {
                System.Diagnostics.Debug.WriteLine($"DELETE Error: {ex.Message}");
                throw new Exception($"API request failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Get system information (GPU, CPU, memory)
        /// </summary>
        public async Task<Dictionary<string, object>> GetSystemInfoAsync()
        {
            var result = await GetAsync<Dictionary<string, object>>("/api/system/info");
            return result ?? new Dictionary<string, object>();
        }

        /// <summary>
        /// Start training a model
        /// </summary>
        public async Task<Dictionary<string, object>> StartTrainingAsync(string projectId, Dictionary<string, object> config)
        {
            var result = await PostAsync<Dictionary<string, object>>($"/api/training/start/{projectId}", config);
            return result ?? new Dictionary<string, object>();
        }

        /// <summary>
        /// Get training results
        /// </summary>
        public async Task<Dictionary<string, object>> GetTrainingResultsAsync(string projectId)
        {
            var result = await GetAsync<Dictionary<string, object>>($"/api/training/results/{projectId}");
            return result ?? new Dictionary<string, object>();
        }

        /// <summary>
        /// Export trained model
        /// </summary>
        public async Task<Dictionary<string, object>> ExportModelAsync(Dictionary<string, object> exportRequest)
        {
            var result = await PostAsync<Dictionary<string, object>>("/api/export/model", exportRequest);
            return result ?? new Dictionary<string, object>();
        }
    }
}

