using Microsoft.EntityFrameworkCore;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;
using System.Text.Json;

namespace Tianyou.Application.Services;

/// <summary>
/// 工作流服务
/// </summary>
public class WorkflowService
{
    private readonly TianyouDbContext _context;
    
    public WorkflowService(TianyouDbContext context)
    {
        _context = context;
    }
    
    /// <summary>
    /// 创建工作流定义
    /// </summary>
    public async Task<WorkflowDefinition> CreateWorkflowAsync(string workflowName, string? description = null, string? stepsConfig = null)
    {
        if (await _context.WorkflowDefinitions.AnyAsync(w => w.WorkflowName == workflowName))
        {
            throw new Exception($"工作流名称 '{workflowName}' 已存在");
        }
        
        var workflow = new WorkflowDefinition
        {
            Id = Guid.NewGuid(),
            WorkflowName = workflowName,
            Description = description,
            StepsConfig = stepsConfig,
            IsActive = true,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        _context.WorkflowDefinitions.Add(workflow);
        await _context.SaveChangesAsync();
        
        return workflow;
    }
    
    /// <summary>
    /// 启动工作流实例
    /// </summary>
    public async Task<WorkflowInstance> StartWorkflowAsync(Guid workflowDefinitionId, Guid? initiatedBy = null, string? instanceData = null)
    {
        var workflow = await _context.WorkflowDefinitions.FindAsync(workflowDefinitionId);
        if (workflow == null)
        {
            throw new Exception("工作流不存在");
        }
        
        if (!workflow.IsActive)
        {
            throw new Exception("工作流未激活");
        }
        
        var instance = new WorkflowInstance
        {
            Id = Guid.NewGuid(),
            WorkflowDefinitionId = workflowDefinitionId,
            Status = "running",
            InitiatedBy = initiatedBy,
            InstanceData = instanceData,
            StartedAt = DateTime.UtcNow
        };
        
        _context.WorkflowInstances.Add(instance);
        await _context.SaveChangesAsync();
        
        return instance;
    }
    
    /// <summary>
    /// 创建任务
    /// </summary>
    public async Task<WorkflowTask> CreateTaskAsync(Guid instanceId, string taskName, string taskType, Guid? assignedTo = null, string? taskData = null)
    {
        var instance = await _context.WorkflowInstances.FindAsync(instanceId);
        if (instance == null)
        {
            throw new Exception("工作流实例不存在");
        }
        
        var task = new WorkflowTask
        {
            Id = Guid.NewGuid(),
            WorkflowInstanceId = instanceId,
            TaskName = taskName,
            TaskType = taskType,
            Status = "pending",
            AssignedTo = assignedTo,
            TaskData = taskData,
            CreatedAt = DateTime.UtcNow
        };
        
        _context.WorkflowTasks.Add(task);
        await _context.SaveChangesAsync();
        
        return task;
    }
    
    /// <summary>
    /// 完成任务
    /// </summary>
    public async Task<WorkflowTask> CompleteTaskAsync(Guid taskId)
    {
        var task = await _context.WorkflowTasks.FindAsync(taskId);
        if (task == null)
        {
            throw new Exception("任务不存在");
        }
        
        task.Status = "completed";
        task.CompletedAt = DateTime.UtcNow;
        
        await _context.SaveChangesAsync();
        
        return task;
    }
    
    /// <summary>
    /// 获取工作流列表
    /// </summary>
    public async Task<List<WorkflowDefinition>> GetWorkflowsAsync()
    {
        return await _context.WorkflowDefinitions
            .Where(w => w.IsActive)
            .OrderByDescending(w => w.CreatedAt)
            .ToListAsync();
    }
    
    /// <summary>
    /// 获取工作流详情
    /// </summary>
    public async Task<WorkflowDefinition?> GetWorkflowAsync(Guid workflowId)
    {
        return await _context.WorkflowDefinitions
            .FirstOrDefaultAsync(w => w.Id == workflowId);
    }
    
    /// <summary>
    /// 获取实例详情
    /// </summary>
    public async Task<WorkflowInstance?> GetInstanceAsync(Guid instanceId)
    {
        return await _context.WorkflowInstances
            .Include(i => i.Tasks)
            .Include(i => i.Workflow)
            .FirstOrDefaultAsync(i => i.Id == instanceId);
    }
    
    /// <summary>
    /// 获取用户待办任务
    /// </summary>
    public async Task<List<WorkflowTask>> GetUserTasksAsync(Guid userId)
    {
        return await _context.WorkflowTasks
            .Include(t => t.Instance)
                .ThenInclude(i => i.Workflow)
            .Where(t => t.AssignedTo == userId && t.Status == "pending")
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync();
    }
}