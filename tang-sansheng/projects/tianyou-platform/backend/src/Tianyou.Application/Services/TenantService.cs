using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;
using Tianyou.Application.Validators;

namespace Tianyou.Application.Services;

/// <summary>
/// 租户管理服务
/// </summary>
public class TenantService
{
    private readonly TianyouDbContext _context;
    private readonly ILogger<TenantService> _logger;
    private readonly ICacheService _cache;

    public TenantService(TianyouDbContext context, ILogger<TenantService> logger, ICacheService cache)
    {
        _context = context;
        _logger = logger;
        _cache = cache;
    }
    
    public async Task<Tenant> CreateTenantAsync(string tenantName, string tenantCode, 
        string? domain = null, string? description = null, int maxUsers = 100)
    {
        // 输入验证
        InputValidator.ValidateTenantName(tenantName);
        InputValidator.ValidateTenantCode(tenantCode);
        InputValidator.ValidateDomain(domain);
        InputValidator.ValidateDescription(description);
        InputValidator.ValidateMaxUsers(maxUsers);

        if (await _context.Tenants.AnyAsync(t => t.TenantCode == tenantCode))
        {
            _logger.LogWarning("创建租户失败：租户代码已存在 - TenantCode: {TenantCode}", tenantCode);
            throw new Exception("租户代码已存在");
        }
        
        var tenant = new Tenant
        {
            Id = Guid.NewGuid(),
            TenantName = tenantName,
            TenantCode = tenantCode,
            Domain = domain,
            Description = description,
            Status = "active",
            MaxUsers = maxUsers,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        _context.Tenants.Add(tenant);
        await _context.SaveChangesAsync();

        // 清除租户列表缓存
        await _cache.RemoveAsync(CacheKeys.Tenant.List(1, 1000));

        _logger.LogInformation("租户创建成功 - TenantId: {TenantId}, TenantCode: {TenantCode}", tenant.Id, tenant.TenantCode);

        return tenant;
    }
    
    public async Task<Tenant> UpdateTenantAsync(Guid tenantId, string tenantName, 
        string? description = null, int? maxUsers = null)
    {
        // 输入验证
        InputValidator.ValidateGuid(tenantId, "租户ID");
        InputValidator.ValidateTenantName(tenantName);
        InputValidator.ValidateDescription(description);

        if (maxUsers.HasValue)
        {
            InputValidator.ValidateMaxUsers(maxUsers.Value);
        }

        var tenant = await _context.Tenants.FindAsync(tenantId);
        if (tenant == null)
        {
            _logger.LogWarning("更新租户失败：租户不存在 - TenantId: {TenantId}", tenantId);
            throw new Exception("租户不存在");
        }

        tenant.TenantName = tenantName;
        tenant.Description = description;
        if (maxUsers.HasValue) tenant.MaxUsers = maxUsers.Value;
        tenant.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();

        // 清除租户相关缓存
        await _cache.RemoveAsync(CacheKeys.Tenant.ById(tenantId));
        await _cache.RemoveAsync(CacheKeys.Tenant.List(1, 1000));

        _logger.LogInformation("租户更新成功 - TenantId: {TenantId}", tenantId);

        return tenant;
    }
    
    public async Task<Tenant> SuspendTenantAsync(Guid tenantId)
    {
        // 输入验证
        InputValidator.ValidateGuid(tenantId, "租户ID");

        var tenant = await _context.Tenants.FindAsync(tenantId);
        if (tenant == null)
        {
            _logger.LogWarning("暂停租户失败：租户不存在 - TenantId: {TenantId}", tenantId);
            throw new Exception("租户不存在");
        }

        tenant.Status = "suspended";
        tenant.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        // 清除租户相关缓存
        await _cache.RemoveAsync(CacheKeys.Tenant.ById(tenantId));
        await _cache.RemoveAsync(CacheKeys.Tenant.List(1, 1000));

        _logger.LogInformation("租户已暂停 - TenantId: {TenantId}", tenantId);

        return tenant;
    }
    
    public async Task<List<Tenant>> GetTenantsAsync()
    {
        var cacheKey = CacheKeys.Tenant.List(1, 1000); // 简化处理，使用固定key
        
        return await _cache.GetOrCreateAsync(cacheKey, async () =>
        {
            _logger.LogDebug("从数据库加载租户列表");
            return await _context.Tenants
                .Include(t => t.Users)
                .OrderByDescending(t => t.CreatedAt)
                .ToListAsync();
        }, TimeSpan.FromMinutes(30));
    }
    
    public async Task<Tenant?> GetTenantAsync(Guid tenantId)
    {
        // 输入验证
        InputValidator.ValidateGuid(tenantId, "租户ID");

        var cacheKey = CacheKeys.Tenant.ById(tenantId);
        
        return await _cache.GetOrCreateAsync(cacheKey, async () =>
        {
            _logger.LogDebug("从数据库加载租户详情 - TenantId: {TenantId}", tenantId);
            return await _context.Tenants
                .Include(t => t.Users)
                .FirstOrDefaultAsync(t => t.Id == tenantId);
        }, TimeSpan.FromMinutes(30));
    }
}