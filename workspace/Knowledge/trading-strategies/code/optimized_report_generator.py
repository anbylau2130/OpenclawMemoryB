#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化交易报告生成器
功能：生成优化的交易报告，包含量价分析、市场情绪、迭代优化
作者：小秘
日期：2026-03-20
"""

import json
import configparser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from volume_price_analyzer import VolumePriceAnalyzer, MarketSentimentAnalyzer


class OptimizedTradingReportGenerator:
    """优化交易报告生成器"""
    
    def __init__(self, config_path: str = None):
        """初始化"""
        self.config = self._load_config(config_path)
        self.vp_analyzer = VolumePriceAnalyzer(config_path)
        self.sentiment_analyzer = MarketSentimentAnalyzer(config_path)
        
    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        """加载配置"""
        config = configparser.ConfigParser()
        if config_path and Path(config_path).exists():
            config.read(config_path)
        else:
            # 默认配置
            config['report'] = {
                'save_path': '/root/.openclaw/workspace/trading',
                'filename_pattern': '{stock_name}-{date}-{scan_count}.md'
            }
        return config
    
    def generate_report(self, 
                       stock_data: Dict, 
                       scan_count: int,
                       historical_data: List[Dict] = None,
                       market_data: Dict = None,
                       iteration: int = 1) -> Dict:
        """
        生成优化报告
        
        Args:
            stock_data: 股票数据
            scan_count: 扫描次数
            historical_data: 历史数据（用于量价分析）
            market_data: 市场数据（用于情绪分析）
            iteration: 迭代次数
            
        Returns:
            报告结果
        """
        # 1. 基础数据分析
        basic_analysis = self._analyze_basic_data(stock_data)
        
        # 2. 量价分析
        volume_price_analysis = None
        if historical_data:
            volume_price_analysis = self.vp_analyzer.analyze(stock_data, historical_data)
        
        # 3. 市场情绪分析
        sentiment_analysis = None
        if market_data:
            sentiment_analysis = self.sentiment_analyzer.analyze(market_data)
        
        # 4. 交易建议生成
        trading_advice = self._generate_trading_advice(
            basic_analysis, 
            volume_price_analysis, 
            sentiment_analysis
        )
        
        # 5. 迭代优化
        optimized_advice = self._iterate_optimize(
            trading_advice, 
            basic_analysis,
            volume_price_analysis,
            sentiment_analysis,
            iteration
        )
        
        # 6. 生成报告内容
        report_content = self._format_report(
            basic_analysis,
            volume_price_analysis,
            sentiment_analysis,
            optimized_advice,
            scan_count,
            iteration
        )
        
        # 7. 保存报告
        save_path = self._save_report(report_content, stock_data, scan_count)
        
        return {
            'save_path': save_path,
            'iteration': iteration,
            'optimized': True,
            'advice': optimized_advice
        }
    
    def _analyze_basic_data(self, stock_data: Dict) -> Dict:
        """分析基础数据"""
        return {
            'code': stock_data.get('code', 'UNKNOWN'),
            'name': stock_data.get('name', 'UNKNOWN'),
            'price': stock_data.get('current_price', 0),
            'change_pct': stock_data.get('change_pct', 0),
            'score': stock_data.get('score', 0),  # 默认0分
            'signals': stock_data.get('signals', []),
            'rsi': stock_data.get('rsi', 50),  # 默认50
            'kdj_k': stock_data.get('kdj_k', 50),  # 默认50
            'vwap': stock_data.get('vwap', stock_data.get('current_price', 0)),  # 默认当前价
            'boll_lower': stock_data.get('boll_lower', stock_data.get('current_price', 0) * 0.9)  # 默认当前价*0.9
        }
    
    def _generate_trading_advice(self, 
                                basic: Dict,
                                volume_price: Optional[Dict],
                                sentiment: Optional[Dict]) -> Dict:
        """生成交易建议"""
        advice = {
            'short_term': {},
            'mid_term': {},
            'long_term': {}
        }
        
        # 短期建议（1-2周）
        if basic['score'] >= 3.0:
            if volume_price and volume_price['pattern'] == 'PRICE_UP_VOLUME_UP':
                advice['short_term'] = {
                    'action': 'BUY',
                    'position': 0.15,
                    'entry_price': basic['price'] * 0.98,
                    'stop_loss': basic['price'] * 0.97,
                    'take_profit_1': basic['price'] * 1.06,
                    'confidence': 0.8,
                    'reason': f"因子得分{basic['score']:.1f}，量价配合良好"
                }
            elif volume_price and volume_price['pattern'] == 'PRICE_DOWN_VOLUME_DOWN':
                advice['short_term'] = {
                    'action': 'WAIT_BUY',
                    'position': 0.10,
                    'entry_price': basic['price'] * 0.95,
                    'stop_loss': basic['price'] * 0.97,
                    'take_profit_1': basic['price'] * 1.06,
                    'confidence': 0.7,
                    'reason': f"因子得分{basic['score']:.1f}，卖盘枯竭，等待企稳"
                }
            else:
                advice['short_term'] = {
                    'action': 'OBSERVE',
                    'position': 0,
                    'confidence': 0.5,
                    'reason': f"因子得分{basic['score']:.1f}，建议观望"
                }
        else:
            advice['short_term'] = {
                'action': 'HOLD',
                'position': 0,
                'confidence': 0.3,
                'reason': f"因子得分{basic['score']:.1f}，信号不足"
            }
        
        # 中期建议（1个月）
        if basic['score'] >= 3.0 and basic['rsi'] < 60:
            advice['mid_term'] = {
                'action': 'BUY',
                'position': 0.20,
                'entry_price': basic['price'] * 0.97,
                'stop_loss': basic['price'] * 0.95,
                'take_profit': basic['price'] * 1.15,
                'confidence': 0.75,
                'reason': f"RSI {basic['rsi']:.1f}，有上涨空间"
            }
        else:
            advice['mid_term'] = {
                'action': 'HOLD',
                'position': 0,
                'confidence': 0.4,
                'reason': "等待更好时机"
            }
        
        # 长期建议（3个月）
        advice['long_term'] = {
            'action': 'VALUE_INVEST',
            'position': 0.30,
            'target_price': basic['price'] * 1.28,
            'stop_loss': basic['price'] * 0.92,
            'confidence': 0.65,
            'reason': "价值投资，长期持有"
        }
        
        return advice
    
    def _iterate_optimize(self, 
                         advice: Dict,
                         basic: Dict,
                         volume_price: Optional[Dict],
                         sentiment: Optional[Dict],
                         iteration: int) -> Dict:
        """迭代优化建议"""
        optimized = advice.copy()
        
        # 迭代1: 调整仓位
        if iteration >= 1:
            if sentiment and sentiment['level'] in ['VERY_BULLISH', 'BULLISH']:
                optimized['short_term']['position'] *= 1.2  # 增加20%仓位
                optimized['mid_term']['position'] *= 1.2
            elif sentiment and sentiment['level'] in ['BEARISH', 'VERY_BEARISH']:
                optimized['short_term']['position'] *= 0.8  # 减少20%仓位
                optimized['mid_term']['position'] *= 0.8
        
        # 迭代2: 调整止盈止损
        if iteration >= 2:
            if volume_price and volume_price['strength'] in ['非常强', '强']:
                optimized['short_term']['take_profit_1'] *= 1.05  # 提高止盈目标
                optimized['mid_term']['take_profit'] *= 1.05
        
        # 迭代3: 根据RSI调整
        if iteration >= 3 and basic.get('rsi'):
            if basic['rsi'] < 30:
                optimized['short_term']['confidence'] *= 1.2  # 提高信心
                optimized['short_term']['reason'] += "，RSI超卖"
            elif basic['rsi'] > 70:
                optimized['short_term']['confidence'] *= 0.8  # 降低信心
                optimized['short_term']['reason'] += "，RSI超买"
        
        # 迭代4: 根据KDJ调整
        if iteration >= 4 and basic.get('kdj_k'):
            if basic['kdj_k'] < 20:
                optimized['short_term']['action'] = 'BUY'
                optimized['short_term']['reason'] += "，KDJ超卖"
            elif basic['kdj_k'] > 80:
                optimized['short_term']['action'] = 'SELL'
                optimized['short_term']['reason'] += "，KDJ超买"
        
        # 迭代5: 根据VWAP调整
        if iteration >= 5 and basic.get('vwap'):
            if basic['price'] < basic['vwap'] * 0.98:
                optimized['short_term']['action'] = 'BUY'
                optimized['short_term']['reason'] += f"，低于VWAP {basic['vwap']:.2f}"
        
        # 迭代6: 根据布林带调整
        if iteration >= 6 and basic.get('boll_lower'):
            if basic['price'] < basic['boll_lower'] * 1.02:
                optimized['short_term']['action'] = 'BUY'
                optimized['short_term']['reason'] += "，接近布林下轨"
        
        # 迭代7: 根据量比调整
        if iteration >= 7 and volume_price:
            if volume_price['volume_ratio'] > 2.0:
                optimized['short_term']['confidence'] *= 1.1
                optimized['short_term']['reason'] += "，量比放大"
        
        # 迭代8: 综合评估
        if iteration >= 8:
            # 计算综合得分
            total_score = 0
            total_score += optimized['short_term'].get('confidence', 0) * 0.4
            total_score += optimized['mid_term'].get('confidence', 0) * 0.35
            total_score += optimized['long_term'].get('confidence', 0) * 0.25
            
            optimized['total_confidence'] = total_score
        
        # 迭代9: 风险评估
        if iteration >= 9:
            risk_level = 'LOW'
            if optimized['short_term'].get('position', 0) > 0.15:
                risk_level = 'MEDIUM'
            if optimized['short_term'].get('position', 0) > 0.20:
                risk_level = 'HIGH'
            
            optimized['risk_level'] = risk_level
        
        # 迭代10: 最终建议
        if iteration >= 10:
            final_action = optimized['short_term'].get('action', 'HOLD')
            final_confidence = optimized.get('total_confidence', 0.5)
            
            if final_confidence >= 0.8:
                optimized['final_recommendation'] = f"强烈建议{final_action}，信心度{final_confidence:.0%}"
            elif final_confidence >= 0.6:
                optimized['final_recommendation'] = f"建议{final_action}，信心度{final_confidence:.0%}"
            else:
                optimized['final_recommendation'] = f"建议观望，信心度{final_confidence:.0%}"
        
        return optimized
    
    def _format_report(self,
                      basic: Dict,
                      volume_price: Optional[Dict],
                      sentiment: Optional[Dict],
                      advice: Dict,
                      scan_count: int,
                      iteration: int) -> str:
        """格式化报告"""
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# 优化交易报告
**报告时间：** {report_time}
**股票代码：** {basic['code']}
**股票名称：** {basic['name']}
**扫描次数：** 第{scan_count}次
**优化迭代：** {iteration}次

---

## 📊 基础数据

| 指标 | 数值 |
|------|------|
| 当前价格 | ¥{basic['price']:.2f} |
| 涨跌幅 | {basic['change_pct']:+.2f}% |
| 因子得分 | {basic['score']:.1f} |
| RSI | {basic['rsi']:.2f} |
| KDJ-K | {basic['kdj_k']:.2f} |
| VWAP | ¥{basic['vwap']:.2f} |
| 布林下轨 | ¥{basic['boll_lower']:.2f} |

**信号：** {', '.join(basic['signals'])}

---

## 📈 量价分析
"""
        
        if volume_price:
            report += f"""
**量价形态：** {volume_price['pattern']}
**量比：** {volume_price['volume_ratio']:.2f}
**平均成交量：** {volume_price['avg_volume']:,}
**当前成交量：** {volume_price['current_volume']:,}

**市场含义：** {volume_price['meaning']}

**交易建议：** {volume_price['advice']}

**信号强度：** {volume_price['strength']}
"""
        else:
            report += "\n⚠️ 暂无历史数据，无法进行量价分析\n"
        
        report += "\n---\n\n## 🎯 市场情绪\n"
        
        if sentiment:
            report += f"""
**情绪得分：** {sentiment['score']:.2f}/100
**情绪等级：** {sentiment['level']}
**情绪描述：** {sentiment['description']}

**情绪建议：** {sentiment['advice']}

**分项得分：**
- 价格得分: {sentiment['components']['price_score']:.2f}
- 成交量得分: {sentiment['components']['volume_score']:.2f}
- 动量得分: {sentiment['components']['momentum_score']:.2f}
- 市场广度得分: {sentiment['components']['breadth_score']:.2f}
- 波动率得分: {sentiment['components']['volatility_score']:.2f}
"""
        else:
            report += "\n⚠️ 暂无市场数据，无法进行情绪分析\n"
        
        report += f"""

---

## 💰 交易建议

### 短期策略（1-2周）
**操作：** {advice['short_term'].get('action', 'HOLD')}
**仓位：** {advice['short_term'].get('position', 0):.0%}
**信心度：** {advice['short_term'].get('confidence', 0):.0%}
**理由：** {advice['short_term'].get('reason', '暂无')}

"""
        
        if advice['short_term'].get('entry_price'):
            report += f"""**买入价：** ¥{advice['short_term']['entry_price']:.2f}
**止损价：** ¥{advice['short_term']['stop_loss']:.2f}
**止盈1：** ¥{advice['short_term']['take_profit_1']:.2f}

"""
        
        report += f"""### 中期策略（1个月）
**操作：** {advice['mid_term'].get('action', 'HOLD')}
**仓位：** {advice['mid_term'].get('position', 0):.0%}
**信心度：** {advice['mid_term'].get('confidence', 0):.0%}
**理由：** {advice['mid_term'].get('reason', '暂无')}

"""
        
        if advice['mid_term'].get('entry_price'):
            report += f"""**买入价：** ¥{advice['mid_term']['entry_price']:.2f}
**止损价：** ¥{advice['mid_term']['stop_loss']:.2f}
**止盈：** ¥{advice['mid_term']['take_profit']:.2f}

"""
        
        report += f"""### 长期策略（3个月）
**操作：** {advice['long_term'].get('action', 'VALUE_INVEST')}
**仓位：** {advice['long_term'].get('position', 0):.0%}
**信心度：** {advice['long_term'].get('confidence', 0):.0%}
**理由：** {advice['long_term'].get('reason', '暂无')}

"""
        
        if advice['long_term'].get('target_price'):
            report += f"""**目标价：** ¥{advice['long_term']['target_price']:.2f}
**止损价：** ¥{advice['long_term']['stop_loss']:.2f}

"""
        
        # 添加优化结果
        if iteration >= 8:
            report += f"""---

## 🎯 优化结果

**综合信心度：** {advice.get('total_confidence', 0):.0%}
**风险等级：** {advice.get('risk_level', 'UNKNOWN')}
"""
        
        if iteration >= 10:
            report += f"""
**最终建议：** {advice.get('final_recommendation', '暂无')}
"""
        
        report += f"""
---

## ⚠️ 风险提示

- 股市有风险，投资需谨慎
- 本报告仅供参考，不构成投资建议
- 请根据自身风险承受能力决策
- 严格执行止损纪律

---

**报告生成时间：** {report_time}
**下次更新时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**负责人：** 小秘（AI交易助手）
"""
        
        return report
    
    def _save_report(self, content: str, stock_data: Dict, scan_count: int) -> str:
        """保存报告"""
        # 获取保存路径
        base_path = Path(self.config['report'].get('save_path', '/root/.openclaw/workspace/trading'))
        
        # 获取股票名称
        stock_name = stock_data.get('name', 'UNKNOWN')
        
        # 创建股票文件夹
        stock_dir = base_path / stock_name
        stock_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        date = datetime.now().strftime('%Y-%m-%d')
        filename = f"{stock_name}-{date}-{scan_count}.md"
        
        # 保存文件
        file_path = stock_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)


if __name__ == '__main__':
    # 测试
    config_path = '/root/.openclaw/workspace/trading/config.ini'
    generator = OptimizedTradingReportGenerator(config_path)
    
    # 模拟数据
    stock_data = {
        'code': '601857',
        'name': '中国石油',
        'current_price': 12.48,
        'change_pct': 5.23,
        'score': 3.0,
        'signals': ['VWAP买入(96.0%)', 'KDJ偏低(K17)'],
        'rsi': 45.04,
        'kdj_k': 16.61,
        'vwap': 13.00,
        'boll_lower': 11.24
    }
    
    historical_data = [
        {'volume': 100000000},
        {'volume': 110000000},
        {'volume': 120000000},
        {'volume': 90000000},
        {'volume': 105000000}
    ]
    
    market_data = {
        'price_change': 0.0523,
        'volume_change': 0.5,
        'momentum': 65,
        'breadth': 0.6,
        'volatility': 0.025
    }
    
    # 生成报告（迭代10次）
    result = generator.generate_report(
        stock_data,
        scan_count=84,
        historical_data=historical_data,
        market_data=market_data,
        iteration=10
    )
    
    print(f"报告已保存: {result['save_path']}")
    print(f"迭代次数: {result['iteration']}")
    print(f"是否优化: {result['optimized']}")
    if 'final_recommendation' in result['advice']:
        print(f"最终建议: {result['advice']['final_recommendation']}")
