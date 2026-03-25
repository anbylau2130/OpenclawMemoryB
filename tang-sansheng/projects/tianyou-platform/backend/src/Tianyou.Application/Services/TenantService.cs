using Microsoft.EntityFrameworkCore;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;

namespace Tianyou.Application.Services;

/// <summary>
/// 租户管理服务
/// </summary>
public class TenantService
{
    private readonly TianyouDbContext _context;
    
    public TenantService(TianyouDbContext context)
    {
        _context = context;
    }
    
    public async Task<Tenant> CreateTenantAsync(string tenantName, string tenantCode, 
        string? domain = null, string? description = null, int maxUsers = 100)
    {
        if (await _context.Tenants.AnyAsync(t => t.TenantCode == tenantCode))
        {
            throw new Exception($"租户代码 '{tenantCode}' 已存在");
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
        
        return tenant;
    }
    
    public async Task<Tenant> UpdateTenantAsync(Guid tenantId, string tenantName, 
        string? description = null, int? maxUsers = null)
    {
        var tenant = await _context.Tenants.FindAsync(tenantId);
        if (tenant == null) throw new Exception("租户不存在");
        
        tenant.TenantName = tenantName;
        tenant.Description = description;
        if (maxUsers.HasValue) tenant.MaxUsers = maxUsers.Value;
        tenant.UpdatedAt = DateTime.UtcNow;
        
        await _context.SaveChangesAsync();
        return tenant;
    }
    
    public async Task<Tenant> SuspendTenantAsync(Guid tenantId)
    {
        var tenant = await _context.Tenants.FindAsync(tenantId);
        if (tenant == null) throw new Exception("租户不存在");
        
        tenant.Status = "suspended";
        tenant.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();
        
        return tenant;
    }
    
    public async Task<List<Tenant>> GetTenantsAsync()
    {
        return await _context.Tenants
            .Include(t => t.Users)
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync();
    }
    
    public async Task<Tenant?> GetTenantAsync(Guid tenantId)
    {
        return await _context.Tenants
            .Include(t => t.Users)
            .FirstOrDefaultAsync(t => t.Id == tenantId);
    }
}