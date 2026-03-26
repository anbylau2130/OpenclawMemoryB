# 天佑平台前端 - Blazor WebAssembly

## 📋 项目概述

这是天佑低代码平台的前端项目，使用 Blazor WebAssembly 技术栈开发。

## 🚀 快速开始

### 前置要求
- .NET 8.0 SDK
- 后端API运行中（http://localhost:5000）

### 启动前端
```bash
cd /root/.openclaw/tang-sansheng/projects/tianyou-platform/frontend/Tianyou.Web
export PATH="/root/.dotnet:$PATH"
dotnet run --urls="http://0.0.0.0:5173"
```

### 访问地址
- 前端：http://localhost:5173
- 后端API：http://localhost:5000

## 📦 已实现功能

### ✅ 用户认证
- 用户注册
- 用户登录
- JWT Token认证
- 自动Token存储（LocalStorage）

### ✅ 页面列表
1. **首页（/）** - 显示用户信息
2. **登录页（/login）** - 用户登录
3. **注册页（/register）** - 用户注册

## 🔧 API接口

### 1. 用户注册
```
POST /api/auth/register
Content-Type: application/json

{
  "Username": "testuser",
  "Email": "test@example.com",
  "Password": "Test123456",
  "FullName": "测试用户"
}
```

### 2. 用户登录
```
POST /api/auth/login
Content-Type: application/json

{
  "Username": "testuser",
  "Password": "Test123456"
}
```

### 3. 获取用户信息
```
GET /api/auth/me
Authorization: Bearer {token}
```

## 📁 项目结构

```
Tianyou.Web/
├── Pages/
│   ├── Home.razor          # 首页（用户信息展示）
│   ├── Login.razor         # 登录页面
│   └── Register.razor      # 注册页面
├── Services/
│   └── AuthService.cs      # 认证服务（JWT）
├── Layout/
│   ├── MainLayout.razor    # 主布局
│   └── NavMenu.razor       # 导航菜单
├── wwwroot/
│   └── appsettings.json    # 配置文件（API地址）
├── Program.cs              # 程序入口
└── App.razor               # 根组件
```

## 🧪 测试账号

### 注册测试
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"Username":"testuser","Email":"test@example.com","Password":"Test123456","FullName":"测试用户"}'
```

### 登录测试
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"Username":"testuser","Password":"Test123456"}'
```

## 🎯 技术栈

- **前端框架**: Blazor WebAssembly (.NET 8.0)
- **UI框架**: Bootstrap 5
- **认证方式**: JWT Token
- **存储方式**: LocalStorage
- **API通信**: HttpClient

## ⚙️ 配置说明

### API基础地址配置
文件：`wwwroot/appsettings.json`
```json
{
  "ApiBaseUrl": "http://localhost:5000"
}
```

## 📝 开发说明

### 添加新页面
1. 在 `Pages/` 目录创建 `.razor` 文件
2. 添加 `@page` 指令指定路由
3. 在 `NavMenu.razor` 中添加导航链接

### 调用API
```csharp
@inject AuthService AuthService

@code {
    private async Task CallApi()
    {
        var result = await AuthService.LoginAsync(username, password);
        if (result.Success)
        {
            // 登录成功
        }
    }
}
```

## 🐛 已知问题

暂无

## 📅 更新日志

### 2026-03-25 06:48
- ✅ 创建Blazor WebAssembly项目
- ✅ 实现用户注册页面
- ✅ 实现用户登录页面
- ✅ 实现首页用户信息展示
- ✅ 实现JWT认证服务
- ✅ 前后端联调测试成功

## 👥 开发团队

- **部门**: 工部（由尚书省派发）
- **上级**: 中书省（主Agent）

---

_更新时间: 2026-03-25 06:48_
_状态: ✅ MVP完成_
_版本: v1.0.0_
