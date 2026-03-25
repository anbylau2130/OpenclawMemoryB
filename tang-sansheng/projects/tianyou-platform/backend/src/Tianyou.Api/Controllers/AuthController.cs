using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using Tianyou.Application.Services;
using Tianyou.Infrastructure.Data;

namespace Tianyou.Api.Controllers;

/// <summary>
/// 认证控制器
/// </summary>
[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly AuthService _authService;
    private readonly ILogger<AuthController> _logger;
    private readonly TianyouDbContext _context;
    
    public AuthController(AuthService authService, ILogger<AuthController> logger, TianyouDbContext context)
    {
        _authService = authService;
        _logger = logger;
        _context = context;
    }
    
    /// <summary>
    /// 用户注册
    /// </summary>
    [HttpPost("register")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> Register([FromBody] RegisterRequest request)
    {
        try
        {
            var (user, token) = await _authService.RegisterAsync(
                request.Username,
                request.Email,
                request.Password,
                request.FullName);
            
            _logger.LogInformation("用户注册成功: {Username}", request.Username);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    userId = user.Id,
                    username = user.Username,
                    email = user.Email,
                    fullName = user.FullName,
                    token,
                    expiresIn = 86400 // 24小时
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "用户注册失败: {Username}", request.Username);
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 用户登录
    /// </summary>
    [HttpPost("login")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        try
        {
            var (user, token) = await _authService.LoginAsync(request.Username, request.Password);
            
            _logger.LogInformation("用户登录成功: {Username}", request.Username);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    userId = user.Id,
                    username = user.Username,
                    email = user.Email,
                    fullName = user.FullName,
                    token,
                    expiresIn = 86400
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "用户登录失败: {Username}", request.Username);
            return Unauthorized(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 获取当前用户信息
    /// </summary>
    [Authorize]
    [HttpGet("me")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> GetCurrentUser()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        
        if (string.IsNullOrEmpty(userIdClaim))
        {
            return Unauthorized(new { success = false, message = "无效的Token" });
        }
        
        var username = User.FindFirst(ClaimTypes.Name)?.Value;
        var email = User.FindFirst(ClaimTypes.Email)?.Value;
        var fullName = User.FindFirst("fullName")?.Value;
        var roles = User.FindAll(ClaimTypes.Role).Select(c => c.Value).ToList();
        var permissions = User.FindAll("permission").Select(c => c.Value).ToList();
        
        return Ok(new
        {
            success = true,
            data = new
            {
                userId = userIdClaim,
                username,
                email,
                fullName,
                roles,
                permissions
            }
        });
    }
    
    /// <summary>
    /// 修改密码
    /// </summary>
    [Authorize]
    [HttpPut("password")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        
        if (string.IsNullOrEmpty(userIdClaim))
        {
            return Unauthorized(new { success = false, message = "无效的Token" });
        }

        // 获取用户
        var userId = int.Parse(userIdClaim);
        var user = await _context.Users.FindAsync(userId);

        if (user == null)
        {
            return NotFound(new { success = false, message = "用户不存在" });
        }

        // 验证旧密码
        if (!BCrypt.Net.BCrypt.Verify(request.OldPassword, user.PasswordHash))
        {
            return BadRequest(new { success = false, message = "旧密码错误" });
        }

        // 验证新密码强度
        if (string.IsNullOrWhiteSpace(request.NewPassword) || request.NewPassword.Length < 6)
        {
            return BadRequest(new { success = false, message = "新密码长度至少6位" });
        }

        // 更新密码
        user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.NewPassword);
        user.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();

        return Ok(new { success = true, message = "密码修改成功" });
    }
}

// DTO类
public record RegisterRequest(string Username, string Email, string Password, string FullName);
public record LoginRequest(string Username, string Password);
public record ChangePasswordRequest(string OldPassword, string NewPassword);