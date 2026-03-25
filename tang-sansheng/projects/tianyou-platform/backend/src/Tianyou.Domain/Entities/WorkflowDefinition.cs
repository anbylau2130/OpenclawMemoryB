using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 工作流定义
/// </summary>
public class WorkflowDefinition
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string WorkflowName { get; set; } = string.Empty;
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    public bool IsActive { get; set; } = true;
    
    public string? StepsConfig { get; set; } // JSON格式（步骤配置）
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    // 导航属性
    public ICollection<WorkflowInstance> Instances { get; set; } = new List<WorkflowInstance>();
}