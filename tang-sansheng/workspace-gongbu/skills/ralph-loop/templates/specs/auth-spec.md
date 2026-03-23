# 认证系统规格

## 概述

实现用户认证系统，包括登录、注册、登出功能。

---

## 登录表单 (Story-1)

### 功能需求
- 邮箱输入框（验证格式）
- 密码输入框（最小长度 8 位）
- 登录按钮
- 错误提示

### 验收标准
- [ ] 邮箱格式验证（正则表达式）
- [ ] 密码最小长度 8 位
- [ ] 错误提示友好
- [ ] 提交到 /api/login
- [ ] 成功后跳转到首页

### 技术要求
- 表单库：React Hook Form
- 验证库：Zod
- API：fetch
- 路由：Next.js router

### 文件位置
- 组件：src/components/auth/LoginForm.tsx
- API：src/api/auth.ts
- 类型：src/types/auth.ts

---

## 注册表单 (Story-2)

### 功能需求
- 邮箱输入框
- 密码输入框
- 确认密码输入框
- 注册按钮

### 验收标准
- [ ] 邮箱格式验证
- [ ] 密码强度检查
- [ ] 两次密码一致
- [ ] 提交到 /api/register
- [ ] 成功后自动登录

### 文件位置
- 组件：src/components/auth/RegisterForm.tsx

---

## 登出按钮 (Story-3)

### 功能需求
- 显示在导航栏
- 点击后清除 session
- 跳转到登录页

### 验收标准
- [ ] 调用 /api/logout
- [ ] 清除本地存储
- [ ] 跳转到 /login

### 文件位置
- 组件：src/components/auth/LogoutButton.tsx
