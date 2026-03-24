using Microsoft.AspNetCore.Mvc;
using YunTianYou.Application.DTOs;
using YunTianYou.Application.Services;

namespace YunTianYou.Api.Controllers;

/// <summary>
/// 用户管理API控制器
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly ILogger<UsersController> _logger;

    public UsersController(IUserService userService, ILogger<UsersController> logger)
    {
        _userService = userService;
        _logger = logger;
    }

    /// <summary>
    /// 用户登录
    /// </summary>
    [HttpPost("login")]
    public async Task<ActionResult<AuthResponseDto>> Login([FromBody] LoginDto dto)
    {
        try
        {
            var result = await _userService.LoginAsync(dto);
            if (!result.Success)
            {
                return Unauthorized(result);
            }
            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "用户登录失败: {Username}", dto.Username);
            return StatusCode(500, new AuthResponseDto { Success = false, Message = "登录失败" });
        }
    }

    /// <summary>
    /// 用户注册
    /// </summary>
    [HttpPost("register")]
    public async Task<ActionResult<AuthResponseDto>> Register([FromBody] RegisterDto dto)
    {
        try
        {
            var result = await _userService.RegisterAsync(dto);
            if (!result.Success)
            {
                return BadRequest(result);
            }
            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "用户注册失败: {Username}", dto.Username);
            return StatusCode(500, new AuthResponseDto { Success = false, Message = "注册失败" });
        }
    }

    /// <summary>
    /// 获取当前用户信息
    /// </summary>
    [HttpGet("me")]
    public async Task<ActionResult<UserDto>> GetCurrentUser()
    {
        try
        {
            // TODO: 从JWT token获取用户ID
            var userId = Guid.Parse("00000000-0000-0000-0000-000000000001");
            var user = await _userService.GetUserByIdAsync(userId);
            if (user == null)
            {
                return NotFound(new { success = false, message = "用户不存在" });
            }
            return Ok(new { success = true, data = user });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取用户信息失败");
            return StatusCode(500, new { success = false, message = "获取用户信息失败" });
        }
    }

    /// <summary>
    /// 获取所有用户（管理员）
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<UserDto>>> GetUsers()
    {
        try
        {
            var users = await _userService.GetAllUsersAsync();
            return Ok(new { success = true, data = users });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取用户列表失败");
            return StatusCode(500, new { success = false, message = "获取用户列表失败" });
        }
    }

    /// <summary>
    /// 更新用户信息
    /// </summary>
    [HttpPut("{id}")]
    public async Task<ActionResult<UserDto>> UpdateUser(Guid id, [FromBody] UpdateUserDto dto)
    {
        try
        {
            var user = await _userService.UpdateUserAsync(id, dto);
            if (user == null)
            {
                return NotFound(new { success = false, message = "用户不存在" });
            }
            return Ok(new { success = true, data = user, message = "用户信息更新成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "更新用户信息失败: {UserId}", id);
            return StatusCode(500, new { success = false, message = "更新用户信息失败" });
        }
    }

    /// <summary>
    /// 删除用户（管理员）
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteUser(Guid id)
    {
        try
        {
            var result = await _userService.DeleteUserAsync(id);
            if (!result)
            {
                return NotFound(new { success = false, message = "用户不存在" });
            }
            return Ok(new { success = true, message = "用户删除成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "删除用户失败: {UserId}", id);
            return StatusCode(500, new { success = false, message = "删除用户失败" });
        }
    }
}

public class UpdateUserDto
{
    public string? Email { get; set; }
    public string? Avatar { get; set; }
    public string? Role { get; set; }
}
