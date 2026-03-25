using Microsoft.EntityFrameworkCore;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;

namespace Tianyou.Application.Services;

/// <summary>
/// 通知服务
/// </summary>
public class NotificationService
{
    private readonly TianyouDbContext _context;
    
    public NotificationService(TianyouDbContext context)
    {
        _context = context;
    }
    
    public async Task<Notification> SendNotificationAsync(string title, string content, 
        string notificationType, string channel, Guid? recipientId = null, 
        string? recipientEmail = null, string? recipientPhone = null, DateTime? expiresAt = null)
    {
        var notification = new Notification
        {
            Id = Guid.NewGuid(),
            Title = title,
            Content = content,
            NotificationType = notificationType,
            Channel = channel,
            RecipientId = recipientId,
            RecipientEmail = recipientEmail,
            RecipientPhone = recipientPhone,
            IsRead = false,
            CreatedAt = DateTime.UtcNow,
            ExpiresAt = expiresAt
        };
        
        _context.Notifications.Add(notification);
        await _context.SaveChangesAsync();
        
        return notification;
    }
    
    public async Task<List<Notification>> GetUserNotificationsAsync(Guid userId, bool unreadOnly = false)
    {
        var query = _context.Notifications
            .Where(n => n.RecipientId == userId && (n.ExpiresAt == null || n.ExpiresAt > DateTime.UtcNow));
        
        if (unreadOnly)
        {
            query = query.Where(n => !n.IsRead);
        }
        
        return await query
            .OrderByDescending(n => n.CreatedAt)
            .Take(50)
            .ToListAsync();
    }
    
    public async Task MarkAsReadAsync(Guid notificationId)
    {
        var notification = await _context.Notifications.FindAsync(notificationId);
        if (notification == null) throw new Exception("通知不存在");
        
        notification.IsRead = true;
        notification.ReadAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();
    }
    
    public async Task<int> GetUnreadCountAsync(Guid userId)
    {
        return await _context.Notifications
            .CountAsync(n => n.RecipientId == userId && !n.IsRead && 
                           (n.ExpiresAt == null || n.ExpiresAt > DateTime.UtcNow));
    }
}