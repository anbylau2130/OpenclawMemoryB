namespace Tianyou.Domain.Entities;

/// <summary>
/// 实体基类 - 提供软删除支持
/// </summary>
public abstract class BaseEntity
{
    /// <summary>
    /// 实体ID
    /// </summary>
    public Guid Id { get; set; }

    /// <summary>
    /// 软删除标记
    /// </summary>
    public bool IsDeleted { get; set; } = false;

    /// <summary>
    /// 删除时间
    /// </summary>
    public DateTime? DeletedAt { get; set; }

    /// <summary>
    /// 创建时间
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// 更新时间
    /// </summary>
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
