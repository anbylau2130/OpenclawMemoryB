#!/usr/bin/env python3
"""
上证100选股系统 - 每日策略选股
=====================================
功能：每天早上8点，从上证100成分股中选出可能上涨突破的股票
策略：多因子策略（价值+动量+质量+规模+低波动）
作者：小秘
日期：2026-03-17
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

# ============================================================
# 一、上证100成分股列表（示例，实际需要从数据源获取）
# ============================================================

SSE100_STOCKS = {
    # 金融
    "600036": "招商银行",
    "601318": "中国平安",
    "601166": "兴业银行",
    "600000": "浦发银行",
    "601398": "工商银行",
    "601288": "农业银行",
    "601939": "建设银行",
    "601988": "中国银行",
    "600030": "中信证券",
    "601211": "国泰君安",
    
    # 能源
    "601857": "中国石油",
    "600028": "中国石化",
    "601088": "中国神华",
    "600019": "宝钢股份",
    "601818": "光大银行",
    
    # 工业
    "600031": "三一重工",
    "601766": "中国中车",
    "600104": "上汽集团",
    "601390": "中国中铁",
    "601186": "中国铁建",
    
    # 消费
    "600519": "贵州茅台",
    "000858": "五粮液",
    "600887": "伊利股份",
    "002304": "洋河股份",
    "000568": "泸州老窖",
    
    # 科技
    "600276": "恒瑞医药",
    "000333": "美的集团",
    "000651": "格力电器",
    "002415": "海康威视",
    "600030": "中信证券",
    
    # 更多股票...
    "600009": "上海机场",
    "600011": "华能国际",
    "600015": "华夏银行",
    "600016": "民生银行",
    "600018": "上港集团",
    "600029": "南方航空",
    "600048": "保利地产",
    "600050": "中国联通",
    "600089": "特变电工",
    "600109": "国金证券",
    "600111": "北方稀土",
    "600115": "东方航空",
    "600118": "中国卫星",
    "600150": "中国船舶",
    "600176": "中国巨石",
    "600183": "生益科技",
    "600196": "复星医药",
    "600208": "新湖中宝",
    "600221": "海南航空",
    "600236": "桂冠电力",
    "600258": "首旅酒店",
    "600269": "赣粤高速",
    "600309": "万华化学",
    "600332": "白云山",
    "600340": "华夏幸福",
    "600352": "浙江龙盛",
    "600377": "宁沪高速",
    "600438": "通威股份",
    "600486": "扬农化工",
    "600489": "中金黄金",
    "600498": "烽火通信",
    "600521": "华海药业",
    "600535": "天士力",
    "600547": "山东黄金",
    "600570": "恒生电子",
    "600585": "海螺水泥",
    "600588": "用友网络",
    "600598": "北大荒",
    "600660": "福耀玻璃",
    "600674": "川投能源",
    "600690": "海尔智家",
    "600703": "三安光电",
    "600741": "华域汽车",
    "600745": "闻泰科技",
    "600795": "国电电力",
    "600809": "山西汾酒",
    "600837": "海通证券",
    "600845": "宝信软件",
    "600848": "上海临港",
    "600867": "通化东宝",
    "600886": "国投电力",
    "600893": "航发动力",
    "600900": "长江电力",
    "600905": "三峡能源",
    "600919": "江苏银行",
    "600926": "杭州银行",
    "600958": "东方证券",
    "600989": "宝丰能源",
    "600998": "九州通",
    "600999": "招商证券",
    "601012": "隆基绿能",
    "601066": "中信建投",
    "601111": "中国国航",
    "601138": "工业富联",
    "601225": "陕西煤业",
    "601236": "红塔证券",
    "601238": "广汽集团",
    "601288": "农业银行",
    "601319": "中国人保",
    "601328": "交通银行",
    "601336": "新华保险",
    "601377": "兴业证券",
    "601390": "中国中铁",
    "601398": "工商银行",
    "601555": "东吴证券",
    "601577": "长沙银行",
    "601600": "中国铝业",
    "601601": "中国太保",
    "601618": "中国中冶",
    "601628": "中国人寿",
    "601633": "长城汽车",
    "601658": "邮储银行",
    "601668": "中国建筑",
    "601669": "中国电建",
    "601688": "华泰证券",
    "601696": "中银证券",
    "601698": "中国卫星",
    "601727": "上海电气",
    "601728": "中国电信",
    "601766": "中国中车",
    "601788": "光大证券",
    "601800": "中国交建",
    "601808": "中海油服",
    "601816": "京沪高铁",
    "601818": "光大银行",
    "601857": "中国石油",
    "601877": "正泰电器",
    "601880": "辽港股份",
    "601881": "中国汽研",
    "601888": "中国中免",
    "601899": "紫金矿业",
    "601901": "方正证券",
    "601919": "中远海控",
    "601933": "永辉超市",
    "601939": "建设银行",
    "601985": "中国核电",
    "601988": "中国银行",
    "601989": "中国重工",
    "601995": "中金公司",
    "601998": "中信银行",
}


# ============================================================
# 二、模拟因子计算（实际需要接入真实数据）
# ============================================================

def calculate_factor_scores(stock_code: str) -> Dict[str, float]:
    """
    计算股票的因子得分
    实际需要接入真实行情和财务数据
    """
    import random
    random.seed(hash(stock_code) % 10000)
    
    # 模拟因子得分（-2 到 2）
    return {
        'value': random.uniform(-1.5, 1.5),      # 价值因子
        'momentum': random.uniform(-1.5, 1.5),  # 动量因子
        'quality': random.uniform(-1.5, 1.5),   # 质量因子
        'size': random.uniform(-1.5, 1.5),      # 规模因子
        'low_vol': random.uniform(-1.5, 1.5),   # 低波动因子
    }


def calculate_composite_score(factor_scores: Dict[str, float], 
                             weights: Dict[str, float]) -> float:
    """计算综合得分"""
    score = 0
    total_weight = 0
    
    for factor, weight in weights.items():
        if factor in factor_scores:
            score += factor_scores[factor] * weight
            total_weight += weight
    
    return score / total_weight if total_weight > 0 else 0


# ============================================================
# 三、选股逻辑
# ============================================================

def select_stocks(weights: Dict[str, float] = None, top_n: int = 10) -> List[Dict]:
    """
    选股：从上证100中选出综合得分最高的股票
    
    参数：
    - weights: 因子权重（默认均衡型）
    - top_n: 选出前N只
    """
    if weights is None:
        # 均衡型权重
        weights = {
            'value': 0.20,
            'momentum': 0.25,  # 动量稍高，抓突破
            'quality': 0.25,
            'size': 0.10,
            'low_vol': 0.20
        }
    
    results = []
    
    for code, name in SSE100_STOCKS.items():
        # 计算因子得分
        factor_scores = calculate_factor_scores(code)
        
        # 计算综合得分
        composite = calculate_composite_score(factor_scores, weights)
        
        results.append({
            'code': code,
            'name': name,
            'composite_score': composite,
            'factor_scores': factor_scores,
            'signal': 'BUY' if composite > 0.5 else ('SELL' if composite < -0.5 else 'HOLD')
        })
    
    # 按综合得分排序
    results.sort(key=lambda x: x['composite_score'], reverse=True)
    
    return results[:top_n]


# ============================================================
# 四、生成选股报告
# ============================================================

def generate_selection_report(selected_stocks: List[Dict]) -> str:
    """生成选股报告"""
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines.append("=" * 60)
    lines.append(f"上证100策略选股报告")
    lines.append(f"时间：{now}")
    lines.append("=" * 60)
    lines.append("")
    
    lines.append("【选股策略】多因子模型")
    lines.append("  价值 20% + 动量 25% + 质量 25% + 规模 10% + 低波动 20%")
    lines.append("")
    
    lines.append(f"【今日精选】共 {len(selected_stocks)} 只")
    lines.append("-" * 60)
    
    for i, stock in enumerate(selected_stocks, 1):
        signal_emoji = "🟢" if stock['signal'] == 'BUY' else ("🔴" if stock['signal'] == 'SELL' else "🟡")
        lines.append(f"{i:2d}. {stock['code']} {stock['name']:<8} | 得分: {stock['composite_score']:+.3f} | {signal_emoji} {stock['signal']}")
        
        # 显示因子详情
        fs = stock['factor_scores']
        lines.append(f"    价值:{fs['value']:+.2f} 动量:{fs['momentum']:+.2f} 质量:{fs['quality']:+.2f} 规模:{fs['size']:+.2f} 低波:{fs['low_vol']:+.2f}")
    
    lines.append("-" * 60)
    lines.append("")
    
    # 买入信号统计
    buy_count = sum(1 for s in selected_stocks if s['signal'] == 'BUY')
    lines.append(f"【统计】买入信号: {buy_count} 只 | 持有: {len(selected_stocks) - buy_count} 只")
    lines.append("")
    
    lines.append("【操作建议】")
    lines.append("  1. 优先关注得分 > 0.5 的股票")
    lines.append("  2. 结合成交量确认突破")
    lines.append("  3. 设置止损 -5%，止盈 +10%")
    lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


# ============================================================
# 五、保存选股结果（用于复盘）
# ============================================================

def save_selection(selected_stocks: List[Dict], output_dir: str = None):
    """保存选股结果，用于复盘验证"""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "selections")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为 JSON
    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(output_dir, f"selection_{today}.json")
    
    data = {
        "date": today,
        "time": datetime.now().strftime("%H:%M"),
        "stocks": selected_stocks,
        "weights": {
            'value': 0.20,
            'momentum': 0.25,
            'quality': 0.25,
            'size': 0.10,
            'low_vol': 0.20
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("上证100策略选股系统")
    print("=" * 60)
    print()
    
    # 选股
    selected = select_stocks(top_n=10)
    
    # 生成报告
    report = generate_selection_report(selected)
    print(report)
    
    # 保存结果
    filename = save_selection(selected)
    print(f"选股结果已保存: {filename}")
