# ERRORS - 错误记录

记录命令失败、异常和技术错误,用于问题追踪和预防。

---

## [ERR-20260326-002] file_path_error

**Logged**: 2026-03-26T16:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
为agents创建AGENTS.md时使用了错误的文件路径

### Error
```
错误位置：/root/.openclaw/agents/*/workspace/AGENTS.md（12个文件）
正确位置：/root/.openclaw/tang-sansheng/workspace-*/AGENTS.md（10个文件）
```

### Context
- **操作**：为所有agent添加Self-Improvement强制要求
- **错误**：没有确认agents的实际工作空间位置,想当然地在`agents/*/workspace/`创建文件
- **发现**：用户指出"删除你创建的文件,我的agents的工作空间在tang-sansheng目录下"
- **影响**：
  - 创建了12个错误位置的文件
  - 需要删除并重新创建
  - 浪费了2次提交（9f5f7fe904ee3926 + 42a833a）

### Root Cause
1. **没有验证路径**：创建文件前没有检查agents的实际工作空间位置
2. **想当然**：假设`agents/*/workspace/`是工作空间,实际在`tang-sansheng/workspace-*/`
3. **没有先问**：不确定路径时应该先询问用户

### Suggested Fix
1. **立即修正**：
   ```bash
   # 删除错误位置的文件
   rm -f /root/.openclaw/agents/*/workspace/AGENTS.md
   
   # 在正确位置创建文件
   for workspace_dir in /root/.openclaw/tang-sansheng/workspace-*; do
     cp /tmp/agents_template.md "$workspace_dir/AGENTS.md"
   done
   ```
2. **预防措施**：
   - 创建文件前,先用`ls -la`验证目录结构
   - 不确定路径时,先询问用户
   - 使用`find`命令确认实际文件位置

### Metadata
- Reproducible: yes
- Related Files: `/root/.openclaw/tang-sansheng/workspace-*/AGENTS.md`
- See Also: LRN-20260326-003
- Pattern-Key: path_verification

### Resolution
- **Resolved**: 2026-03-26T16:00:00+08:00
- **Commit**: 42a833a
- **Notes**: 删除错误位置文件,在正确的tang-sansheng目录创建AGENTS.md

---

## [ERR-20260326-001] stock_data_unit_conversion

**Logged**: 2026-03-26T15:35:00+08:00
**Priority**: high
**Status**: resolved
**Area**: backend

### Summary
股票成交量单位转换错误导致量价分析完全错误

### Error
```
错误数据：41454369（新浪API返回，单位：股）
错误理解：41454369手 = 4145.43万手
错误对比：与5日均量407万手对比,得出"放量6.45倍"

正确转换：41454369股 / 100 = 414543.69手 = 41.45万手
正确结论：缩量下跌（正常范围30-50万手）
```

### Context
- **操作**：分析三一重工（600031）今日量价关系
- **数据源**：新浪财经API（`https://hq.sinajs.cn/list=sh600031`）
- **数据字段**：`data[8]` - 成交量（单位：股）
- **错误**：没有验证数据单位就进行计算
- **影响**：给出完全错误的量价分析和投资建议

### Root Cause
1. **API文档缺失**：新浪财经API没有明确说明数据单位
2. **没有验证**：没有与正常范围对比验证
3. **想当然**：看到数字就理解为"手",没有思考

### Suggested Fix
1. **立即修复代码**：
```python
# 所有获取成交量的代码必须添加单位转换
volume_shares = int(data[8])  # 单位：股
volume_lots = volume_shares / 100  # 转换为手
volume_wan_shou = volume_lots / 10000  # 转换为万手

# 验证合理性
assert 1 <= volume_wan_shou <= 200, f"成交量异常：{volume_wan_shou}万手"
```

2. **更新文档**：
在`TOOLS.md`中添加：
```markdown
## 新浪财经API数据单位

- 成交量（data[8]）：单位是**股**,需要除以100转换为手
- 成交额（data[9]）：单位是元
```

3. **添加测试**：
- 测试用例：已知股票的成交量应该在合理范围
- 边界检查：成交量不应为负数或超大值

### Metadata
- Reproducible: yes（如果重复相同错误）
- Related Files: `Knowledge/trading-strategies/code/*.py`
- See Also: LRN-20260326-001（相关的学习记录）

### Resolution
- **Resolved**: 2026-03-26T15:41:00+08:00
- **Commit**: N/A（代码修复待执行）
- **Notes**: 已记录错误并推广到AGENTS.md和SOUL.md

---

## 错误记录格式

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending | in_progress | resolved | wont_fix
**Area**: frontend | backend | infra | tests | docs | config

### Summary
简短描述什么失败了

### Error
```
实际的错误消息或输出
```

### Context
- 尝试的命令/操作
- 使用的输入或参数
- 环境详情（如果相关）

### Root Cause
根本原因分析

### Suggested Fix
如何修复这个问题的具体建议

### Metadata
- Reproducible: yes | no | unknown
- Related Files: 相关文件路径
- See Also: ERR-20250110-001（相关的错误）

### Resolution
- **Resolved**: 2025-01-16T09:00:00Z
- **Commit/PR**: abc123 or #42
- **Notes**: 修复说明
```
