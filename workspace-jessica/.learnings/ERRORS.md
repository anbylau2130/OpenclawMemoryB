# Errors

This file captures command failures, exceptions, and unexpected behaviors to enable continuous improvement.

## Format

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
Brief description of what failed

### Error
```
Actual error message or output
```

### Context
- Command/operation attempted
- Input or parameters used
- Environment details if relevant

### Suggested Fix
If identifiable, what might resolve this

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001

---
```

---

---

## [ERR-20260316-001] github_connection_timeout

**Logged**: 2026-03-16T08:00:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
GitHub访问超时，无法clone或下载仓库

### Error
```
git clone --depth 1 https://github.com/mvanhorn/last30days-skill.git
Process still running...
curl --max-time 30 https://github.com/
curl: (28) Connection timed out after 5001 milliseconds
```

### Context
- 尝试安装 last30days-skill 等技能
- git clone 超时
- curl 下载ZIP也超时
- GitHub API无法访问（无Brave API密钥）

### Suggested Fix
- 建议用户手动下载ZIP文件
- 等网络稳定后再尝试自动安装
- 配置GitHub镜像或代理

### Metadata
- Reproducible: yes
- Related Files: /root/.openclaw/workspace/skills/
- See Also: ERR-20260323-001

---

## [ERR-20260323-001] skill_repository_not_found

**Logged**: 2026-03-23T09:50:00+08:00
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
GitHub仓库 paulshe/china-stock-analysis 不存在

### Error
```
curl "https://api.github.com/repos/paulshe/china-stock-analysis"
响应: Not Found (404)
```

### Context
- 用户请求安装 https://clawhub.ai/paulshe/china-stock-analysis
- ClawHub查询未找到该skill
- 直接查询GitHub API返回404
- 可能是仓库名称错误或已删除

### Suggested Fix
- 确认正确的仓库地址
- 通过搜索找到正确的skill
- 用户手动下载ZIP后安装

### Metadata
- Reproducible: no
- Related Files: /root/.openclaw/workspace/skills/

---

## [ERR-20260323-002] unzip_command_not_found

**Logged**: 2026-03-23T09:55:00+08:00
**Priority**: low
**Status**: resolved
**Area**: infra

### Error
```
unzip -l 5793e67b-d28a-48ce-b95a-d91534c17d6a.zip
sh: 1: unzip: not found
```

### Context
- 用户发送ZIP文件到钉钉
- 尝试用unzip解压查看内容
- 系统中没有安装unzip命令

### Suggested Fix
- 使用Python zipfile模块替代
- 安装unzip工具：apt-get install unzip

### Resolution
- **Resolved**: 2026-03-23T09:56:00Z
- **Method**: 使用 Python zipfile 模块
- **Notes**: `import zipfile` 可以处理ZIP文件，无需unzip

### Metadata
- Reproducible: yes
- Related Files: /root/.openclaw/media/inbound/

---
