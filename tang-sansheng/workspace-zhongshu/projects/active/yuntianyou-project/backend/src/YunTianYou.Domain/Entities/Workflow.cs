using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace YunTianYou.Domain.Entities;

/// <summary>
/// 工作流定义实体 - 流程模板
/// </summary>
[Table("workflows")]
public class Workflow : BaseEntity
{
    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    [Required]
    public string Definition { get; set; } = "{}"; // JSON: nodes, edges, conditions
    
    public bool IsActive { get; set; } = true;
    
    public int Version { get; set; } = 1;
    
    [Required]
    public Guid CreatedByUserId { get; set; }
    
    [ForeignKey(nameof(CreatedByUserId))]
    public virtual User CreatedByUser { get; set; } = null!;
    
    public virtual ICollection<WorkflowInstance> Instances { get; set; } = new List<WorkflowInstance>();
}

/// <summary>
/// 工作流实例实体 - 流程执行记录
/// </summary>
[Table("workflow_instances")]
public class WorkflowInstance : BaseEntity
{
    [Required]
    public Guid WorkflowId { get; set; }
    
    [ForeignKey(nameof(WorkflowId))]
    public virtual Workflow Workflow { get; set; } = null!;
    
    public string Status { get; set; } = "pending"; // pending, running, completed, cancelled
    
    public string CurrentNode { get; set; } = "start";
    
    [Required]
    public string Data { get; set; } = "{}"; // 流程数据
    
    [Required]
    public Guid InitiatedByUserId { get; set; }
    
    [ForeignKey(nameof(InitiatedByUserId))]
    public virtual User InitiatedByUser { get; set; } = null!;
    
    public DateTime? StartedAt { get; set; }
    
    public DateTime? CompletedAt { get; set; }
    
    public virtual ICollection<WorkflowApproval> Approvals { get; set; } = new List<WorkflowApproval>();
}

/// <summary>
/// 工作流审批记录
/// </summary>
[Table("workflow_approvals")]
public class WorkflowApproval : BaseEntity
{
    [Required]
    public Guid WorkflowInstanceId { get; set; }
    
    [ForeignKey(nameof(WorkflowInstanceId))]
    public virtual WorkflowInstance WorkflowInstance { get; set; } = null!;
    
    public string NodeName { get; set; } = string.Empty;
    
    [Required]
    public Guid ApprovedByUserId { get; set; }
    
    [ForeignKey(nameof(ApprovedByUserId))]
    public virtual User ApprovedByUser { get; set; } = null!;
    
    public string Action { get; set; } = "pending"; // pending, approved, rejected
    
    public string? Comment { get; set; }
    
    public DateTime? ActionAt { get; set; }
}

/// <summary>
/// 数据模型定义 - 低代码数据建模
/// </summary>
[Table("data_models")]
public class DataModel : BaseEntity
{
    [Required]
    [StringLength(100)]
    public string Name { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    [Required]
    public string Schema { get; set; } = "{}"; // JSON: fields, indexes, relations
    
    public string TableName { get; set; } = string.Empty; // 生成的数据库表名
    
    public bool IsPublished { get; set; } = false;
    
    [Required]
    public Guid CreatedByUserId { get; set; }
    
    [ForeignKey(nameof(CreatedByUserId))]
    public virtual User CreatedByUser { get; set; } = null!;
    
    public virtual ICollection<GeneratedCode> GeneratedCodes { get; set; } = new List<GeneratedCode>();
}

/// <summary>
/// 生成的代码记录
/// </summary>
[Table("generated_codes")]
public class GeneratedCode : BaseEntity
{
    [Required]
    public Guid DataModelId { get; set; }
    
    [ForeignKey(nameof(DataModelId))]
    public virtual DataModel DataModel { get; set; } = null!;
    
    public string CodeType { get; set; } = string.Empty; // entity, service, controller, react
    
    public string FileName { get; set; } = string.Empty;
    
    [Required]
    public string Content { get; set; } = string.Empty;
    
    public string Language { get; set; } = "csharp"; // csharp, typescript, sql
}
