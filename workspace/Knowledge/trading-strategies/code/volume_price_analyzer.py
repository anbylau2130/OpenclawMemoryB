#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量价分析与市场情绪模块
功能：分析量价关系、计算市场情绪、优化交易建议
作者：小秘
日期：2026-03-20
"""

import json
import configparser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


class VolumePriceAnalyzer:
    """量价分析器"""
    
    def __init__(self, config_path: str = None):
        """初始化"""
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        """加载配置"""
        config = configparser.ConfigParser()
        if config_path and Path(config_path).exists():
            config.read(config_path)
        else:
            # 默认配置
            config['volume_price'] = {
                'volume_surge_threshold': '1.5',
                'volume_shrink_threshold': '0.5'
            }
        return config
    
    def analyze(self, current_data: Dict, historical_data: List[Dict]) -> Dict:
        """
        分析量价关系
        
        Args:
            current_data: 当前数据（price, volume, change_pct）
            historical_data: 历史数据列表
            
        Returns:
            量价分析结果
        """
        if not historical_data or len(historical_data) < 5:
            return self._default_analysis()
        
        # 计算平均成交量
        avg_volume = np.mean([d.get('volume', 0) for d in historical_data[-5:]])
        current_volume = current_data.get('volume', 0)
        current_price = current_data.get('current_price', 0)
        change_pct = current_data.get('change_pct', 0)
        
        # 量比
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # 判断量价关系
        volume_surge_threshold = float(self.config['volume_price'].get('volume_surge_threshold', 1.5))
        volume_shrink_threshold = float(self.config['volume_price'].get('volume_shrink_threshold', 0.5))
        
        # 量价形态
        pattern = self._identify_pattern(change_pct, volume_ratio, volume_surge_threshold, volume_shrink_threshold)
        
        # 市场含义
        meaning = self._interpret_pattern(pattern)
        
        # 交易建议
        advice = self._generate_advice(pattern, change_pct, volume_ratio)
        
        return {
            'pattern': pattern,
            'volume_ratio': round(volume_ratio, 2),
            'avg_volume': int(avg_volume),
            'current_volume': int(current_volume),
            'meaning': meaning,
            'advice': advice,
            'strength': self._calculate_strength(pattern, volume_ratio)
        }
    
    def _identify_pattern(self, change_pct: float, volume_ratio: float, 
                          surge_threshold: float, shrink_threshold: float) -> str:
        """识别量价形态"""
        if change_pct > 0:
            if volume_ratio >= surge_threshold:
                return 'PRICE_UP_VOLUME_UP'  # 价涨量增
            elif volume_ratio <= shrink_threshold:
                return 'PRICE_UP_VOLUME_DOWN'  # 价涨量缩
            else:
                return 'PRICE_UP_VOLUME_NORMAL'  # 价涨量平
        elif change_pct < 0:
            if volume_ratio >= surge_threshold:
                return 'PRICE_DOWN_VOLUME_UP'  # 价跌量增
            elif volume_ratio <= shrink_threshold:
                return 'PRICE_DOWN_VOLUME_DOWN'  # 价跌量缩
            else:
                return 'PRICE_DOWN_VOLUME_NORMAL'  # 价跌量平
        else:
            if volume_ratio >= surge_threshold:
                return 'PRICE_FLAT_VOLUME_UP'  # 价平量增
            elif volume_ratio <= shrink_threshold:
                return 'PRICE_FLAT_VOLUME_DOWN'  # 价平量缩
            else:
                return 'PRICE_FLAT_VOLUME_NORMAL'  # 价平量平
    
    def _interpret_pattern(self, pattern: str) -> str:
        """解释量价形态含义"""
        meanings = {
            'PRICE_UP_VOLUME_UP': '健康上涨，买盘积极，趋势有望延续',
            'PRICE_UP_VOLUME_DOWN': '上涨乏力，买盘谨慎，可能面临回调',
            'PRICE_UP_VOLUME_NORMAL': '温和上涨，市场观望，需观察后续',
            'PRICE_DOWN_VOLUME_UP': '恐慌抛售，卖盘涌出，短期继续承压',
            'PRICE_DOWN_VOLUME_DOWN': '下跌抵抗，卖盘枯竭，可能止跌回升',
            'PRICE_DOWN_VOLUME_NORMAL': '正常回调，市场冷静，观察支撑',
            'PRICE_FLAT_VOLUME_UP': '资金介入，积蓄动能，可能突破',
            'PRICE_FLAT_VOLUME_DOWN': '成交清淡，市场观望，方向不明',
            'PRICE_FLAT_VOLUME_NORMAL': '横盘整理，等待方向，建议观望'
        }
        return meanings.get(pattern, '未知形态')
    
    def _generate_advice(self, pattern: str, change_pct: float, volume_ratio: float) -> str:
        """生成交易建议"""
        if pattern == 'PRICE_UP_VOLUME_UP':
            if change_pct > 3:
                return '强势上涨，可持股或轻仓追涨'
            else:
                return '健康上涨，持股待涨'
        elif pattern == 'PRICE_UP_VOLUME_DOWN':
            return '上涨乏力，逢高减仓'
        elif pattern == 'PRICE_DOWN_VOLUME_UP':
            return '恐慌抛售，暂时观望，等待企稳'
        elif pattern == 'PRICE_DOWN_VOLUME_DOWN':
            return '卖盘枯竭，可考虑逢低吸纳'
        elif pattern == 'PRICE_FLAT_VOLUME_UP':
            return '资金介入，关注突破方向'
        else:
            return '市场观望，等待明确信号'
    
    def _calculate_strength(self, pattern: str, volume_ratio: float) -> str:
        """计算信号强度"""
        strong_patterns = ['PRICE_UP_VOLUME_UP', 'PRICE_DOWN_VOLUME_DOWN']
        weak_patterns = ['PRICE_UP_VOLUME_DOWN', 'PRICE_DOWN_VOLUME_UP']
        
        if pattern in strong_patterns:
            if volume_ratio >= 2.0:
                return '非常强'
            else:
                return '强'
        elif pattern in weak_patterns:
            return '弱'
        else:
            return '中性'
    
    def _default_analysis(self) -> Dict:
        """默认分析结果"""
        return {
            'pattern': 'UNKNOWN',
            'volume_ratio': 1.0,
            'avg_volume': 0,
            'current_volume': 0,
            'meaning': '数据不足，无法分析',
            'advice': '建议观望',
            'strength': '未知'
        }


class MarketSentimentAnalyzer:
    """市场情绪分析器"""
    
    def __init__(self, config_path: str = None):
        """初始化"""
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        """加载配置"""
        config = configparser.ConfigParser()
        if config_path and Path(config_path).exists():
            config.read(config_path)
        else:
            # 默认配置
            config['market_sentiment'] = {
                'very_bullish': '80',
                'bullish': '60',
                'neutral': '40',
                'bearish': '20',
                'very_bearish': '0',
                'price_weight': '0.3',
                'volume_weight': '0.25',
                'momentum_weight': '0.2',
                'breadth_weight': '0.15',
                'volatility_weight': '0.1'
            }
        return config
    
    def analyze(self, market_data: Dict) -> Dict:
        """
        分析市场情绪
        
        Args:
            market_data: 市场数据
                - price_change: 价格变化
                - volume_change: 成交量变化
                - momentum: 动量指标
                - breadth: 市场广度（上涨股票占比）
                - volatility: 波动率
                
        Returns:
            情绪分析结果
        """
        # 获取权重
        weights = {
            'price': float(self.config['market_sentiment'].get('price_weight', 0.3)),
            'volume': float(self.config['market_sentiment'].get('volume_weight', 0.25)),
            'momentum': float(self.config['market_sentiment'].get('momentum_weight', 0.2)),
            'breadth': float(self.config['market_sentiment'].get('breadth_weight', 0.15)),
            'volatility': float(self.config['market_sentiment'].get('volatility_weight', 0.1))
        }
        
        # 计算各项得分（0-100）
        price_score = self._calculate_price_score(market_data.get('price_change', 0))
        volume_score = self._calculate_volume_score(market_data.get('volume_change', 0))
        momentum_score = market_data.get('momentum', 50)  # 假设已经计算好
        breadth_score = market_data.get('breadth', 50) * 100  # 转换为0-100
        volatility_score = self._calculate_volatility_score(market_data.get('volatility', 0))
        
        # 加权平均
        sentiment_score = (
            price_score * weights['price'] +
            volume_score * weights['volume'] +
            momentum_score * weights['momentum'] +
            breadth_score * weights['breadth'] +
            volatility_score * weights['volatility']
        )
        
        # 判断情绪等级
        sentiment_level = self._get_sentiment_level(sentiment_score)
        
        # 生成情绪描述
        description = self._describe_sentiment(sentiment_level, sentiment_score)
        
        # 交易建议
        advice = self._generate_sentiment_advice(sentiment_level)
        
        return {
            'score': round(sentiment_score, 2),
            'level': sentiment_level,
            'description': description,
            'advice': advice,
            'components': {
                'price_score': round(price_score, 2),
                'volume_score': round(volume_score, 2),
                'momentum_score': round(momentum_score, 2),
                'breadth_score': round(breadth_score, 2),
                'volatility_score': round(volatility_score, 2)
            }
        }
    
    def _calculate_price_score(self, price_change: float) -> float:
        """计算价格得分"""
        # price_change: -10% 到 +10% 映射到 0-100
        score = 50 + price_change * 5  # 1% = 5分
        return max(0, min(100, score))
    
    def _calculate_volume_score(self, volume_change: float) -> float:
        """计算成交量得分"""
        # 成交量温和放大为正面，过度放大或缩小为负面
        if volume_change > 0:
            if volume_change <= 0.5:  # 温和放大
                return 60 + volume_change * 40
            else:  # 过度放大
                return 70 - (volume_change - 0.5) * 20
        else:
            return 50 + volume_change * 30  # 缩量为负面
    
    def _calculate_volatility_score(self, volatility: float) -> float:
        """计算波动率得分"""
        # 波动率适中为正面，过高或过低为负面
        optimal_volatility = 0.02  # 2%为最佳波动率
        deviation = abs(volatility - optimal_volatility)
        score = 70 - deviation * 500  # 偏差越大得分越低
        return max(0, min(100, score))
    
    def _get_sentiment_level(self, score: float) -> str:
        """获取情绪等级"""
        very_bullish = float(self.config['market_sentiment'].get('very_bullish', 80))
        bullish = float(self.config['market_sentiment'].get('bullish', 60))
        neutral = float(self.config['market_sentiment'].get('neutral', 40))
        bearish = float(self.config['market_sentiment'].get('bearish', 20))
        
        if score >= very_bullish:
            return 'VERY_BULLISH'
        elif score >= bullish:
            return 'BULLISH'
        elif score >= neutral:
            return 'NEUTRAL'
        elif score >= bearish:
            return 'BEARISH'
        else:
            return 'VERY_BEARISH'
    
    def _describe_sentiment(self, level: str, score: float) -> str:
        """描述市场情绪"""
        descriptions = {
            'VERY_BULLISH': f'市场非常看多（得分{score:.0f}），投资者信心高涨，市场情绪乐观',
            'BULLISH': f'市场看多（得分{score:.0f}），投资者情绪积极，市场氛围良好',
            'NEUTRAL': f'市场中性（得分{score:.0f}），投资者观望情绪浓厚，市场方向不明',
            'BEARISH': f'市场看空（得分{score:.0f}），投资者情绪谨慎，市场氛围偏弱',
            'VERY_BEARISH': f'市场非常看空（得分{score:.0f}），投资者恐慌情绪蔓延，市场信心不足'
        }
        return descriptions.get(level, '未知情绪')
    
    def _generate_sentiment_advice(self, level: str) -> str:
        """根据情绪生成建议"""
        advices = {
            'VERY_BULLISH': '市场情绪高涨，可适当加仓，但注意止盈',
            'BULLISH': '市场情绪良好，持股待涨，逢低可加仓',
            'NEUTRAL': '市场方向不明，建议观望，控制仓位',
            'BEARISH': '市场情绪偏弱，建议减仓，等待机会',
            'VERY_BEARISH': '市场恐慌情绪蔓延，建议空仓观望，等待企稳'
        }
        return advices.get(level, '建议观望')


if __name__ == '__main__':
    # 测试
    config_path = '/root/.openclaw/workspace/trading/config.ini'
    
    # 测试量价分析
    vp_analyzer = VolumePriceAnalyzer(config_path)
    current_data = {
        'current_price': 12.48,
        'volume': 150000000,
        'change_pct': 5.23
    }
    historical_data = [
        {'volume': 100000000},
        {'volume': 110000000},
        {'volume': 120000000},
        {'volume': 90000000},
        {'volume': 105000000}
    ]
    vp_result = vp_analyzer.analyze(current_data, historical_data)
    print("量价分析结果:")
    print(json.dumps(vp_result, indent=2, ensure_ascii=False))
    
    # 测试市场情绪
    sentiment_analyzer = MarketSentimentAnalyzer(config_path)
    market_data = {
        'price_change': 0.0523,
        'volume_change': 0.5,
        'momentum': 65,
        'breadth': 0.6,
        'volatility': 0.025
    }
    sentiment_result = sentiment_analyzer.analyze(market_data)
    print("\n市场情绪分析结果:")
    print(json.dumps(sentiment_result, indent=2, ensure_ascii=False))
