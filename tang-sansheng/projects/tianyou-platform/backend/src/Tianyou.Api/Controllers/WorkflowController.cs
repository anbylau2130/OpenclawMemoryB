using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using Tianyou.Application.Services;

namespace Tianyou.Api.Controllers;

/// <summary>
/// 工作流控制器
/// </summary>
[ApiController]
[Route("api/workflows")]
[Authorize]
public class WorkflowController : ControllerBase
{
    private readonly WorkflowService _workflowService;
    private readonly ILogger<WorkflowController> _logger;
    
    public WorkflowController(WorkflowService workflowService, ILogger<WorkflowController> logger)
    {
        _workflowService = workflowService;
        _logger = logger;
    }
    
    /// <summary>
    /// 创建工作流
    /// </summary>
    [HttpPost]
    public async Task<IActionResult> CreateWorkflow([FromBody] CreateWorkflowRequest request)
    {
        try
        {
            var workflow = await _workflowService.CreateWorkflowAsync(
                request.WorkflowName,
                request.Description,
                request.StepsConfig);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    workflowId = workflow.Id,
                    workflowName = workflow.WorkflowName,
                    description = workflow.Description,
                    isActive = workflow.IsActive,
                    createdAt = workflow.CreatedAt
                }
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 启动工作流
    /// </summary>
    [HttpPost("{workflowId}/start")]
    public async Task<IActionResult> StartWorkflow(Guid workflowId, [FromBody] StartWorkflowRequest request)
    {
        try
        {
            var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            Guid? initiatedBy = Guid.TryParse(userIdClaim, out var userId) ? userId : (Guid?)null;
            
            var instance = await _workflowService.StartWorkflowAsync(
                workflowId,
                initiatedBy,
                request.InstanceData);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    instanceId = instance.Id,
                    status = instance.Status,
                    startedAt = instance.StartedAt
                }
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 创建任务
    /// </summary>
    [HttpPost("instances/{instanceId}/tasks")]
    public async Task<IActionResult> CreateTask(Guid instanceId, [FromBody] CreateTaskRequest request)
    {
        try
        {
            var task = await _workflowService.CreateTaskAsync(
                instanceId,
                request.TaskName,
                request.TaskType,
                request.AssignedTo,
                request.TaskData);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    taskId = task.Id,
                    taskName = task.TaskName,
                    status = task.Status,
                    createdAt = task.CreatedAt
                }
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 完成任务
    /// </summary>
    [HttpPost("tasks/{taskId}/complete")]
    public async Task<IActionResult> CompleteTask(Guid taskId)
    {
        try
        {
            var task = await _workflowService.CompleteTaskAsync(taskId);
            
            return Ok(new
            {
                success = true,
                data = new
                {
                    taskId = task.Id,
                    status = task.Status,
                    completedAt = task.CompletedAt
                }
            });
        }
        catch (Exception ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
    }
    
    /// <summary>
    /// 获取工作流列表
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetWorkflows()
    {
        var workflows = await _workflowService.GetWorkflowsAsync();
        
        return Ok(new
        {
            success = true,
            data = workflows.Select(w => new
            {
                workflowId = w.Id,
                workflowName = w.WorkflowName,
                description = w.Description,
                isActive = w.IsActive,
                createdAt = w.CreatedAt
            })
        });
    }
    
    /// <summary>
    /// 获取我的待办任务
    /// </summary>
    [HttpGet("my-tasks")]
    public async Task<IActionResult> GetMyTasks()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Unauthorized(new { success = false, message = "用户未认证" });
        }
        
        var tasks = await _workflowService.GetUserTasksAsync(userId);
        
        return Ok(new
        {
            success = true,
            data = tasks.Select(t => new
            {
                taskId = t.Id,
                taskName = t.TaskName,
                taskType = t.TaskType,
                status = t.Status,
                workflowName = t.Instance.Workflow.WorkflowName,
                createdAt = t.CreatedAt
            })
        });
    }
    
    /// <summary>
    /// 获取实例详情
    /// </summary>
    [HttpGet("instances/{instanceId}")]
    public async Task<IActionResult> GetInstance(Guid instanceId)
    {
        var instance = await _workflowService.GetInstanceAsync(instanceId);
        
        if (instance == null)
        {
            return NotFound(new { success = false, message = "实例不存在" });
        }
        
        return Ok(new
        {
            success = true,
            data = new
            {
                instanceId = instance.Id,
                workflowName = instance.Workflow.WorkflowName,
                status = instance.Status,
                startedAt = instance.StartedAt,
                tasks = instance.Tasks.Select(t => new
                {
                    taskId = t.Id,
                    taskName = t.TaskName,
                    taskType = t.TaskType,
                    status = t.Status,
                    createdAt = t.CreatedAt
                })
            }
        });
    }
}

// DTO类
public record CreateWorkflowRequest(string WorkflowName, string? Description, string? StepsConfig);
public record StartWorkflowRequest(string? InstanceData);
public record CreateTaskRequest(string TaskName, string TaskType, Guid? AssignedTo, string? TaskData);