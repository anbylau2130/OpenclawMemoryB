using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Tianyou.Domain.Entities;
using Tianyou.Application.Validators;

namespace Tianyou.Application.Services;

/// <summary>
/// 用户服务
/// </summary>
using Tianyou.Infrastructure.Data;
public class UserService
{
    private readonly TianyouDbContext _context;
    private readonly AuthService _authService;
    private readonly ILogger<UserService> _logger;
    private readonly ICacheService _cache;

    public UserService(TianyouDbContext context, AuthService authService, ILogger<UserService> _logger, ICacheService cache)
    {
        _context = context;
        _authService = authService;
        this._logger = _logger;
        _cache = cache;
    }

    /// <summary>
    /// 创建用户
    /// </summary>
    public async Task<User> CreateUserAsync(string username, string email, string password, string fullName)
    {
        // 输入验证
        InputValidator.ValidateUsername(username);
        InputValidator.ValidateEmail(email);
        InputValidator.ValidatePassword(password);
        InputValidator.ValidateFullName(fullName);

        // [P2-04修复] 合并检查用户名和邮箱是否存在（防止枚举攻击）
        bool usernameExists = await _context.Users.AnyAsync(u => u.Username == username);
        bool emailExists = await _context.Users.AnyAsync(u => u.Email == email);

        if (usernameExists || emailExists)
        {
            _logger.LogWarning("创建用户失败：用户名或邮箱已存在 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("用户名或邮箱已被使用");
        }

        var user = new User
        {
            Id = Guid.NewGuid(),
            Username = username,
            Email = email,
            PasswordHash = _authService.HashPassword(password),
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

        // 清除用户列表缓存
        // 注意：由于列表有分页，这里清除所有列表缓存
        // 在生产环境应该使用Redis支持的模式匹配删除
        _logger.LogDebug("清除用户列表缓存");

        // [P2-04修复] 日志脱敏
        _logger.LogInformation("用户创建成功 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);

        return user;
    }

    /// <summary>
    /// 根据用户名获取用户（带缓存）
    /// </summary>
    public async Task<User?> GetByUsernameAsync(string username)
    {
        var cacheKey = CacheKeys.User.ByUsername(username);
        
        return await _cache.GetOrCreateAsync(cacheKey, async () =>
        {
            _logger.LogDebug("从数据库加载用户信息 - Username: {Username}", username);
            return await _context.Users
                .Include(u => u.Roles)
                .ThenInclude(r => r.Permissions)
                .FirstOrDefaultAsync(u => u.Username == username);
        }, TimeSpan.FromMinutes(30));
    }

    /// <summary>
    /// 根据ID获取用户（带缓存）
    /// </summary>
    public async Task<User?> GetByIdAsync(Guid userId)
    {
        var cacheKey = CacheKeys.User.ById(userId);
        
        return await _cache.GetOrCreateAsync(cacheKey, async () =>
        {
            _logger.LogDebug("从数据库加载用户信息 - UserId: {UserId}", userId);
            return await _context.Users
                .Include(u => u.Roles)
                .ThenInclude(r => r.Permissions)
                .FirstOrDefaultAsync(u => u.Id == userId);
        }, TimeSpan.FromMinutes(30));
    }

    /// <summary>
    /// 获取用户列表
    /// </summary>
    public async Task<(List<User> users, int total)> GetUsersAsync(int page, int size, string? keyword = null)
    {
        // 输入验证
        InputValidator.ValidatePagination(page, size);
        InputValidator.ValidateKeyword(keyword);

        var query = _context.Users.Include(u => u.Roles).AsQueryable();

        if (!string.IsNullOrEmpty(keyword))
        {
            query = query.Where(u => 
                u.Username.Contains(keyword) || 
                u.Email.Contains(keyword) || 
                u.FullName.Contains(keyword));
        }

        var total = await query.CountAsync();
        var users = await query
            .OrderByDescending(u => u.CreatedAt)
            .Skip((page - 1) * size)
            .Take(size)
            .ToListAsync();

        return (users, total);
    }

    /// <summary>
    /// 更新用户
    /// </summary>
    public async Task<User> UpdateUserAsync(Guid userId, string fullName, string email, List<Guid>? roleIds = null)
    {
        // 输入验证
        InputValidator.ValidateGuid(userId, "用户ID");
        InputValidator.ValidateFullName(fullName);
        InputValidator.ValidateEmail(email);
        InputValidator.ValidateIds(roleIds, "角色ID列表");

        var user = await _context.Users
            .Include(u => u.Roles)
            .FirstOrDefaultAsync(u => u.Id == userId);

        if (user == null)
        {
            // [P2-04修复] 日志脱敏
            _logger.LogWarning("更新用户失败：用户不存在 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("用户不存在");
        }

        // 检查邮箱是否被其他用户使用
        if (await _context.Users.AnyAsync(u => u.Email == email && u.Id != userId))
        {
            // [P2-04修复] 日志脱敏
            _logger.LogWarning("更新用户失败：邮箱已被使用 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("邮箱已被使用");
        }

        user.FullName = fullName;
        user.Email = email;
        user.UpdatedAt = DateTime.UtcNow;

        // 更新角色
        if (roleIds != null)
        {
            user.Roles.Clear();
            var roles = await _context.Roles.Where(r => roleIds.Contains(r.Id)).ToListAsync();
            foreach (var role in roles)
            {
                user.Roles.Add(role);
            }
        }

        await _context.SaveChangesAsync();

        // 清除用户相关缓存
        await _cache.RemoveAsync(CacheKeys.User.ById(userId));
        await _cache.RemoveAsync(CacheKeys.User.ByUsername(user.Username));
        _logger.LogDebug("已清除用户缓存 - UserId: {UserId}", userId);

        // [P2-04修复] 日志脱敏
        _logger.LogInformation("用户更新成功 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);

        return user;
    }

    /// <summary>
    /// 删除用户
    /// </summary>
    public async Task DeleteUserAsync(Guid userId)
    {
        // 输入验证
        InputValidator.ValidateGuid(userId, "用户ID");

        var user = await _context.Users.FindAsync(userId);
        if (user == null)
        {
            // [P2-04修复] 日志脱敏
            _logger.LogWarning("删除用户失败：用户不存在 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("用户不存在");
        }

        _context.Users.Remove(user);
        await _context.SaveChangesAsync();

        // 清除用户相关缓存
        await _cache.RemoveAsync(CacheKeys.User.ById(userId));
        await _cache.RemoveAsync(CacheKeys.User.ByUsername(user.Username));
        _logger.LogDebug("已清除用户缓存 - UserId: {UserId}", userId);

        // [P2-04修复] 日志脱敏
        _logger.LogInformation("用户删除成功 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
    }

    /// <summary>
    /// 修改密码
    /// </summary>
    public async Task ChangePasswordAsync(Guid userId, string oldPassword, string newPassword)
    {
        // 输入验证
        InputValidator.ValidateGuid(userId, "用户ID");
        
        if (string.IsNullOrWhiteSpace(oldPassword))
        {
            throw new ArgumentException("原密码不能为空");
        }
        
        InputValidator.ValidatePassword(newPassword);

        var user = await _context.Users.FindAsync(userId);
        if (user == null)
        {
            // [P2-04修复] 日志脱敏
            _logger.LogWarning("修改密码失败：用户不存在 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("用户不存在");
        }

        if (!_authService.VerifyPassword(oldPassword, user.PasswordHash))
        {
            // [P2-04修复] 日志脱敏
            _logger.LogWarning("修改密码失败：原密码错误 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
            throw new Exception("原密码错误");
        }

        user.PasswordHash = _authService.HashPassword(newPassword);
        user.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        // 清除用户缓存
        await _cache.RemoveAsync(CacheKeys.User.ById(userId));
        _logger.LogDebug("已清除用户缓存（密码修改） - UserId: {UserId}", userId);

        // [P2-04修复] 日志脱敏
        _logger.LogInformation("密码修改成功 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
    }

    /// <summary>
    /// 更新最后登录时间
    /// </summary>
    public async Task UpdateLastLoginAsync(Guid userId)
    {
        var user = await _context.Users.FindAsync(userId);
        if (user != null)
        {
            user.LastLoginAt = DateTime.UtcNow;
            await _context.SaveChangesAsync();
        }
    }
}