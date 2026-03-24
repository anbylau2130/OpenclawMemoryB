using YunTianYou.Application.DTOs;

namespace YunTianYou.Application.Services;

/// <summary>
/// 插件服务接口
/// </summary>
public interface IPluginService
{
    Task<IEnumerable<PluginDto>> GetAllPluginsAsync();
    Task<IEnumerable<PluginDto>> GetPluginsByTypeAsync(string type);
    Task<PluginDto?> GetPluginByIdAsync(Guid id);
    Task<PluginDto> CreatePluginAsync(CreatePluginDto dto);
    Task<PluginDto?> UpdatePluginAsync(Guid id, UpdatePluginDto dto);
    Task<bool> DeletePluginAsync(Guid id);
    Task<bool> EnablePluginAsync(Guid id);
    Task<bool> DisablePluginAsync(Guid id);
    Task<string> ExecutePluginAsync(Guid id, Dictionary<string, object> context);
}

/// <summary>
/// 插件服务实现
/// </summary>
public class PluginService : IPluginService
{
    private readonly YunTianYouDbContext _context;
    private readonly ILogger<PluginService> _logger;
    private readonly IJavaScriptEngine _jsEngine;

    public PluginService(YunTianYouDbContext context, ILogger<PluginService> logger, IJavaScriptEngine jsEngine)
    {
        _context = context;
        _logger = logger;
        _jsEngine = jsEngine;
    }

    public async Task<IEnumerable<PluginDto>> GetAllPluginsAsync()
    {
        var plugins = await _context.Plugins
            .Where(p => !p.IsDeleted)
            .OrderBy(p => p.Type)
            .ThenBy(p => p.OrderIndex)
            .ToListAsync();

        return plugins.Select(p => new PluginDto
        {
            Id = p.Id,
            Name = p.Name,
            DisplayName = p.DisplayName,
            Description = p.Description,
            Type = p.Type,
            Category = p.Category,
            Version = p.Version,
            IsEnabled = p.IsEnabled,
            IsSystem = p.IsSystem,
            Author = p.Author,
            Icon = p.Icon
        });
    }

    public async Task<IEnumerable<PluginDto>> GetPluginsByTypeAsync(string type)
    {
        var plugins = await _context.Plugins
            .Where(p => p.Type == type && !p.IsDeleted)
            .OrderBy(p => p.OrderIndex)
            .ToListAsync();

        return plugins.Select(p => new PluginDto
        {
            Id = p.Id,
            Name = p.Name,
            DisplayName = p.DisplayName,
            Description = p.Description,
            Type = p.Type,
            IsEnabled = p.IsEnabled
        });
    }

    public async Task<PluginDto?> GetPluginByIdAsync(Guid id)
    {
        var plugin = await _context.Plugins.FindAsync(id);
        if (plugin == null) return null;

        return new PluginDto
        {
            Id = plugin.Id,
            Name = plugin.Name,
            DisplayName = plugin.DisplayName,
            Description = plugin.Description,
            Type = plugin.Type,
            Category = plugin.Category,
            Version = plugin.Version,
            Script = plugin.Script,
            ConfigSchema = plugin.ConfigSchema,
            IsEnabled = plugin.IsEnabled,
            IsSystem = plugin.IsSystem,
            Author = plugin.Author,
            Icon = plugin.Icon
        };
    }

    public async Task<PluginDto> CreatePluginAsync(CreatePluginDto dto)
    {
        var plugin = new Plugin
        {
            Name = dto.Name,
            DisplayName = dto.DisplayName,
            Description = dto.Description,
            Type = dto.Type,
            Category = dto.Category ?? "custom",
            Version = dto.Version ?? "1.0.0",
            Script = dto.Script,
            ConfigSchema = dto.ConfigSchema ?? "{}",
            Author = dto.Author,
            Icon = dto.Icon,
            IsEnabled = false,
            IsSystem = false
        };

        _context.Plugins.Add(plugin);
        await _context.SaveChangesAsync();

        return await GetPluginByIdAsync(plugin.Id) ?? throw new Exception("创建插件失败");
    }

    public async Task<PluginDto?> UpdatePluginAsync(Guid id, UpdatePluginDto dto)
    {
        var plugin = await _context.Plugins.FindAsync(id);
        if (plugin == null) return null;

        if (!string.IsNullOrEmpty(dto.DisplayName))
            plugin.DisplayName = dto.DisplayName;
        if (dto.Description != null)
            plugin.Description = dto.Description;
        if (!string.IsNullOrEmpty(dto.Script))
            plugin.Script = dto.Script;
        if (dto.ConfigSchema != null)
            plugin.ConfigSchema = dto.ConfigSchema;
        if (dto.Icon != null)
            plugin.Icon = dto.Icon;

        plugin.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        return await GetPluginByIdAsync(id);
    }

    public async Task<bool> DeletePluginAsync(Guid id)
    {
        var plugin = await _context.Plugins.FindAsync(id);
        if (plugin == null || plugin.IsSystem) return false;

        plugin.IsDeleted = true;
        plugin.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        return true;
    }

    public async Task<bool> EnablePluginAsync(Guid id)
    {
        var plugin = await _context.Plugins.FindAsync(id);
        if (plugin == null) return false;

        plugin.IsEnabled = true;
        plugin.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        _logger.LogInformation("插件已启用: {PluginName}", plugin.Name);
        return true;
    }

    public async Task<bool> DisablePluginAsync(Guid id)
    {
        var plugin = await _context.Plugins.FindAsync(id);
        if (plugin == null || plugin.IsSystem) return false;

        plugin.IsEnabled = false;
        plugin.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        _logger.LogInformation("插件已禁用: {PluginName}", plugin.Name);
        return true;
    }

    public async Task<string> ExecutePluginAsync(Guid id, Dictionary<string, object> context)
    {
        var plugin = await _context.Plugins.FindAsync(id);
        if (plugin == null || !plugin.IsEnabled)
        {
            throw new Exception("插件不存在或未启用");
        }

        try
        {
            // 执行插件脚本
            var result = await _jsEngine.ExecuteAsync(plugin.Script, context);
            _logger.LogInformation("插件执行成功: {PluginName}", plugin.Name);
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "插件执行失败: {PluginName}", plugin.Name);
            throw new Exception($"插件执行失败: {ex.Message}");
        }
    }
}

// 接口定义
public interface IJavaScriptEngine
{
    Task<string> ExecuteAsync(string script, Dictionary<string, object> context);
}

// DTO定义
public class PluginDto
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string Type { get; set; } = string.Empty;
    public string Category { get; set; } = "custom";
    public string Version { get; set; } = "1.0.0";
    public string? Script { get; set; }
    public string? ConfigSchema { get; set; }
    public bool IsEnabled { get; set; }
    public bool IsSystem { get; set; }
    public string? Author { get; set; }
    public string? Icon { get; set; }
}

public class CreatePluginDto
{
    public string Name { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string Type { get; set; } = string.Empty;
    public string? Category { get; set; }
    public string? Version { get; set; }
    public string Script { get; set; } = string.Empty;
    public string? ConfigSchema { get; set; }
    public string? Author { get; set; }
    public string? Icon { get; set; }
}

public class UpdatePluginDto
{
    public string? DisplayName { get; set; }
    public string? Description { get; set; }
    public string? Script { get; set; }
    public string? ConfigSchema { get; set; }
    public string? Icon { get; set; }
}
