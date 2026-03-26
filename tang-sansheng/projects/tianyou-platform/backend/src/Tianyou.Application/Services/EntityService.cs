using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;
using Tianyou.Application.Validators;
using Tianyou.Application.Security;
using System.Text.Json;

namespace Tianyou.Application.Services;

/// <summary>
/// 实体管理服务
/// </summary>
public class EntityService
{
    private readonly TianyouDbContext _context;
    private readonly ILogger<EntityService> _logger;
    private readonly ICacheService _cache;

    public EntityService(TianyouDbContext context, ILogger<EntityService> logger, ICacheService cache)
    {
        _context = context;
        _logger = logger;
        _cache = cache;
    }
    
    /// <summary>
    /// 创建实体定义
    /// </summary>
    public async Task<EntityDefinition> CreateEntityAsync(string entityName, string tableName, string? description = null)
    {
        // 输入验证
        InputValidator.ValidateEntityName(entityName);
        InputValidator.ValidateTableName(tableName);
        InputValidator.ValidateDescription(description);

        // 检查实体名是否已存在
        if (await _context.EntityDefinitions.AnyAsync(e => e.EntityName == entityName))
        {
            _logger.LogWarning("创建实体失败：实体名称已存在 - EntityName: {EntityName}", entityName);
            throw new Exception("实体名称已存在");
        }

        // 检查表名是否已存在
        if (await _context.EntityDefinitions.AnyAsync(e => e.TableName == tableName))
        {
            _logger.LogWarning("创建实体失败：表名称已存在 - TableName: {TableName}", tableName);
            throw new Exception("表名称已存在");
        }

        // XSS防护：清理描述
        var safeDescription = XssProtector.SanitizeHtml(description);

        var entity = new EntityDefinition
        {
            Id = Guid.NewGuid(),
            EntityName = entityName,
            TableName = tableName,
            Description = safeDescription,
            IsSystem = false,
            IsActive = true,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        _context.EntityDefinitions.Add(entity);
        await _context.SaveChangesAsync();

        // 清除实体列表缓存
        await _cache.RemoveAsync(CacheKeys.Entity.All());

        _logger.LogInformation("实体创建成功 - EntityId: {EntityId}, EntityName: {EntityName}", entity.Id, entity.EntityName);

        return entity;
    }
    
    /// <summary>
    /// 添加字段定义
    /// </summary>
    public async Task<FieldDefinition> AddFieldAsync(Guid entityId, string fieldName, string fieldType, 
        bool isRequired = false, bool isUnique = false, int? maxLength = null, 
        string? defaultValue = null, string? validationRule = null)
    {
        // 输入验证
        InputValidator.ValidateGuid(entityId, "实体ID");
        InputValidator.ValidateFieldName(fieldName);
        InputValidator.ValidateFieldType(fieldType);
        InputValidator.ValidateMaxLength(maxLength);

        var entity = await _context.EntityDefinitions.FindAsync(entityId);
        if (entity == null)
        {
            _logger.LogWarning("添加字段失败：实体不存在 - EntityId: {EntityId}", entityId);
            throw new Exception("实体不存在");
        }

        // 检查字段名是否已存在
        if (await _context.FieldDefinitions.AnyAsync(f => f.EntityDefinitionId == entityId && f.FieldName == fieldName))
        {
            _logger.LogWarning("添加字段失败：字段已存在 - EntityId: {EntityId}, FieldName: {FieldName}", entityId, fieldName);
            throw new Exception("字段已存在");
        }

        // XSS防护：清理默认值和验证规则
        var safeDefaultValue = XssProtector.SanitizeHtml(defaultValue);
        var safeValidationRule = XssProtector.SanitizeHtml(validationRule);

        var field = new FieldDefinition
        {
            Id = Guid.NewGuid(),
            EntityDefinitionId = entityId,
            FieldName = fieldName,
            FieldType = fieldType,
            IsRequired = isRequired,
            IsUnique = isUnique,
            MaxLength = maxLength,
            DefaultValue = safeDefaultValue,
            ValidationRule = safeValidationRule,
            DisplayOrder = await _context.FieldDefinitions.CountAsync(f => f.EntityDefinitionId == entityId),
            CreatedAt = DateTime.UtcNow
        };
        
        _context.FieldDefinitions.Add(field);
        await _context.SaveChangesAsync();

        // 清除相关缓存
        await _cache.RemoveAsync(CacheKeys.Entity.ById(entityId));
        await _cache.RemoveAsync(CacheKeys.Entity.Fields(entityId));
        await _cache.RemoveAsync(CacheKeys.Entity.All());

        _logger.LogInformation("字段添加成功 - FieldId: {FieldId}, FieldName: {FieldName}, EntityId: {EntityId}", 
            field.Id, field.FieldName, entityId);

        return field;
    }
    
    /// <summary>
    /// 创建数据实例
    /// </summary>
    public async Task<DynamicData> CreateDataAsync(Guid entityId, Dictionary<string, object> data, Guid? createdBy = null)
    {
        // 输入验证
        InputValidator.ValidateGuid(entityId, "实体ID");

        if (data == null || data.Count == 0)
        {
            throw new ArgumentException("数据不能为空");
        }

        var entity = await _context.EntityDefinitions
            .Include(e => e.Fields)
            .FirstOrDefaultAsync(e => e.Id == entityId);

        if (entity == null)
        {
            _logger.LogWarning("创建数据失败：实体不存在 - EntityId: {EntityId}", entityId);
            throw new Exception("实体不存在");
        }
        
        // 验证必填字段
        foreach (var field in entity.Fields.Where(f => f.IsRequired))
        {
            if (!data.ContainsKey(field.FieldName) || data[field.FieldName] == null)
            {
                throw new Exception($"字段 '{field.FieldName}' 是必填的");
            }
        }

        // 验证字段值类型
        foreach (var field in entity.Fields)
        {
            if (data.ContainsKey(field.FieldName) && data[field.FieldName] != null)
            {
                InputValidator.ValidateFieldValueType(field.FieldName, field.FieldType, data[field.FieldName]);
            }
        }

        // XSS防护：清理所有数据值
        var sanitizedData = new Dictionary<string, object>();
        foreach (var kvp in data)
        {
            var safeKey = XssProtector.SanitizeHtml(kvp.Key);
            var safeValue = kvp.Value?.ToString() ?? string.Empty;
            safeValue = XssProtector.SanitizeHtml(safeValue);
            sanitizedData[safeKey] = safeValue;
        }

        var dynamicData = new DynamicData
        {
            Id = Guid.NewGuid(),
            EntityDefinitionId = entityId,
            DataJson = JsonSerializer.Serialize(sanitizedData),
            CreatedBy = createdBy,
            UpdatedBy = createdBy,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        _context.DynamicData.Add(dynamicData);
        await _context.SaveChangesAsync();

        _logger.LogInformation("数据创建成功 - DataId: {DataId}, EntityId: {EntityId}", dynamicData.Id, entityId);

        return dynamicData;
    }
    
    /// <summary>
    /// 查询数据列表
    /// </summary>
    public async Task<List<Dictionary<string, object>>> QueryDataAsync(Guid entityId, int page = 1, int pageSize = 20)
    {
        // 输入验证
        InputValidator.ValidateGuid(entityId, "实体ID");
        InputValidator.ValidatePagination(page, pageSize);

        var query = _context.DynamicData
            .Where(d => d.EntityDefinitionId == entityId)
            .OrderByDescending(d => d.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize);
        
        var dataList = await query.ToListAsync();
        
        return dataList.Select(d => 
        {
            var dict = JsonSerializer.Deserialize<Dictionary<string, object>>(d.DataJson) ?? new Dictionary<string, object>();
            dict["_id"] = d.Id;
            dict["_createdAt"] = d.CreatedAt;
            dict["_updatedAt"] = d.UpdatedAt;
            return dict;
        }).ToList();
    }
    
    /// <summary>
    /// 更新数据
    /// </summary>
    public async Task<DynamicData> UpdateDataAsync(Guid dataId, Dictionary<string, object> data, Guid? updatedBy = null)
    {
        // 输入验证
        InputValidator.ValidateGuid(dataId, "数据ID");

        if (data == null || data.Count == 0)
        {
            throw new ArgumentException("数据不能为空");
        }

        var dynamicData = await _context.DynamicData.FindAsync(dataId);
        if (dynamicData == null)
        {
            _logger.LogWarning("更新数据失败：数据不存在 - DataId: {DataId}", dataId);
            throw new Exception("数据不存在");
        }

        // 获取实体定义以验证字段类型
        var entity = await _context.EntityDefinitions
            .Include(e => e.Fields)
            .FirstOrDefaultAsync(e => e.Id == dynamicData.EntityDefinitionId);

        if (entity != null)
        {
            // 验证字段值类型
            foreach (var field in entity.Fields)
            {
                if (data.ContainsKey(field.FieldName) && data[field.FieldName] != null)
                {
                    InputValidator.ValidateFieldValueType(field.FieldName, field.FieldType, data[field.FieldName]);
                }
            }
        }

        // XSS防护：清理所有数据值
        var sanitizedData = new Dictionary<string, object>();
        foreach (var kvp in data)
        {
            var safeKey = XssProtector.SanitizeHtml(kvp.Key);
            var safeValue = kvp.Value?.ToString() ?? string.Empty;
            safeValue = XssProtector.SanitizeHtml(safeValue);
            sanitizedData[safeKey] = safeValue;
        }

        dynamicData.DataJson = JsonSerializer.Serialize(sanitizedData);
        dynamicData.UpdatedBy = updatedBy;
        dynamicData.UpdatedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();

        _logger.LogInformation("数据更新成功 - DataId: {DataId}", dataId);

        return dynamicData;
    }
    
    /// <summary>
    /// 删除数据（软删除）
    /// </summary>
    public async Task DeleteDataAsync(Guid dataId)
    {
        // 输入验证
        InputValidator.ValidateGuid(dataId, "数据ID");

        var dynamicData = await _context.DynamicData.FindAsync(dataId);
        if (dynamicData == null)
        {
            _logger.LogWarning("删除数据失败：数据不存在 - DataId: {DataId}", dataId);
            throw new Exception("数据不存在");
        }

        // 软删除：标记IsDeleted为true
        dynamicData.IsDeleted = true;
        dynamicData.DeletedAt = DateTime.UtcNow;

        await _context.SaveChangesAsync();

        _logger.LogInformation("数据已软删除 - DataId: {DataId}", dataId);
    }
    
    /// <summary>
    /// 获取所有实体定义（带缓存）
    /// </summary>
    public async Task<List<EntityDefinition>> GetEntitiesAsync()
    {
        var cacheKey = CacheKeys.Entity.All();
        
        return await _cache.GetOrCreateAsync(cacheKey, async () =>
        {
            _logger.LogDebug("从数据库加载实体列表 - CacheKey: {CacheKey}", cacheKey);
            return await _context.EntityDefinitions
                .Include(e => e.Fields)
                .Where(e => e.IsActive)
                .OrderBy(e => e.CreatedAt)
                .ToListAsync();
        }, TimeSpan.FromMinutes(30)); // 缓存30分钟
    }
    
    /// <summary>
    /// 获取实体详情（带缓存）
    /// </summary>
    public async Task<EntityDefinition?> GetEntityAsync(Guid entityId)
    {
        var cacheKey = CacheKeys.Entity.ById(entityId);
        
        return await _cache.GetOrCreateAsync(cacheKey, async () =>
        {
            _logger.LogDebug("从数据库加载实体详情 - EntityId: {EntityId}, CacheKey: {CacheKey}", entityId, cacheKey);
            return await _context.EntityDefinitions
                .Include(e => e.Fields)
                .FirstOrDefaultAsync(e => e.Id == entityId);
        }, TimeSpan.FromMinutes(30)); // 缓存30分钟
    }
}