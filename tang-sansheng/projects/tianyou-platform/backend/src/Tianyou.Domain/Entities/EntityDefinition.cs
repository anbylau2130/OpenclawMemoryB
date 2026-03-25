using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 动态实体定义
/// </summary>
public class EntityDefinition
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string EntityName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(100)]
    public string TableName { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    public bool IsSystem { get; set; } = false;
    
    public bool IsActive { get; set; } = true;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    // 导航属性
    public ICollection<FieldDefinition> Fields { get; set; } = new List<FieldDefinition>();
}