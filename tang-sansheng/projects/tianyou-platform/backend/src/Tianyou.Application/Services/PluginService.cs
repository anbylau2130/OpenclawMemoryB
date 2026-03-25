using Microsoft.EntityFrameworkCore;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;

namespace Tianyou.Application.Services;

/// <summary>
/// 插件管理服务
/// </summary>
public class PluginService
{
    private readonly TianyouDbContext _context;
    
    public PluginService(TianyouDbContext context)
    {
        _context = context;
    }
    
    public async Task<PluginDefinition> InstallPluginAsync(string pluginName, string pluginCode, 
        string pluginType, string assemblyPath, string className, string? description = null, string? config = null)
    {
        if (await _context.PluginDefinitions.AnyAsync(p => p.PluginCode == pluginCode))
        {
            throw new Exception($"插件代码 '{pluginCode}' 已存在");
        }
        
        var plugin = new PluginDefinition
        {
            Id = Guid.NewGuid(),
            PluginName = pluginName,
            PluginCode = pluginCode,
            PluginType = pluginType,
            AssemblyPath = assemblyPath,
            ClassName = className,
            Description = description,
            Config = config,
            IsEnabled = false,
            Version = 1,
            InstalledAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        _context.PluginDefinitions.Add(plugin);
        await _context.SaveChangesAsync();
        
        return plugin;
    }
    
    public async Task<PluginDefinition> EnablePluginAsync(Guid pluginId)
    {
        var plugin = await _context.PluginDefinitions.FindAsync(pluginId);
        if (plugin == null) throw new Exception("插件不存在");
        
        plugin.IsEnabled = true;
        plugin.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();
        
        return plugin;
    }
    
    public async Task<PluginDefinition> DisablePluginAsync(Guid pluginId)
    {
        var plugin = await _context.PluginDefinitions.FindAsync(pluginId);
        if (plugin == null) throw new Exception("插件不存在");
        
        plugin.IsEnabled = false;
        plugin.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();
        
        return plugin;
    }
    
    public async Task<List<PluginDefinition>> GetPluginsAsync()
    {
        return await _context.PluginDefinitions
            .OrderByDescending(p => p.InstalledAt)
            .ToListAsync();
    }
}