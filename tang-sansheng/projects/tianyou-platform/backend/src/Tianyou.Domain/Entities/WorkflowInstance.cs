using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 工作流实例
/// </summary>
public class WorkflowInstance
{
    public Guid Id { get; set; }
    
    public Guid WorkflowDefinitionId { get; set; }
    
    [Required]
    [StringLength(50)]
    public string Status { get; set; } = "pending"; // pending, running, completed, cancelled
    
    public Guid? InitiatedBy { get; set; }
    
    public string? CurrentStep { get; set; }
    
    public string? InstanceData { get; set; } // JSON格式（实例数据）
    
    public DateTime StartedAt { get; set; } = DateTime.UtcNow;
    public DateTime? CompletedAt { get; set; }
    
    // 导航属性
    public WorkflowDefinition Workflow { get; set; } = null!;
    public ICollection<WorkflowTask> Tasks { get; set; } = new List<WorkflowTask>();
}