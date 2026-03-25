using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 租户
/// </summary>
public class Tenant
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(100)]
    public string TenantName { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string TenantCode { get; set; } = string.Empty;
    
    [StringLength(200)]
    public string? Domain { get; set; }
    
    [StringLength(500)]
    public string? Description { get; set; }
    
    [Required]
    [StringLength(20)]
    public string Status { get; set; } = "active"; // active, suspended, cancelled
    
    public string? Config { get; set; } // JSON格式配置
    
    public int MaxUsers { get; set; } = 100;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? ExpiresAt { get; set; }
    
    // 导航属性
    public ICollection<User> Users { get; set; } = new List<User>();
}