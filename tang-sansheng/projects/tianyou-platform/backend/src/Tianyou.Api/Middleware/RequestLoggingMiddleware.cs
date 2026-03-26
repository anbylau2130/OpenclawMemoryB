using Serilog;
using Serilog.Events;

namespace Tianyou.Api.Middleware;

/// <summary>
/// 请求日志中间件 - 记录所有HTTP请求和响应
/// </summary>
public class RequestLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestLoggingMiddleware> _logger;

    public RequestLoggingMiddleware(RequestDelegate next, ILogger<RequestLoggingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var startTime = DateTime.UtcNow;
        var requestId = Guid.NewGuid().ToString();

        // 记录请求信息
        var requestInfo = new
        {
            RequestId = requestId,
            Method = context.Request.Method,
            Path = context.Request.Path.Value,
            QueryString = context.Request.QueryString.Value,
            UserAgent = context.Request.Headers["User-Agent"].ToString(),
            RemoteIpAddress = context.Connection.RemoteIpAddress?.ToString(),
            UserId = context.User?.Identity?.Name ?? "Anonymous",
            Timestamp = startTime
        };

        // 记录请求开始
        Log.Information("HTTP Request Started: {@RequestInfo}", requestInfo);

        // 保存原始响应流
        var originalBodyStream = context.Response.Body;
        using var responseBody = new MemoryStream();
        context.Response.Body = responseBody;

        try
        {
            await _next(context);

            var duration = (DateTime.UtcNow - startTime).TotalMilliseconds;

            // 记录响应信息
            var responseInfo = new
            {
                RequestId = requestId,
                StatusCode = context.Response.StatusCode,
                Duration = duration,
                ContentType = context.Response.ContentType,
                Timestamp = DateTime.UtcNow
            };

            // 根据状态码选择日志级别
            var logLevel = context.Response.StatusCode switch
            {
                >= 500 => LogEventLevel.Error,
                >= 400 => LogEventLevel.Warning,
                _ => LogEventLevel.Information
            };

            Log.Write(logLevel, "HTTP Request Completed: {@ResponseInfo}", responseInfo);

            // 复制响应数据到原始流
            responseBody.Seek(0, SeekOrigin.Begin);
            await responseBody.CopyToAsync(originalBodyStream);
        }
        catch (Exception ex)
        {
            var duration = (DateTime.UtcNow - startTime).TotalMilliseconds;

            // 记录异常信息
            Log.Error(ex, "HTTP Request Failed: {@ErrorInfo}", new
            {
                RequestId = requestId,
                Method = context.Request.Method,
                Path = context.Request.Path.Value,
                Duration = duration,
                Exception = ex.Message,
                StackTrace = ex.StackTrace
            });

            // 重新抛出异常
            throw;
        }
        finally
        {
            context.Response.Body = originalBodyStream;
        }
    }
}

/// <summary>
/// 审计日志中间件 - 记录关键业务操作
/// </summary>
public class AuditLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<AuditLoggingMiddleware> _logger;

    // 需要审计的API路径
    private static readonly string[] AuditPaths = new[]
    {
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/change-password",
        "/api/entities/",
        "/api/forms/",
        "/api/workflows/",
        "/api/users/",
        "/api/roles/",
        "/api/permissions/"
    };

    public AuditLoggingMiddleware(RequestDelegate next, ILogger<AuditLoggingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var path = context.Request.Path.Value ?? "";

        // 检查是否需要审计
        var requiresAudit = AuditPaths.Any(auditPath => 
            path.StartsWith(auditPath, StringComparison.OrdinalIgnoreCase)) &&
            context.Request.Method != "GET";

        if (!requiresAudit)
        {
            await _next(context);
            return;
        }

        var startTime = DateTime.UtcNow;
        var auditId = Guid.NewGuid().ToString();

        // 读取请求体
        string requestBody = "";
        if (context.Request.ContentLength > 0 && context.Request.Body.CanRead)
        {
            using var reader = new StreamReader(context.Request.Body, leaveOpen: true);
            requestBody = await reader.ReadToEndAsync();
            context.Request.Body.Position = 0;
        }

        // 记录审计日志（开始）
        var auditInfo = new
        {
            AuditId = auditId,
            Action = context.Request.Method,
            Path = path,
            QueryString = context.Request.QueryString.Value,
            UserId = context.User?.Identity?.Name ?? "Anonymous",
            UserIp = context.Connection.RemoteIpAddress?.ToString(),
            RequestBody = TruncateBody(requestBody),
            Timestamp = startTime
        };

        Log.Information("Audit Log - Action Started: {@AuditInfo}", auditInfo);

        try
        {
            await _next(context);

            var duration = (DateTime.UtcNow - startTime).TotalMilliseconds;

            // 记录审计日志（完成）
            var auditResult = new
            {
                AuditId = auditId,
                Action = context.Request.Method,
                Path = path,
                StatusCode = context.Response.StatusCode,
                Duration = duration,
                Success = context.Response.StatusCode < 400,
                Timestamp = DateTime.UtcNow
            };

            Log.Information("Audit Log - Action Completed: {@AuditResult}", auditResult);
        }
        catch (Exception ex)
        {
            var duration = (DateTime.UtcNow - startTime).TotalMilliseconds;

            // 记录审计日志（失败）
            var auditError = new
            {
                AuditId = auditId,
                Action = context.Request.Method,
                Path = path,
                Duration = duration,
                Success = false,
                Error = ex.Message,
                Timestamp = DateTime.UtcNow
            };

            Log.Error(ex, "Audit Log - Action Failed: {@AuditError}", auditError);

            throw;
        }
    }

    private string TruncateBody(string body, int maxLength = 1000)
    {
        if (string.IsNullOrEmpty(body) || body.Length <= maxLength)
            return body;

        return body.Substring(0, maxLength) + "...[truncated]";
    }
}

/// <summary>
/// 中间件扩展方法
/// </summary>
public static class LoggingMiddlewareExtensions
{
    public static IApplicationBuilder UseRequestLogging(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<RequestLoggingMiddleware>();
    }

    public static IApplicationBuilder UseAuditLogging(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<AuditLoggingMiddleware>();
    }
}
