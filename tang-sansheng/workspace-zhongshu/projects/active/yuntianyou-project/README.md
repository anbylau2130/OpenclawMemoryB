# 云天佑 - 低代码开发平台

## 项目概述

云天佑是一个基于DDD（领域驱动设计）和微服务架构的低代码开发平台，旨在帮助用户快速构建企业级业务应用。

## 核心功能

### 🎯 低代码平台（核心）
- 可视化表单设计器
- 数据模型可视化编辑
- 工作流配置器
- 代码自动生成器
- 拖拽式页面设计

### 👥 用户管理
- 用户注册、登录、注销
- 角色和权限管理（RBAC）
- 用户组管理
- 多租户支持

### 📋 项目管理
- 项目创建、编辑、删除
- 项目成员管理
- 项目进度跟踪
- 项目模板

### ✅ 任务分配
- 任务创建和分配
- 任务状态管理
- 任务优先级设置
- 任务看板

### 🔌 API管理
- API自动生成
- API文档管理
- API测试工具
- API版本控制

### 🚀 部署管理
- 一键部署
- 版本管理
- 环境配置
- 监控告警

## 技术架构

### 后端
- **框架**: ASP.NET Core 8.0
- **语言**: C# 12
- **数据库**: PostgreSQL 15+
- **ORM**: Entity Framework Core 8.0
- **缓存**: Redis
- **消息队列**: RabbitMQ（可选）
- **API**: RESTful + GraphQL（可选）

### 前端
- **框架**: React 18+
- **语言**: TypeScript 5+
- **UI库**: Ant Design 5.x / Material-UI
- **状态管理**: Redux Toolkit / Zustand
- **可视化设计器**: React Flow + Custom Components

### 部署
- **容器化**: Docker
- **编排**: Docker Compose / Kubernetes（可选）
- **反向代理**: Nginx
- **监控**: Prometheus + Grafana

## 开发计划

### Phase 1: 基础架构（今晚 23:20 - 01:00）
- [ ] 创建.NET 8项目结构
- [ ] 配置PostgreSQL数据库
- [ ] 实现DDD基础架构
- [ ] 创建核心领域模型

### Phase 2: 低代码核心（01:00 - 03:00）
- [ ] 表单设计器引擎
- [ ] 数据模型编辑器
- [ ] 代码生成器
- [ ] 页面设计器

### Phase 3: 业务功能（03:00 - 05:00）
- [ ] 用户管理模块
- [ ] 项目管理模块
- [ ] 任务管理模块
- [ ] API管理模块

### Phase 4: 前端开发（05:00 - 07:00）
- [ ] React项目初始化
- [ ] 基础布局和路由
- [ ] 低代码设计器UI
- [ ] 业务功能页面

### Phase 5: 集成测试（07:00 - 08:00）
- [ ] API集成测试
- [ ] 前端E2E测试
- [ ] 性能测试
- [ ] 安全测试

### Phase 6: 部署上线（08:00 - 09:00）
- [ ] Docker镜像构建
- [ ] 环境配置
- [ ] 部署到生产环境
- [ ] 监控配置

## 目录结构

```
yuntianyou-project/
├── backend/                        # 后端代码
│   ├── src/
│   │   ├── YTY.Domain/            # 领域层
│   │   ├── YTY.Application/       # 应用层
│   │   ├── YTY.Infrastructure/    # 基础设施层
│   │   └── YTY.Api/               # API层
│   ├── tests/
│   ├── YTY.sln
│   └── README.md
├── frontend/                       # 前端代码
│   ├── src/
│   │   ├── components/            # React组件
│   │   ├── pages/                 # 页面
│   │   ├── services/              # API服务
│   │   ├── stores/                # 状态管理
│   │   └── designer/              # 低代码设计器
│   ├── public/
│   ├── package.json
│   └── README.md
├── docker/                         # Docker配置
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── .env.example
├── docs/                           # 文档
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── ARCHITECTURE.md
└── README.md
```

## 成功标准

### 必须完成
- ✅ 低代码表单设计器可用
- ✅ 用户可以注册和登录
- ✅ 用户可以创建和管理项目
- ✅ 基本API可用且有文档
- ✅ 系统可以成功部署

### 加分项
- 🌟 工作流配置器可用
- 🌟 代码自动生成功能
- 🌟 完整的监控和日志
- 🌟 用户培训和文档

## 注意事项

1. **时间紧迫**: 必须按照最优方案执行
2. **PostgreSQL**: 使用PostgreSQL而不是MySQL
3. **低代码优先**: 低代码平台是核心功能
4. **质量保证**: 不因时间紧而降低质量
5. **沟通机制**: 每阶段汇报进度

## 下一步行动

1. ✅ 创建.NET 8项目结构
2. ⏳ 配置PostgreSQL数据库
3. ⏳ 实现DDD基础架构
4. ⏳ 开发低代码核心功能
5. ⏳ 前端开发
6. ⏳ 集成测试
7. ⏳ 部署上线
