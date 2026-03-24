# ❌ 错误记录

本文件记录三省六部系统运行中的错误、异常和失败案例。

---

## [ERR-20260324-001] Office加入失败-join key无效

**Logged**: 2026-03-24T11:08:00Z
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
所有agents使用`ocj_example_team_01`加入Office时被拒绝，错误信息"接入密钥无效"。

### Error
```
❌ 加入失败：{"msg":"接入密钥无效","ok":false}
```

### Context
- 使用join key: `ocj_example_team_01`
- 所有11个agents均失败
- 时间：2026-03-24 11:08

### Suggested Fix
重新获取有效的join key或确认密钥是否正确。

### Resolution
- **Resolved**: 2026-03-24T12:56:00Z
- **Notes**: join key `ocj_example_team_01` 有效，是其他配置问题。清理state文件后重新启动成功。

---

## [ERR-20260324-002] 进程自动退出

**Logged**: 2026-03-24T11:30:00Z
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
office-push-*.py脚本启动后立即退出，无错误信息。

### Error
```
进程启动后立即退出，ps显示0个进程
```

### Context
- 脚本路径：/root/.openclaw/tang-sansheng/workspace-zhongshu/office-push-*.py
- 使用nohup后台运行
- 日志文件为空

### Suggested Fix
检查脚本的import路径和模块依赖。

### Resolution
- **Resolved**: 2026-03-24T12:56:00Z
- **Notes**: 脚本正常，是之前手动测试时的临时问题。批量启动后正常运行。

---
