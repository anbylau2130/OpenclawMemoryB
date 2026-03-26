using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Tianyou.Application.Services;

namespace Tianyou.Api.Controllers;

/// <summary>
/// 缓存管理控制器
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Authorize] // 需要认证
public class CacheController : ControllerBase
{
    private readonly ICacheService _cacheService;
    private readonly ILogger<CacheController> _logger;

    public CacheController(ICacheService cacheService, ILogger<CacheController> logger)
    {
        _cacheService = cacheService;
        _logger = logger;
    }

    /// <summary>
    /// 获取缓存统计信息
    /// </summary>
    [HttpGet("stats")]
    public IActionResult GetStatistics()
    {
        try
        {
            var stats = _cacheService.GetStatistics();
            
            _logger.LogInformation("缓存统计信息查询 - HitRate: {HitRate}%", stats.HitRate);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    totalHits = stats.TotalHits,
                    totalMisses = stats.TotalMisses,
                    totalSets = stats.TotalSets,
                    totalRemoves = stats.TotalRemoves,
                    currentEntryCount = stats.CurrentEntryCount,
                    hitRate = Math.Round(stats.HitRate, 2),
                    timestamp = DateTime.UtcNow
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取缓存统计信息失败");
            return StatusCode(500, new { success = false, message = "获取缓存统计信息失败" });
        }
    }

    /// <summary>
    /// 清空所有缓存
    /// </summary>
    [HttpDelete("clear")]
    [Authorize(Roles = "admin")] // 仅管理员可访问
    public async Task<IActionResult> ClearCache()
    {
        try
        {
            await _cacheService.ClearAsync();
            
            _logger.LogWarning("缓存已清空 - Operator: {Operator}", User.Identity?.Name ?? "Unknown");
            
            return Ok(new
            {
                success = true,
                message = "缓存已清空",
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "清空缓存失败");
            return StatusCode(500, new { success = false, message = "清空缓存失败" });
        }
    }

    /// <summary>
    /// 删除指定键的缓存
    /// </summary>
    [HttpDelete("keys/{*key}")]
    [Authorize(Roles = "admin")] // 仅管理员可访问
    public async Task<IActionResult> RemoveCacheKey(string key)
    {
        try
        {
            await _cacheService.RemoveAsync(key);
            
            _logger.LogInformation("缓存键已删除 - Key: {Key}, Operator: {Operator}", 
                key, User.Identity?.Name ?? "Unknown");
            
            return Ok(new
            {
                success = true,
                message = $"缓存键 '{key}' 已删除",
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "删除缓存键失败 - Key: {Key}", key);
            return StatusCode(500, new { success = false, message = "删除缓存键失败" });
        }
    }

    /// <summary>
    /// 健康检查
    /// </summary>
    [HttpGet("health")]
    [AllowAnonymous] // 允许匿名访问
    public IActionResult HealthCheck()
    {
        try
        {
            var stats = _cacheService.GetStatistics();
            
            return Ok(new
            {
                status = "healthy",
                cacheType = "MemoryCache",
                entryCount = stats.CurrentEntryCount,
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "缓存健康检查失败");
            return StatusCode(500, new { status = "unhealthy", message = ex.Message });
        }
    }
}
