using Microsoft.AspNetCore.Authorization;

namespace Tianyou.Api.Authorization;

/// <summary>
/// 权限授权特性
/// </summary>
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method, AllowMultiple = true)]
public class RequirePermissionAttribute : AuthorizeAttribute
{
    public RequirePermissionAttribute(params string[] permissions)
    {
        Policy = $"Permission:{string.Join(",", permissions)}";
        Permissions = permissions;
    }

    public string[] Permissions { get; }
}

/// <summary>
/// 角色授权特性
/// </summary>
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method, AllowMultiple = true)]
public class RequireRoleAttribute : AuthorizeAttribute
{
    public RequireRoleAttribute(params string[] roles)
    {
        Policy = $"Role:{string.Join(",", roles)}";
        Roles = string.Join(",", roles);
    }
}

/// <summary>
/// 管理员专用特性
/// </summary>
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class AdminOnlyAttribute : RequireRoleAttribute
{
    public AdminOnlyAttribute() : base(PermissionPolicy.Admin)
    {
    }
}
