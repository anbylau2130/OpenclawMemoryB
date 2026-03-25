using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 动态数据（存储实体实例数据）
/// </summary>
public class DynamicData
{
    public Guid Id { get; set; }
    
    public Guid EntityDefinitionId { get; set; }
    
    public Guid? CreatedBy { get; set; }
    
    public Guid? UpdatedBy { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    // JSON格式存储字段值
    public string DataJson { get; set; } = "{}";
    
    // 导航属性
    public EntityDefinition Entity { get; set; } = null!;
}