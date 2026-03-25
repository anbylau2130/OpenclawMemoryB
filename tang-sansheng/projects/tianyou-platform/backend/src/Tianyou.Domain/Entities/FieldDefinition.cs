using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 字段定义
/// </summary>
public class FieldDefinition
{
    public Guid Id { get; set; }
    
    public Guid EntityDefinitionId { get; set; }
    
    [Required]
    [StringLength(100)]
    public string FieldName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string FieldType { get; set; } = "text"; // text, number, date, datetime, boolean, select, etc.
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    public bool IsRequired { get; set; } = false;
    
    public bool IsUnique { get; set; } = false;
    
    public int? MaxLength { get; set; }
    
    public string? DefaultValue { get; set; }
    
    public string? ValidationRule { get; set; }
    
    public int DisplayOrder { get; set; } = 0;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    // 导航属性
    public EntityDefinition Entity { get; set; } = null!;
}