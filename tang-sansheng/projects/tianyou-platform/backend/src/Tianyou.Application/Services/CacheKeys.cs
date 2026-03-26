namespace Tianyou.Application.Services;

/// <summary>
/// 缓存键管理
/// </summary>
public static class CacheKeys
{
    /// <summary>
    /// 缓存键前缀
    /// </summary>
    public static readonly string Prefix = "tianyou";

    /// <summary>
    /// 用户相关缓存键
    /// </summary>
    public static class User
    {
        private static readonly string _prefix = $"{Prefix}:user";

        /// <summary>
        /// 用户信息缓存键
        /// </summary>
        public static string ById(Guid userId) => $"{_prefix}:id:{userId}";

        /// <summary>
        /// 用户名缓存键
        /// </summary>
        public static string ByUsername(string username) => $"{_prefix}:username:{username}";

        /// <summary>
        /// 用户权限缓存键
        /// </summary>
        public static string Permissions(Guid userId) => $"{_prefix}:permissions:{userId}";

        /// <summary>
        /// 用户角色缓存键
        /// </summary>
        public static string Roles(Guid userId) => $"{_prefix}:roles:{userId}";

        /// <summary>
        /// 用户列表缓存键
        /// </summary>
        public static string List(int page, int pageSize) => $"{_prefix}:list:{page}:{pageSize}";
    }

    /// <summary>
    /// 实体定义相关缓存键
    /// </summary>
    public static class Entity
    {
        private static readonly string _prefix = $"{Prefix}:entity";

        /// <summary>
        /// 实体定义缓存键
        /// </summary>
        public static string ById(Guid entityId) => $"{_prefix}:id:{entityId}";

        /// <summary>
        /// 实体名称缓存键
        /// </summary>
        public static string ByName(string entityName) => $"{_prefix}:name:{entityName}";

        /// <summary>
        /// 实体字段定义缓存键
        /// </summary>
        public static string Fields(Guid entityId) => $"{_prefix}:fields:{entityId}";

        /// <summary>
        /// 实体列表缓存键
        /// </summary>
        public static string List(int page, int pageSize) => $"{_prefix}:list:{page}:{pageSize}";

        /// <summary>
        /// 所有实体定义缓存键
        /// </summary>
        public static string All() => $"{_prefix}:all";
    }

    /// <summary>
    /// 表单定义相关缓存键
    /// </summary>
    public static class Form
    {
        private static readonly string _prefix = $"{Prefix}:form";

        /// <summary>
        /// 表单定义缓存键
        /// </summary>
        public static string ById(Guid formId) => $"{_prefix}:id:{formId}";

        /// <summary>
        /// 表单字段缓存键
        /// </summary>
        public static string Fields(Guid formId) => $"{_prefix}:fields:{formId}";

        /// <summary>
        /// 表单列表缓存键
        /// </summary>
        public static string List(int page, int pageSize) => $"{_prefix}:list:{page}:{pageSize}";
    }

    /// <summary>
    /// 工作流相关缓存键
    /// </summary>
    public static class Workflow
    {
        private static readonly string _prefix = $"{Prefix}:workflow";

        /// <summary>
        /// 工作流定义缓存键
        /// </summary>
        public static string ById(Guid workflowId) => $"{_prefix}:id:{workflowId}";

        /// <summary>
        /// 工作流实例缓存键
        /// </summary>
        public static string Instance(Guid instanceId) => $"{_prefix}:instance:{instanceId}";

        /// <summary>
        /// 工作流列表缓存键
        /// </summary>
        public static string List(int page, int pageSize) => $"{_prefix}:list:{page}:{pageSize}";
    }

    /// <summary>
    /// 权限相关缓存键
    /// </summary>
    public static class Permission
    {
        private static readonly string _prefix = $"{Prefix}:permission";

        /// <summary>
        /// 角色权限缓存键
        /// </summary>
        public static string ByRole(Guid roleId) => $"{_prefix}:role:{roleId}";

        /// <summary>
        /// 所有权限缓存键
        /// </summary>
        public static string All() => $"{_prefix}:all";
    }

    /// <summary>
    /// 租户相关缓存键
    /// </summary>
    public static class Tenant
    {
        private static readonly string _prefix = $"{Prefix}:tenant";

        /// <summary>
        /// 租户信息缓存键
        /// </summary>
        public static string ById(Guid tenantId) => $"{_prefix}:id:{tenantId}";

        /// <summary>
        /// 租户配置缓存键
        /// </summary>
        public static string Config(Guid tenantId) => $"{_prefix}:config:{tenantId}";

        /// <summary>
        /// 租户列表缓存键
        /// </summary>
        public static string List(int page, int pageSize) => $"{_prefix}:list:{page}:{pageSize}";
    }

    /// <summary>
    /// 插件相关缓存键
    /// </summary>
    public static class Plugin
    {
        private static readonly string _prefix = $"{Prefix}:plugin";

        /// <summary>
        /// 插件定义缓存键
        /// </summary>
        public static string ById(Guid pluginId) => $"{_prefix}:id:{pluginId}";

        /// <summary>
        /// 插件列表缓存键
        /// </summary>
        public static string List(int page, int pageSize) => $"{_prefix}:list:{page}:{pageSize}";

        /// <summary>
        /// 所有插件缓存键
        /// </summary>
        public static string All() => $"{_prefix}:all";
    }

    /// <summary>
    /// 报表相关缓存键
    /// </summary>
    public static class Report
    {
        private static readonly string _prefix = $"{Prefix}:report";

        /// <summary>
        /// 报表定义缓存键
        /// </summary>
        public static string ById(Guid reportId) => $"{_prefix}:id:{reportId}";

        /// <summary>
        /// 报表数据缓存键
        /// </summary>
        public static string Data(Guid reportId, string parameters) => $"{_prefix}:data:{reportId}:{parameters}";
    }

    /// <summary>
    /// 系统配置相关缓存键
    /// </summary>
    public static class System
    {
        private static readonly string _prefix = $"{Prefix}:system";

        /// <summary>
        /// 系统配置缓存键
        /// </summary>
        public static string Config(string key) => $"{_prefix}:config:{key}";

        /// <summary>
        /// 系统统计缓存键
        /// </summary>
        public static string Statistics() => $"{_prefix}:statistics";
    }
}
