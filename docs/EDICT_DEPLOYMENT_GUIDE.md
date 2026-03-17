# Edict部署指南 - 开机自启版

> 创建时间：2026-03-17 11:31
> 更新时间：2026-03-17 11:34
> 适用环境：OpenClaw已安装
> 项目地址：https://github.com/cft0808/edict

---

## 📋 项目简介

**Edict** - 三省六部制 · OpenClaw多Agent协作系统

**核心架构：**
- 12个AI Agent（11个业务角色 + 1个兼容角色）
- 三省六部制度：太子分拣 → 中书省规划 → 门下省审核 → 尚书省派发 → 六部执行
- 实时看板 + 完整审计 + 任务干预

**核心优势：**
- ✅ 门下省专职审核（可封驳）
- ✅ 实时看板（军机处Kanban + 时间线）
- ✅ 任务干预（叫停/取消/恢复）
- ✅ 完整奏折存档
- ✅ Agent健康监控
- ✅ 热切换模型
- ✅ 技能管理
- ✅ 新闻聚合推送

---

## 🎯 部署方案

### Systemd服务管理

**优势：**
- ✅ 开机自动启动
- ✅ 崩溃自动重启（10秒后）
- ✅ 统一管理命令
- ✅ 日志集中管理
- ✅ 与OpenClaw一致

---

## 📦 快速部署

### 方式1：一键部署（推荐）

```bash
# 给脚本执行权限
chmod +x /root/.openclaw/workspace/projects/deploy_edict.sh

# 运行部署
bash /root/.openclaw/workspace/projects/deploy_edict.sh
```

**部署脚本会自动：**
1. ✅ 检查OpenClaw环境
2. ✅ 克隆Edict项目
3. ✅ 运行安装脚本（配置Agent）
4. ✅ 配置systemd服务
5. ✅ 启动服务
6. ✅ 启用开机自启

**注意：** 如果提示需要配置API Key，请按提示操作后重新运行脚本。

---

### 方式2：使用管理脚本

```bash
# 给脚本执行权限
chmod +x /root/.openclaw/workspace/projects/edict_ctl.sh

# 克隆项目
./edict_ctl.sh install

# 完整部署（含开机自启）
./edict_ctl.sh deploy

# 启动服务
./edict_ctl.sh start

# 查看状态
./edict_ctl.sh status
```

---

## 🎛️ 服务管理

### 管理命令（使用脚本）

```bash
# 进入脚本目录
cd /root/.openclaw/workspace/projects

# 使用管理脚本
./edict_ctl.sh start     # 启动
./edict_ctl.sh stop      # 停止
./edict_ctl.sh restart   # 重启
./edict_ctl.sh status    # 状态
./edict_ctl.sh logs      # 日志
./edict_ctl.sh enable    # 启用开机自启
./edict_ctl.sh disable   # 禁用开机自启
```

### 管理命令（直接使用systemctl）

```bash
# 启动
sudo systemctl start edict-loop edict-dashboard

# 停止
sudo systemctl stop edict-loop edict-dashboard

# 重启
sudo systemctl restart edict-loop edict-dashboard

# 状态
sudo systemctl status edict-loop edict-dashboard

# 日志
sudo journalctl -u edict-loop -u edict-dashboard -f

# 启用开机自启
sudo systemctl enable edict-loop edict-dashboard

# 禁用开机自启
sudo systemctl disable edict-loop edict-dashboard
```

---

## 📊 两个服务说明

### 1. edict-loop.service（数据刷新）

**功能：** 每15秒刷新一次数据
- 更新看板数据
- 同步Agent状态
- 刷新任务进度
- 收集统计数据

**配置文件：** `/etc/systemd/system/edict-loop.service`

**工作目录：** `/root/.openclaw/workspace/projects/edict`

**执行脚本：** `scripts/run_loop.sh`

**日志查看：**
```bash
sudo journalctl -u edict-loop -f
```

**性能：**
- CPU: <5%
- 内存: <20MB

---

### 2. edict-dashboard.service（看板服务）

**功能：** 提供Web界面
- 端口：7891
- 访问：http://127.0.0.1:7891
- 零依赖（Python标准库）
- 单文件前端（dashboard.html）

**配置文件：** `/etc/systemd/system/edict-dashboard.service`

**工作目录：** `/root/.openclaw/workspace/projects/edict`

**执行脚本：** `dashboard/server.py`

**日志查看：**
```bash
sudo journalctl -u edict-dashboard -f
```

**性能：**
- CPU: <2%
- 内存: <50MB

---

## 🔧 高级配置

### 修改端口

**编辑服务文件：**
```bash
sudo nano /etc/systemd/system/edict-dashboard.service
```

**添加环境变量：**
```ini
[Service]
Environment="PORT=8888"
ExecStart=/usr/bin/python3 /root/.openclaw/workspace/projects/edict/dashboard/server.py
```

**重载并重启：**
```bash
sudo systemctl daemon-reload
sudo systemctl restart edict-dashboard
```

---

### 修改扫描间隔

**编辑脚本：**
```bash
nano /root/.openclaw/workspace/projects/edict/scripts/run_loop.sh
```

**修改间隔（默认15秒）：**
```bash
SLEEP_INTERVAL=30  # 改为30秒
```

**重启服务：**
```bash
sudo systemctl restart edict-loop
```

---

### 修改重启延迟

**编辑服务文件：**
```bash
sudo nano /etc/systemd/system/edict-loop.service
```

**修改RestartSec（默认10秒）：**
```ini
RestartSec=30  # 改为30秒
```

**重载：**
```bash
sudo systemctl daemon-reload
```

---

## 🚨 故障排查

### 服务无法启动

**检查日志：**
```bash
# 查看最近50行日志
sudo journalctl -u edict-loop -u edict-dashboard -n 50

# 实时查看日志
sudo journalctl -u edict-loop -u edict-dashboard -f
```

**常见问题：**

#### 1. API Key未配置

**错误：** Agent无法启动，缺少API Key

**解决：**
```bash
# 配置太子Agent的API Key
openclaw agents add taizi
# 输入您的API Key

# 重新运行安装脚本同步API Key
cd /root/.openclaw/workspace/projects/edict
./install.sh

# 重启服务
sudo systemctl restart edict-loop edict-dashboard
```

---

#### 2. 端口被占用

**错误：** `Address already in use`

**检查：**
```bash
# 查看端口占用
sudo netstat -tulpn | grep 7891

# 或使用ss命令
sudo ss -tulpn | grep 7891
```

**解决：**
```bash
# 找到占用进程
sudo lsof -i :7891

# 停止占用进程
sudo kill -9 <PID>

# 或修改端口
sudo nano /etc/systemd/system/edict-dashboard.service
# 添加 Environment="PORT=8888"
sudo systemctl daemon-reload
sudo systemctl restart edict-dashboard
```

---

#### 3. 权限问题

**错误：** `Permission denied`

**解决：**
```bash
# 修复项目权限
sudo chown -R root:root /root/.openclaw/workspace/projects/edict
sudo chmod -R 755 /root/.openclaw/workspace/projects/edict

# 修复脚本权限
chmod +x /root/.openclaw/workspace/projects/edict/scripts/*.sh
chmod +x /root/.openclaw/workspace/projects/edict/scripts/*.py

# 重启服务
sudo systemctl restart edict-loop edict-dashboard
```

---

#### 4. OpenClaw Gateway未运行

**错误：** Agent无法连接Gateway

**检查：**
```bash
# 检查Gateway状态
openclaw gateway status
```

**解决：**
```bash
# 启动Gateway（如果未运行）
openclaw gateway start

# 等待Gateway启动（约5秒）
sleep 5

# 重启Edict服务
sudo systemctl restart edict-loop edict-dashboard
```

---

### 服务崩溃自动重启

**systemd已配置自动重启：**
```ini
Restart=always
RestartSec=10
```

**查看重启记录：**
```bash
sudo journalctl -u edict-loop -u edict-dashboard | grep "Restarting"
```

**查看崩溃原因：**
```bash
sudo journalctl -u edict-loop -u edict-dashboard -b | grep -i error
```

---

## 📋 开机自启验证

### 检查是否启用

```bash
sudo systemctl is-enabled edict-loop
sudo systemctl is-enabled edict-dashboard
```

**预期输出：** `enabled`

---

### 测试重启

```bash
# 重启系统
sudo reboot
```

**重启后验证：**
```bash
# 检查服务状态
sudo systemctl status edict-loop edict-dashboard

# 检查服务是否运行
sudo systemctl is-active edict-loop edict-dashboard

# 访问看板
curl http://127.0.0.1:7891
```

---

## 💡 与V5交易系统集成

### Edict管理V5的12个场景

| Agent | 职责 | V5集成场景 |
|-------|------|-----------|
| **太子** | 消息分拣 | 识别交易相关旨意 |
| **中书省** | 规划 | 制定交易策略方案 |
| **门下省** | 审核 | 审核交易方案风险 |
| **尚书省** | 派发 | 协调交易任务执行 |
| **户部** | 数据 | 执行V5选股任务 |
| **礼部** | 文档 | 编写交易报告 |
| **兵部** | 工程 | 运行实时监控 |
| **刑部** | 合规 | 风险合规检查 |
| **工部** | 基建 | 管理Docker部署 |
| **吏部** | 人事 | Agent注册管理 |
| **早朝官** | 情报 | 每日市场播报 |

---

### 配置V5作为Skill

**添加V5选股系统：**
```bash
cd /root/.openclaw/workspace/projects/edict
python3 scripts/skill_manager.py add hubu \
  --name "V5选股系统" \
  --script "/root/.openclaw/workspace/Knowledge/trading-strategies/code/stock_selector_v5_real.py" \
  --desc "V5多因子选股，高胜率因子VWAP+BOLL+KDJ+RSI"
```

**添加实时监控：**
```bash
python3 scripts/skill_manager.py add bingbu \
  --name "实时监控" \
  --script "/root/.openclaw/workspace/Knowledge/trading-strategies/code/realtime_trading_system.py" \
  --desc "60秒扫描，毫秒级响应，21,541次/秒吞吐量"
```

**添加风险检查：**
```bash
python3 scripts/skill_manager.py add xingbu \
  --name "风险检查" \
  --script "/root/.openclaw/workspace/Knowledge/trading-strategies/code/parameter_optimizer.py" \
  --desc "验证选股准确率，优化参数，盈亏比5.0"
```

---

## 📊 性能监控

### 资源占用

**数据刷新服务（edict-loop）：**
- CPU: <5%
- 内存: <20MB
- 磁盘: 极小（仅日志）

**看板服务（edict-dashboard）：**
- CPU: <2%
- 内存: <50MB
- 网络: 极小（仅本地）

---

### 监控命令

**CPU和内存：**
```bash
# 查看资源占用
sudo systemctl show edict-loop edict-dashboard \
  --property=MemoryCurrent,CPUUsageNSec

# 或使用top
top -p $(pgrep -f "run_loop|server.py")
```

**进程状态：**
```bash
# 查看进程
ps aux | grep -E "run_loop|server.py"

# 查看进程树
pstree -p | grep -A5 edict
```

**网络连接：**
```bash
# 查看端口
sudo ss -tulpn | grep 7891

# 查看连接数
sudo ss -tn | grep :7891 | wc -l
```

---

## 📁 文件结构

```
/root/.openclaw/workspace/
├── docs/
│   ├── edict-loop.service          # 数据刷新服务
│   ├── edict-dashboard.service     # 看板服务
│   └── EDICT_DEPLOYMENT_GUIDE.md   # 部署文档
├── projects/
│   ├── deploy_edict.sh             # 一键部署脚本
│   ├── edict_ctl.sh                # 管理脚本
│   └── edict/                      # 项目目录（部署后）
│       ├── agents/                 # Agent配置
│       ├── dashboard/              # 看板前端
│       ├── scripts/                # 脚本工具
│       └── install.sh              # 安装脚本
```

---

## ✅ 部署检查清单

### 部署前
- [ ] OpenClaw已安装
- [ ] Python 3.9+已安装
- [ ] Node.js 18+已安装（可选，用于构建React前端）
- [ ] Git已安装
- [ ] sudo权限可用

### 部署中
- [ ] 项目已克隆到 `/root/.openclaw/workspace/projects/edict`
- [ ] install.sh已执行
- [ ] API Key已配置（`openclaw agents add taizi`）
- [ ] API Key已同步到所有Agent（重新运行install.sh）

### 部署后
- [ ] systemd服务已安装（2个）
- [ ] 服务已启动（edict-loop + edict-dashboard）
- [ ] 服务状态正常（`systemctl status`）
- [ ] 开机自启已启用（`systemctl is-enabled`）
- [ ] 看板可访问（http://127.0.0.1:7891）
- [ ] 日志正常（`journalctl -u edict-loop -u edict-dashboard`）

---

## 🎯 快速命令参考

```bash
# 一键部署
bash /root/.openclaw/workspace/projects/deploy_edict.sh

# 启动服务
./edict_ctl.sh start

# 停止服务
./edict_ctl.sh stop

# 重启服务
./edict_ctl.sh restart

# 查看状态
./edict_ctl.sh status

# 查看日志
./edict_ctl.sh logs

# 启用开机自启
./edict_ctl.sh enable

# 禁用开机自启
./edict_ctl.sh disable
```

---

## 📞 技术支持

**项目地址：** https://github.com/cft0808/edict

**文档：**
- [Getting Started](https://github.com/cft0808/edict/blob/main/docs/getting-started.md)
- [架构文档](https://github.com/cft0808/edict/blob/main/docs/task-dispatch-architecture.md)

**社区：**
- [OpenClaw社区](https://discord.com/invite/clawd)
- [ClawHub](https://clawhub.com)

---

## 📝 更新日志

### v1.0 - 2026-03-17 11:34
- ✅ 创建完整部署方案
- ✅ 配置systemd服务
- ✅ 实现开机自启
- ✅ 编写管理脚本
- ✅ 添加故障排查指南
- ✅ 集成V5交易系统说明

---

_创建人：小秘_
_时间：2026-03-17 11:34_
_版本：v1.0_
