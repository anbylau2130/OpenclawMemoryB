-- Tianyou低代码平台数据库初始化脚本
-- 数据库：SQLite
-- 创建时间：2026-03-25

-- ============================================
-- 1. 用户认证表
-- ============================================

-- 用户表
CREATE TABLE IF NOT EXISTS Users (
    Id TEXT PRIMARY KEY,
    Username TEXT NOT NULL UNIQUE,
    Email TEXT NOT NULL UNIQUE,
    PasswordHash TEXT NOT NULL,
    FullName TEXT,
    AvatarUrl TEXT,
    Status TEXT NOT NULL DEFAULT 'active',
    CreatedAt TEXT NOT NULL,
    UpdatedAt TEXT NOT NULL,
    LastLoginAt TEXT
);

CREATE INDEX IF NOT EXISTS IX_Users_Username ON Users(Username);
CREATE INDEX IF NOT EXISTS IX_Users_Email ON Users(Email);

-- 角色表
CREATE TABLE IF NOT EXISTS Roles (
    Id TEXT PRIMARY KEY,
    RoleName TEXT NOT NULL UNIQUE,
    RoleCode TEXT NOT NULL UNIQUE,
    Description TEXT,
    CreatedAt TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_Roles_RoleName ON Roles(RoleName);
CREATE INDEX IF NOT EXISTS IX_Roles_RoleCode ON Roles(RoleCode);

-- 权限表
CREATE TABLE IF NOT EXISTS Permissions (
    Id TEXT PRIMARY KEY,
    PermissionName TEXT NOT NULL UNIQUE,
    PermissionCode TEXT NOT NULL UNIQUE,
    Resource TEXT,
    Action TEXT,
    Description TEXT,
    CreatedAt TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_Permissions_PermissionName ON Permissions(PermissionName);
CREATE INDEX IF NOT EXISTS IX_Permissions_PermissionCode ON Permissions(PermissionCode);

-- 用户-角色关联表
CREATE TABLE IF NOT EXISTS RoleUser (
    RolesId TEXT NOT NULL,
    UsersId TEXT NOT NULL,
    PRIMARY KEY (RolesId, UsersId),
    FOREIGN KEY (RolesId) REFERENCES Roles(Id) ON DELETE CASCADE,
    FOREIGN KEY (UsersId) REFERENCES Users(Id) ON DELETE CASCADE
);

-- 角色-权限关联表
CREATE TABLE IF NOT EXISTS PermissionRole (
    PermissionsId TEXT NOT NULL,
    RolesId TEXT NOT NULL,
    PRIMARY KEY (PermissionsId, RolesId),
    FOREIGN KEY (PermissionsId) REFERENCES Permissions(Id) ON DELETE CASCADE,
    FOREIGN KEY (RolesId) REFERENCES Roles(Id) ON DELETE CASCADE
);

-- ============================================
-- 2. 数据管理表
-- ============================================

-- 实体定义表
CREATE TABLE IF NOT EXISTS EntityDefinitions (
    Id TEXT PRIMARY KEY,
    EntityName TEXT NOT NULL UNIQUE,
    TableName TEXT NOT NULL UNIQUE,
    Description TEXT,
    IsSystem INTEGER NOT NULL DEFAULT 0,
    IsActive INTEGER NOT NULL DEFAULT 1,
    CreatedAt TEXT NOT NULL,
    UpdatedAt TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_EntityDefinitions_EntityName ON EntityDefinitions(EntityName);
CREATE INDEX IF NOT EXISTS IX_EntityDefinitions_TableName ON EntityDefinitions(TableName);

-- 字段定义表
CREATE TABLE IF NOT EXISTS FieldDefinitions (
    Id TEXT PRIMARY KEY,
    EntityDefinitionId TEXT NOT NULL,
    FieldName TEXT NOT NULL,
    FieldType TEXT NOT NULL DEFAULT 'text',
    Description TEXT,
    IsRequired INTEGER NOT NULL DEFAULT 0,
    IsUnique INTEGER NOT NULL DEFAULT 0,
    MaxLength INTEGER,
    DefaultValue TEXT,
    ValidationRule TEXT,
    DisplayOrder INTEGER NOT NULL DEFAULT 0,
    CreatedAt TEXT NOT NULL,
    FOREIGN KEY (EntityDefinitionId) REFERENCES EntityDefinitions(Id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS IX_FieldDefinitions_EntityId_FieldName 
    ON FieldDefinitions(EntityDefinitionId, FieldName);

-- 动态数据表
CREATE TABLE IF NOT EXISTS DynamicData (
    Id TEXT PRIMARY KEY,
    EntityDefinitionId TEXT NOT NULL,
    CreatedBy TEXT,
    UpdatedBy TEXT,
    CreatedAt TEXT NOT NULL,
    UpdatedAt TEXT NOT NULL,
    DataJson TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (EntityDefinitionId) REFERENCES EntityDefinitions(Id) ON DELETE CASCADE
);

-- ============================================
-- 3. 表单设计器表
-- ============================================

-- 表单定义表
CREATE TABLE IF NOT EXISTS FormDefinitions (
    Id TEXT PRIMARY KEY,
    FormName TEXT NOT NULL UNIQUE,
    Description TEXT,
    EntityDefinitionId TEXT,
    IsPublished INTEGER NOT NULL DEFAULT 0,
    CreatedAt TEXT NOT NULL,
    UpdatedAt TEXT NOT NULL,
    FOREIGN KEY (EntityDefinitionId) REFERENCES EntityDefinitions(Id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS IX_FormDefinitions_FormName ON FormDefinitions(FormName);

-- 表单字段表
CREATE TABLE IF NOT EXISTS FormFields (
    Id TEXT PRIMARY KEY,
    FormDefinitionId TEXT NOT NULL,
    FieldName TEXT NOT NULL,
    FieldType TEXT NOT NULL DEFAULT 'text',
    Label TEXT,
    Placeholder TEXT,
    DefaultValue TEXT,
    IsRequired INTEGER NOT NULL DEFAULT 0,
    IsVisible INTEGER NOT NULL DEFAULT 1,
    IsEditable INTEGER NOT NULL DEFAULT 1,
    DisplayOrder INTEGER NOT NULL DEFAULT 0,
    ValidationRules TEXT,
    FieldConfig TEXT,
    CreatedAt TEXT NOT NULL,
    FOREIGN KEY (FormDefinitionId) REFERENCES FormDefinitions(Id) ON DELETE CASCADE
);

-- ============================================
-- 4. 工作流引擎表
-- ============================================

-- 工作流定义表
CREATE TABLE IF NOT EXISTS WorkflowDefinitions (
    Id TEXT PRIMARY KEY,
    WorkflowName TEXT NOT NULL UNIQUE,
    Description TEXT,
    IsActive INTEGER NOT NULL DEFAULT 1,
    StepsConfig TEXT,
    CreatedAt TEXT NOT NULL,
    UpdatedAt TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_WorkflowDefinitions_WorkflowName ON WorkflowDefinitions(WorkflowName);

-- 工作流实例表
CREATE TABLE IF NOT EXISTS WorkflowInstances (
    Id TEXT PRIMARY KEY,
    WorkflowDefinitionId TEXT NOT NULL,
    Status TEXT NOT NULL DEFAULT 'pending',
    InitiatedBy TEXT,
    CurrentStep TEXT,
    InstanceData TEXT,
    StartedAt TEXT NOT NULL,
    CompletedAt TEXT,
    FOREIGN KEY (WorkflowDefinitionId) REFERENCES WorkflowDefinitions(Id) ON DELETE CASCADE
);

-- 工作流任务表
CREATE TABLE IF NOT EXISTS WorkflowTasks (
    Id TEXT PRIMARY KEY,
    WorkflowInstanceId TEXT NOT NULL,
    TaskName TEXT NOT NULL,
    TaskType TEXT NOT NULL DEFAULT 'approval',
    Status TEXT NOT NULL DEFAULT 'pending',
    AssignedTo TEXT,
    TaskData TEXT,
    CreatedAt TEXT NOT NULL,
    CompletedAt TEXT,
    FOREIGN KEY (WorkflowInstanceId) REFERENCES WorkflowInstances(Id) ON DELETE CASCADE
);

-- ============================================
-- 5. 高级功能表
-- ============================================

-- 插件定义表
CREATE TABLE IF NOT EXISTS PluginDefinitions (
    Id TEXT PRIMARY KEY,
    PluginName TEXT NOT NULL,
    PluginCode TEXT NOT NULL UNIQUE,
    Description TEXT,
    PluginType TEXT NOT NULL DEFAULT 'module',
    AssemblyPath TEXT NOT NULL,
    ClassName TEXT NOT NULL,
    IsEnabled INTEGER NOT NULL DEFAULT 0,
    Version INTEGER NOT NULL DEFAULT 1,
    Config TEXT,
    InstalledAt TEXT NOT NULL,
    UpdatedAt TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_PluginDefinitions_PluginCode ON PluginDefinitions(PluginCode);

-- 代码模板表
CREATE TABLE IF NOT EXISTS CodeTemplates (
    Id TEXT PRIMARY KEY,
    TemplateName TEXT NOT NULL UNIQUE,
    TemplateType TEXT NOT NULL,
    TemplateContent TEXT NOT NULL,
    Description TEXT,
    Language TEXT DEFAULT 'csharp',
    IsSystem INTEGER NOT NULL DEFAULT 0,
    CreatedAt TEXT NOT NULL,
    UpdatedAt TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_CodeTemplates_TemplateName ON CodeTemplates(TemplateName);

-- 报表定义表
CREATE TABLE IF NOT EXISTS ReportDefinitions (
    Id TEXT PRIMARY KEY,
    ReportName TEXT NOT NULL UNIQUE,
    ReportType TEXT NOT NULL DEFAULT 'table',
    DataSource TEXT NOT NULL,
    Columns TEXT,
    Filters TEXT,
    ChartConfig TEXT,
    Description TEXT,
    IsPublic INTEGER NOT NULL DEFAULT 0,
    CreatedBy TEXT,
    CreatedAt TEXT NOT NULL,
    UpdatedAt TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_ReportDefinitions_ReportName ON ReportDefinitions(ReportName);

-- 通知表
CREATE TABLE IF NOT EXISTS Notifications (
    Id TEXT PRIMARY KEY,
    Title TEXT NOT NULL,
    Content TEXT NOT NULL,
    NotificationType TEXT NOT NULL DEFAULT 'info',
    Channel TEXT NOT NULL DEFAULT 'system',
    RecipientId TEXT,
    RecipientEmail TEXT,
    RecipientPhone TEXT,
    IsRead INTEGER NOT NULL DEFAULT 0,
    ReadAt TEXT,
    CreatedAt TEXT NOT NULL,
    ExpiresAt TEXT
);

-- 租户表
CREATE TABLE IF NOT EXISTS Tenants (
    Id TEXT PRIMARY KEY,
    TenantName TEXT NOT NULL,
    TenantCode TEXT NOT NULL UNIQUE,
    Domain TEXT,
    Description TEXT,
    Status TEXT NOT NULL DEFAULT 'active',
    Config TEXT,
    MaxUsers INTEGER NOT NULL DEFAULT 100,
    CreatedAt TEXT NOT NULL,
    UpdatedAt TEXT NOT NULL,
    ExpiresAt TEXT
);

CREATE INDEX IF NOT EXISTS IX_Tenants_TenantCode ON Tenants(TenantCode);

-- ============================================
-- 6. 初始数据
-- ============================================

-- 插入默认角色
INSERT OR IGNORE INTO Roles (Id, RoleName, RoleCode, Description, CreatedAt) VALUES
    ('11111111-1111-1111-1111-111111111111', '超级管理员', 'super_admin', '系统超级管理员', datetime('now')),
    ('22222222-2222-2222-2222-222222222222', '管理员', 'admin', '系统管理员', datetime('now')),
    ('33333333-3333-3333-3333-333333333333', '开发者', 'developer', '开发者', datetime('now')),
    ('44444444-4444-4444-4444-444444444444', '普通用户', 'user', '普通用户', datetime('now'));

-- 插入默认权限
INSERT OR IGNORE INTO Permissions (Id, PermissionName, PermissionCode, Resource, Action, Description, CreatedAt) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '用户创建', 'user:create', 'user', 'create', '创建用户', datetime('now')),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '用户查看', 'user:read', 'user', 'read', '查看用户', datetime('now')),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '用户更新', 'user:update', 'user', 'update', '更新用户', datetime('now')),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', '用户删除', 'user:delete', 'user', 'delete', '删除用户', datetime('now'));

-- 插入示例实体
INSERT OR IGNORE INTO EntityDefinitions (Id, EntityName, TableName, Description, IsSystem, IsActive, CreatedAt, UpdatedAt) VALUES
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '产品', 'products', '产品信息表', 0, 1, datetime('now'), datetime('now'));

-- 插入示例表单
INSERT OR IGNORE INTO FormDefinitions (Id, FormName, Description, IsPublished, CreatedAt, UpdatedAt) VALUES
    ('ffffffff-ffff-ffff-ffff-ffffffffffff', '用户注册表单', '用户注册信息采集', 1, datetime('now'), datetime('now'));

-- 插入示例工作流
INSERT OR IGNORE INTO WorkflowDefinitions (Id, WorkflowName, Description, IsActive, CreatedAt, UpdatedAt) VALUES
    ('00000000-0000-0000-0000-000000000000', '审批流程', '通用审批流程', 1, datetime('now'), datetime('now'));

-- 插入示例插件
INSERT OR IGNORE INTO PluginDefinitions (Id, PluginName, PluginCode, Description, PluginType, AssemblyPath, ClassName, IsEnabled, Version, InstalledAt, UpdatedAt) VALUES
    ('11111111-2222-3333-4444-555555555555', '数据导出插件', 'data-export', '导出数据到Excel', 'module', 'plugins/DataExport.dll', 'DataExportPlugin', 1, 1, datetime('now'), datetime('now'));

-- 插入示例报表
INSERT OR IGNORE INTO ReportDefinitions (Id, ReportName, ReportType, DataSource, Description, IsPublic, CreatedAt, UpdatedAt) VALUES
    ('66666666-6666-6666-6666-666666666666', '用户统计报表', 'table', 'SELECT * FROM Users', '用户数据统计', 1, datetime('now'), datetime('now'));

-- ============================================
-- 数据库初始化完成
-- ============================================