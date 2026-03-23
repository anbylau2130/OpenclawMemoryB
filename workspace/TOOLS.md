# TOOLS.md - 本地笔记

技能定义工具_如何_工作。这个文件是给_你的_具体情况用的 — 你的设置独有的东西。

## 这里放什么

比如：

- 摄像头名称和位置
- SSH 主机和别名
- TTS 的首选语音
- 扬声器/房间名称
- 设备昵称
- 任何环境特定的东西

## 示例

```markdown
### 摄像头

- 客厅 → 主区域，180° 广角
- 前门 → 入口，运动触发

### SSH

- 家庭服务器 → 192.168.50.251, 用户: admin

### TTS

- 首选语音: "Nova"（温暖，略带英式）
- 默认扬声器: 厨房 HomePod
```

## 为什么要分开？

技能是共享的。你的设置是你的。把它们分开意味着你可以更新技能而不丢失笔记，可以分享技能而不泄露你的基础设施。

---

添加任何能帮你工作的东西。这是你的备忘单。

---
## 新浪股价API（实时）

- **URL:** https://hq.sinajs.cn/list=sh600031,sh601857
- **用法:** `curl -s -H "Referer: https://finance.sina.com.cn" "https://hq.sinajs.cn/list=sh600031"`
- **返回:** `var hq_str_sh600031="股票名,今开,昨收,当前,最高,最低,买一,卖一,成交量,成交额,..."`
- **注意:** 需要带 Referer 头

## 新浪财经7x24 API（快讯）

- **URL:** https://zhibo.sina.com.cn/api/zhibo/feed
- **用法:** `curl -s "https://zhibo.sina.com.cn/api/zhibo/feed?page=1&page_size=15&zhibo_id=152&tag_id=0&dire=f&dpc=1&pagesize=15&type=0"`
- **返回:** JSON格式的实时财经快讯
- **字段:** rich_text（内容）、create_time（时间）


## 📊 回测系统 - Backtrader

### 数据保存路径
```
/root/.openclaw/workspace/data/backtest/
```

### 快速使用
```bash
cd /root/.openclaw/workspace/Knowledge/trading-strategies/code
python3 backtest_engine.py
```

### 回测框架
- **Backtrader**: 经典Python回测框架（已安装）
- **策略**: 多因子策略V3
- **因子**: VWAP(+2), 布林带(+1), 均线多头(+2), 放量(+1), MACD(+0.5), RSI(+1)
- **止盈止损**: 10%/4% = 盈亏比2.5

### 回测输出格式
```json
{
  "timestamp": "回测时间",
  "strategy": "策略名称",
  "results": {
    "total_return": "总收益率%",
    "sharpe_ratio": "夏普比率",
    "max_drawdown": "最大回撤%",
    "win_rate": "胜率%"
  },
  "trades": ["交易记录"]
}
```

---

## 🔍 本地搜索 - SearXNG

### 服务信息

| 项目 | 值 |
|------|-----|
| **地址** | http://192.168.50.251:10011 |
| **状态** | ✅ 运行中 |
| **引擎** | 247 个可用 |
| **默认** | duckduckgo, bing |

### 快速使用

```bash
# 中文搜索
cd /root/.openclaw/workspace/tools
python3 search.py "量化交易策略" --limit=5

# 英文搜索
python3 search.py "python tutorial" --lang=en

# 最近一周
python3 search.py "bitcoin" --time=week

# JSON 输出
python3 search.py "关键词" --json
```

### API 调用

```bash
# 直接调用
curl "http://192.168.50.251:10011/search?q=关键词&format=json&engines=duckduckgo,bing"

# 中文
curl "http://192.168.50.251:10011/search?q=量化交易&format=json&engines=duckduckgo,bing&language=zh"
```

### 在 Python 中使用

```python
import requests

def search(query, engines="duckduckgo,bing"):
    params = {
        'q': query,
        'format': 'json',
        'engines': engines
    }
    response = requests.get("http://192.168.50.251:10011/search", params=params, timeout=10)
    return response.json().get('results', [])

# 使用
results = search("量化交易")
for r in results[:5]:
    print(f"{r['title']}: {r['url']}")
```

### 推荐引擎

| 场景 | 引擎 |
|------|------|
| 通用 | duckduckgo, bing |
| 中文 | baidu, bing |
| 技术 | github, duckduckgo |
| 新闻 | bing news |

### 相关文档

- 配置文档: `docs/searxng-ready.md`
- 技能文档: `skills/searxng/SKILL.md`
- 搜索脚本: `tools/search.py`

---

## 🌐 GitHub访问优化

### 问题：GitHub访问慢/超时

**解决方案：使用 GitHub520 hosts 加速**

### GitHub520 项目

- **地址**: https://github.com/521xueweihan/GitHub520
- **说明**: 持续更新的GitHub hosts，解决访问慢的问题

### 使用方法

```bash
# 1. 获取最新hosts
curl -s https://raw.githubusercontent.com/521xueweihan/GitHub520/main/hosts >> /etc/hosts

# 2. 或者手动编辑
vi /etc/hosts
# 添加GitHub520提供的IP映射

# 3. 刷新DNS缓存
systemctl restart nscd  # 或
service dns-clean restart
```

### 何时使用

- `git clone` 超时
- `git pull` 速度极慢
- GitHub下载zip失败
- curl访问GitHub API超时

### 注意事项

- hosts会定期更新，建议每月刷新一次
- 如果某天突然变慢，检查hosts是否过期
- 备份：更新前先备份`/etc/hosts`
