using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;

namespace Tianyou.Api.Authorization;

/// <summary>
/// 权限要求
/// </summary>
public class PermissionRequirement : IAuthorizationRequirement
{
    public string[] RequiredPermissions { get; }

    public PermissionRequirement(params string[] requiredPermissions)
    {
        RequiredPermissions = requiredPermissions;
    }
}

/// <summary>
/// 权限要求处理程序
/// </summary>
public class PermissionHandler : AuthorizationHandler<PermissionRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        PermissionRequirement requirement)
    {
        // 获取用户的所有权限声明
        var userPermissions = context.User
            .FindAll("permission")
            .Select(c => c.Value)
            .ToHashSet();

        // 获取用户角色
        var userRoles = context.User
            .FindAll(ClaimTypes.Role)
            .Select(c => c.Value)
            .ToHashSet();

        // 检查用户是否拥有任一所需权限
        var hasPermission = requirement.RequiredPermissions.Any(p => userPermissions.Contains(p));

        // 或者检查用户是否拥有管理员角色
        var isAdmin = userRoles.Contains(PermissionPolicy.Admin);

        if (hasPermission || isAdmin)
        {
            context.Succeed(requirement);
        }
        else
        {
            // 记录权限不足
            var userId = context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            // 可以在这里添加日志记录
        }

        return Task.CompletedTask;
    }
}

/// <summary>
/// 角色要求处理程序
/// </summary>
public class RoleHandler : AuthorizationHandler<RoleRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        RoleRequirement requirement)
    {
        // 获取用户角色
        var userRoles = context.User
            .FindAll(ClaimTypes.Role)
            .Select(c => c.Value)
            .ToHashSet();

        // 检查用户是否拥有任一所需角色
        var hasRole = requirement.RequiredRoles.Any(r => userRoles.Contains(r));

        if (hasRole)
        {
            context.Succeed(requirement);
        }

        return Task.CompletedTask;
    }
}

/// <summary>
/// 角色要求
/// </summary>
public class RoleRequirement : IAuthorizationRequirement
{
    public string[] RequiredRoles { get; }

    public RoleRequirement(params string[] requiredRoles)
    {
        RequiredRoles = requiredRoles;
    }
}
