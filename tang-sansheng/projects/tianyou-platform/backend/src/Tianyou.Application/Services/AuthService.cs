using Microsoft.Extensions.Configuration;
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
    
    public AuthService(TianyouDbContext context, IConfiguration configuration)
    {
        _context = context;
        _configuration = configuration;
    }
    
    /// <summary>
    /// 注册新用户
    /// </summary>
    public async Task<(User user, string token)> RegisterAsync(string username, string email, string password, string fullName)
    {
        // 检查用户名是否已存在
        if (await _context.Users.AnyAsync(u => u.Username == username))
        {
            throw new Exception("用户名已存在");
        }
        
        // 检查邮箱是否已存在
        if (await _context.Users.AnyAsync(u => u.Email == email))
        {
            throw new Exception("邮箱已存在");
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
        
        // 生成JWT Token
        var token = GenerateJwtToken(user);
        
        return (user, token);
    }
    
    /// <summary>
    /// 用户登录
    /// </summary>
    public async Task<(User user, string token)> LoginAsync(string username, string password)
    {
        var user = await _context.Users
            .Include(u => u.Roles)
            .ThenInclude(r => r.Permissions)
            .FirstOrDefaultAsync(u => u.Username == username);
        
        if (user == null || !BCrypt.Net.BCrypt.Verify(password, user.PasswordHash))
        {
            throw new Exception("用户名或密码错误");
        }
        
        // 更新最后登录时间
        user.LastLoginAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();
        
        // 生成JWT Token
        var token = GenerateJwtToken(user);
        
        return (user, token);
    }
    
    /// <summary>
    /// 生成JWT Token
    /// </summary>
    private string GenerateJwtToken(User user)
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