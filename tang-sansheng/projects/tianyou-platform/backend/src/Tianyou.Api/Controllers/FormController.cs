using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Tianyou.Application.Services;

namespace Tianyou.Api.Controllers;

/// <summary>
/// 表单管理控制器
/// </summary>
[ApiController]
[Route("api/forms")]
[Authorize]
public class FormController : ControllerBase
{
    private readonly FormService _formService;
    private readonly ILogger<FormController> _logger;
    
    public FormController(FormService formService, ILogger<FormController> logger)
    {
        _formService = formService;
        _logger = logger;
    }
    
    /// <summary>
    /// 创建表单
    /// </summary>
    [HttpPost]
    public async Task<IActionResult> CreateForm([FromBody] CreateFormRequest request)
    {
        try
        {
            var form = await _formService.CreateFormAsync(
                request.FormName,
                request.Description,
                request.EntityDefinitionId);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    formId = form.Id,
                    formName = form.FormName,
                    description = form.Description,
                    isPublished = form.IsPublished,
                    createdAt = form.CreatedAt
                }
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 添加表单字段
    /// </summary>
    [HttpPost("{formId}/fields")]
    public async Task<IActionResult> AddField(Guid formId, [FromBody] AddFormFieldRequest request)
    {
        try
        {
            var field = await _formService.AddFormFieldAsync(
                formId,
                request.FieldName,
                request.FieldType,
                request.Label,
                request.Placeholder,
                request.DefaultValue,
                request.IsRequired,
                request.IsVisible,
                request.IsEditable,
                request.ValidationRules,
                request.FieldConfig);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    fieldId = field.Id,
                    fieldName = field.FieldName,
                    fieldType = field.FieldType,
                    label = field.Label
                }
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 发布表单
    /// </summary>
    [HttpPost("{formId}/publish")]
    public async Task<IActionResult> PublishForm(Guid formId)
    {
        try
        {
            var form = await _formService.PublishFormAsync(formId);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    formId = form.Id,
                    isPublished = form.IsPublished,
                    updatedAt = form.UpdatedAt
                }
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 获取表单列表
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetForms()
    {
        var forms = await _formService.GetFormsAsync();
        
        return Ok(new
        {
            success = true,
            data = forms.Select(f => new
            {
                formId = f.Id,
                formName = f.FormName,
                description = f.Description,
                isPublished = f.IsPublished,
                fieldCount = f.Fields.Count,
                createdAt = f.CreatedAt
            })
        });
    }
    
    /// <summary>
    /// 获取表单详情
    /// </summary>
    [HttpGet("{formId}")]
    public async Task<IActionResult> GetForm(Guid formId)
    {
        var form = await _formService.GetFormAsync(formId);
        
        if (form == null)
        {
            return NotFound(new { success = false, message = "表单不存在" });
        }
        
        return Ok(new
        {
            success = true,
            data = new
            {
                formId = form.Id,
                formName = form.FormName,
                description = form.Description,
                isPublished = form.IsPublished,
                fields = form.Fields.Select(f => new
                {
                    fieldId = f.Id,
                    fieldName = f.FieldName,
                    fieldType = f.FieldType,
                    label = f.Label,
                    isRequired = f.IsRequired,
                    isVisible = f.IsVisible
                })
            }
        });
    }
}

// DTO类
public record CreateFormRequest(string FormName, string? Description, Guid? EntityDefinitionId);
public record AddFormFieldRequest(
    string FieldName,
    string FieldType,
    string? Label,
    string? Placeholder,
    string? DefaultValue,
    bool IsRequired = false,
    bool IsVisible = true,
    bool IsEditable = true,
    string? ValidationRules = null,
    string? FieldConfig = null);