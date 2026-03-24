using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;
using YunTianYou.Domain.Entities;

namespace YunTianYou.Application.Services;

/// <summary>
/// JWT认证服务
/// </summary>
public class AuthService
{
    private readonly IConfiguration _configuration;
    private readonly UserService _userService;
    
    public AuthService(IConfiguration configuration, UserService userService)
    {
        _configuration = configuration;
        _userService = userService;
    }
    
    /// <summary>
    /// 用户注册
    /// </summary>
    public async Task<(User? User, string? Token, string? Error)> RegisterAsync(
        string username, string email, string password)
    {
        // 检查用户是否存在
        var existingUser = await _userService.GetByUsernameAsync(username);
        if (existingUser != null)
        {
            return (null, null, "用户名已存在");
        }
        
        var existingEmail = await _userService.GetByEmailAsync(email);
        if (existingEmail != null)
        {
            return (null, null, "邮箱已被注册");
        }
        
        // 创建用户
        var user = new User
        {
            Username = username,
            Email = email,
            PasswordHash = HashPassword(password),
            Role = "user",
            IsActive = true
        };
        
        var createdUser = await _userService.CreateAsync(user);
        var token = GenerateJwtToken(createdUser);
        
        return (createdUser, token, null);
    }
    
    /// <summary>
    /// 用户登录
    /// </summary>
    public async Task<(User? User, string? Token, string? Error)> LoginAsync(
        string username, string password)
    {
        var user = await _userService.GetByUsernameAsync(username);
        if (user == null)
        {
            return (null, null, "用户名或密码错误");
        }
        
        if (!user.IsActive)
        {
            return (null, null, "账户已被禁用");
        }
        
        if (!VerifyPassword(password, user.PasswordHash))
        {
            return (null, null, "用户名或密码错误");
        }
        
        var token = GenerateJwtToken(user);
        return (user, token, null);
    }
    
    /// <summary>
    /// 生成JWT Token
    /// </summary>
    private string GenerateJwtToken(User user)
    {
        var jwtKey = _configuration["Jwt:Key"] ?? "YunTianYou_Secret_Key_2026_Very_Long_Key_For_Security";
        var jwtIssuer = _configuration["Jwt:Issuer"] ?? "YunTianYou";
        var jwtAudience = _configuration["Jwt:Audience"] ?? "YunTianYou";
        var expirationHours = int.Parse(_configuration["Jwt:ExpirationHours"] ?? "24");
        
        var securityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey));
        var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.HmacSha256);
        
        var claims = new[]
        {
            new Claim(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
            new Claim(JwtRegisteredClaimNames.UniqueName, user.Username),
            new Claim(JwtRegisteredClaimNames.Email, user.Email),
            new Claim(ClaimTypes.Role, user.Role ?? "user"),
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
        };
        
        var token = new JwtSecurityToken(
            issuer: jwtIssuer,
            audience: jwtAudience,
            claims: claims,
            expires: DateTime.UtcNow.AddHours(expirationHours),
            signingCredentials: credentials
        );
        
        return new JwtSecurityTokenHandler().WriteToken(token);
    }
    
    /// <summary>
    /// 密码哈希
    /// </summary>
    private string HashPassword(string password)
    {
        using var sha256 = SHA256.Create();
        var salt = "YunTianYou_Salt_2026";
        var saltedPassword = password + salt;
        var bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(saltedPassword));
        return Convert.ToBase64String(bytes);
    }
    
    /// <summary>
    /// 验证密码
    /// </summary>
    private bool VerifyPassword(string password, string hash)
    {
        return HashPassword(password) == hash;
    }
    
    /// <summary>
    /// 验证JWT Token
    /// </summary>
    public ClaimsPrincipal? ValidateToken(string token)
    {
        try
        {
            var jwtKey = _configuration["Jwt:Key"] ?? "YunTianYou_Secret_Key_2026_Very_Long_Key_For_Security";
            var jwtIssuer = _configuration["Jwt:Issuer"] ?? "YunTianYou";
            var jwtAudience = _configuration["Jwt:Audience"] ?? "YunTianYou";
            
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.UTF8.GetBytes(jwtKey);
            
            var validationParameters = new TokenValidationParameters
            {
                ValidateIssuer = true,
                ValidateAudience = true,
                ValidateLifetime = true,
                ValidateIssuerSigningKey = true,
                ValidIssuer = jwtIssuer,
                ValidAudience = jwtAudience,
                IssuerSigningKey = new SymmetricSecurityKey(key)
            };
            
            var principal = tokenHandler.ValidateToken(token, validationParameters, out _);
            return principal;
        }
        catch
        {
            return null;
        }
    }
}
