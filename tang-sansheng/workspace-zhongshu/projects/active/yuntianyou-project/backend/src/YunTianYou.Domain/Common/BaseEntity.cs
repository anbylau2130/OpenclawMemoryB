namespace YunTianYou.Domain.Common;

/// <summary>
/// 基础实体类
/// </summary>
public abstract class BaseEntity
{
    /// <summary>
    /// 实体ID
    /// </summary>
    public Guid Id { get; set; }
    
    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; }
    
    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime? UpdatedAt { get; set; }
    
    /// <summary>
    /// 创建人ID
    /// </summary>
    public Guid? CreatedBy { get; set; }
    
    /// <summary>
    /// 更新人ID
    /// </summary>
    public Guid? UpdatedBy { get; set; }
    
    protected BaseEntity()
    {
        Id = Guid.NewGuid();
        CreatedAt = DateTime.UtcNow;
    }
}
