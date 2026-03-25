using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 角色实体
/// </summary>
public class Role
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(50)]
    public string RoleName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string RoleCode { get; set; } = string.Empty;
    
    [StringLength(200)]
    public string? Description { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    // 导航属性
    public ICollection<User> Users { get; set; } = new List<User>();
    public ICollection<Permission> Permissions { get; set; } = new List<Permission>();
}