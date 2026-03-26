# 数据库索引优化方案 (P3-03)

## 优化目标
- 提升高频查询性能
- 优化外键关联查询
- 加速排序和筛选操作

## 当前索引分析

### 已有索引
✅ Users表：Username(UNIQUE), Email(UNIQUE)
✅ Roles表：RoleName(UNIQUE), RoleCode(UNIQUE)
✅ EntityDefinitions表：EntityName(UNIQUE), TableName(UNIQUE)
✅ FieldDefinitions表：EntityDefinitionId+FieldName(UNIQUE)
✅ FormDefinitions表：FormName(UNIQUE)
✅ WorkflowDefinitions表：WorkflowName(UNIQUE)
✅ PluginDefinitions表：PluginCode(UNIQUE)
✅ Tenant表：TenantCode(UNIQUE)

## 新增索引方案

### 1. Users表优化
```sql
-- 状态筛选索引（高频查询）
CREATE INDEX IX_Users_Status ON Users(Status);

-- 软删除索引
CREATE INDEX IX_Users_IsDeleted ON Users(IsDeleted);

-- 租户筛选索引（多租户场景）
CREATE INDEX IX_Users_TenantId ON Users(TenantId);

-- 创建时间索引（排序优化）
CREATE INDEX IX_Users_CreatedAt ON Users(CreatedAt DESC);

-- 最后登录时间索引
CREATE INDEX IX_Users_LastLoginAt ON Users(LastLoginAt DESC);
```

### 2. EntityDefinitions表优化
```sql
-- 活跃状态筛选（高频查询）
CREATE INDEX IX_EntityDefinitions_IsActive ON EntityDefinitions(IsActive);

-- 系统标识索引
CREATE INDEX IX_EntityDefinitions_IsSystem ON EntityDefinitions(IsSystem);

-- 创建时间索引（排序优化）
CREATE INDEX IX_EntityDefinitions_CreatedAt ON EntityDefinitions(CreatedAt);
```

### 3. FieldDefinitions表优化
```sql
-- 外键索引（已存在，但需确认）
-- CREATE INDEX IX_FieldDefinitions_EntityDefinitionId ON FieldDefinitions(EntityDefinitionId);

-- 显示顺序索引
CREATE INDEX IX_FieldDefinitions_DisplayOrder ON FieldDefinitions(EntityDefinitionId, DisplayOrder);
```

### 4. DynamicData表优化
```sql
-- 实体ID索引（高频查询）
CREATE INDEX IX_DynamicData_EntityDefinitionId ON DynamicData(EntityDefinitionId);

-- 软删除索引
CREATE INDEX IX_DynamicData_IsDeleted ON DynamicData(IsDeleted);

-- 创建时间索引（排序优化）
CREATE INDEX IX_DynamicData_CreatedAt ON DynamicData(CreatedAt DESC);

-- 创建人索引
CREATE INDEX IX_DynamicData_CreatedBy ON DynamicData(CreatedBy);

-- 组合索引：实体ID + 创建时间（最常用查询模式）
CREATE INDEX IX_DynamicData_Entity_CreatedAt ON DynamicData(EntityDefinitionId, CreatedAt DESC);
```

### 5. FormDefinitions表优化
```sql
-- 活跃状态筛选
CREATE INDEX IX_FormDefinitions_IsActive ON FormDefinitions(IsActive);

-- 创建时间索引
CREATE INDEX IX_FormDefinitions_CreatedAt ON FormDefinitions(CreatedAt);
```

### 6. WorkflowInstance表优化
```sql
-- 工作流定义ID索引
CREATE INDEX IX_WorkflowInstances_WorkflowDefinitionId ON WorkflowInstances(WorkflowDefinitionId);

-- 状态筛选索引（高频查询）
CREATE INDEX IX_WorkflowInstances_Status ON WorkflowInstances(Status);

-- 创建时间索引
CREATE INDEX IX_WorkflowInstances_CreatedAt ON WorkflowInstances(CreatedAt DESC);

-- 组合索引：工作流ID + 状态
CREATE INDEX IX_WorkflowInstances_Workflow_Status ON WorkflowInstances(WorkflowDefinitionId, Status);
```

### 7. WorkflowTask表优化
```sql
-- 实例ID索引
CREATE INDEX IX_WorkflowTasks_WorkflowInstanceId ON WorkflowTasks(WorkflowInstanceId);

-- 状态筛选索引
CREATE INDEX IX_WorkflowTasks_Status ON WorkflowTasks(Status);

-- 处理人索引
CREATE INDEX IX_WorkflowTasks_AssignedTo ON WorkflowTasks(AssignedTo);

-- 组合索引：实例ID + 状态
CREATE INDEX IX_WorkflowTasks_Instance_Status ON WorkflowTasks(WorkflowInstanceId, Status);
```

### 8. Notifications表优化
```sql
-- 用户索引（高频查询：获取用户通知）
CREATE INDEX IX_Notifications_UserId ON Notifications(UserId);

-- 已读状态索引
CREATE INDEX IX_Notifications_IsRead ON Notifications(IsRead);

-- 创建时间索引（排序优化）
CREATE INDEX IX_Notifications_CreatedAt ON Notifications(CreatedAt DESC);

-- 组合索引：用户ID + 已读状态
CREATE INDEX IX_Notifications_User_IsRead ON Notifications(UserId, IsRead);
```

### 9. Tenant表优化
```sql
-- 状态筛选索引
CREATE INDEX IX_Tenants_Status ON Tenants(Status);

-- 软删除索引
CREATE INDEX IX_Tenants_IsDeleted ON Tenants(IsDeleted);

-- 创建时间索引
CREATE INDEX IX_Tenants_CreatedAt ON Tenants(CreatedAt DESC);
```

## 性能预期

### 查询性能提升
- **用户列表查询**：30-50% 提升（状态筛选 + 排序优化）
- **实体数据查询**：50-70% 提升（组合索引优化）
- **工作流实例查询**：40-60% 提升（状态筛选优化）
- **通知查询**：60-80% 提升（用户 + 已读状态组合索引）

### 索引维护成本
- **写入性能影响**：约5-10%（新增索引）
- **存储空间增加**：约15-20%（索引占用）

## 实施步骤

1. ✅ 创建索引SQL脚本
2. ⏳ 在测试环境验证性能提升
3. ⏳ 在生产环境执行索引创建
4. ⏳ 监控查询性能变化

## 注意事项

⚠️ **重要提示**：
- SQLite不支持并发写入，索引创建期间会锁定表
- 建议在低峰期执行索引创建
- 对于大型表（>10万条记录），索引创建可能需要较长时间
- 建议分批创建索引，每次创建2-3个

## 后续优化建议

1. **定期索引维护**
   - 执行 `ANALYZE` 更新统计信息
   - 监控索引使用率，删除低效索引

2. **查询优化**
   - 使用 `EXPLAIN QUERY PLAN` 分析查询计划
   - 避免 `SELECT *`，只查询必要字段

3. **数据库升级**
   - 考虑升级到 PostgreSQL（支持更强大的索引功能）
   - 考虑使用 Redis 缓存热点数据

---

**任务状态**：P3-03 ✅ 已完成
**创建时间**：2026-03-25
**维护部门**：兵部
