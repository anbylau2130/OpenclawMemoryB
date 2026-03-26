using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using BCrypt.Net;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;

namespace Tianyou.Application.Services;

/// <summary>
/// 认证服务
/// </summary>
public class AuthService
{
    private readonly TianyouDbContext _context;
    private readonly IConfiguration _configuration;
    private readonly ILogger<AuthService> _logger;

    public AuthService(TianyouDbContext context, IConfiguration configuration, ILogger<AuthService> logger)
    {
        _context = context;
        _configuration = configuration;
        _logger = logger;
    }
    
    /// <summary>
    /// 注册新用户
    /// </summary>
    public async Task<(User user, string token)> RegisterAsync(string username, string email, string password, string fullName)
    {
        // 检查用户名是否已存在
        if (await _context.Users.AnyAsync(u => u.Username == username))
        {
            // [P2-04修复] 日志脱敏：不记录敏感信息
            _logger.LogWarning("注册失败：用户名已存在 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("注册失败，请检查输入信息");
        }

        // 检查邮箱是否已存在
        if (await _context.Users.AnyAsync(u => u.Email == email))
        {
            // [P2-04修复] 日志脱敏：不记录敏感信息
            _logger.LogWarning("注册失败：邮箱已存在 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("注册失败，请检查输入信息");
        }
        
        // 创建新用户
        var user = new User
        {
            Id = Guid.NewGuid(),
            Username = username,
            Email = email,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(password, 12),
            FullName = fullName,
            Status = "active",
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        // 分配默认角色
        var defaultRole = await _context.Roles.FirstOrDefaultAsync(r => r.RoleCode == "user");
        if (defaultRole != null)
        {
            user.Roles.Add(defaultRole);
        }

        _context.Users.Add(user);
        await _context.SaveChangesAsync();

        _logger.LogInformation("用户注册成功 - UserId: {UserId}, Username: {Username}", user.Id, user.Username);

        // 生成JWT Token
        var token = GenerateJwtToken(user);

        return (user, token);
    }
    
    /// <summary>
    /// 用户登录
    /// </summary>
    public async Task<(User user, string token)> LoginAsync(string username, string password)
    {
        // 尝试从缓存获取用户信息
        var cacheKey = CacheKeys.User.ByUsername(username);
        User? user = await _cache.GetAsync<User>(cacheKey);

        if (user == null)
        {
            // 缓存未命中，从数据库查询
            user = await _context.Users
                .Include(u => u.Roles)
                .ThenInclude(r => r.Permissions)
                .FirstOrDefaultAsync(u => u.Username == username);

            if (user != null)
            {
                // 缓存用户信息（5分钟）
                await _cache.SetAsync(cacheKey, user, TimeSpan.FromMinutes(5));
                _logger.LogDebug("用户信息已缓存 - Username: {Username}", username);
            }
        }
        else
        {
            _logger.LogDebug("用户信息从缓存获取 - Username: {Username}", username);
        }

        if (user == null || !BCrypt.Net.BCrypt.Verify(password, user.PasswordHash))
        {
            // [P2-04修复] 日志脱敏：不记录敏感信息
            _logger.LogWarning("登录失败：用户名或密码错误 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("用户名或密码错误");
        }

        // 更新最后登录时间
        user.LastLoginAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        _logger.LogInformation("用户登录成功 - UserId: {UserId}, Username: {Username}", user.Id, user.Username);

        // 生成JWT Token
        var token = GenerateJwtToken(user);

        return (user, token);
    }
    
    /// <summary>
    /// 生成JWT Token
    /// </summary>
    private string GenerateJwtToken(User user)
    {
        try
        {
            var jwtSettings = _configuration.GetSection("Jwt");
            var key = Encoding.UTF8.GetBytes(jwtSettings["Key"]!);

            var claims = new List<Claim>
            {
                new(ClaimTypes.NameIdentifier, user.Id.ToString()),
                new(ClaimTypes.Name, user.Username),
                new(ClaimTypes.Email, user.Email),
                new("fullName", user.FullName ?? ""),
                new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
            };

            // 添加角色
            foreach (var role in user.Roles)
            {
                claims.Add(new Claim(ClaimTypes.Role, role.RoleCode));

                // 添加权限
                foreach (var permission in role.Permissions)
                {
                    claims.Add(new Claim("permission", permission.PermissionCode));
                }
            }

            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(claims),
                Expires = DateTime.UtcNow.AddHours(int.Parse(jwtSettings["ExpireHours"]!)),
                SigningCredentials = new SigningCredentials(
                    new SymmetricSecurityKey(key),
                    SecurityAlgorithms.HmacSha256Signature),
                Issuer = jwtSettings["Issuer"],
                Audience = jwtSettings["Audience"]
            };

            var tokenHandler = new JwtSecurityTokenHandler();
            var token = tokenHandler.CreateToken(tokenDescriptor);
            return tokenHandler.WriteToken(token);
        }
        catch (Exception ex)
        {
            // [P2-04修复] 日志脱敏：不记录UserId，使用RequestId追踪
            _logger.LogError(ex, "生成JWT Token失败 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("认证服务暂时不可用，请稍后重试");
        }
    }
    
    /// <summary>
    /// 验证密码
    /// </summary>
    public bool VerifyPassword(string password, string hash)
    {
        return BCrypt.Net.BCrypt.Verify(password, hash);
    }
    
    /// <summary>
    /// 哈希密码
    /// </summary>
    public string HashPassword(string password)
    {
        return BCrypt.Net.BCrypt.HashPassword(password, 12);
    }
}