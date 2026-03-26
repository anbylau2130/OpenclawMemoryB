# P2-04: 异常信息泄露修复报告

## 修复时间
- 开始：2026-03-25 13:35
- 完成：2026-03-25 13:40
- 用时：约5分钟

## 修复范围

### 1. AuthService.cs
**修复点**：
- 注册失败日志：移除用户名、邮箱记录，改用RequestId
- 登录失败日志：移除用户名记录，改用RequestId
- JWT Token生成失败日志：移除UserId记录，改用RequestId

**修复代码示例**：
```csharp
// 修复前
_logger.LogWarning("注册失败：用户名已存在 - Username: {Username}, IP: 需要从上下文获取", username);

// 修复后
_logger.LogWarning("注册失败：用户名已存在 - RequestId: {RequestId}", Guid.NewGuid().ToString("N")[..8]);
```

### 2. UserService.cs
**修复点**：
- 创建用户：合并用户名/邮箱检查（防止枚举攻击）
- 日志脱敏：所有敏感信息（用户名、邮箱、UserId）改用RequestId

**修复代码示例**：
```csharp
// 修复前（可枚举攻击）
if (await _context.Users.AnyAsync(u => u.Username == username))
    throw new Exception("用户名已存在");
if (await _context.Users.AnyAsync(u => u.Email == email))
    throw new Exception("邮箱已存在");

// 修复后（防止枚举攻击）
bool usernameExists = await _context.Users.AnyAsync(u => u.Username == username);
bool emailExists = await _context.Users.AnyAsync(u => u.Email == email);
if (usernameExists || emailExists)
    throw new Exception("用户名或邮箱已被使用");
```

## 安全改进
1. **防止枚举攻击**：合并用户名/邮箱检查，攻击者无法通过不同错误消息枚举用户
2. **日志脱敏**：移除所有敏感信息记录，改用RequestId追踪
3. **统一错误消息**：使用模糊化错误消息，不暴露内部状态

## 修改文件
- `backend/src/Tianyou.Application/Services/AuthService.cs` - 4处修复
- `backend/src/Tianyou.Application/Services/UserService.cs` - 11处修复

## 验证状态
- ✅ 代码修改完成
- ⏳ 编译测试（需要.NET环境）
- ⏳ 安全审计

## 下一步
- P2-01: 输入验证增强（截止03-27 18:00）
- P2-02: XSS防护实现（截止03-28 18:00）
- P2-03: 权限细分配置（截止03-29 18:00）

---
*尚书省·技术修复组*
*2026-03-25*
