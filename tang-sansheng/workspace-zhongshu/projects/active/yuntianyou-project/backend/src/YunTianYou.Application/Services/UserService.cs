using YunTianYou.Application.DTOs;

namespace YunTianYou.Application.Services;

/// <summary>
/// 用户服务接口
/// </summary>
public interface IUserService
{
    Task<AuthResponseDto> LoginAsync(LoginDto dto);
    Task<AuthResponseDto> RegisterAsync(RegisterDto dto);
    Task<UserDto?> GetUserByIdAsync(Guid id);
    Task<IEnumerable<UserDto>> GetAllUsersAsync();
    Task<UserDto?> UpdateUserAsync(Guid id, UpdateUserDto dto);
    Task<bool> DeleteUserAsync(Guid id);
}

/// <summary>
/// 用户服务实现
/// </summary>
public class UserService : IUserService
{
    private readonly YunTianYouDbContext _context;
    private readonly IJwtService _jwtService;
    private readonly ILogger<UserService> _logger;

    public UserService(YunTianYouDbContext context, IJwtService jwtService, ILogger<UserService> logger)
    {
        _context = context;
        _jwtService = jwtService;
        _logger = logger;
    }

    public async Task<AuthResponseDto> LoginAsync(LoginDto dto)
    {
        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Username == dto.Username && u.IsActive);

        if (user == null || !VerifyPassword(dto.Password, user.PasswordHash))
        {
            return new AuthResponseDto
            {
                Success = false,
                Message = "用户名或密码错误"
            };
        }

        var token = _jwtService.GenerateToken(user);

        return new AuthResponseDto
        {
            Success = true,
            Token = token,
            User = new UserDto
            {
                Id = user.Id,
                Username = user.Username,
                Email = user.Email,
                Role = user.Role,
                Avatar = user.Avatar,
                IsActive = user.IsActive,
                CreatedAt = user.CreatedAt
            }
        };
    }

    public async Task<AuthResponseDto> RegisterAsync(RegisterDto dto)
    {
        // 检查用户名是否已存在
        if (await _context.Users.AnyAsync(u => u.Username == dto.Username))
        {
            return new AuthResponseDto
            {
                Success = false,
                Message = "用户名已存在"
            };
        }

        // 检查邮箱是否已存在
        if (await _context.Users.AnyAsync(u => u.Email == dto.Email))
        {
            return new AuthResponseDto
            {
                Success = false,
                Message = "邮箱已被注册"
            };
        }

        var user = new User
        {
            Username = dto.Username,
            Email = dto.Email,
            PasswordHash = HashPassword(dto.Password),
            Role = "user",
            IsActive = true
        };

        _context.Users.Add(user);
        await _context.SaveChangesAsync();

        var token = _jwtService.GenerateToken(user);

        return new AuthResponseDto
        {
            Success = true,
            Token = token,
            User = new UserDto
            {
                Id = user.Id,
                Username = user.Username,
                Email = user.Email,
                Role = user.Role,
                IsActive = user.IsActive,
                CreatedAt = user.CreatedAt
            }
        };
    }

    public async Task<UserDto?> GetUserByIdAsync(Guid id)
    {
        var user = await _context.Users.FindAsync(id);
        if (user == null) return null;

        return new UserDto
        {
            Id = user.Id,
            Username = user.Username,
            Email = user.Email,
            Role = user.Role,
            Avatar = user.Avatar,
            IsActive = user.IsActive,
            CreatedAt = user.CreatedAt
        };
    }

    public async Task<IEnumerable<UserDto>> GetAllUsersAsync()
    {
        var users = await _context.Users
            .Where(u => !u.IsDeleted)
            .OrderByDescending(u => u.CreatedAt)
            .ToListAsync();

        return users.Select(u => new UserDto
        {
            Id = u.Id,
            Username = u.Username,
            Email = u.Email,
            Role = u.Role,
            Avatar = u.Avatar,
            IsActive = u.IsActive,
            CreatedAt = u.CreatedAt
        });
    }

    public async Task<UserDto?> UpdateUserAsync(Guid id, UpdateUserDto dto)
    {
        var user = await _context.Users.FindAsync(id);
        if (user == null) return null;

        if (!string.IsNullOrEmpty(dto.Email))
            user.Email = dto.Email;
        
        if (!string.IsNullOrEmpty(dto.Avatar))
            user.Avatar = dto.Avatar;
        
        if (!string.IsNullOrEmpty(dto.Role))
            user.Role = dto.Role;

        user.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        return await GetUserByIdAsync(id);
    }

    public async Task<bool> DeleteUserAsync(Guid id)
    {
        var user = await _context.Users.FindAsync(id);
        if (user == null) return false;

        user.IsDeleted = true;
        user.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        return true;
    }

    private string HashPassword(string password)
    {
        // 使用BCrypt哈希密码
        return BCrypt.Net.BCrypt.HashPassword(password, 12);
    }

    private bool VerifyPassword(string password, string hash)
    {
        return BCrypt.Net.BCrypt.Verify(password, hash);
    }
}

public interface IJwtService
{
    string GenerateToken(User user);
}

public class JwtService : IJwtService
{
    private readonly IConfiguration _configuration;

    public JwtService(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public string GenerateToken(User user)
    {
        // TODO: 实现JWT token生成
        return $"token_{user.Id}_{DateTime.UtcNow.Ticks}";
    }
}

public class UpdateUserDto
{
    public string? Email { get; set; }
    public string? Avatar { get; set; }
    public string? Role { get; set; }
}
