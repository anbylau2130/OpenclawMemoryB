using Microsoft.AspNetCore.Mvc;
using YunTianYou.Application.DTOs;
using YunTianYou.Application.Services;

namespace YunTianYou.Api.Controllers;

/// <summary>
/// 表单实例API控制器 - 处理用户提交的表单数据
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class FormInstancesController : ControllerBase
{
    private readonly IFormInstanceService _formInstanceService;
    private readonly ILogger<FormInstancesController> _logger;

    public FormInstancesController(IFormInstanceService formInstanceService, ILogger<FormInstancesController> logger)
    {
        _formInstanceService = formInstanceService;
        _logger = logger;
    }

    /// <summary>
    /// 获取所有表单实例
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<FormInstanceDto>>> GetFormInstances([FromQuery] Guid? formId, [FromQuery] string? status)
    {
        try
        {
            var instances = await _formInstanceService.GetFormInstancesAsync(formId, status);
            return Ok(new { success = true, data = instances });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取表单实例列表失败");
            return StatusCode(500, new { success = false, message = "获取表单实例列表失败" });
        }
    }

    /// <summary>
    /// 根据ID获取表单实例
    /// </summary>
    [HttpGet("{id}")]
    public async Task<ActionResult<FormInstanceDto>> GetFormInstance(Guid id)
    {
        try
        {
            var instance = await _formInstanceService.GetFormInstanceByIdAsync(id);
            if (instance == null)
            {
                return NotFound(new { success = false, message = "表单实例不存在" });
            }
            return Ok(new { success = true, data = instance });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "获取表单实例失败: {InstanceId}", id);
            return StatusCode(500, new { success = false, message = "获取表单实例失败" });
        }
    }

    /// <summary>
    /// 提交表单实例
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<FormInstanceDto>> SubmitFormInstance([FromBody] SubmitFormInstanceDto dto)
    {
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new { success = false, errors = ModelState });
            }

            var instance = await _formInstanceService.SubmitFormInstanceAsync(dto);
            return CreatedAtAction(nameof(GetFormInstance), new { id = instance.Id },
                new { success = true, data = instance, message = "表单提交成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "提交表单实例失败");
            return StatusCode(500, new { success = false, message = "提交表单失败" });
        }
    }

    /// <summary>
    /// 更新表单实例数据
    /// </summary>
    [HttpPut("{id}")]
    public async Task<ActionResult<FormInstanceDto>> UpdateFormInstance(Guid id, [FromBody] UpdateFormInstanceDto dto)
    {
        try
        {
            var instance = await _formInstanceService.UpdateFormInstanceAsync(id, dto);
            if (instance == null)
            {
                return NotFound(new { success = false, message = "表单实例不存在" });
            }
            return Ok(new { success = true, data = instance, message = "表单更新成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "更新表单实例失败: {InstanceId}", id);
            return StatusCode(500, new { success = false, message = "更新表单失败" });
        }
    }

    /// <summary>
    /// 删除表单实例
    /// </summary>
    [HttpDelete("{id}")]
    public async Task<ActionResult> DeleteFormInstance(Guid id)
    {
        try
        {
            var result = await _formInstanceService.DeleteFormInstanceAsync(id);
            if (!result)
            {
                return NotFound(new { success = false, message = "表单实例不存在" });
            }
            return Ok(new { success = true, message = "表单删除成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "删除表单实例失败: {InstanceId}", id);
            return StatusCode(500, new { success = false, message = "删除表单失败" });
        }
    }

    /// <summary>
    /// 审批表单实例
    /// </summary>
    [HttpPost("{id}/approve")]
    public async Task<ActionResult> ApproveFormInstance(Guid id, [FromBody] ApprovalDto dto)
    {
        try
        {
            var result = await _formInstanceService.ApproveFormInstanceAsync(id, dto);
            if (!result)
            {
                return NotFound(new { success = false, message = "表单实例不存在" });
            }
            return Ok(new { success = true, message = "表单审批成功" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "审批表单实例失败: {InstanceId}", id);
            return StatusCode(500, new { success = false, message = "审批失败" });
        }
    }

    /// <summary>
    /// 驳回表单实例
    /// </summary>
    [HttpPost("{id}/reject")]
    public async Task<ActionResult> RejectFormInstance(Guid id, [FromBody] RejectionDto dto)
    {
        try
        {
            var result = await _formInstanceService.RejectFormInstanceAsync(id, dto);
            if (!result)
            {
                return NotFound(new { success = false, message = "表单实例不存在" });
            }
            return Ok(new { success = true, message = "表单已驳回" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "驳回表单实例失败: {InstanceId}", id);
            return StatusCode(500, new { success = false, message = "驳回失败" });
        }
    }
}

public class UpdateFormInstanceDto
{
    public string Data { get; set; } = "{}";
}

public class ApprovalDto
{
    public string? Comment { get; set; }
}

public class RejectionDto
{
    public string Reason { get; set; } = string.Empty;
}
