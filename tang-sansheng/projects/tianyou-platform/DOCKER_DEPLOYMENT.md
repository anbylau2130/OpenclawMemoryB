# Docker 部署指南

## 快速启动

### 1. 环境准备

```bash
# 复制环境变量配置文件
cp .env.example .env

# 编辑配置（可选）
vim .env
```

### 2. 构建并启动服务

```bash
# 构建所有服务
docker-compose build

# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问服务

- **前端应用**: http://localhost:8080
- **API服务**: http://localhost:5000
- **API健康检查**: http://localhost:5000/health
- **RabbitMQ管理界面**: http://localhost:15672 (admin/admin@123)

## 服务架构

```
┌─────────────────────────────────────────────────┐
│                  Nginx (8080)                    │
│              Blazor WebAssembly                 │
└─────────────────┬───────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────┐
│            ASP.NET Core API (5000)              │
│              Health Check: /health              │
└───┬──────────┬──────────┬──────────────────────┘
    │          │          │
    ↓          ↓          ↓
┌────────┐ ┌────────┐ ┌──────────┐
│PostgreSQL│ │ Redis  │ │ RabbitMQ │
│  (5432) │ │ (6379) │ │  (5672)  │
└─────────┘ └────────┘ └──────────┘
```

## 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 停止并删除所有容器、网络、卷
docker-compose down -v
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f tianyou-api
docker-compose logs -f tianyou-web
docker-compose logs -f postgres
```

### 进入容器

```bash
# 进入API容器
docker-compose exec tianyou-api /bin/bash

# 进入PostgreSQL容器
docker-compose exec postgres /bin/sh

# 进入Redis容器
docker-compose exec redis /bin/sh
```

### 数据库操作

```bash
# 连接PostgreSQL
docker-compose exec postgres psql -U tianyou_admin -d tianyou_platform

# 备份数据库
docker-compose exec postgres pg_dump -U tianyou_admin tianyou_platform > backup.sql

# 恢复数据库
cat backup.sql | docker-compose exec -T postgres psql -U tianyou_admin tianyou_platform
```

## 性能优化

### 资源限制

已在 `docker-compose.yml` 中配置资源限制：

- **PostgreSQL**: CPU 1核, 内存 512MB
- **Redis**: CPU 0.5核, 内存 256MB
- **RabbitMQ**: CPU 1核, 内存 512MB
- **API**: CPU 2核, 内存 1GB
- **Web**: CPU 0.5核, 内存 256MB

### 日志轮转

已配置日志轮转策略：

- 最大文件大小: 10MB-50MB
- 最大文件数量: 3-5个

## 健康检查

所有服务都配置了健康检查：

- **PostgreSQL**: `pg_isready`
- **Redis**: `redis-cli ping`
- **RabbitMQ**: `rabbitmq-diagnostics ping`
- **API**: `curl http://localhost:80/health`
- **Web**: `curl http://localhost:80/health`

## 生产环境建议

### 1. 安全加固

- 修改默认密码
- 使用 Docker Secrets 管理敏感信息
- 配置防火墙规则
- 启用 HTTPS

### 2. 监控

- 集成 Prometheus + Grafana
- 配置日志聚合（ELK Stack）
- 设置告警规则

### 3. 备份策略

- 定期备份 PostgreSQL
- 备份 Redis 持久化数据
- 配置卷快照

### 4. 高可用

- 使用 Docker Swarm 或 Kubernetes
- 配置负载均衡
- 数据库主从复制

## 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker-compose logs <service-name>

# 查看容器状态
docker-compose ps

# 检查资源使用
docker stats
```

### 数据库连接失败

```bash
# 检查数据库是否运行
docker-compose ps postgres

# 测试数据库连接
docker-compose exec postgres pg_isready -U tianyou_admin

# 检查网络
docker network inspect tianyou-network
```

### API无法访问

```bash
# 检查API容器日志
docker-compose logs tianyou-api

# 测试健康检查
curl http://localhost:5000/health

# 进入容器排查
docker-compose exec tianyou-api /bin/bash
```

## 版本管理

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose build
docker-compose up -d
```

### 回滚版本

```bash
# 停止服务
docker-compose down

# 使用指定版本镜像
docker-compose up -d tianyou-api:v1.0.0
```

## 开发环境

### 本地开发

```bash
# 仅启动数据库服务
docker-compose up -d postgres redis rabbitmq

# 本地运行API
cd backend
dotnet run --project src/Tianyou.Api

# 本地运行前端
cd frontend/Tianyou.Web
dotnet run
```

### 热重载

```bash
# 挂载本地代码到容器
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

**维护部门**: 兵部
**更新时间**: 2026-03-25
**版本**: v1.0
