namespace Tianyou.Api.Authorization;

/// <summary>
/// 权限策略定义
/// </summary>
public static class PermissionPolicy
{
    // 角色定义
    public const string Admin = "admin";
    public const string User = "user";
    public const string Guest = "guest";

    // 权限定义
    public static class Permissions
    {
        // 用户管理
        public const string UserRead = "user:read";
        public const string UserCreate = "user:create";
        public const string UserUpdate = "user:update";
        public const string UserDelete = "user:delete";

        // 实体管理
        public const string EntityRead = "entity:read";
        public const string EntityCreate = "entity:create";
        public const string EntityUpdate = "entity:update";
        public const string EntityDelete = "entity:delete";

        // 租户管理
        public const string TenantRead = "tenant:read";
        public const string TenantCreate = "tenant:create";
        public const string TenantUpdate = "tenant:update";
        public const string TenantDelete = "tenant:delete";
        public const string TenantSuspend = "tenant:suspend";

        // 表单管理
        public const string FormRead = "form:read";
        public const string FormCreate = "form:create";
        public const string FormUpdate = "form:update";
        public const string FormDelete = "form:delete";

        // 工作流管理
        public const string WorkflowRead = "workflow:read";
        public const string WorkflowCreate = "workflow:create";
        public const string WorkflowUpdate = "workflow:update";
        public const string WorkflowDelete = "workflow:delete";

        // 代码生成
        public const string CodeGenerate = "code:generate";
        public const string TemplateManage = "template:manage";

        // 系统管理
        public const string SystemAdmin = "system:admin";
        public const string SystemConfig = "system:config";
    }

    // 策略名称
    public static class Policies
    {
        public const string AdminOnly = "AdminOnly";
        public const string UserManagement = "UserManagement";
        public const string EntityManagement = "EntityManagement";
        public const string TenantManagement = "TenantManagement";
        public const string FormManagement = "FormManagement";
        public const string WorkflowManagement = "WorkflowManagement";
        public const string CodeGeneration = "CodeGeneration";
        public const string SystemManagement = "SystemManagement";
    }

    // 角色权限映射
    public static readonly Dictionary<string, string[]> RolePermissions = new()
    {
        [Admin] = new[]
        {
            Permissions.UserRead, Permissions.UserCreate, Permissions.UserUpdate, Permissions.UserDelete,
            Permissions.EntityRead, Permissions.EntityCreate, Permissions.EntityUpdate, Permissions.EntityDelete,
            Permissions.TenantRead, Permissions.TenantCreate, Permissions.TenantUpdate, Permissions.TenantDelete, Permissions.TenantSuspend,
            Permissions.FormRead, Permissions.FormCreate, Permissions.FormUpdate, Permissions.FormDelete,
            Permissions.WorkflowRead, Permissions.WorkflowCreate, Permissions.WorkflowUpdate, Permissions.WorkflowDelete,
            Permissions.CodeGenerate, Permissions.TemplateManage,
            Permissions.SystemAdmin, Permissions.SystemConfig
        },
        [User] = new[]
        {
            Permissions.UserRead, Permissions.UserUpdate,
            Permissions.EntityRead, Permissions.EntityCreate, Permissions.EntityUpdate,
            Permissions.FormRead, Permissions.FormCreate, Permissions.FormUpdate,
            Permissions.WorkflowRead, Permissions.WorkflowCreate, Permissions.WorkflowUpdate,
            Permissions.CodeGenerate
        },
        [Guest] = new[]
        {
            Permissions.UserRead,
            Permissions.EntityRead,
            Permissions.FormRead,
            Permissions.WorkflowRead
        }
    };
}
