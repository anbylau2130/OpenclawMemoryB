using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Tianyou.Application.Services;

namespace Tianyou.Api.Controllers;

/// <summary>
/// 实体管理控制器
/// </summary>
[ApiController]
[Route("api/entities")]
[Authorize]
public class EntityController : ControllerBase
{
    private readonly EntityService _entityService;
    private readonly ILogger<EntityController> _logger;
    
    public EntityController(EntityService entityService, ILogger<EntityController> logger)
    {
        _entityService = entityService;
        _logger = logger;
    }
    
    /// <summary>
    /// 创建实体定义
    /// </summary>
    [HttpPost]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreateEntity([FromBody] CreateEntityRequest request)
    {
        try
        {
            var entity = await _entityService.CreateEntityAsync(
                request.EntityName,
                request.TableName,
                request.Description);
            
            _logger.LogInformation("实体创建成功: {EntityName}", request.EntityName);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    entityId = entity.Id,
                    entityName = entity.EntityName,
                    tableName = entity.TableName,
                    description = entity.Description,
                    createdAt = entity.CreatedAt
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "实体创建失败: {EntityName}", request.EntityName);
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 添加字段
    /// </summary>
    [HttpPost("{entityId}/fields")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> AddField(Guid entityId, [FromBody] AddFieldRequest request)
    {
        try
        {
            var field = await _entityService.AddFieldAsync(
                entityId,
                request.FieldName,
                request.FieldType,
                request.IsRequired,
                request.IsUnique,
                request.MaxLength,
                request.DefaultValue,
                request.ValidationRule);
            
            _logger.LogInformation("字段添加成功: {FieldName}", request.FieldName);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    fieldId = field.Id,
                    fieldName = field.FieldName,
                    fieldType = field.FieldType,
                    isRequired = field.IsRequired
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "字段添加失败: {FieldName}", request.FieldName);
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 获取所有实体
    /// </summary>
    [HttpGet]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> GetEntities()
    {
        var entities = await _entityService.GetEntitiesAsync();
        
        return Ok(new
        {
            success = true,
            data = entities.Select(e => new
            {
                entityId = e.Id,
                entityName = e.EntityName,
                tableName = e.TableName,
                description = e.Description,
                fieldCount = e.Fields.Count,
                createdAt = e.CreatedAt
            })
        });
    }
    
    /// <summary>
    /// 获取实体详情
    /// </summary>
    [HttpGet("{entityId}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetEntity(Guid entityId)
    {
        var entity = await _entityService.GetEntityAsync(entityId);
        
        if (entity == null)
        {
            return NotFound(new { success = false, message = "实体不存在" });
        }
        
        return Ok(new
        {
            success = true,
            data = new
            {
                entityId = entity.Id,
                entityName = entity.EntityName,
                tableName = entity.TableName,
                description = entity.Description,
                fields = entity.Fields.Select(f => new
                {
                    fieldId = f.Id,
                    fieldName = f.FieldName,
                    fieldType = f.FieldType,
                    isRequired = f.IsRequired,
                    isUnique = f.IsUnique,
                    maxLength = f.MaxLength,
                    defaultValue = f.DefaultValue
                })
            }
        });
    }
    
    /// <summary>
    /// 创建数据
    /// </summary>
    [HttpPost("{entityId}/data")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreateData(Guid entityId, [FromBody] Dictionary<string, object> data)
    {
        try
        {
            var userIdClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            Guid? createdBy = Guid.TryParse(userIdClaim, out var userId) ? userId : (Guid?)null;
            
            var dynamicData = await _entityService.CreateDataAsync(entityId, data, createdBy);
            
            _logger.LogInformation("数据创建成功: EntityId={EntityId}", entityId);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    dataId = dynamicData.Id,
                    createdAt = dynamicData.CreatedAt
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "数据创建失败: EntityId={EntityId}", entityId);
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 查询数据列表
    /// </summary>
    [HttpGet("{entityId}/data")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> QueryData(Guid entityId, [FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var dataList = await _entityService.QueryDataAsync(entityId, page, pageSize);
        
        return Ok(new
        {
            success = true,
            data = dataList,
            page,
            pageSize
        });
    }
    
    /// <summary>
    /// 更新数据
    /// </summary>
    [HttpPut("data/{dataId}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> UpdateData(Guid dataId, [FromBody] Dictionary<string, object> data)
    {
        try
        {
            var userIdClaim = User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
            Guid? updatedBy = Guid.TryParse(userIdClaim, out var userId) ? userId : (Guid?)null;
            
            var dynamicData = await _entityService.UpdateDataAsync(dataId, data, updatedBy);
            
            _logger.LogInformation("数据更新成功: DataId={DataId}", dataId);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    dataId = dynamicData.Id,
                    updatedAt = dynamicData.UpdatedAt
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "数据更新失败: DataId={DataId}", dataId);
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 删除数据
    /// </summary>
    [HttpDelete("data/{dataId}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> DeleteData(Guid dataId)
    {
        try
        {
            await _entityService.DeleteDataAsync(dataId);
            
            _logger.LogInformation("数据删除成功: DataId={DataId}", dataId);
            
            return Ok(new { success = true, message = "数据删除成功" });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "数据删除失败: DataId={DataId}", dataId);
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
}

// DTO类
public record CreateEntityRequest(string EntityName, string TableName, string? Description);
public record AddFieldRequest(string FieldName, string FieldType, bool IsRequired = false, bool IsUnique = false, int? MaxLength = null, string? DefaultValue = null, string? ValidationRule = null);