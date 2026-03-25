using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 报表定义
/// </summary>
public class ReportDefinition
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string ReportName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string ReportType { get; set; } = "table"; // table, chart, pivot
    
    [Required]
    public string DataSource { get; set; } = string.Empty; // SQL or API
    
    public string? Columns { get; set; } // JSON格式
    
    public string? Filters { get; set; } // JSON格式
    
    public string? ChartConfig { get; set; } // JSON格式（图表配置）
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    public bool IsPublic { get; set; } = false;
    
    public Guid? CreatedBy { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}