-- ============================================
-- 数据库索引优化脚本 (P3-03)
-- 创建时间: 2026-03-25
-- 维护部门: 兵部
-- ============================================

-- 说明：
-- 1. 此脚本为SQLite数据库优化索引
-- 2. 建议在低峰期执行
-- 3. 执行前请备份数据库
-- 4. 可以分批执行，每次执行2-3个索引创建

-- ============================================
-- 1. Users表索引优化
-- ============================================

-- 状态筛选索引（高频查询）
CREATE INDEX IF NOT EXISTS IX_Users_Status ON Users(Status);

-- 软删除索引
CREATE INDEX IF NOT EXISTS IX_Users_IsDeleted ON Users(IsDeleted);

-- 租户筛选索引（多租户场景）
CREATE INDEX IF NOT EXISTS IX_Users_TenantId ON Users(TenantId);

-- 创建时间索引（排序优化）
CREATE INDEX IF NOT EXISTS IX_Users_CreatedAt ON Users(CreatedAt DESC);

-- 最后登录时间索引
CREATE INDEX IF NOT EXISTS IX_Users_LastLoginAt ON Users(LastLoginAt DESC);

-- ============================================
-- 2. EntityDefinitions表索引优化
-- ============================================

-- 活跃状态筛选（高频查询）
CREATE INDEX IF NOT EXISTS IX_EntityDefinitions_IsActive ON EntityDefinitions(IsActive);

-- 系统标识索引
CREATE INDEX IF NOT EXISTS IX_EntityDefinitions_IsSystem ON EntityDefinitions(IsSystem);

-- 创建时间索引（排序优化）
CREATE INDEX IF NOT EXISTS IX_EntityDefinitions_CreatedAt ON EntityDefinitions(CreatedAt);

-- ============================================
-- 3. FieldDefinitions表索引优化
-- ============================================

-- 显示顺序索引（组合索引）
CREATE INDEX IF NOT EXISTS IX_FieldDefinitions_DisplayOrder ON FieldDefinitions(EntityDefinitionId, DisplayOrder);

-- ============================================
-- 4. DynamicData表索引优化
-- ============================================

-- 实体ID索引（高频查询）
CREATE INDEX IF NOT EXISTS IX_DynamicData_EntityDefinitionId ON DynamicData(EntityDefinitionId);

-- 软删除索引
CREATE INDEX IF NOT EXISTS IX_DynamicData_IsDeleted ON DynamicData(IsDeleted);

-- 创建时间索引（排序优化）
CREATE INDEX IF NOT EXISTS IX_DynamicData_CreatedAt ON DynamicData(CreatedAt DESC);

-- 创建人索引
CREATE INDEX IF NOT EXISTS IX_DynamicData_CreatedBy ON DynamicData(CreatedBy);

-- 组合索引：实体ID + 创建时间（最常用查询模式）
CREATE INDEX IF NOT EXISTS IX_DynamicData_Entity_CreatedAt ON DynamicData(EntityDefinitionId, CreatedAt DESC);

-- ============================================
-- 5. FormDefinitions表索引优化
-- ============================================

-- 活跃状态筛选
CREATE INDEX IF NOT EXISTS IX_FormDefinitions_IsActive ON FormDefinitions(IsActive);

-- 创建时间索引
CREATE INDEX IF NOT EXISTS IX_FormDefinitions_CreatedAt ON FormDefinitions(CreatedAt);

-- ============================================
-- 6. WorkflowInstance表索引优化
-- ============================================

-- 工作流定义ID索引
CREATE INDEX IF NOT EXISTS IX_WorkflowInstances_WorkflowDefinitionId ON WorkflowInstances(WorkflowDefinitionId);

-- 状态筛选索引（高频查询）
CREATE INDEX IF NOT EXISTS IX_WorkflowInstances_Status ON WorkflowInstances(Status);

-- 创建时间索引
CREATE INDEX IF NOT EXISTS IX_WorkflowInstances_CreatedAt ON WorkflowInstances(CreatedAt DESC);

-- 组合索引：工作流ID + 状态
CREATE INDEX IF NOT EXISTS IX_WorkflowInstances_Workflow_Status ON WorkflowInstances(WorkflowDefinitionId, Status);

-- ============================================
-- 7. WorkflowTask表索引优化
-- ============================================

-- 实例ID索引
CREATE INDEX IF NOT EXISTS IX_WorkflowTasks_WorkflowInstanceId ON WorkflowTasks(WorkflowInstanceId);

-- 状态筛选索引
CREATE INDEX IF NOT EXISTS IX_WorkflowTasks_Status ON WorkflowTasks(Status);

-- 处理人索引
CREATE INDEX IF NOT EXISTS IX_WorkflowTasks_AssignedTo ON WorkflowTasks(AssignedTo);

-- 组合索引：实例ID + 状态
CREATE INDEX IF NOT EXISTS IX_WorkflowTasks_Instance_Status ON WorkflowTasks(WorkflowInstanceId, Status);

-- ============================================
-- 8. Notifications表索引优化
-- ============================================

-- 用户索引（高频查询：获取用户通知）
CREATE INDEX IF NOT EXISTS IX_Notifications_UserId ON Notifications(UserId);

-- 已读状态索引
CREATE INDEX IF NOT EXISTS IX_Notifications_IsRead ON Notifications(IsRead);

-- 创建时间索引（排序优化）
CREATE INDEX IF NOT EXISTS IX_Notifications_CreatedAt ON Notifications(CreatedAt DESC);

-- 组合索引：用户ID + 已读状态
CREATE INDEX IF NOT EXISTS IX_Notifications_User_IsRead ON Notifications(UserId, IsRead);

-- ============================================
-- 9. Tenant表索引优化
-- ============================================

-- 状态筛选索引
CREATE INDEX IF NOT EXISTS IX_Tenants_Status ON Tenants(Status);

-- 软删除索引
CREATE INDEX IF NOT EXISTS IX_Tenants_IsDeleted ON Tenants(IsDeleted);

-- 创建时间索引
CREATE INDEX IF NOT EXISTS IX_Tenants_CreatedAt ON Tenants(CreatedAt DESC);

-- ============================================
-- 更新统计信息
-- ============================================

-- 更新数据库统计信息（提升查询优化器性能）
ANALYZE;

-- ============================================
-- 验证索引创建
-- ============================================

-- 查询所有索引
SELECT 
    name AS IndexName,
    tbl_name AS TableName,
    sql AS IndexDefinition
FROM sqlite_master
WHERE type = 'index'
    AND name LIKE 'IX_%'
ORDER BY tbl_name, name;

-- ============================================
-- 性能测试查询示例
-- ============================================

-- 测试用户列表查询性能（使用索引：IX_Users_Status, IX_Users_CreatedAt）
EXPLAIN QUERY PLAN
SELECT * FROM Users
WHERE Status = 'active'
ORDER BY CreatedAt DESC
LIMIT 20;

-- 测试实体数据查询性能（使用索引：IX_DynamicData_Entity_CreatedAt）
EXPLAIN QUERY PLAN
SELECT * FROM DynamicData
WHERE EntityDefinitionId = 'xxx'
    AND IsDeleted = 0
ORDER BY CreatedAt DESC
LIMIT 20;

-- 测试通知查询性能（使用索引：IX_Notifications_User_IsRead）
EXPLAIN QUERY PLAN
SELECT * FROM Notifications
WHERE UserId = 'xxx'
    AND IsRead = 0
ORDER BY CreatedAt DESC
LIMIT 20;

-- ============================================
-- 索引使用情况监控（SQLite 3.8.0+）
-- ============================================

-- 注意：SQLite不支持直接查询索引使用情况
-- 建议使用 EXPLAIN QUERY PLAN 分析具体查询

-- ============================================
-- 完成提示
-- ============================================

-- ✅ 索引创建完成
-- ✅ 统计信息已更新
-- ✅ 建议重启应用程序以使查询优化器生效

SELECT '✅ 索引优化完成 - ' || datetime('now') AS Status;
