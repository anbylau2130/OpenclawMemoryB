using System.ComponentModel.DataAnnotations.Schema;

namespace YunTianYou.Domain.Entities;

/// <summary>
/// 基础实体类
/// </summary>
public abstract class BaseEntity
{
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public Guid Id { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    public DateTime? UpdatedAt { get; set; }
    
    public Guid? CreatedBy { get; set; }
    
    public Guid? UpdatedBy { get; set; }
    
    public bool IsDeleted { get; set; } = false;
}
