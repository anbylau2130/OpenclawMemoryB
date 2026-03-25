# Tianyou - 企业级低代码开发平台

## 项目概述

**项目名称**: Tianyou（天佑）
**版本**: 1.0.0
**开发周期**: 9个月（Phase 1: 120天）
**技术栈**: .NET 8 LTS + Blazor + PostgreSQL 15+

## 项目结构

```
tianyou-platform/
├── backend/                    # 后端（.NET 8）
│   ├── src/
│   │   ├── Tianyou.Api/       # WebAPI层
│   │   ├── Tianyou.Application/ # 应用层
│   │   ├── Tianyou.Domain/    # 领域层
│   │   └── Tianyou.Infrastructure/ # 基础设施层
│   ├── tests/
│   │   ├── Tianyou.UnitTests/ # 单元测试
│   │   └── Tianyou.IntegrationTests/ # 集成测试
│   └── Tianyou.sln
├── frontend/                   # 前端（Blazor）
│   ├── Tianyou.Web/           # Blazor WebAssembly
│   └── Tianyou.Shared/        # 共享组件
├── database/                   # 数据库脚本
│   ├── init/                  # 初始化脚本
│   └── migrations/            # 迁移脚本
├── docker/                     # Docker配置
├── docs/                       # 文档
└── README.md
```

## 快速开始

### 环境要求

- .NET 8 SDK
- PostgreSQL 15+
- Redis 7+
- Docker (可选)

### 安装步骤

```bash
# 克隆项目
git clone <repository-url>
cd tianyou-platform

# 还原依赖
cd backend
dotnet restore

# 创建数据库
createdb tianyou_platform

# 执行数据库脚本
psql -d tianyou_platform -f ../database/init/001_create_tables.sql

# 运行项目
dotnet run --project src/Tianyou.Api
```

## 核心功能

### Phase 1: MVP核心（120天）
- ✅ 用户认证授权（JWT + RBAC）
- ✅ 单据建模
- ✅ 数据模型编辑器
- ✅ 表单设计器
- ✅ 列表页面
- ✅ REST API（56个接口）
- ✅ 基础插件系统

### Phase 2: 高级功能（60天）
- 工作流引擎
- 报表系统
- 数据集成

### Phase 3: 多平台（90天）
- 桌面端（Blazor MAUI）
- 移动端（Blazor Hybrid）
- 离线功能

## API文档

启动项目后访问: `http://localhost:5000/swagger`

## 技术栈

**后端**:
- .NET 8 LTS
- Entity Framework Core 8
- PostgreSQL 15
- Redis 7
- RabbitMQ 3.12

**前端**:
- Blazor WebAssembly
- MudBlazor
- Blazor MAUI

## 开发团队

- 产品经理: 1人
- 架构师: 1人
- 后端开发: 3人
- 前端开发: 3人
- UI/UX设计师: 1人
- 测试工程师: 2人
- DevOps工程师: 1人

## 许可证

Copyright © 2026 Tianyou Platform

---

**开发状态**: 🚧 Phase 1 开发中
**最后更新**: 2026-03-24 22:45