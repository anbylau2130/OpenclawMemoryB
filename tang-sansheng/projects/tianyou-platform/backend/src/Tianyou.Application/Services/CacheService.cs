using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Logging;
using System.Diagnostics;

namespace Tianyou.Application.Services;

/// <summary>
/// 缓存服务接口
/// </summary>
public interface ICacheService
{
    /// <summary>
    /// 获取缓存值
    /// </summary>
    Task<T?> GetAsync<T>(string key);

    /// <summary>
    /// 设置缓存值
    /// </summary>
    Task SetAsync<T>(string key, T value, TimeSpan? expiration = null);

    /// <summary>
    /// 获取或创建缓存
    /// </summary>
    Task<T> GetOrCreateAsync<T>(string key, Func<Task<T>> factory, TimeSpan? expiration = null);

    /// <summary>
    /// 删除缓存
    /// </summary>
    Task RemoveAsync(string key);

    /// <summary>
    /// 按前缀删除缓存
    /// </summary>
    Task RemoveByPrefixAsync(string prefix);

    /// <summary>
    /// 清空所有缓存
    /// </summary>
    Task ClearAsync();

    /// <summary>
    /// 获取缓存统计信息
    /// </summary>
    CacheStatistics GetStatistics();
}

/// <summary>
/// 缓存统计信息
/// </summary>
public class CacheStatistics
{
    public long TotalHits { get; set; }
    public long TotalMisses { get; set; }
    public long TotalSets { get; set; }
    public long TotalRemoves { get; set; }
    public int CurrentEntryCount { get; set; }
    public long TotalSizeBytes { get; set; }
    public double HitRate => TotalHits + TotalMisses > 0 ? (double)TotalHits / (TotalHits + TotalMisses) * 100 : 0;
}

/// <summary>
/// 内存缓存服务实现
/// </summary>
public class MemoryCacheService : ICacheService
{
    private readonly IMemoryCache _cache;
    private readonly ILogger<MemoryCacheService> _logger;
    private readonly CacheStatistics _statistics;
    private static readonly object _lock = new();

    // 默认缓存过期时间
    private static readonly TimeSpan DefaultExpiration = TimeSpan.FromMinutes(30);
    private static readonly TimeSpan ShortExpiration = TimeSpan.FromMinutes(5);
    private static readonly TimeSpan LongExpiration = TimeSpan.FromHours(2);

    public MemoryCacheService(IMemoryCache cache, ILogger<MemoryCacheService> logger)
    {
        _cache = cache;
        _logger = logger;
        _statistics = new CacheStatistics();
    }

    /// <summary>
    /// 获取缓存值
    /// </summary>
    public async Task<T?> GetAsync<T>(string key)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            if (_cache.TryGetValue(key, out T? value))
            {
                lock (_lock)
                {
                    _statistics.TotalHits++;
                }

                _logger.LogDebug("缓存命中 - Key: {Key}, Type: {Type}, Duration: {Duration}ms",
                    key, typeof(T).Name, stopwatch.ElapsedMilliseconds);

                return value;
            }

            lock (_lock)
            {
                _statistics.TotalMisses++;
            }

            _logger.LogDebug("缓存未命中 - Key: {Key}, Type: {Type}", key, typeof(T).Name);
            return default;
        }
        finally
        {
            stopwatch.Stop();
        }
    }

    /// <summary>
    /// 设置缓存值
    /// </summary>
    public async Task SetAsync<T>(string key, T value, TimeSpan? expiration = null)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            var cacheExpiration = expiration ?? DefaultExpiration;

            var options = new MemoryCacheEntryOptions()
                .SetAbsoluteExpiration(cacheExpiration)
                .SetSlidingExpiration(TimeSpan.FromMinutes(10))
                .SetPriority(CacheItemPriority.Normal)
                .SetSize(1); // 启用大小限制

            _cache.Set(key, value, options);

            lock (_lock)
            {
                _statistics.TotalSets++;
                _statistics.CurrentEntryCount++;
            }

            _logger.LogDebug("缓存设置成功 - Key: {Key}, Type: {Type}, Expiration: {Expiration}, Duration: {Duration}ms",
                key, typeof(T).Name, cacheExpiration, stopwatch.ElapsedMilliseconds);
        }
        finally
        {
            stopwatch.Stop();
        }
    }

    /// <summary>
    /// 获取或创建缓存
    /// </summary>
    public async Task<T> GetOrCreateAsync<T>(string key, Func<Task<T>> factory, TimeSpan? expiration = null)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            // 先尝试从缓存获取
            var cachedValue = await GetAsync<T>(key);
            if (cachedValue != null)
            {
                return cachedValue;
            }

            // 缓存未命中，执行工厂方法
            _logger.LogDebug("执行缓存工厂方法 - Key: {Key}", key);
            var value = await factory();

            // 设置缓存
            await SetAsync(key, value, expiration);

            return value;
        }
        finally
        {
            stopwatch.Stop();
            _logger.LogDebug("GetOrCreate完成 - Key: {Key}, TotalDuration: {Duration}ms",
                key, stopwatch.ElapsedMilliseconds);
        }
    }

    /// <summary>
    /// 删除缓存
    /// </summary>
    public async Task RemoveAsync(string key)
    {
        _cache.Remove(key);

        lock (_lock)
        {
            _statistics.TotalRemoves++;
            if (_statistics.CurrentEntryCount > 0)
            {
                _statistics.CurrentEntryCount--;
            }
        }

        _logger.LogDebug("缓存删除成功 - Key: {Key}", key);
    }

    /// <summary>
    /// 按前缀删除缓存（简化实现）
    /// </summary>
    public async Task RemoveByPrefixAsync(string prefix)
    {
        // MemoryCache不支持按前缀删除，这里记录日志
        // 在实际生产环境中，应该使用Redis等支持模式匹配的缓存系统
        _logger.LogWarning("MemoryCache不支持按前缀删除，建议使用Redis - Prefix: {Prefix}", prefix);

        // 可以通过维护一个前缀到键的映射来实现，但这会增加复杂度
        // 这里只是记录警告，实际生产环境应该使用Redis
    }

    /// <summary>
    /// 清空所有缓存
    /// </summary>
    public async Task ClearAsync()
    {
        if (_cache is MemoryCache memoryCache)
        {
            memoryCache.Compact(1.0); // 清空所有缓存

            lock (_lock)
            {
                _statistics.CurrentEntryCount = 0;
            }

            _logger.LogInformation("缓存已清空");
        }
    }

    /// <summary>
    /// 获取缓存统计信息
    /// </summary>
    public CacheStatistics GetStatistics()
    {
        lock (_lock)
        {
            return new CacheStatistics
            {
                TotalHits = _statistics.TotalHits,
                TotalMisses = _statistics.TotalMisses,
                TotalSets = _statistics.TotalSets,
                TotalRemoves = _statistics.TotalRemoves,
                CurrentEntryCount = _statistics.CurrentEntryCount,
                TotalSizeBytes = _statistics.TotalSizeBytes
            };
        }
    }
}

/// <summary>
/// Redis缓存服务实现（预留，需要在appsettings.json中配置Redis连接）
/// </summary>
public class RedisCacheService : ICacheService
{
    private readonly ILogger<RedisCacheService> _logger;
    private readonly CacheStatistics _statistics;

    public RedisCacheService(ILogger<RedisCacheService> logger)
    {
        _logger = logger;
        _statistics = new CacheStatistics();
        _logger.LogInformation("Redis缓存服务已初始化（待实现）");
    }

    public Task<T?> GetAsync<T>(string key)
    {
        throw new NotImplementedException("Redis缓存服务待实现，请使用MemoryCacheService");
    }

    public Task SetAsync<T>(string key, T value, TimeSpan? expiration = null)
    {
        throw new NotImplementedException("Redis缓存服务待实现，请使用MemoryCacheService");
    }

    public Task<T> GetOrCreateAsync<T>(string key, Func<Task<T>> factory, TimeSpan? expiration = null)
    {
        throw new NotImplementedException("Redis缓存服务待实现，请使用MemoryCacheService");
    }

    public Task RemoveAsync(string key)
    {
        throw new NotImplementedException("Redis缓存服务待实现，请使用MemoryCacheService");
    }

    public Task RemoveByPrefixAsync(string prefix)
    {
        throw new NotImplementedException("Redis缓存服务待实现，请使用MemoryCacheService");
    }

    public Task ClearAsync()
    {
        throw new NotImplementedException("Redis缓存服务待实现，请使用MemoryCacheService");
    }

    public CacheStatistics GetStatistics()
    {
        return _statistics;
    }
}
