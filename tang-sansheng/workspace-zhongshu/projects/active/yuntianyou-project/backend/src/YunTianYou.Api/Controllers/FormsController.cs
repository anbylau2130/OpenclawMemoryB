using Microsoft.AspNetCore.Mvc;
using YunTianYou.Application.DTOs;
using YunTianYou.Application.Services;

namespace YunTianYou.Api.Controllers;

/// <summary>
/// 表单管理API控制器 - 低代码核心功能
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class FormsController : ControllerBase
{
    private readonly IFormService _formService;
    private readonly ILogger<FormsController> _logger;
    
    public FormsController(IFormService formService, ILogger<FormsController> logger)
    {
        _formService = formService;
        _logger = logger;
    }
    
    /// <summary>
    /// 获取所有表单模板
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<FormDto>>> GetForms()
    {
        try
        {
            var forms = await _formService.GetAllFormsAsync();
            return Ok(new { success = true, data = forms });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取表单列表失败");
            return StatusCode(500, new { success = false, message = "获取表单列表失败" });
        }
    }
    
    /// <summary>
    /// 根据ID获取表单模板
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<FormDto>> GetForm(Guid id)
    {
        try
        {
            var form = await _formService.GetFormByIdAsync(id);
            if (form == null)
            {
                return NotFound(new { success = false, message = "表单不存在" });
            }
            return Ok(new { success = true, data = form });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取表单失败: {FormId}", id);
            return StatusCode(500, new { success = false, message = "获取表单失败" });
        }
    }
    
    /// <summary>
    /// 创建新表单模板
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<FormDto>> CreateForm([FromBody] CreateFormDto dto)
    {
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new { success = false, errors = ModelState });
            }
            
            var form = await _formService.CreateFormAsync(dto);
            return CreatedAtAction(nameof(GetForm), new { id = form.Id }, 
                new { success = true, data = form, message = "表单创建成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "创建表单失败");
            return StatusCode(500, new { success = false, message = "创建表单失败" });
        }
    }
    
    /// <summary>
    /// 更新表单模板
    /// </summary>
    [HttpPut("{id}")]
    public async Task<ActionResult<FormDto>> UpdateForm(Guid id, [FromBody] UpdateFormDto dto)
    {
        try
        {
            var form = await _formService.UpdateFormAsync(id, dto);
            if (form == null)
            {
                return NotFound(new { success = false, message = "表单不存在" });
            }
            return Ok(new { success = true, data = form, message = "表单更新成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "更新表单失败: {FormId}", id);
            return StatusCode(500, new { success = false, message = "更新表单失败" });
        }
    }
    
    /// <summary>
    /// 删除表单模板
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteForm(Guid id)
    {
        try
        {
            var result = await _formService.DeleteFormAsync(id);
            if (!result)
            {
                return NotFound(new { success = false, message = "表单不存在" });
            }
            return Ok(new { success = true, message = "表单删除成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "删除表单失败: {FormId}", id);
            return StatusCode(500, new { success = false, message = "删除表单失败" });
        }
    }
    
    /// <summary>
    /// 发布表单模板
    /// </summary>
    [HttpPost("{id}/publish")]
    public async Task<ActionResult> PublishForm(Guid id)
    {
        try
        {
            var result = await _formService.PublishFormAsync(id);
            if (!result)
            {
                return NotFound(new { success = false, message = "表单不存在" });
            }
            return Ok(new { success = true, message = "表单发布成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "发布表单失败: {FormId}", id);
            return StatusCode(500, new { success = false, message = "发布表单失败" });
        }
    }
    
    /// <summary>
    /// 获取表单字段定义
    /// </summary>
    [HttpGet("{id}/fields")]
    public async Task<ActionResult> GetFormFields(Guid id)
    {
        try
        {
            var fields = await _formService.GetFormFieldsAsync(id);
            return Ok(new { success = true, data = fields });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取表单字段失败: {FormId}", id);
            return StatusCode(500, new { success = false, message = "获取表单字段失败" });
        }
    }
}
