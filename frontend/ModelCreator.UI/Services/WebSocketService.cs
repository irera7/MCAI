using System.Net.WebSockets;
using System.Text;
using System.Text.Json;

namespace ModelCreator.UI.Services
{
    /// <summary>
    /// WebSocket service interface
    /// </summary>
    public interface IWebSocketService
    {
        Task ConnectAsync(string url);
        Task DisconnectAsync();
        Task SendAsync(string message);
        event EventHandler<string>? MessageReceived;
        bool IsConnected { get; }
    }

    /// <summary>
    /// WebSocket service for real-time communication with backend
    /// </summary>
    public class WebSocketService : IWebSocketService
    {
        private ClientWebSocket? _webSocket;
        private CancellationTokenSource? _cancellationTokenSource;
        
        public event EventHandler<string>? MessageReceived;
        
        public bool IsConnected => _webSocket?.State == WebSocketState.Open;

        /// <summary>
        /// Connect to WebSocket server
        /// </summary>
        public async Task ConnectAsync(string url)
        {
            if (IsConnected)
                await DisconnectAsync();

            _webSocket = new ClientWebSocket();
            _cancellationTokenSource = new CancellationTokenSource();

            try
            {
                System.Diagnostics.Debug.WriteLine($"[WebSocket] Attempting to connect to: {url}");
                
                // Set timeout
                var timeoutCts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
                var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(
                    _cancellationTokenSource.Token, 
                    timeoutCts.Token
                );
                
                await _webSocket.ConnectAsync(new Uri(url), linkedCts.Token);
                
                System.Diagnostics.Debug.WriteLine($"[WebSocket] Connected successfully! State: {_webSocket.State}");
                
                // Start receiving messages
                _ = Task.Run(ReceiveLoop, _cancellationTokenSource.Token);
            }
            catch (OperationCanceledException)
            {
                throw new Exception("WebSocket connection timed out after 10 seconds");
            }
            catch (System.Net.WebSockets.WebSocketException wsEx)
            {
                System.Diagnostics.Debug.WriteLine($"[WebSocket] Connection error: {wsEx.Message}");
                System.Diagnostics.Debug.WriteLine($"[WebSocket] Error code: {wsEx.WebSocketErrorCode}");
                throw new Exception($"WebSocket connection failed: {wsEx.Message} (Code: {wsEx.WebSocketErrorCode})", wsEx);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[WebSocket] Unexpected error: {ex.GetType().Name}: {ex.Message}");
                throw new Exception($"WebSocket connection failed: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Disconnect from WebSocket server
        /// </summary>
        public async Task DisconnectAsync()
        {
            if (_webSocket == null)
                return;

            try
            {
                _cancellationTokenSource?.Cancel();
                
                if (_webSocket.State == WebSocketState.Open)
                {
                    await _webSocket.CloseAsync(
                        WebSocketCloseStatus.NormalClosure, 
                        "Client disconnecting", 
                        CancellationToken.None
                    );
                }
                
                _webSocket.Dispose();
                _webSocket = null;
            }
            catch (Exception)
            {
                // Ignore errors during disconnect
            }
        }

        /// <summary>
        /// Send message through WebSocket
        /// </summary>
        public async Task SendAsync(string message)
        {
            if (!IsConnected || _webSocket == null)
                throw new InvalidOperationException("WebSocket is not connected");

            var bytes = Encoding.UTF8.GetBytes(message);
            await _webSocket.SendAsync(
                new ArraySegment<byte>(bytes), 
                WebSocketMessageType.Text, 
                true, 
                CancellationToken.None
            );
        }

        /// <summary>
        /// Receive messages loop
        /// </summary>
        private async Task ReceiveLoop()
        {
            if (_webSocket == null || _cancellationTokenSource == null)
                return;

            var buffer = new byte[1024 * 4];

            try
            {
                System.Diagnostics.Debug.WriteLine("[WebSocket] Starting receive loop");
                
                while (!_cancellationTokenSource.Token.IsCancellationRequested && 
                       _webSocket.State == WebSocketState.Open)
                {
                    var result = await _webSocket.ReceiveAsync(
                        new ArraySegment<byte>(buffer), 
                        _cancellationTokenSource.Token
                    );

                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        System.Diagnostics.Debug.WriteLine("[WebSocket] Received close message");
                        await _webSocket.CloseAsync(
                            WebSocketCloseStatus.NormalClosure, 
                            string.Empty, 
                            CancellationToken.None
                        );
                    }
                    else
                    {
                        var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                        System.Diagnostics.Debug.WriteLine($"[WebSocket] Received message: {message.Substring(0, Math.Min(100, message.Length))}...");
                        MessageReceived?.Invoke(this, message);
                    }
                }
                
                System.Diagnostics.Debug.WriteLine("[WebSocket] Receive loop ended");
            }
            catch (OperationCanceledException)
            {
                System.Diagnostics.Debug.WriteLine("[WebSocket] Receive cancelled");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[WebSocket] Receive error: {ex.GetType().Name}: {ex.Message}");
            }
        }
    }
}

