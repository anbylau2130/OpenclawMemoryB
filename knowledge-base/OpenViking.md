# OpenViking - AI Agent上下文数据库

**文档创建时间**: 2026-03-24 22:34
**GitHub**: https://github.com/volcengine/OpenViking
**Stars**: ⭐ 18,677
**License**: Apache 2.0
**维护方**: 火山引擎（字节跳动）

---

## 📋 快速导航

- [项目概述](#项目概述)
- [核心优势](#核心优势)
- [性能对比](#性能对比)
- [安装部署](#安装部署)
- [配置示例](#配置示例)
- [OpenClaw集成](#openclaw集成)
- [常见问题](#常见问题)

---

## 项目概述

OpenViking是一个开源的AI Agent上下文数据库，专为AI Agent（如OpenClaw）设计。

### 核心理念

用**文件系统范式**统一管理AI Agent所需的上下文（记忆、资源、技能），实现分层上下文交付和自我进化。

### 解决的问题

1. **上下文碎片化** - 记忆在代码中、资源在向量数据库中、技能分散各处
2. **上下文需求激增** - Agent长期运行产生的上下文，简单截断会导致信息丢失
3. **检索效果差** - 传统RAG使用扁平存储，缺乏全局视角
4. **上下文不可观察** - 传统RAG的隐式检索链像黑盒
5. **记忆迭代有限** - 当前记忆只是用户交互记录，缺乏Agent相关任务记忆

---

## 核心优势

### 1. 文件系统管理范式 → 解决碎片化
统一管理记忆、资源、技能的上下文，基于文件系统范式。

### 2. 分层上下文加载 → 降低Token消耗
L0/L1/L2三层结构，按需加载，显著节省成本。

### 3. 目录递归检索 → 提高检索效果
支持原生文件系统检索方法，结合目录定位与语义搜索。

### 4. 可视化检索轨迹 → 可观察上下文
支持目录检索轨迹可视化，清晰观察问题根源。

### 5. 自动会话管理 → 上下文自我迭代
自动压缩对话中的内容，提取长期记忆，让Agent越用越聪明。

---

## 性能对比

### 官方基准测试

| 实验组 | 任务完成率 | Token消耗 | 改进幅度 |
|--------|-----------|----------|---------|
| **OpenClaw (原生)** | 35.65% | 24,611,530 | 基线 |
| **OpenClaw + LanceDB** | 44.55% | 51,574,530 | +25% / -0% |
| **OpenClaw + OpenViking** | **52.08%** | **4,264,396** | **+46% / -83%** ✅ |

### 关键指标

- ✅ **任务完成率提升**: +46%
- ✅ **Token消耗降低**: -83%
- ✅ **检索准确性**: 显著提升

---

## 安装部署

### 系统要求

- **Python**: 3.10+
- **Go**: 1.22+（可选）
- **C++编译器**: GCC 9+或Clang 11+
- **操作系统**: Linux、macOS、Windows

### 安装方式

```bash
# 方式1：pip安装（推荐）
pip install openviking --upgrade --force-reinstall

# 方式2：使用安装脚本
curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/crates/ov_cli/install.sh | bash
```

---

## 配置示例

### 方案1：NVIDIA NIM（推荐，免费）

```bash
# 获取API Key: https://build.nvidia.com/
```

```json
{
  "storage": {
    "workspace": "/root/.openviking_workspace"
  },
  "embedding": {
    "dense": {
      "api_base": "https://integrate.api.nvidia.com/v1",
      "api_key": "nvapi-YOUR-KEY-HERE",
      "provider": "openai",
      "dimension": 4096,
      "model": "nvidia/nv-embed-v1"
    }
  },
  "vlm": {
    "api_base": "https://integrate.api.nvidia.com/v1",
    "api_key": "nvapi-YOUR-KEY-HERE",
    "provider": "openai",
    "model": "meta/llama-3.3-70b-instruct"
  }
}
```

### 方案2：Google Gemini（免费，中文支持好）

```bash
# 获取API Key: https://aistudio.google.com/apikey
pip install "google-genai>=1.0.0"
```

```json
{
  "storage": {
    "workspace": "/root/.openviking_workspace"
  },
  "embedding": {
    "dense": {
      "provider": "gemini",
      "api_key": "YOUR-GOOGLE-API-KEY",
      "model": "gemini-embedding-2-preview",
      "dimension": 3072
    }
  }
}
```

### 配置文件位置

```bash
mkdir -p ~/.openviking
vim ~/.openviking/ov.conf
```

设置环境变量：

```bash
echo 'export OPENVIKING_CONFIG_FILE=~/.openviking/ov.conf' >> ~/.bashrc
source ~/.bashrc
```

---

## 使用示例

### CLI命令

```bash
# 查看状态
ov status

# 添加资源
ov add-resource https://github.com/volcengine/OpenViking --wait

# 添加本地文件
ov add-file ./my-document.md

# 批量添加目录
ov add-dir ./docs/

# 语义搜索
ov find "what is openviking"

# 列出所有资源
ov list-resources

# 读取文件摘要
ov summary viking://resources/my_project/README.md
```

### OpenClaw集成

```bash
# 查看状态
bash /root/.openclaw/workspace/skills/openviking/scripts/viking.sh info

# 索引文件
bash /root/.openclaw/workspace/skills/openviking/scripts/viking.sh add ./my-document.md

# 语义搜索
bash /root/.openclaw/workspace/skills/openviking/scripts/viking.sh search "某个话题"
```

---

## OpenClaw集成

### 已集成位置

- **Skill路径**: `/root/.openclaw/workspace/skills/openviking/`
- **翰林院专用**: `/root/.openclaw/extensions/novel-openviking/skills/novel-openviking/`

### 三省六部应用建议

| 部门 | 用途 | 收益 |
|------|------|------|
| **兵部** | 索引代码仓库 | 快速搜索代码片段 |
| **户部** | 索引财务报表 | 查询历史数据 |
| **礼部** | 索引品牌素材 | 搜索营销案例 |
| **工部** | 索引运维文档 | 快速查找runbook |
| **中书省** | 索引项目文档 | 快速检索文档 |
| **翰林院** | 小说记忆增强 | ✅ **已集成** |

---

## 常见问题

### Q1: OpenViking与Qdrant/ChromaDB的区别？

**A**: OpenViking是完整的上下文数据库解决方案，包含：
- 自动摘要生成（L0/L1/L2三层）
- 文件系统范式管理
- 目录递归检索
- 可视化检索轨迹
- 自动会话管理

而Qdrant/ChromaDB只是向量数据库。

### Q2: 免费API Key是否有使用限制？

**A**: 
- **NVIDIA NIM**: 免费层有速率限制，对个人使用足够
- **Google Gemini**: 免费层每天15 RPM

### Q3: OpenViking支持中文吗？

**A**: 完全支持。推荐使用：
- NVIDIA NIM（中文支持优秀）
- Google Gemini（中文支持优秀）
- Volcengine豆包（中文原生）

### Q4: Token消耗为什么能降低83%？

**A**: 通过三层上下文加载策略：
- L0摘要层（100 tokens）快速判断相关性
- L1概览层（2k tokens）理解结构
- L2详情层只在必要时加载

---

## 参考资源

### 官方资源

- **GitHub**: https://github.com/volcengine/OpenViking
- **官网**: https://www.openviking.ai
- **文档**: https://www.openviking.ai/docs
- **Discord**: https://discord.com/invite/eHvx8E9XF3

### API Key获取

- **NVIDIA NIM**: https://build.nvidia.com/
- **Google Gemini**: https://aistudio.google.com/apikey
- **Volcengine**: https://console.volcengine.com/ark
- **OpenAI**: https://platform.openai.com/

---

**维护者**: OpenClaw Main Agent
**最后更新**: 2026-03-24 22:34
