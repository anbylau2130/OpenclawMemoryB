using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 权限实体
/// </summary>
public class Permission
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string PermissionName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(100)]
    public string PermissionCode { get; set; } = string.Empty;
    
    [StringLength(100)]
    public string? Resource { get; set; }
    
    [StringLength(50)]
    public string? Action { get; set; }
    
    [StringLength(200)]
    public string? Description { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    // 导航属性
    public ICollection<Role> Roles { get; set; } = new List<Role>();
}