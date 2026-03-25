using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 代码生成模板
/// </summary>
public class CodeTemplate
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string TemplateName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string TemplateType { get; set; } = "entity"; // entity, api, service, ui
    
    [Required]
    public string TemplateContent { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    public string? Language { get; set; } = "csharp"; // csharp, typescript, sql
    
    public bool IsSystem { get; set; } = false;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}