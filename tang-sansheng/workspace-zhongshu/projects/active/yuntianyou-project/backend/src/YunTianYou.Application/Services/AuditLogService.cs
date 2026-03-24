using YunTianYou.Application.DTOs;

namespace YunTianYou.Application.Services;

/// <summary>
/// 审计日志服务
/// </summary>
public interface IAuditLogService
{
    Task LogAsync(string action, string entityType, string? entityId, string? oldValues, string? newValues, string? description = null);
    Task<IEnumerable<AuditLogDto>> GetLogsAsync(AuditLogQueryDto query);
    Task<AuditLogDto?> GetLogByIdAsync(Guid id);
}

public class AuditLogService : IAuditLogService
{
    private readonly YunTianYouDbContext _context;
    private readonly IHttpContextAccessor _httpContextAccessor;
    private readonly ILogger<AuditLogService> _logger;

    public AuditLogService(
        YunTianYouDbContext context,
        IHttpContextAccessor httpContextAccessor,
        ILogger<AuditLogService> logger)
    {
        _context = context;
        _httpContextAccessor = httpContextAccessor;
        _logger = logger;
    }

    public async Task LogAsync(string action, string entityType, string? entityId, string? oldValues, string? newValues, string? description = null)
    {
        var httpContext = _httpContextAccessor.HttpContext;
        var userIdClaim = httpContext?.User?.FindFirst("sub");

        var log = new AuditLog
        {
            UserId = userIdClaim != null ? Guid.Parse(userIdClaim.Value) : null,
            Action = action,
            EntityType = entityType,
            EntityId = entityId,
            OldValues = oldValues,
            NewValues = newValues,
            IpAddress = httpContext?.Connection?.RemoteIpAddress?.ToString(),
            UserAgent = httpContext?.Request?.Headers["User-Agent"].ToString(),
            Description = description,
            CreatedAt = DateTime.UtcNow
        };

        _context.AuditLogs.Add(log);
        await _context.SaveChangesAsync();

        _logger.LogInformation(
            "审计日志: {Action} - {EntityType}({EntityId}) - {Description}",
            action, entityType, entityId, description);
    }

    public async Task<IEnumerable<AuditLogDto>> GetLogsAsync(AuditLogQueryDto query)
    {
        var queryable = _context.AuditLogs
            .Include(l => l.User)
            .AsQueryable();

        if (query.UserId.HasValue)
            queryable = queryable.Where(l => l.UserId == query.UserId);

        if (!string.IsNullOrEmpty(query.Action))
            queryable = queryable.Where(l => l.Action.Contains(query.Action));

        if (!string.IsNullOrEmpty(query.EntityType))
            queryable = queryable.Where(l => l.EntityType == query.EntityType);

        if (query.StartDate.HasValue)
            queryable = queryable.Where(l => l.CreatedAt >= query.StartDate);

        if (query.EndDate.HasValue)
            queryable = queryable.Where(l => l.CreatedAt <= query.EndDate);

        var logs = await queryable
            .OrderByDescending(l => l.CreatedAt)
            .Skip((query.Page - 1) * query.PageSize)
            .Take(query.PageSize)
            .ToListAsync();

        return logs.Select(l => new AuditLogDto
        {
            Id = l.Id,
            UserId = l.UserId,
            UserName = l.User?.Username,
            Action = l.Action,
            EntityType = l.EntityType,
            EntityId = l.EntityId,
            OldValues = l.OldValues,
            NewValues = l.NewValues,
            IpAddress = l.IpAddress,
            Description = l.Description,
            CreatedAt = l.CreatedAt
        });
    }

    public async Task<AuditLogDto?> GetLogByIdAsync(Guid id)
    {
        var log = await _context.AuditLogs
            .Include(l => l.User)
            .FirstOrDefaultAsync(l => l.Id == id);

        if (log == null) return null;

        return new AuditLogDto
        {
            Id = log.Id,
            UserId = log.UserId,
            UserName = log.User?.Username,
            Action = log.Action,
            EntityType = log.EntityType,
            EntityId = log.EntityId,
            OldValues = log.OldValues,
            NewValues = log.NewValues,
            IpAddress = log.IpAddress,
            UserAgent = log.UserAgent,
            Description = log.Description,
            CreatedAt = log.CreatedAt
        };
    }
}

// DTO定义
public class AuditLogDto
{
    public Guid Id { get; set; }
    public Guid? UserId { get; set; }
    public string? UserName { get; set; }
    public string Action { get; set; } = string.Empty;
    public string EntityType { get; set; } = string.Empty;
    public string? EntityId { get; set; }
    public string? OldValues { get; set; }
    public string? NewValues { get; set; }
    public string? IpAddress { get; set; }
    public string? UserAgent { get; set; }
    public string? Description { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class AuditLogQueryDto
{
    public Guid? UserId { get; set; }
    public string? Action { get; set; }
    public string? EntityType { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public int Page { get; set; } = 1;
    public int PageSize { get; set; } = 50;
}
