using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 插件定义
/// </summary>
public class PluginDefinition
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string PluginName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(100)]
    public string PluginCode { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    [Required]
    [StringLength(50)]
    public string PluginType { get; set; } = "module"; // module, theme, connector
    
    [Required]
    [StringLength(200)]
    public string AssemblyPath { get; set; } = string.Empty;
    
    [Required]
    [StringLength(200)]
    public string ClassName { get; set; } = string.Empty;
    
    public bool IsEnabled { get; set; } = false;
    
    public int Version { get; set; } = 1;
    
    public string? Config { get; set; } // JSON格式配置
    
    public DateTime InstalledAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}