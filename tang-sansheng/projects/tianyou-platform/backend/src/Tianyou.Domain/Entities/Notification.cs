using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// 消息通知
/// </summary>
public class Notification
{
    public Guid Id { get; set; }
    
    [Required]
    [StringLength(200)]
    public string Title { get; set; } = string.Empty;
    
    [Required]
    public string Content { get; set; } = string.Empty;
    
    [Required]
    [StringLength(50)]
    public string NotificationType { get; set; } = "info"; // info, warning, error, success
    
    [Required]
    [StringLength(50)]
    public string Channel { get; set; } = "system"; // system, email, sms, webhook
    
    public Guid? RecipientId { get; set; }
    
    public string? RecipientEmail { get; set; }
    
    public string? RecipientPhone { get; set; }
    
    public bool IsRead { get; set; } = false;
    
    public DateTime? ReadAt { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    public DateTime? ExpiresAt { get; set; }
}