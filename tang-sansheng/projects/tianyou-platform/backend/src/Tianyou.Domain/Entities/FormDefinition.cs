using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 表单定义
/// </summary>
public class FormDefinition
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string FormName { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    public Guid? EntityDefinitionId { get; set; }
    
    public bool IsPublished { get; set; } = false;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    // 导航属性
    public ICollection<FormField> Fields { get; set; } = new List<FormField>();
}