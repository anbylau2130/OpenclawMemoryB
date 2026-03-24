using System.ComponentModel.DataAnnotations.Schema;

namespace YunTianYou.Domain.Entities;

/// <summary>
/// 插件实体 - 低代码平台插件管理
/// </summary>
[Table("plugins")]
public class Plugin : BaseEntity
{
    [Column("name", TypeName = "varchar(100)")]
    public string Name { get; set; } = string.Empty;
    
    [Column("display_name", TypeName = "varchar(200)")]
    public string DisplayName { get; set; } = string.Empty;
    
    [Column("description", TypeName = "text")]
    public string? Description { get; set; }
    
    [Column("type", TypeName = "varchar(50)")]
    public string Type { get; set; } = string.Empty; // form, list, operation, workflow
    
    [Column("category", TypeName = "varchar(50)")]
    public string Category { get; set; } = "custom";
    
    [Column("version", TypeName = "varchar(20)")]
    public string Version { get; set; } = "1.0.0";
    
    [Column("script", TypeName = "text")]
    public string Script { get; set; } = string.Empty;
    
    [Column("config_schema", TypeName = "jsonb")]
    public string ConfigSchema { get; set; } = "{}";
    
    [Column("is_enabled")]
    public bool IsEnabled { get; set; } = true;
    
    [Column("is_system")]
    public bool IsSystem { get; set; } = false;
    
    [Column("author", TypeName = "varchar(100)")]
    public string? Author { get; set; }
    
    [Column("icon", TypeName = "varchar(100)")]
    public string? Icon { get; set; }
    
    [Column("order_index")]
    public int OrderIndex { get; set; } = 0;
}

/// <summary>
/// 审计日志实体 - 操作记录
/// </summary>
[Table("audit_logs")]
public class AuditLog : BaseEntity
{
    [Column("user_id")]
    public Guid? UserId { get; set; }
    
    [ForeignKey("UserId")]
    public virtual User? User { get; set; }
    
    [Column("action", TypeName = "varchar(100)")]
    public string Action { get; set; } = string.Empty;
    
    [Column("entity_type", TypeName = "varchar(100)")]
    public string EntityType { get; set; } = string.Empty;
    
    [Column("entity_id", TypeName = "varchar(100)")]
    public string? EntityId { get; set; }
    
    [Column("old_values", TypeName = "jsonb")]
    public string? OldValues { get; set; }
    
    [Column("new_values", TypeName = "jsonb")]
    public string? NewValues { get; set; }
    
    [Column("ip_address", TypeName = "varchar(50)")]
    public string? IpAddress { get; set; }
    
    [Column("user_agent", TypeName = "varchar(500)")]
    public string? UserAgent { get; set; }
    
    [Column("description", TypeName = "text")]
    public string? Description { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// 表单实例 - 用户提交的表单数据
/// </summary>
[Table("form_instances")]
public class FormInstance : BaseEntity
{
    [Column("form_id")]
    public Guid FormId { get; set; }
    
    [ForeignKey("FormId")]
    public virtual Form Form { get; set; } = null!;
    
    [Column("data", TypeName = "jsonb")]
    public string Data { get; set; } = "{}";
    
    [Column("status", TypeName = "varchar(20)")]
    public string Status { get; set; } = "draft"; // draft, submitted, approved, rejected
    
    [Column("submitted_by_user_id")]
    public Guid SubmittedByUserId { get; set; }
    
    [ForeignKey("SubmittedByUserId")]
    public virtual User SubmittedByUser { get; set; } = null!;
    
    public DateTime? SubmittedAt { get; set; }
    
    public DateTime? ApprovedAt { get; set; }
    
    [Column("approved_by_user_id")]
    public Guid? ApprovedByUserId { get; set; }
    
    [ForeignKey("ApprovedByUserId")]
    public virtual User? ApprovedByUser { get; set; }
    
    public virtual ICollection<WorkflowInstance> WorkflowInstances { get; set; } = new List<WorkflowInstance>();
}
