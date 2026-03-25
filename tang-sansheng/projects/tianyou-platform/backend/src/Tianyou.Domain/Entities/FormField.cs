using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 表单字段
/// </summary>
public class FormField
{
    public Guid Id { get; set; }
    
    public Guid FormDefinitionId { get; set; }
    
    [Required]
    [StringLength(100)]
    public string FieldName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string FieldType { get; set; } = "text";
    
    [StringLength(200)]
    public string? Label { get; set; }
    
    public string? Placeholder { get; set; }
    
    public string? DefaultValue { get; set; }
    
    public bool IsRequired { get; set; } = false;
    
    public bool IsVisible { get; set; } = true;
    
    public bool IsEditable { get; set; } = true;
    
    public int DisplayOrder { get; set; } = 0;
    
    public string? ValidationRules { get; set; } // JSON格式
    
    public string? FieldConfig { get; set; } // JSON格式（额外配置）
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    // 导航属性
    public FormDefinition Form { get; set; } = null!;
}