using Microsoft.EntityFrameworkCore;
using Tianyou.Domain.Entities;

namespace Tianyou.Application.Services;

/// <summary>
/// 用户服务
/// </summary>
using Tianyou.Infrastructure.Data;
public class UserService
{
    private readonly TianyouDbContext _context;
    private readonly AuthService _authService;

    public UserService(TianyouDbContext context, AuthService authService)
    {
        _context = context;
        _authService = authService;
    }

    /// <summary>
    /// 创建用户
    /// </summary>
    public async Task<User> CreateUserAsync(string username, string email, string password, string fullName)
    {
        // 检查用户名是否存在
        if (await _context.Users.AnyAsync(u => u.Username == username))
        {
            throw new Exception("用户名已存在");
        }

        // 检查邮箱是否存在
        if (await _context.Users.AnyAsync(u => u.Email == email))
        {
            throw new Exception("邮箱已存在");
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

        return user;
    }

    /// <summary>
    /// 根据用户名获取用户
    /// </summary>
    public async Task<User?> GetByUsernameAsync(string username)
    {
        return await _context.Users
            .Include(u => u.Roles)
            .ThenInclude(r => r.Permissions)
            .FirstOrDefaultAsync(u => u.Username == username);
    }

    /// <summary>
    /// 根据ID获取用户
    /// </summary>
    public async Task<User?> GetByIdAsync(Guid userId)
    {
        return await _context.Users
            .Include(u => u.Roles)
            .ThenInclude(r => r.Permissions)
            .FirstOrDefaultAsync(u => u.Id == userId);
    }

    /// <summary>
    /// 获取用户列表
    /// </summary>
    public async Task<(List<User> users, int total)> GetUsersAsync(int page, int size, string? keyword = null)
    {
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
        var user = await _context.Users
            .Include(u => u.Roles)
            .FirstOrDefaultAsync(u => u.Id == userId);

        if (user == null)
        {
            throw new Exception("用户不存在");
        }

        // 检查邮箱是否被其他用户使用
        if (await _context.Users.AnyAsync(u => u.Email == email && u.Id != userId))
        {
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
        return user;
    }

    /// <summary>
    /// 删除用户
    /// </summary>
    public async Task DeleteUserAsync(Guid userId)
    {
        var user = await _context.Users.FindAsync(userId);
        if (user == null)
        {
            throw new Exception("用户不存在");
        }

        _context.Users.Remove(user);
        await _context.SaveChangesAsync();
    }

    /// <summary>
    /// 修改密码
    /// </summary>
    public async Task ChangePasswordAsync(Guid userId, string oldPassword, string newPassword)
    {
        var user = await _context.Users.FindAsync(userId);
        if (user == null)
        {
            throw new Exception("用户不存在");
        }

        if (!_authService.VerifyPassword(oldPassword, user.PasswordHash))
        {
            throw new Exception("原密码错误");
        }

        user.PasswordHash = _authService.HashPassword(newPassword);
        user.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();
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