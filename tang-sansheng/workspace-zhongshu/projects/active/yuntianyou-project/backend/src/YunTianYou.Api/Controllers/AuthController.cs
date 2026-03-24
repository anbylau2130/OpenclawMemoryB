using Microsoft.AspNetCore.Mvc;
using YunTianYou.Application.DTOs;
using YunTianYou.Application.Services;

namespace YunTianYou.Api.Controllers;

/// <summary>
/// 认证控制器 - 登录注册
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly AuthService _authService;
    
    public AuthController(AuthService authService)
    {
        _authService = authService;
    }
    
    /// <summary>
    /// 用户注册
    /// </summary>
    [HttpPost("register")]
    public async Task<ActionResult<AuthResponse>> Register([FromBody] RegisterRequest request)
    {
        var (user, token, error) = await _authService.RegisterAsync(
            request.Username, request.Email, request.Password);
        
        if (error != null || user == null || token == null)
        {
            return BadRequest(new { error = error ?? "注册失败" });
        }
        
        return Ok(new AuthResponse
        {
            UserId = user.Id,
            Username = user.Username,
            Email = user.Email,
            Token = token,
            Role = user.Role ?? "user"
        });
    }
    
    /// <summary>
    /// 用户登录
    /// </summary>
    [HttpPost("login")]
    public async Task<ActionResult<AuthResponse>> Login([FromBody] LoginRequest request)
    {
        var (user, token, error) = await _authService.LoginAsync(
            request.Username, request.Password);
        
        if (error != null || user == null || token == null)
        {
            return Unauthorized(new { error = error ?? "登录失败" });
        }
        
        return Ok(new AuthResponse
        {
            UserId = user.Id,
            Username = user.Username,
            Email = user.Email,
            Token = token,
            Role = user.Role ?? "user"
        });
    }
    
    /// <summary>
    /// 验证Token
    /// </summary>
    [HttpPost("validate")]
    public ActionResult ValidateToken([FromBody] ValidateTokenRequest request)
    {
        var principal = _authService.ValidateToken(request.Token);
        if (principal == null)
        {
            return Unauthorized(new { error = "Token无效" });
        }
        
        return Ok(new { valid = true, username = principal.Identity?.Name });
    }
}

// DTOs
public class RegisterRequest
{
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}

public class LoginRequest
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}

public class ValidateTokenRequest
{
    public string Token { get; set; } = string.Empty;
}

public class AuthResponse
{
    public Guid UserId { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Token { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
}
