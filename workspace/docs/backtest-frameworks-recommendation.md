# 量化回测框架推荐

> 2026-03-17 基于GitHub Stars和活跃度筛选

---

## 🏆 Top 5 推荐

| 排名 | 项目 | Stars | 特点 | 推荐场景 |
|------|------|-------|------|----------|
| 1 | **VeighNa (vn.py)** | 37,702 | 国产最强，A股完美支持 | ⭐⭐⭐⭐⭐ A股实盘 |
| 2 | **Qlib** | 38,814 | 微软AI量化，自动化因子挖掘 | ⭐⭐⭐⭐⭐ AI策略 |
| 3 | **Backtrader** | 20,764 | 经典框架，文档丰富 | ⭐⭐⭐⭐ 学习研究 |
| 4 | **RQAlpha** | 6,231 | 米筐开源，分钟级回测 | ⭐⭐⭐⭐ A股回测 |
| 5 | **AKQuant** | 500 | AKShare官方，轻量级 | ⭐⭐⭐ 快速验证 |

---

## 1. VeighNa (vn.py) ⭐⭐⭐⭐⭐

**GitHub:** https://github.com/vnpy/vnpy

**Stars:** 37,702 | **Forks:** 11,084

### 优势
- ✅ 国产最强量化框架
- ✅ A股/期货/数字货币全支持
- ✅ 中文文档完善
- ✅ 实盘交易接口丰富（CTP、XTP等）
- ✅ 可视化GUI界面
- ✅ 社区活跃，更新频繁

### 安装
```bash
pip install vnpy
```

### 适用场景
- A股实盘交易
- 期货量化
- 策略开发和回测

---

## 2. Microsoft Qlib ⭐⭐⭐⭐⭐

**GitHub:** https://github.com/microsoft/qlib

**Stars:** 38,814 | **Forks:** 6,044

### 优势
- ✅ 微软官方出品
- ✅ AI/ML深度集成
- ✅ 自动化因子挖掘
- ✅ 强化学习支持
- ✅ RD-Agent自动研发

### 安装
```bash
pip install pyqlib
```

### 适用场景
- AI量化策略
- 因子挖掘
- 机器学习研究

---

## 3. Backtrader ⭐⭐⭐⭐

**GitHub:** https://github.com/mementum/backtrader

**Stars:** 20,764 | **Forks:** 4,949

### 优势
- ✅ 经典框架，文档最丰富
- ✅ 纯Python，易于学习
- ✅ 内置100+技术指标
- ✅ 多数据源支持
- ✅ 实盘交易接口

### 安装
```bash
pip install backtrader
```

### 适用场景
- 学习量化交易
- 策略研究
- 多市场回测

### 中文教程
https://github.com/jrothschild33/learn_backtrader

---

## 4. RQAlpha ⭐⭐⭐⭐

**GitHub:** https://github.com/ricequant/rqalpha

**Stars:** 6,231 | **Forks:** 1,717

### 优势
- ✅ 米筐科技开源
- ✅ 专为A股设计
- ✅ 分钟级回测
- ✅ 可对接米筐实盘
- ✅ 中文文档

### 安装
```bash
pip install rqalpha
```

### 适用场景
- A股策略回测
- 分钟级高频策略
- 实盘对接

---

## 5. AKQuant ⭐⭐⭐

**GitHub:** https://github.com/akfamily/akquant

**Stars:** 500

### 优势
- ✅ AKShare官方出品
- ✅ 轻量级，快速上手
- ✅ 数据获取便捷
- ✅ 与AKShare无缝集成

### 安装
```bash
pip install akquant
```

### 适用场景
- 快速策略验证
- 轻量级回测
- 学习研究

---

## 🎯 针对我们的需求推荐

### 最佳选择: VeighNa (vn.py)

**理由:**
1. A股完美支持
2. 可对接实盘（CTP、XTP）
3. 中文社区活跃
4. 支持多因子策略
5. 可视化分析

### 快速验证: AKQuant

**理由:**
1. 已安装AKShare
2. 轻量级，无需复杂配置
3. 适合验证我们的多因子策略

---

## 📦 安装命令

```bash
# 方案1: vn.py (推荐)
pip install vnpy

# 方案2: Backtrader (学习)
pip install backtrader

# 方案3: AKQuant (轻量)
pip install akquant
```

---

## 🔗 相关资源

- vn.py文档: https://www.vnpy.com/
- Backtrader文档: https://www.backtrader.com/
- RQAlpha文档: https://rqalpha.readthedocs.io/
- Qlib文档: https://qlib.readthedocs.io/

---

_更新时间: 2026-03-17_
