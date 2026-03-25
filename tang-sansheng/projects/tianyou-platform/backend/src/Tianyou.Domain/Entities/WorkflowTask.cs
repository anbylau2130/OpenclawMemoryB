using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 工作流任务
/// </summary>
public class WorkflowTask
{
    public Guid Id { get; set; }
    
    public Guid WorkflowInstanceId { get; set; }
    
    [Required]
    [StringLength(100)]
    public string TaskName { get; set; } = string.Empty;
    
    [StringLength(50)]
    public string TaskType { get; set; } = "approval"; // approval, review, notification, etc.
    
    [Required]
    [StringLength(50)]
    public string Status { get; set; } = "pending"; // pending, completed, cancelled
    
    public Guid? AssignedTo { get; set; }
    
    public string? TaskData { get; set; } // JSON格式
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? CompletedAt { get; set; }
    
    // 导航属性
    public WorkflowInstance Instance { get; set; } = null!;
}