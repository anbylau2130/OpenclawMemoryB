using System.ComponentModel.DataAnnotations.Schema;

namespace YunTianYou.Domain.Entities;

/// <summary>
/// 工作流实例实体 - 运行时工作流数据
/// </summary>
[Table("workflow_instances")]
public class WorkflowInstance : BaseEntity
{
    [Column("workflow_id")]
    public Guid WorkflowId { get; set; }
    
    [ForeignKey("WorkflowId")]
    public virtual Workflow Workflow { get; set; } = null!;
    
    [Column("form_instance_id")]
    public Guid FormInstanceId { get; set; }
    
    [ForeignKey("FormInstanceId")]
    public virtual FormInstance FormInstance { get; set; } = null!;
    
    [Column("current_node_id", TypeName = "varchar(100)")]
    public string CurrentNodeId { get; set; } = string.Empty;
    
    [Column("status", TypeName = "varchar(20)")]
    public string Status { get; set; } = "running"; // running, completed, cancelled
    
    [Column("data", TypeName = "jsonb")]
    public string Data { get; set; } = "{}";
    
    [Column("started_by_user_id")]
    public Guid StartedByUserId { get; set; }
    
    [ForeignKey("StartedByUserId")]
    public virtual User StartedByUser { get; set; } = null!;
    
    public DateTime? CompletedAt { get; set; }
    
    public virtual ICollection<WorkflowHistory> History { get; set; } = new List<WorkflowHistory>();
}

/// <summary>
/// 工作流历史记录
/// </summary>
[Table("workflow_histories")]
public class WorkflowHistory : BaseEntity
{
    [Column("workflow_instance_id")]
    public Guid WorkflowInstanceId { get; set; }
    
    [ForeignKey("WorkflowInstanceId")]
    public virtual WorkflowInstance WorkflowInstance { get; set; } = null!;
    
    [Column("node_id", TypeName = "varchar(100)")]
    public string NodeId { get; set; } = string.Empty;
    
    [Column("node_name", TypeName = "varchar(200)")]
    public string NodeName { get; set; } = string.Empty;
    
    [Column("action", TypeName = "varchar(50)")]
    public string Action { get; set; } = string.Empty; // approve, reject, submit
    
    [Column("comment", TypeName = "text")]
    public string? Comment { get; set; }
    
    [Column("operator_user_id")]
    public Guid OperatorUserId { get; set; }
    
    [ForeignKey("OperatorUserId")]
    public virtual User OperatorUser { get; set; } = null!;
    
    public DateTime OperatedAt { get; set; } = DateTime.UtcNow;
}
