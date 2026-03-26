namespace Tianyou.Api.Middleware;

/// <summary>
/// 中间件扩展方法
/// </summary>
public static class MiddlewareExtensions
{
    /// <summary>
    /// 使用缓存监控中间件
    /// </summary>
    public static IApplicationBuilder UseCacheMonitoring(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<CacheMonitoringMiddleware>();
    }
}
