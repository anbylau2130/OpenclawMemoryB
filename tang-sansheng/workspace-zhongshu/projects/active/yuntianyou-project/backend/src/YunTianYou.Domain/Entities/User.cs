using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace YunTianYou.Domain.Entities;

/// <summary>
/// 用户实体 - 低代码平台用户
/// </summary>
[Table("users")]
public class User : BaseEntity
{
    [Required]
    [StringLength(50)]
    public string Username { get; set; } = string.Empty;
    
    [Required]
    [StringLength(100)]
    public string Email { get; set; } = string.Empty;
    
    [Required]
    [StringLength(255)]
    public string PasswordHash { get; set; } = string.Empty;
    
    [StringLength(50)]
    public string? Role { get; set; } = "user";
    
    public bool IsActive { get; set; } = true;
    
    public string? Avatar { get; set; }
    
    // 导航属性
    public virtual ICollection<Form> Forms { get; set; } = new List<Form>();
    public virtual ICollection<FormInstance> FormInstances { get; set; } = new List<FormInstance>();
}

/// <summary>
/// 表单模板实体 - 低代码表单定义
/// </summary>
[Table("forms")]
public class Form : BaseEntity
{
    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    [Required]
    public string Schema { get; set; } = "{}"; // JSON schema
    
    [Required]
    public string Fields { get; set; } = "[]"; // JSON array of field definitions
    
    public bool IsPublished { get; set; } = false;
    
    public int Version { get; set; } = 1;
    
    [Required]
    public Guid CreatedByUserId { get; set; }
    
    [ForeignKey(nameof(CreatedByUserId))]
    public virtual User CreatedByUser { get; set; } = null!;
    
    public virtual ICollection<FormInstance> Instances { get; set; } = new List<FormInstance>();
}

/// <summary>
/// 表单实例实体 - 用户提交的表单数据
/// </summary>
[Table("form_instances")]
public class FormInstance : BaseEntity
{
    [Required]
    public Guid FormId { get; set; }
    
    [ForeignKey(nameof(FormId))]
    public virtual Form Form { get; set; } = null!;
    
    [Required]
    public string Data { get; set; } = "{}"; // JSON data
    
    public string Status { get; set; } = "draft"; // draft, submitted, approved, rejected
    
    [Required]
    public Guid SubmittedByUserId { get; set; }
    
    [ForeignKey(nameof(SubmittedByUserId))]
    public virtual User SubmittedByUser { get; set; } = null!;
    
    public DateTime? SubmittedAt { get; set; }
}

/// <summary>
/// 字段类型枚举
/// </summary>
public enum FieldType
{
    Text = 1,
    Number = 2,
    Date = 3,
    DateTime = 4,
    Select = 5,
    MultiSelect = 6,
    Checkbox = 7,
    Radio = 8,
    Textarea = 9,
    File = 10,
    Image = 11,
    Email = 12,
    Phone = 13,
    Url = 14,
    Currency = 15
}
