-- Tianyou Platform - Database Initialization
-- Version: 1.0.0
-- Date: 2026-03-24
-- Database: PostgreSQL 15+

-- ============================================
-- 1. 创建数据库和Schema
-- ============================================

-- 创建数据库（需要超级用户权限）
-- CREATE DATABASE tianyou_platform;

-- 连接到数据库后执行
\c tianyou_platform;

-- 创建Schema
CREATE SCHEMA IF NOT EXISTS tianyou;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ============================================
-- 2. 用户与权限模块（6张表）
-- ============================================

-- 用户表
CREATE TABLE tianyou.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'locked')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

COMMENT ON TABLE tianyou.users IS '用户表';
COMMENT ON COLUMN tianyou.users.status IS '状态: active-激活, inactive-未激活, locked-锁定';

-- 角色表
CREATE TABLE tianyou.roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    role_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.roles IS '角色表';

-- 权限表
CREATE TABLE tianyou.permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    permission_code VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(100),
    action VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.permissions IS '权限表';
COMMENT ON COLUMN tianyou.permissions.resource IS '资源类型: form, entity, workflow等';
COMMENT ON COLUMN tianyou.permissions.action IS '操作: create, read, update, delete';

-- 租户表（多租户）
CREATE TABLE tianyou.tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_name VARCHAR(100) UNIQUE NOT NULL,
    tenant_code VARCHAR(50) UNIQUE NOT NULL,
    schema_name VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.tenants IS '租户表（多租户）';

-- 用户角色关联表
CREATE TABLE tianyou.user_roles (
    user_id UUID NOT NULL REFERENCES tianyou.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES tianyou.roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

COMMENT ON TABLE tianyou.user_roles IS '用户角色关联表';

-- 角色权限关联表
CREATE TABLE tianyou.role_permissions (
    role_id UUID NOT NULL REFERENCES tianyou.roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES tianyou.permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

COMMENT ON TABLE tianyou.role_permissions IS '角色权限关联表';

-- 用户租户关联表
CREATE TABLE tianyou.user_tenants (
    user_id UUID NOT NULL REFERENCES tianyou.users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tianyou.tenants(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, tenant_id)
);

COMMENT ON TABLE tianyou.user_tenants IS '用户租户关联表';

-- ============================================
-- 3. 数据模型模块（4张表）
-- ============================================

-- 实体模型表
CREATE TABLE tianyou.entity_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_name VARCHAR(100) NOT NULL,
    entity_code VARCHAR(50) UNIQUE NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    tenant_id UUID REFERENCES tianyou.tenants(id),
    created_by UUID REFERENCES tianyou.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.entity_models IS '实体模型表';

-- 字段定义表
CREATE TABLE tianyou.field_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL REFERENCES tianyou.entity_models(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_code VARCHAR(50) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    is_required BOOLEAN DEFAULT FALSE,
    is_unique BOOLEAN DEFAULT FALSE,
    default_value TEXT,
    validation_rules JSONB,
    properties JSONB,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_id, field_code)
);

COMMENT ON TABLE tianyou.field_definitions IS '字段定义表';
COMMENT ON COLUMN tianyou.field_definitions.field_type IS '字段类型: text, number, date, select等';

-- 索引定义表
CREATE TABLE tianyou.index_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL REFERENCES tianyou.entity_models(id) ON DELETE CASCADE,
    index_name VARCHAR(100) NOT NULL,
    index_type VARCHAR(20) DEFAULT 'btree',
    fields JSONB NOT NULL,
    is_unique BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.index_definitions IS '索引定义表';
COMMENT ON COLUMN tianyou.index_definitions.index_type IS '索引类型: btree, hash, gin等';

-- 关联关系表
CREATE TABLE tianyou.relation_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_entity_id UUID NOT NULL REFERENCES tianyou.entity_models(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES tianyou.entity_models(id) ON DELETE CASCADE,
    relation_type VARCHAR(20) NOT NULL,
    source_field VARCHAR(100),
    target_field VARCHAR(100),
    foreign_key_field VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.relation_definitions IS '关联关系表';
COMMENT ON COLUMN tianyou.relation_definitions.relation_type IS '关联类型: one-to-one, one-to-many, many-to-many';

-- ============================================
-- 4. 表单系统模块（5张表）
-- ============================================

-- 表单模板表
CREATE TABLE tianyou.form_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_name VARCHAR(200) NOT NULL,
    form_code VARCHAR(50) UNIQUE NOT NULL,
    form_type VARCHAR(50) NOT NULL,
    entity_id UUID REFERENCES tianyou.entity_models(id),
    schema JSONB NOT NULL,
    layout JSONB,
    rules JSONB,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    tenant_id UUID REFERENCES tianyou.tenants(id),
    created_by UUID REFERENCES tianyou.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

COMMENT ON TABLE tianyou.form_templates IS '表单模板表';
COMMENT ON COLUMN tianyou.form_templates.form_type IS '表单类型: bill, list, report';

-- 表单字段配置表
CREATE TABLE tianyou.form_fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id UUID NOT NULL REFERENCES tianyou.form_templates(id) ON DELETE CASCADE,
    field_definition_id UUID REFERENCES tianyou.field_definitions(id),
    field_label VARCHAR(200),
    field_type VARCHAR(50) NOT NULL,
    properties JSONB,
    validation JSONB,
    visibility_rules JSONB,
    default_value TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.form_fields IS '表单字段配置表';

-- 表单实例表
CREATE TABLE tianyou.form_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id UUID NOT NULL REFERENCES tianyou.form_templates(id),
    instance_number VARCHAR(100) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    tenant_id UUID REFERENCES tianyou.tenants(id),
    created_by UUID REFERENCES tianyou.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP
);

COMMENT ON TABLE tianyou.form_instances IS '表单实例表';
COMMENT ON COLUMN tianyou.form_instances.status IS '状态: draft, submitted, approved等';

-- 表单操作日志表
CREATE TABLE tianyou.form_audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_instance_id UUID NOT NULL REFERENCES tianyou.form_instances(id) ON DELETE CASCADE,
    operation VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    operated_by UUID REFERENCES tianyou.users(id),
    operated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT
);

COMMENT ON TABLE tianyou.form_audit_logs IS '表单操作日志表';
COMMENT ON COLUMN tianyou.form_audit_logs.operation IS '操作: create, update, submit, approve等';

-- 表单字段值表（用于复杂查询）
CREATE TABLE tianyou.form_field_values (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_instance_id UUID NOT NULL REFERENCES tianyou.form_instances(id) ON DELETE CASCADE,
    field_definition_id UUID NOT NULL REFERENCES tianyou.field_definitions(id),
    field_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.form_field_values IS '表单字段值表（用于复杂查询）';

-- ============================================
-- 5. 工作流系统模块（5张表）
-- ============================================

-- 工作流定义表
CREATE TABLE tianyou.workflow_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_name VARCHAR(200) NOT NULL,
    workflow_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    tenant_id UUID REFERENCES tianyou.tenants(id),
    created_by UUID REFERENCES tianyou.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

COMMENT ON TABLE tianyou.workflow_definitions IS '工作流定义表';
COMMENT ON COLUMN tianyou.workflow_definitions.definition IS '流程定义（BPMN 2.0格式）';

-- 工作流实例表
CREATE TABLE tianyou.workflow_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES tianyou.workflow_definitions(id),
    form_instance_id UUID REFERENCES tianyou.form_instances(id),
    instance_number VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    current_node VARCHAR(100),
    variables JSONB,
    tenant_id UUID REFERENCES tianyou.tenants(id),
    started_by UUID REFERENCES tianyou.users(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

COMMENT ON TABLE tianyou.workflow_instances IS '工作流实例表';
COMMENT ON COLUMN tianyou.workflow_instances.status IS '状态: running, completed, terminated';

-- 工作流历史表
CREATE TABLE tianyou.workflow_histories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_instance_id UUID NOT NULL REFERENCES tianyou.workflow_instances(id) ON DELETE CASCADE,
    node_id VARCHAR(100) NOT NULL,
    node_name VARCHAR(200),
    action VARCHAR(50) NOT NULL,
    operator UUID REFERENCES tianyou.users(id),
    comment TEXT,
    operated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.workflow_histories IS '工作流历史表';
COMMENT ON COLUMN tianyou.workflow_histories.action IS '动作: start, approve, reject, transfer等';

-- 工作流待办表
CREATE TABLE tianyou.workflow_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_instance_id UUID NOT NULL REFERENCES tianyou.workflow_instances(id),
    task_name VARCHAR(200) NOT NULL,
    assignee UUID REFERENCES tianyou.users(id),
    status VARCHAR(50) DEFAULT 'pending',
    due_date TIMESTAMP,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

COMMENT ON TABLE tianyou.workflow_tasks IS '工作流待办表';
COMMENT ON COLUMN tianyou.workflow_tasks.status IS '状态: pending, completed, cancelled';

-- 工作流变量表
CREATE TABLE tianyou.workflow_variables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_instance_id UUID NOT NULL REFERENCES tianyou.workflow_instances(id) ON DELETE CASCADE,
    variable_name VARCHAR(100) NOT NULL,
    variable_value TEXT,
    variable_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workflow_instance_id, variable_name)
);

COMMENT ON TABLE tianyou.workflow_variables IS '工作流变量表';

-- ============================================
-- 6. 插件系统模块（2张表）
-- ============================================

-- 插件定义表
CREATE TABLE tianyou.plugins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plugin_name VARCHAR(200) NOT NULL,
    plugin_code VARCHAR(50) UNIQUE NOT NULL,
    plugin_type VARCHAR(50) NOT NULL,
    description TEXT,
    assembly_name VARCHAR(200),
    class_name VARCHAR(200),
    configuration JSONB,
    is_enabled BOOLEAN DEFAULT TRUE,
    tenant_id UUID REFERENCES tianyou.tenants(id),
    created_by UUID REFERENCES tianyou.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.plugins IS '插件定义表';
COMMENT ON COLUMN tianyou.plugins.plugin_type IS '插件类型: form, list, operation, workflow';

-- 插件绑定表
CREATE TABLE tianyou.plugin_bindings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plugin_id UUID NOT NULL REFERENCES tianyou.plugins(id) ON DELETE CASCADE,
    target_type VARCHAR(50) NOT NULL,
    target_id UUID NOT NULL,
    event_type VARCHAR(50),
    execution_order INTEGER DEFAULT 0,
    configuration JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tianyou.plugin_bindings IS '插件绑定表';
COMMENT ON COLUMN tianyou.plugin_bindings.target_type IS '目标类型: form, field, operation等';
COMMENT ON COLUMN tianyou.plugin_bindings.event_type IS '事件类型: onLoad, onSave, onSubmit等';

-- ============================================
-- 7. 创建索引
-- ============================================

-- 用户表索引
CREATE INDEX idx_users_username ON tianyou.users(username);
CREATE INDEX idx_users_email ON tianyou.users(email);
CREATE INDEX idx_users_status ON tianyou.users(status);
CREATE INDEX idx_users_created_at ON tianyou.users(created_at);

-- 实体模型表索引
CREATE INDEX idx_entity_models_tenant ON tianyou.entity_models(tenant_id);
CREATE INDEX idx_entity_models_code ON tianyou.entity_models(entity_code);
CREATE INDEX idx_entity_models_created_at ON tianyou.entity_models(created_at);

-- 字段定义表索引
CREATE INDEX idx_field_definitions_entity ON tianyou.field_definitions(entity_id);
CREATE INDEX idx_field_definitions_sort ON tianyou.field_definitions(entity_id, sort_order);

-- 表单模板表索引
CREATE INDEX idx_form_templates_tenant ON tianyou.form_templates(tenant_id);
CREATE INDEX idx_form_templates_status ON tianyou.form_templates(status);
CREATE INDEX idx_form_templates_entity ON tianyou.form_templates(entity_id);
CREATE INDEX idx_form_templates_code ON tianyou.form_templates(form_code);

-- 表单实例表索引
CREATE INDEX idx_form_instances_form ON tianyou.form_instances(form_id);
CREATE INDEX idx_form_instances_tenant ON tianyou.form_instances(tenant_id);
CREATE INDEX idx_form_instances_status ON tianyou.form_instances(status);
CREATE INDEX idx_form_instances_created ON tianyou.form_instances(created_at);
CREATE INDEX idx_form_instances_number ON tianyou.form_instances(instance_number);

-- 表单字段值表索引
CREATE INDEX idx_form_field_values_instance ON tianyou.form_field_values(form_instance_id);
CREATE INDEX idx_form_field_values_field ON tianyou.form_field_values(field_definition_id);

-- 工作流定义表索引
CREATE INDEX idx_workflow_definitions_tenant ON tianyou.workflow_definitions(tenant_id);
CREATE INDEX idx_workflow_definitions_status ON tianyou.workflow_definitions(status);
CREATE INDEX idx_workflow_definitions_code ON tianyou.workflow_definitions(workflow_code);

-- 工作流实例表索引
CREATE INDEX idx_workflow_instances_workflow ON tianyou.workflow_instances(workflow_id);
CREATE INDEX idx_workflow_instances_form ON tianyou.workflow_instances(form_instance_id);
CREATE INDEX idx_workflow_instances_status ON tianyou.workflow_instances(status);
CREATE INDEX idx_workflow_instances_started ON tianyou.workflow_instances(started_at);

-- 工作流历史表索引
CREATE INDEX idx_workflow_histories_instance ON tianyou.workflow_histories(workflow_instance_id);
CREATE INDEX idx_workflow_histories_operator ON tianyou.workflow_histories(operator);

-- 工作流待办表索引
CREATE INDEX idx_workflow_tasks_assignee ON tianyou.workflow_tasks(assignee);
CREATE INDEX idx_workflow_tasks_status ON tianyou.workflow_tasks(status);
CREATE INDEX idx_workflow_tasks_due ON tianyou.workflow_tasks(due_date);

-- 插件表索引
CREATE INDEX idx_plugins_tenant ON tianyou.plugins(tenant_id);
CREATE INDEX idx_plugins_type ON tianyou.plugins(plugin_type);
CREATE INDEX idx_plugins_enabled ON tianyou.plugins(is_enabled);

-- 插件绑定表索引
CREATE INDEX idx_plugin_bindings_plugin ON tianyou.plugin_bindings(plugin_id);
CREATE INDEX idx_plugin_bindings_target ON tianyou.plugin_bindings(target_type, target_id);

-- ============================================
-- 8. 插入初始数据
-- ============================================

-- 插入默认租户
INSERT INTO tianyou.tenants (tenant_name, tenant_code, schema_name, status)
VALUES ('Default Tenant', 'default', 'public', 'active');

-- 插入默认角色
INSERT INTO tianyou.roles (role_name, role_code, description) VALUES
('超级管理员', 'super_admin', '系统超级管理员，拥有所有权限'),
('管理员', 'admin', '系统管理员，拥有大部分权限'),
('开发者', 'developer', '开发者，可以创建和编辑应用'),
('普通用户', 'user', '普通用户，只能使用应用');

-- 插入默认权限
INSERT INTO tianyou.permissions (permission_name, permission_code, resource, action, description) VALUES
-- 用户管理权限
('用户创建', 'user:create', 'user', 'create', '创建用户'),
('用户查看', 'user:read', 'user', 'read', '查看用户'),
('用户更新', 'user:update', 'user', 'update', '更新用户'),
('用户删除', 'user:delete', 'user', 'delete', '删除用户'),
-- 实体管理权限
('实体创建', 'entity:create', 'entity', 'create', '创建实体'),
('实体查看', 'entity:read', 'entity', 'read', '查看实体'),
('实体更新', 'entity:update', 'entity', 'update', '更新实体'),
('实体删除', 'entity:delete', 'entity', 'delete', '删除实体'),
-- 表单管理权限
('表单创建', 'form:create', 'form', 'create', '创建表单'),
('表单查看', 'form:read', 'form', 'read', '查看表单'),
('表单更新', 'form:update', 'form', 'update', '更新表单'),
('表单删除', 'form:delete', 'form', 'delete', '删除表单'),
-- 工作流管理权限
('工作流创建', 'workflow:create', 'workflow', 'create', '创建工作流'),
('工作流查看', 'workflow:read', 'workflow', 'read', '查看工作流'),
('工作流更新', 'workflow:update', 'workflow', 'update', '更新工作流'),
('工作流删除', 'workflow:delete', 'workflow', 'delete', '删除工作流');

-- 插入角色权限关联（超级管理员拥有所有权限）
INSERT INTO tianyou.role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM tianyou.roles r
CROSS JOIN tianyou.permissions p
WHERE r.role_code = 'super_admin';

-- 插入默认管理员用户
INSERT INTO tianyou.users (username, email, password_hash, full_name, status)
VALUES ('admin', 'admin@tianyou.com', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4wq.OZ3M8.9KZ7aC', '系统管理员', 'active');
-- 密码: Admin@123

-- 关联用户和角色
INSERT INTO tianyou.user_roles (user_id, role_id)
SELECT u.id, r.id
FROM tianyou.users u
CROSS JOIN tianyou.roles r
WHERE u.username = 'admin' AND r.role_code = 'super_admin';

-- 关联用户和租户
INSERT INTO tianyou.user_tenants (user_id, tenant_id)
SELECT u.id, t.id
FROM tianyou.users u
CROSS JOIN tianyou.tenants t
WHERE u.username = 'admin' AND t.tenant_code = 'default';

-- ============================================
-- 完成
-- ============================================

-- 显示统计信息
SELECT 
    '用户' AS table_name, COUNT(*) AS count FROM tianyou.users
UNION ALL
SELECT '角色', COUNT(*) FROM tianyou.roles
UNION ALL
SELECT '权限', COUNT(*) FROM tianyou.permissions
UNION ALL
SELECT '租户', COUNT(*) FROM tianyou.tenants;

-- 显示完成信息
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tianyou Platform 数据库初始化完成！';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已创建表: 22张';
    RAISE NOTICE '已创建索引: 30+个';
    RAISE NOTICE '默认用户: admin / Admin@123';
    RAISE NOTICE '========================================';
END $$;