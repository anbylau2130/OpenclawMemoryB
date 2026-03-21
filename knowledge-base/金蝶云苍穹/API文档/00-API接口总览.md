# 金蝶云苍穹 API 接口文档

## 📋 API概述

金蝶云苍穹提供丰富的API接口，支持REST和GraphQL两种方式。

## 🔗 API网关

### 基础URL
```
https://api.kingdee.com/cosmic/v1
```

### 认证方式
1. **OAuth 2.0**
   - Client Credentials
   - Authorization Code
   - Refresh Token

2. **API Key**
   - AppId + AppSecret
   - 请求签名

## 📚 API分类

### 一、基础数据API

#### 1.1 组织架构
```
GET  /api/organizations          # 获取组织列表
GET  /api/organizations/{id}     # 获取组织详情
POST /api/organizations          # 创建组织
PUT  /api/organizations/{id}     # 更新组织
DEL  /api/organizations/{id}     # 删除组织
```

#### 1.2 用户管理
```
GET  /api/users                  # 获取用户列表
GET  /api/users/{id}             # 获取用户详情
POST /api/users                  # 创建用户
PUT  /api/users/{id}             # 更新用户
DEL  /api/users/{id}             # 删除用户
```

#### 1.3 角色权限
```
GET  /api/roles                  # 获取角色列表
POST /api/roles                  # 创建角色
PUT  /api/roles/{id}             # 更新角色
DEL  /api/roles/{id}             # 删除角色
```

### 二、业务单据API

#### 2.1 单据操作
```
GET  /api/bills                  # 获取单据列表
GET  /api/bills/{billNo}         # 获取单据详情
POST /api/bills                  # 创建单据
PUT  /api/bills/{billNo}         # 更新单据
DEL  /api/bills/{billNo}         # 删除单据
POST /api/bills/{billNo}/submit  # 提交审批
POST /api/bills/{billNo}/audit   # 审批单据
```

#### 2.2 工作流API
```
GET  /api/workflow/instances     # 获取流程实例
POST /api/workflow/start         # 启动流程
POST /api/workflow/approve       # 审批通过
POST /api/workflow/reject        # 审批拒绝
```

### 三、报表查询API

#### 3.1 报表数据
```
POST /api/reports/query          # 查询报表数据
GET  /api/reports/templates      # 获取报表模板
POST /api/reports/export         # 导出报表
```

#### 3.2 数据分析
```
POST /api/analysis/aggregate     # 聚合分析
POST /api/analysis/trend         # 趋势分析
POST /api/analysis/compare       # 对比分析
```

### 四、系统集成API

#### 4.1 数据同步
```
POST /api/sync/push              # 推送数据
GET  /api/sync/pull              # 拉取数据
GET  /api/sync/status            # 同步状态
```

#### 4.2 Webhook
```
POST /api/webhooks               # 创建Webhook
GET  /api/webhooks               # 获取Webhook列表
DEL  /api/webhooks/{id}          # 删除Webhook
```

### 五、文件服务API

#### 5.1 文件上传下载
```
POST /api/files/upload           # 上传文件
GET  /api/files/{fileId}         # 下载文件
DEL  /api/files/{fileId}         # 删除文件
```

## 📝 请求格式

### Headers
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {token}",
  "X-App-Id": "{appId}",
  "X-Timestamp": "{timestamp}",
  "X-Signature": "{signature}"
}
```

### 请求示例
```json
POST /api/bills
{
  "billType": "PO",
  "billDate": "2026-03-19",
  "supplier": "SUP001",
  "items": [
    {
      "material": "MAT001",
      "qty": 100,
      "price": 10.5
    }
  ]
}
```

## 📤 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "billNo": "PO20260319001",
    "status": "created"
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "参数错误",
  "errors": [
    {
      "field": "supplier",
      "message": "供应商不存在"
    }
  ]
}
```

## 🔐 签名算法

### HMAC-SHA256
```python
import hmac
import hashlib

def sign(params, secret):
    sorted_params = sorted(params.items())
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
    signature = hmac.new(
        secret.encode(),
        sign_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature
```

## 📊 限流策略

- **默认限制**: 100次/分钟
- **并发限制**: 10个请求
- **批量限制**: 1000条/次

## 🔄 版本控制

- URL版本: `/api/v1/bills`
- Header版本: `X-API-Version: 1.0`

## 📅 更新记录

- 2026-03-19: 创建API文档框架
