using Microsoft.EntityFrameworkCore;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;
using System.Text.Json;

namespace Tianyou.Application.Services;

/// <summary>
/// 实体管理服务
/// </summary>
public class EntityService
{
    private readonly TianyouDbContext _context;
    
    public EntityService(TianyouDbContext context)
    {
        _context = context;
    }
    
    /// <summary>
    /// 创建实体定义
    /// </summary>
    public async Task<EntityDefinition> CreateEntityAsync(string entityName, string tableName, string? description = null)
    {
        // 检查实体名是否已存在
        if (await _context.EntityDefinitions.AnyAsync(e => e.EntityName == entityName))
        {
            throw new Exception($"实体名称 '{entityName}' 已存在");
        }
        
        // 检查表名是否已存在
        if (await _context.EntityDefinitions.AnyAsync(e => e.TableName == tableName))
        {
            throw new Exception($"表名称 '{tableName}' 已存在");
        }
        
        var entity = new EntityDefinition
        {
            Id = Guid.NewGuid(),
            EntityName = entityName,
            TableName = tableName,
            Description = description,
            IsSystem = false,
            IsActive = true,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        _context.EntityDefinitions.Add(entity);
        await _context.SaveChangesAsync();
        
        return entity;
    }
    
    /// <summary>
    /// 添加字段定义
    /// </summary>
    public async Task<FieldDefinition> AddFieldAsync(Guid entityId, string fieldName, string fieldType, 
        bool isRequired = false, bool isUnique = false, int? maxLength = null, 
        string? defaultValue = null, string? validationRule = null)
    {
        var entity = await _context.EntityDefinitions.FindAsync(entityId);
        if (entity == null)
        {
            throw new Exception("实体不存在");
        }
        
        // 检查字段名是否已存在
        if (await _context.FieldDefinitions.AnyAsync(f => f.EntityDefinitionId == entityId && f.FieldName == fieldName))
        {
            throw new Exception($"字段 '{fieldName}' 已存在");
        }
        
        var field = new FieldDefinition
        {
            Id = Guid.NewGuid(),
            EntityDefinitionId = entityId,
            FieldName = fieldName,
            FieldType = fieldType,
            IsRequired = isRequired,
            IsUnique = isUnique,
            MaxLength = maxLength,
            DefaultValue = defaultValue,
            ValidationRule = validationRule,
            DisplayOrder = await _context.FieldDefinitions.CountAsync(f => f.EntityDefinitionId == entityId),
            CreatedAt = DateTime.UtcNow
        };
        
        _context.FieldDefinitions.Add(field);
        await _context.SaveChangesAsync();
        
        return field;
    }
    
    /// <summary>
    /// 创建数据实例
    /// </summary>
    public async Task<DynamicData> CreateDataAsync(Guid entityId, Dictionary<string, object> data, Guid? createdBy = null)
    {
        var entity = await _context.EntityDefinitions
            .Include(e => e.Fields)
            .FirstOrDefaultAsync(e => e.Id == entityId);
            
        if (entity == null)
        {
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
        
        var dynamicData = new DynamicData
        {
            Id = Guid.NewGuid(),
            EntityDefinitionId = entityId,
            DataJson = JsonSerializer.Serialize(data),
            CreatedBy = createdBy,
            UpdatedBy = createdBy,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        _context.DynamicData.Add(dynamicData);
        await _context.SaveChangesAsync();
        
        return dynamicData;
    }
    
    /// <summary>
    /// 查询数据列表
    /// </summary>
    public async Task<List<Dictionary<string, object>>> QueryDataAsync(Guid entityId, int page = 1, int pageSize = 20)
    {
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
        var dynamicData = await _context.DynamicData.FindAsync(dataId);
        if (dynamicData == null)
        {
            throw new Exception("数据不存在");
        }
        
        dynamicData.DataJson = JsonSerializer.Serialize(data);
        dynamicData.UpdatedBy = updatedBy;
        dynamicData.UpdatedAt = DateTime.UtcNow;
        
        await _context.SaveChangesAsync();
        
        return dynamicData;
    }
    
    /// <summary>
    /// 删除数据
    /// </summary>
    public async Task DeleteDataAsync(Guid dataId)
    {
        var dynamicData = await _context.DynamicData.FindAsync(dataId);
        if (dynamicData == null)
        {
            throw new Exception("数据不存在");
        }
        
        _context.DynamicData.Remove(dynamicData);
        await _context.SaveChangesAsync();
    }
    
    /// <summary>
    /// 获取所有实体定义
    /// </summary>
    public async Task<List<EntityDefinition>> GetEntitiesAsync()
    {
        return await _context.EntityDefinitions
            .Include(e => e.Fields)
            .Where(e => e.IsActive)
            .OrderBy(e => e.CreatedAt)
            .ToListAsync();
    }
    
    /// <summary>
    /// 获取实体详情
    /// </summary>
    public async Task<EntityDefinition?> GetEntityAsync(Guid entityId)
    {
        return await _context.EntityDefinitions
            .Include(e => e.Fields)
            .FirstOrDefaultAsync(e => e.Id == entityId);
    }
}