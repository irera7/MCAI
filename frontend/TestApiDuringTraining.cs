using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Text.Json;

namespace ModelCreator.UI.Tests
{
    /// <summary>
    /// Simple test to verify API is responding during training
    /// Run this while training is active
    /// </summary>
    public class TestApiDuringTraining
    {
        public static async Task Main(string[] args)
        {
            string projectId = "53569a3d-1248-4b5d-8e8b-be8b75556767"; // Your active training project
            string baseUrl = "http://127.0.0.1:8181";
            string endpoint = $"{baseUrl}/api/training/status/{projectId}";
            
            Console.WriteLine("=" * 70);
            Console.WriteLine("🔍 Testing Training Status API");
            Console.WriteLine("=" * 70);
            Console.WriteLine($"Endpoint: {endpoint}");
            Console.WriteLine($"Project ID: {projectId}");
            Console.WriteLine();
            
            using (var httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(10) })
            {
                try
                {
                    Console.WriteLine("📡 Sending request...");
                    var response = await httpClient.GetAsync(endpoint);
                    
                    Console.WriteLine($"✅ Status Code: {response.StatusCode}");
                    
                    if (response.IsSuccessStatusCode)
                    {
                        var json = await response.Content.ReadAsStringAsync();
                        Console.WriteLine("\n📊 Raw JSON Response:");
                        Console.WriteLine(json);
                        
                        // Try to deserialize
                        Console.WriteLine("\n🔍 Parsing JSON...");
                        var status = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
                        
                        if (status != null)
                        {
                            Console.WriteLine("\n✅ Successfully deserialized to Dictionary<string, object>");
                            Console.WriteLine($"Keys in dictionary: {status.Count}");
                            Console.WriteLine();
                            
                            foreach (var kvp in status)
                            {
                                var valueType = kvp.Value?.GetType().Name ?? "null";
                                Console.WriteLine($"  {kvp.Key}: {kvp.Value} (Type: {valueType})");
                            }
                            
                            // Extract key metrics
                            Console.WriteLine("\n" + "=" * 70);
                            Console.WriteLine("📈 Key Metrics:");
                            Console.WriteLine("=" * 70);
                            
                            if (status.ContainsKey("status"))
                                Console.WriteLine($"Status: {status["status"]}");
                            
                            if (status.ContainsKey("current_epoch") && status.ContainsKey("total_epochs"))
                            {
                                // Handle JsonElement properly
                                int currentEpoch = GetIntValue(status, "current_epoch");
                                int totalEpochs = GetIntValue(status, "total_epochs");
                                Console.WriteLine($"Epoch: {currentEpoch} / {totalEpochs}");
                            }
                            
                            if (status.ContainsKey("train_loss"))
                            {
                                double trainLoss = GetDoubleValue(status, "train_loss");
                                Console.WriteLine($"Train Loss: {trainLoss:F4}");
                            }
                            
                            if (status.ContainsKey("train_acc"))
                            {
                                double trainAcc = GetDoubleValue(status, "train_acc");
                                Console.WriteLine($"Train Accuracy: {trainAcc:F4}");
                            }
                            
                            if (status.ContainsKey("val_loss"))
                            {
                                double valLoss = GetDoubleValue(status, "val_loss");
                                Console.WriteLine($"Val Loss: {valLoss:F4}");
                            }
                            
                            if (status.ContainsKey("val_acc"))
                            {
                                double valAcc = GetDoubleValue(status, "val_acc");
                                Console.WriteLine($"Val Accuracy: {valAcc:F4}");
                            }
                            
                            if (status.ContainsKey("message"))
                                Console.WriteLine($"Message: {status["message"]}");
                            
                            Console.WriteLine("\n" + "=" * 70);
                            Console.WriteLine("✅ API is responding correctly!");
                            Console.WriteLine("=" * 70);
                        }
                        else
                        {
                            Console.WriteLine("\n❌ Failed to deserialize JSON");
                        }
                    }
                    else
                    {
                        Console.WriteLine($"\n❌ Error: {response.StatusCode} - {response.ReasonPhrase}");
                        var errorContent = await response.Content.ReadAsStringAsync();
                        Console.WriteLine($"Error content: {errorContent}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"\n❌ Exception: {ex.GetType().Name}");
                    Console.WriteLine($"Message: {ex.Message}");
                    Console.WriteLine($"Stack trace: {ex.StackTrace}");
                }
            }
            
            Console.WriteLine("\n\n🔄 Monitoring for 10 seconds (5 polls, 2 seconds apart)...");
            Console.WriteLine("=" * 70);
            
            using (var httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(10) })
            {
                for (int i = 0; i < 5; i++)
                {
                    await Task.Delay(2000);
                    
                    try
                    {
                        var response = await httpClient.GetAsync(endpoint);
                        if (response.IsSuccessStatusCode)
                        {
                            var status = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
                            if (status != null)
                            {
                                int epoch = GetIntValue(status, "current_epoch");
                                int total = GetIntValue(status, "total_epochs");
                                string statusStr = status.ContainsKey("status") ? status["status"].ToString() : "unknown";
                                double trainLoss = GetDoubleValue(status, "train_loss");
                                double trainAcc = GetDoubleValue(status, "train_acc");
                                
                                Console.WriteLine($"[{i+1}/5] Epoch: {epoch}/{total} | Status: {statusStr} | Loss: {trainLoss:F4} | Acc: {trainAcc:F4}");
                            }
                        }
                        else
                        {
                            Console.WriteLine($"[{i+1}/5] ❌ Error: {response.StatusCode}");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"[{i+1}/5] ❌ Exception: {ex.Message}");
                    }
                }
            }
            
            Console.WriteLine("\n" + "=" * 70);
            Console.WriteLine("✅ Test completed!");
            Console.WriteLine("=" * 70);
            
            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }
        
        // Helper methods to handle JsonElement
        private static int GetIntValue(Dictionary<string, object> dict, string key)
        {
            if (!dict.ContainsKey(key)) return 0;
            var value = dict[key];
            
            if (value is int i) return i;
            if (value is JsonElement je && je.ValueKind == JsonValueKind.Number)
                return je.GetInt32();
            
            try
            {
                return Convert.ToInt32(value);
            }
            catch
            {
                return 0;
            }
        }
        
        private static double GetDoubleValue(Dictionary<string, object> dict, string key)
        {
            if (!dict.ContainsKey(key)) return 0.0;
            var value = dict[key];
            
            if (value is double d) return d;
            if (value is JsonElement je && je.ValueKind == JsonValueKind.Number)
                return je.GetDouble();
            
            try
            {
                return Convert.ToDouble(value);
            }
            catch
            {
                return 0.0;
            }
        }
    }
}

