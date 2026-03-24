using YunTianYou.Domain.Entities;

namespace YunTianYou.Application.Services;

/// <summary>
/// 工作流服务 - 流程引擎核心
/// </summary>
public class WorkflowService
{
    private readonly List<Workflow> _workflows = new();
    private readonly List<WorkflowInstance> _instances = new();
    private readonly List<WorkflowApproval> _approvals = new();
    
    /// <summary>
    /// 创建工作流定义
    /// </summary>
    public async Task<Workflow> CreateWorkflowAsync(
        string name, string description, string definition, Guid createdByUserId)
    {
        var workflow = new Workflow
        {
            Id = Guid.NewGuid(),
            Name = name,
            Description = description,
            Definition = definition,
            IsActive = true,
            Version = 1,
            CreatedByUserId = createdByUserId,
            CreatedAt = DateTime.UtcNow
        };
        
        _workflows.Add(workflow);
        return await Task.FromResult(workflow);
    }
    
    /// <summary>
    /// 启动工作流实例
    /// </summary>
    public async Task<WorkflowInstance> StartInstanceAsync(
        Guid workflowId, string data, Guid initiatedByUserId)
    {
        var workflow = _workflows.FirstOrDefault(w => w.Id == workflowId);
        if (workflow == null)
        {
            throw new ArgumentException("工作流不存在");
        }
        
        var instance = new WorkflowInstance
        {
            Id = Guid.NewGuid(),
            WorkflowId = workflowId,
            Status = "running",
            CurrentNode = "start",
            Data = data,
            InitiatedByUserId = initiatedByUserId,
            StartedAt = DateTime.UtcNow,
            CreatedAt = DateTime.UtcNow
        };
        
        _instances.Add(instance);
        
        // 触发开始节点
        await ProcessNodeAsync(instance, "start");
        
        return instance;
    }
    
    /// <summary>
    /// 处理流程节点
    /// </summary>
    private async Task ProcessNodeAsync(WorkflowInstance instance, string nodeName)
    {
        instance.CurrentNode = nodeName;
        
        // 根据节点类型执行不同逻辑
        switch (nodeName)
        {
            case "start":
                // 开始节点，自动流转到下一个节点
                await MoveToNextNodeAsync(instance, "submit");
                break;
                
            case "submit":
                // 提交节点，等待审批
                instance.Status = "pending_approval";
                break;
                
            case "approve":
                // 审批节点
                instance.Status = "approved";
                await MoveToNextNodeAsync(instance, "end");
                break;
                
            case "reject":
                // 拒绝节点
                instance.Status = "rejected";
                await MoveToNextNodeAsync(instance, "end");
                break;
                
            case "end":
                // 结束节点
                instance.Status = "completed";
                instance.CompletedAt = DateTime.UtcNow;
                break;
        }
    }
    
    /// <summary>
    /// 移动到下一个节点
    /// </summary>
    private async Task MoveToNextNodeAsync(WorkflowInstance instance, string nextNode)
    {
        await ProcessNodeAsync(instance, nextNode);
    }
    
    /// <summary>
    /// 审批操作
    /// </summary>
    public async Task<WorkflowApproval> ApproveAsync(
        Guid instanceId, Guid approvedByUserId, string action, string? comment)
    {
        var instance = _instances.FirstOrDefault(i => i.Id == instanceId);
        if (instance == null)
        {
            throw new ArgumentException("工作流实例不存在");
        }
        
        var approval = new WorkflowApproval
        {
            Id = Guid.NewGuid(),
            WorkflowInstanceId = instanceId,
            NodeName = instance.CurrentNode,
            ApprovedByUserId = approvedByUserId,
            Action = action,
            Comment = comment,
            ActionAt = DateTime.UtcNow,
            CreatedAt = DateTime.UtcNow
        };
        
        _approvals.Add(approval);
        
        // 根据审批动作流转
        if (action == "approved")
        {
            await MoveToNextNodeAsync(instance, "approve");
        }
        else if (action == "rejected")
        {
            await MoveToNextNodeAsync(instance, "reject");
        }
        
        return approval;
    }
    
    /// <summary>
    /// 获取工作流列表
    /// </summary>
    public async Task<List<Workflow>> GetWorkflowsAsync()
    {
        return await Task.FromResult(_workflows.ToList());
    }
    
    /// <summary>
    /// 获取工作流实例
    /// </summary>
    public async Task<WorkflowInstance?> GetInstanceAsync(Guid instanceId)
    {
        return await Task.FromResult(_instances.FirstOrDefault(i => i.Id == instanceId));
    }
    
    /// <summary>
    /// 获取用户的待办任务
    /// </summary>
    public async Task<List<WorkflowInstance>> GetPendingTasksAsync(Guid userId)
    {
        return await Task.FromResult(
            _instances.Where(i => i.Status == "pending_approval").ToList());
    }
}
