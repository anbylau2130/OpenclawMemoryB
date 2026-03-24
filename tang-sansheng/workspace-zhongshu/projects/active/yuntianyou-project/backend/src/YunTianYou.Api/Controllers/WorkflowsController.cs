using Microsoft.AspNetCore.Mvc;
using YunTianYou.Application.Services;

namespace YunTianYou.Api.Controllers;

/// <summary>
/// 工作流控制器 - 流程管理
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class WorkflowsController : ControllerBase
{
    private readonly WorkflowService _workflowService;
    
    public WorkflowsController(WorkflowService workflowService)
    {
        _workflowService = workflowService;
    }
    
    /// <summary>
    /// 获取工作流列表
    /// </summary>
    [HttpGet]
    public async Task<ActionResult> GetAll()
    {
        var workflows = await _workflowService.GetWorkflowsAsync();
        return Ok(workflows);
    }
    
    /// <summary>
    /// 创建工作流
    /// </summary>
    [HttpPost]
    public async Task<ActionResult> Create([FromBody] CreateWorkflowRequest request)
    {
        var workflow = await _workflowService.CreateWorkflowAsync(
            request.Name, request.Description ?? "", request.Definition, request.CreatedByUserId);
        return Ok(workflow);
    }
    
    /// <summary>
    /// 启动工作流实例
    /// </summary>
    [HttpPost("{id}/start")]
    public async Task<ActionResult> StartInstance(Guid id, [FromBody] StartWorkflowRequest request)
    {
        try
        {
            var instance = await _workflowService.StartInstanceAsync(
                id, request.Data, request.InitiatedByUserId);
            return Ok(instance);
        }
        catch (ArgumentException ex)
        {
            return NotFound(new { error = ex.Message });
        }
    }
    
    /// <summary>
    /// 获取工作流实例
    /// </summary>
    [HttpGet("instances/{instanceId}")]
    public async Task<ActionResult> GetInstance(Guid instanceId)
    {
        var instance = await _workflowService.GetInstanceAsync(instanceId);
        if (instance == null)
        {
            return NotFound();
        }
        return Ok(instance);
    }
    
    /// <summary>
    /// 审批操作
    /// </summary>
    [HttpPost("instances/{instanceId}/approve")]
    public async Task<ActionResult> Approve(Guid instanceId, [FromBody] ApproveRequest request)
    {
        try
        {
            var approval = await _workflowService.ApproveAsync(
                instanceId, request.ApprovedByUserId, request.Action, request.Comment);
            return Ok(approval);
        }
        catch (ArgumentException ex)
        {
            return NotFound(new { error = ex.Message });
        }
    }
    
    /// <summary>
    /// 获取待办任务
    /// </summary>
    [HttpGet("pending/{userId}")]
    public async Task<ActionResult> GetPendingTasks(Guid userId)
    {
        var tasks = await _workflowService.GetPendingTasksAsync(userId);
        return Ok(tasks);
    }
}

// DTOs
public class CreateWorkflowRequest
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string Definition { get; set; } = "{}";
    public Guid CreatedByUserId { get; set; }
}

public class StartWorkflowRequest
{
    public string Data { get; set; } = "{}";
    public Guid InitiatedByUserId { get; set; }
}

public class ApproveRequest
{
    public Guid ApprovedByUserId { get; set; }
    public string Action { get; set; } = "approved"; // approved, rejected
    public string? Comment { get; set; }
}
