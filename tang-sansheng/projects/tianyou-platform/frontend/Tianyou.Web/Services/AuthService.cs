using System.Net.Http.Json;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Microsoft.JSInterop;

namespace Tianyou.Web.Services;

/// <summary>
/// 认证服务
/// </summary>
public class AuthService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AuthService> _logger;
    private readonly IConfiguration _configuration;
    private readonly IJSRuntime _jsRuntime;
    
    // API基础地址
    private readonly string _apiBaseUrl;
    
    // JWT Token存储key
    private const string TokenKey = "jwt_token";
    private const string UserKey = "user_info";
    
    public AuthService(HttpClient httpClient, ILogger<AuthService> logger, IConfiguration configuration, IJSRuntime jsRuntime)
    {
        _httpClient = httpClient;
        _logger = logger;
        _configuration = configuration;
        _jsRuntime = jsRuntime;
        _apiBaseUrl = _configuration["ApiBaseUrl"] ?? "http://localhost:5000";
        
        // 初始化JSRuntimeHelper
        JSRuntimeHelper.Initialize(jsRuntime);
    }
    
    /// <summary>
    /// 用户注册
    /// </summary>
    public async Task<AuthResult> RegisterAsync(string username, string email, string password, string fullName)
    {
        try
        {
            var request = new { Username = username, Email = email, Password = password, FullName = fullName };
            var response = await _httpClient.PostAsJsonAsync($"{_apiBaseUrl}/api/auth/register", request);
            
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadFromJsonAsync<ApiResponse<AuthData>>();
                
                if (result?.Success == true && result.Data != null)
                {
                    // 保存Token和用户信息
                    await SaveTokenAsync(result.Data.Token);
                    await SaveUserInfoAsync(result.Data);
                    
                    _logger.LogInformation("用户注册成功: {Username}", username);
                    return new AuthResult { Success = true, Data = result.Data };
                }
            }
            
            var errorResult = await response.Content.ReadFromJsonAsync<ApiResponse<object>>();
            _logger.LogWarning("用户注册失败: {Message}", errorResult?.Message);
            return new AuthResult { Success = false, Message = errorResult?.Message ?? "注册失败" };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "注册请求异常");
            return new AuthResult { Success = false, Message = $"注册失败: {ex.Message}" };
        }
    }
    
    /// <summary>
    /// 用户登录
    /// </summary>
    public async Task<AuthResult> LoginAsync(string username, string password)
    {
        try
        {
            var request = new { Username = username, Password = password };
            var response = await _httpClient.PostAsJsonAsync($"{_apiBaseUrl}/api/auth/login", request);
            
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadFromJsonAsync<ApiResponse<AuthData>>();
                
                if (result?.Success == true && result.Data != null)
                {
                    // 保存Token和用户信息
                    await SaveTokenAsync(result.Data.Token);
                    await SaveUserInfoAsync(result.Data);
                    
                    _logger.LogInformation("用户登录成功: {Username}", username);
                    return new AuthResult { Success = true, Data = result.Data };
                }
            }
            
            var errorResult = await response.Content.ReadFromJsonAsync<ApiResponse<object>>();
            _logger.LogWarning("用户登录失败: {Message}", errorResult?.Message);
            return new AuthResult { Success = false, Message = errorResult?.Message ?? "登录失败" };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "登录请求异常");
            return new AuthResult { Success = false, Message = $"登录失败: {ex.Message}" };
        }
    }
    
    /// <summary>
    /// 获取当前用户信息
    /// </summary>
    public async Task<UserInfo?> GetCurrentUserAsync()
    {
        try
        {
            var token = await GetTokenAsync();
            if (string.IsNullOrEmpty(token))
            {
                return null;
            }
            
            _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            var response = await _httpClient.GetAsync($"{_apiBaseUrl}/api/auth/me");
            
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadFromJsonAsync<ApiResponse<UserInfo>>();
                return result?.Data;
            }
            
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取用户信息异常");
            return null;
        }
    }
    
    /// <summary>
    /// 登出
    /// </summary>
    public async Task LogoutAsync()
    {
        await ClearTokenAsync();
        await ClearUserInfoAsync();
        _logger.LogInformation("用户已登出");
    }
    
    /// <summary>
    /// 检查是否已登录
    /// </summary>
    public async Task<bool> IsAuthenticatedAsync()
    {
        var token = await GetTokenAsync();
        return !string.IsNullOrEmpty(token);
    }
    
    /// <summary>
    /// 获取存储的Token
    /// </summary>
    public async Task<string?> GetTokenAsync()
    {
        try
        {
            // Blazor WebAssembly使用LocalStorage
            return await JSRuntimeHelper.InvokeAsync<string?>("localStorage.getItem", TokenKey);
        }
        catch
        {
            return null;
        }
    }
    
    /// <summary>
    /// 保存Token到LocalStorage
    /// </summary>
    public async Task SaveTokenAsync(string token)
    {
        await JSRuntimeHelper.InvokeVoidAsync("localStorage.setItem", TokenKey, token);
    }
    
    /// <summary>
    /// 清除Token
    /// </summary>
    private async Task ClearTokenAsync()
    {
        await JSRuntimeHelper.InvokeVoidAsync("localStorage.removeItem", TokenKey);
    }
    
    /// <summary>
    /// 保存用户信息到LocalStorage
    /// </summary>
    private async Task SaveUserInfoAsync(AuthData data)
    {
        var json = JsonSerializer.Serialize(data);
        await JSRuntimeHelper.InvokeVoidAsync("localStorage.setItem", UserKey, json);
    }
    
    /// <summary>
    /// 清除用户信息
    /// </summary>
    private async Task ClearUserInfoAsync()
    {
        await JSRuntimeHelper.InvokeVoidAsync("localStorage.removeItem", UserKey);
    }
}

/// <summary>
/// 认证结果
/// </summary>
public class AuthResult
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public AuthData? Data { get; set; }
}

/// <summary>
/// API响应
/// </summary>
public class ApiResponse<T>
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public T? Data { get; set; }
}

/// <summary>
/// 认证数据
/// </summary>
public class AuthData
{
    public string? UserId { get; set; }
    public string? Username { get; set; }
    public string? Email { get; set; }
    public string? FullName { get; set; }
    public string? Token { get; set; }
    public int ExpiresIn { get; set; }
}

/// <summary>
/// 用户信息
/// </summary>
public class UserInfo
{
    public string? UserId { get; set; }
    public string? Username { get; set; }
    public string? Email { get; set; }
    public string? FullName { get; set; }
    public List<string>? Roles { get; set; }
    public List<string>? Permissions { get; set; }
}

/// <summary>
/// JS运行时帮助类
/// </summary>
public static class JSRuntimeHelper
{
    private static IJSRuntime? _jsRuntime;
    
    public static void Initialize(IJSRuntime jsRuntime)
    {
        _jsRuntime = jsRuntime;
    }
    
    public static async Task<T?> InvokeAsync<T>(string identifier, params object[] args)
    {
        if (_jsRuntime == null) return default;
        return await _jsRuntime.InvokeAsync<T>(identifier, args);
    }
    
    public static async Task InvokeVoidAsync(string identifier, params object[] args)
    {
        if (_jsRuntime == null) return;
        await _jsRuntime.InvokeVoidAsync(identifier, args);
    }
}
