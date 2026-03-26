using System.Diagnostics;
using System.Text.Json;

namespace Tianyou.Api.Middleware;

/// <summary>
/// 缓存监控中间件
/// </summary>
public class CacheMonitoringMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<CacheMonitoringMiddleware> _logger;

    public CacheMonitoringMiddleware(RequestDelegate next, ILogger<CacheMonitoringMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();

        // 记录请求开始
        var requestMethod = context.Request.Method;
        var requestPath = context.Request.Path;

        try
        {
            await _next(context);
        }
        finally
        {
            stopwatch.Stop();

            // 记录请求性能
            var statusCode = context.Response.StatusCode;
            var duration = stopwatch.ElapsedMilliseconds;

            // 慢请求告警（超过1秒）
            if (duration > 1000)
            {
                _logger.LogWarning("慢请求告警 - Method: {Method}, Path: {Path}, StatusCode: {StatusCode}, Duration: {Duration}ms",
                    requestMethod, requestPath, statusCode, duration);
            }
            else
            {
                _logger.LogDebug("请求完成 - Method: {Method}, Path: {Path}, StatusCode: {StatusCode}, Duration: {Duration}ms",
                    requestMethod, requestPath, statusCode, duration);
            }

            // 添加性能头
            context.Response.Headers["X-Response-Time-ms"] = duration.ToString();
        }
    }
}

/// <summary>
/// 缓存健康检查端点
/// </summary>
public static class CacheHealthCheckExtensions
{
    public static IEndpointRouteBuilder MapCacheHealthCheck(
        this IEndpointRouteBuilder endpoints,
        string pattern = "/health/cache")
    {
        endpoints.MapGet(pattern, async (HttpContext context) =>
        {
            var cacheService = context.RequestServices.GetService<Application.Services.ICacheService>();

            if (cacheService == null)
            {
                context.Response.StatusCode = 503;
                await context.Response.WriteAsJsonAsync(new
                {
                    status = "unhealthy",
                    message = "缓存服务未注册"
                });
                return;
            }

            try
            {
                var statistics = cacheService.GetStatistics();

                var healthStatus = new
                {
                    status = "healthy",
                    timestamp = DateTime.UtcNow,
                    cache = new
                    {
                        totalHits = statistics.TotalHits,
                        totalMisses = statistics.TotalMisses,
                        totalSets = statistics.TotalSets,
                        totalRemoves = statistics.TotalRemoves,
                        currentEntryCount = statistics.CurrentEntryCount,
                        hitRate = $"{statistics.HitRate:F2}%",
                        totalSizeBytes = statistics.TotalSizeBytes
                    }
                };

                context.Response.StatusCode = 200;
                await context.Response.WriteAsJsonAsync(healthStatus);
            }
            catch (Exception ex)
            {
                context.Response.StatusCode = 503;
                await context.Response.WriteAsJsonAsync(new
                {
                    status = "unhealthy",
                    message = ex.Message
                });
            }
        });

        return endpoints;
    }
}
