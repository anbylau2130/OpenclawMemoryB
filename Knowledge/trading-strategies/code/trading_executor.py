#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易执行模块 - Trading Module
功能：执行交易决策、仓位管理、订单管理、交易日志
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum


class OrderStatus(Enum):
    """订单状态"""
    PENDING = 'pending'      # 待执行
    FILLED = 'filled'        # 已成交
    CANCELLED = 'cancelled'  # 已取消
    FAILED = 'failed'        # 失败


class OrderType(Enum):
    """订单类型"""
    BUY = 'buy'
    SELL = 'sell'


class Order:
    """订单类"""
    
    def __init__(self, 
                 symbol: str,
                 order_type: OrderType,
                 price: float,
                 shares: int,
                 reason: str = ''):
        """
        初始化订单
        
        Args:
            symbol: 股票代码
            order_type: 订单类型
            price: 价格
            shares: 股数
            reason: 下单原因
        """
        self.order_id = f"{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.symbol = symbol
        self.order_type = order_type
        self.price = price
        self.shares = shares
        self.reason = reason
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.filled_at = None
        self.filled_price = None
        self.message = ''
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'order_type': self.order_type.value,
            'price': self.price,
            'shares': self.shares,
            'reason': self.reason,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'filled_at': self.filled_at.isoformat() if self.filled_at else None,
            'filled_price': self.filled_price,
            'message': self.message
        }


class Position:
    """持仓类"""
    
    def __init__(self, 
                 symbol: str,
                 shares: int,
                 buy_price: float,
                 buy_time: datetime):
        """
        初始化持仓
        
        Args:
            symbol: 股票代码
            shares: 持仓股数
            buy_price: 买入价格
            buy_time: 买入时间
        """
        self.symbol = symbol
        self.shares = shares
        self.buy_price = buy_price
        self.buy_time = buy_time
        self.current_price = buy_price
        self.stop_loss = buy_price * 0.98  # -2%（优化：-3% → -2%）
        self.take_profit_1 = buy_price * 1.06  # +6%
        self.take_profit_2 = buy_price * 1.10  # +10%
        self.sold_shares = 0  # 已卖出股数
    
    def update_price(self, current_price: float):
        """更新当前价格"""
        self.current_price = current_price
    
    def get_pnl(self) -> Tuple[float, float]:
        """
        计算盈亏
        
        Returns:
            (盈亏金额, 盈亏比例)
        """
        remaining_shares = self.shares - self.sold_shares
        if remaining_shares == 0:
            return 0, 0
        
        pnl_amount = (self.current_price - self.buy_price) * remaining_shares
        pnl_pct = (self.current_price - self.buy_price) / self.buy_price * 100
        
        return pnl_amount, pnl_pct
    
    def should_stop_loss(self) -> bool:
        """是否触发止损"""
        return self.current_price <= self.stop_loss
    
    def should_take_profit_1(self) -> bool:
        """是否触发第一档止盈"""
        return self.current_price >= self.take_profit_1 and self.sold_shares == 0
    
    def should_take_profit_2(self) -> bool:
        """是否触发第二档止盈"""
        return self.current_price >= self.take_profit_2 and self.sold_shares < self.shares * 0.7
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        pnl_amount, pnl_pct = self.get_pnl()
        
        return {
            'symbol': self.symbol,
            'shares': self.shares,
            'remaining_shares': self.shares - self.sold_shares,
            'buy_price': self.buy_price,
            'current_price': self.current_price,
            'stop_loss': self.stop_loss,
            'take_profit_1': self.take_profit_1,
            'take_profit_2': self.take_profit_2,
            'pnl_amount': round(pnl_amount, 2),
            'pnl_pct': round(pnl_pct, 2),
            'buy_time': self.buy_time.isoformat()
        }


class Portfolio:
    """投资组合类"""
    
    def __init__(self, initial_capital: float = 100000):
        """
        初始化投资组合
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.available_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.total_pnl = 0
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """获取持仓"""
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        """是否有持仓"""
        return symbol in self.positions and self.positions[symbol].shares > self.positions[symbol].sold_shares
    
    def get_total_value(self) -> float:
        """获取总资产"""
        position_value = sum(
            pos.shares * pos.current_price 
            for pos in self.positions.values()
        )
        return self.available_capital + position_value
    
    def get_total_pnl(self) -> Tuple[float, float]:
        """
        获取总盈亏
        
        Returns:
            (盈亏金额, 盈亏比例)
        """
        total_value = self.get_total_value()
        pnl_amount = total_value - self.initial_capital
        pnl_pct = (total_value - self.initial_capital) / self.initial_capital * 100
        
        return pnl_amount, pnl_pct
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        total_value = self.get_total_value()
        pnl_amount, pnl_pct = self.get_total_pnl()
        
        return {
            'initial_capital': self.initial_capital,
            'available_capital': round(self.available_capital, 2),
            'position_count': len([p for p in self.positions.values() if p.shares > p.sold_shares]),
            'total_value': round(total_value, 2),
            'total_pnl': round(pnl_amount, 2),
            'total_pnl_pct': round(pnl_pct, 2),
            'positions': {symbol: pos.to_dict() for symbol, pos in self.positions.items()}
        }


class TradingLogger:
    """交易日志记录器"""
    
    def __init__(self, log_dir: str = None):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志目录
        """
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / 'data' / 'trading_logs'
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 当日日志文件
        self.log_file = self.log_dir / f"trading_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    
    def log(self, event_type: str, data: Dict):
        """
        记录日志
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        
        # 追加写入日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def log_order(self, order: Order):
        """记录订单"""
        self.log('ORDER', order.to_dict())
    
    def log_trade(self, symbol: str, action: str, shares: int, price: float, pnl: float = None):
        """记录交易"""
        self.log('TRADE', {
            'symbol': symbol,
            'action': action,
            'shares': shares,
            'price': price,
            'pnl': pnl
        })
    
    def log_position_update(self, position: Position):
        """记录持仓更新"""
        self.log('POSITION_UPDATE', position.to_dict())
    
    def log_risk_alert(self, symbol: str, alert_type: str, message: str):
        """记录风险告警"""
        self.log('RISK_ALERT', {
            'symbol': symbol,
            'alert_type': alert_type,
            'message': message
        })


class TradingExecutor:
    """交易执行器"""
    
    def __init__(self,
                 initial_capital: float = 100000,
                 max_position_pct: float = 0.1,  # 优化：20% → 10%
                 max_total_position_pct: float = 0.6):  # 优化：80% → 60%
        """
        初始化交易执行器
        
        Args:
            initial_capital: 初始资金
            max_position_pct: 单只股票最大仓位比例
            max_total_position_pct: 总仓位最大比例
        """
        self.portfolio = Portfolio(initial_capital)
        self.max_position_pct = max_position_pct
        self.max_total_position_pct = max_total_position_pct
        self.logger = TradingLogger()
        
        self.orders: List[Order] = []
        self.pending_orders: List[Order] = []
    
    def calculate_position_size(self, 
                                price: float,
                                signal_strength: str = 'medium') -> int:
        """
        计算仓位大小
        
        Args:
            price: 股票价格
            signal_strength: 信号强度（'strong', 'medium', 'weak'）
            
        Returns:
            股数
        """
        # 根据信号强度调整仓位比例
        position_pct = {
            'strong': 0.30,   # 强信号：30%
            'medium': 0.20,   # 中等信号：20%
            'weak': 0.10      # 弱信号：10%
        }.get(signal_strength, 0.20)
        
        # 不超过单只股票最大仓位
        position_pct = min(position_pct, self.max_position_pct)
        
        # 计算可用资金
        available = self.portfolio.available_capital * position_pct
        
        # 计算股数（100股为一手）
        shares = int(available / price / 100) * 100
        
        return shares
    
    def can_buy(self, symbol: str, shares: int, price: float) -> Tuple[bool, str]:
        """
        检查是否可以买入
        
        Args:
            symbol: 股票代码
            shares: 股数
            price: 价格
            
        Returns:
            (是否可以买入, 原因)
        """
        # 检查是否已有持仓
        if self.portfolio.has_position(symbol):
            return False, "已有持仓"
        
        # 检查资金是否充足
        required_capital = shares * price
        if required_capital > self.portfolio.available_capital:
            return False, f"资金不足（需要{required_capital:.2f}，可用{self.portfolio.available_capital:.2f}）"
        
        # 检查总仓位是否超限
        current_position_value = sum(
            pos.shares * pos.current_price 
            for pos in self.portfolio.positions.values()
        )
        new_position_value = current_position_value + required_capital
        max_position_value = self.portfolio.initial_capital * self.max_total_position_pct
        
        if new_position_value > max_position_value:
            return False, f"总仓位超限（当前{current_position_value:.2f}，新增{required_capital:.2f}，上限{max_position_value:.2f}）"
        
        return True, "可以买入"
    
    def create_buy_order(self, 
                        symbol: str,
                        price: float,
                        shares: int = None,
                        signal_strength: str = 'medium',
                        reason: str = '') -> Order:
        """
        创建买入订单
        
        Args:
            symbol: 股票代码
            price: 价格
            shares: 股数（None则自动计算）
            signal_strength: 信号强度
            reason: 买入原因
            
        Returns:
            订单对象
        """
        # 计算仓位
        if shares is None:
            shares = self.calculate_position_size(price, signal_strength)
        
        # 检查是否可以买入
        can_buy, msg = self.can_buy(symbol, shares, price)
        
        # 创建订单
        order = Order(symbol, OrderType.BUY, price, shares, reason)
        
        if not can_buy:
            order.status = OrderStatus.FAILED
            order.message = msg
        else:
            order.status = OrderStatus.PENDING
            self.pending_orders.append(order)
        
        self.orders.append(order)
        self.logger.log_order(order)
        
        return order
    
    def execute_buy_order(self, order: Order, current_price: float = None) -> bool:
        """
        执行买入订单
        
        Args:
            order: 订单对象
            current_price: 当前价格（None则使用订单价格）
            
        Returns:
            是否成功
        """
        if order.status != OrderStatus.PENDING:
            return False
        
        # 使用当前价格或订单价格
        fill_price = current_price or order.price
        
        # 扣除资金
        cost = order.shares * fill_price
        if cost > self.portfolio.available_capital:
            order.status = OrderStatus.FAILED
            order.message = "资金不足"
            self.logger.log_order(order)
            return False
        
        # 执行买入
        self.portfolio.available_capital -= cost
        
        # 创建持仓
        position = Position(
            symbol=order.symbol,
            shares=order.shares,
            buy_price=fill_price,
            buy_time=datetime.now()
        )
        self.portfolio.positions[order.symbol] = position
        
        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now()
        order.filled_price = fill_price
        
        # 从待执行列表移除
        if order in self.pending_orders:
            self.pending_orders.remove(order)
        
        # 记录日志
        self.logger.log_order(order)
        self.logger.log_trade(order.symbol, 'BUY', order.shares, fill_price)
        self.logger.log_position_update(position)
        
        return True
    
    def create_sell_order(self,
                         symbol: str,
                         shares: int,
                         price: float,
                         reason: str = '') -> Order:
        """
        创建卖出订单
        
        Args:
            symbol: 股票代码
            shares: 股数
            price: 价格
            reason: 卖出原因
            
        Returns:
            订单对象
        """
        # 检查持仓
        position = self.portfolio.get_position(symbol)
        if not position:
            order = Order(symbol, OrderType.SELL, price, shares, reason)
            order.status = OrderStatus.FAILED
            order.message = "无持仓"
            self.orders.append(order)
            self.logger.log_order(order)
            return order
        
        # 检查可卖股数
        available_shares = position.shares - position.sold_shares
        if shares > available_shares:
            shares = available_shares
        
        # 创建订单
        order = Order(symbol, OrderType.SELL, price, shares, reason)
        order.status = OrderStatus.PENDING
        self.pending_orders.append(order)
        self.orders.append(order)
        self.logger.log_order(order)
        
        return order
    
    def execute_sell_order(self, order: Order, current_price: float = None) -> bool:
        """
        执行卖出订单
        
        Args:
            order: 订单对象
            current_price: 当前价格
            
        Returns:
            是否成功
        """
        if order.status != OrderStatus.PENDING:
            return False
        
        # 获取持仓
        position = self.portfolio.get_position(order.symbol)
        if not position:
            order.status = OrderStatus.FAILED
            order.message = "无持仓"
            self.logger.log_order(order)
            return False
        
        # 使用当前价格或订单价格
        fill_price = current_price or order.price
        
        # 计算盈亏
        pnl = (fill_price - position.buy_price) * order.shares
        
        # 执行卖出
        self.portfolio.available_capital += order.shares * fill_price
        position.sold_shares += order.shares
        position.update_price(fill_price)
        
        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now()
        order.filled_price = fill_price
        
        # 从待执行列表移除
        if order in self.pending_orders:
            self.pending_orders.remove(order)
        
        # 记录日志
        self.logger.log_order(order)
        self.logger.log_trade(order.symbol, 'SELL', order.shares, fill_price, pnl)
        self.logger.log_position_update(position)
        
        return True
    
    def check_risk_alerts(self, symbol: str, current_price: float):
        """
        检查风险告警
        
        Args:
            symbol: 股票代码
            current_price: 当前价格
        """
        position = self.portfolio.get_position(symbol)
        if not position:
            return
        
        position.update_price(current_price)
        
        # 检查止损
        if position.should_stop_loss():
            self.logger.log_risk_alert(
                symbol, 
                'STOP_LOSS',
                f"触发止损！当前价{current_price:.2f}，止损价{position.stop_loss:.2f}"
            )
        
        # 检查第一档止盈
        if position.should_take_profit_1():
            self.logger.log_risk_alert(
                symbol,
                'TAKE_PROFIT_1',
                f"触发第一档止盈！当前价{current_price:.2f}，止盈价{position.take_profit_1:.2f}，建议卖出30%"
            )
        
        # 检查第二档止盈
        if position.should_take_profit_2():
            self.logger.log_risk_alert(
                symbol,
                'TAKE_PROFIT_2',
                f"触发第二档止盈！当前价{current_price:.2f}，止盈价{position.take_profit_2:.2f}，建议卖出40%"
            )
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        return self.portfolio.to_dict()
    
    def get_trade_history(self) -> List[Dict]:
        """获取交易历史"""
        return [order.to_dict() for order in self.orders if order.status == OrderStatus.FILLED]


# 使用示例
if __name__ == '__main__':
    # 创建交易执行器
    executor = TradingExecutor(initial_capital=100000)
    
    print("="*60)
    print("交易模块测试")
    print("="*60)
    
    # 1. 买入测试
    print("\n【买入测试】")
    order1 = executor.create_buy_order(
        symbol='600031',
        price=20.85,
        signal_strength='strong',
        reason='V5选股：VWAP+布林带+RSI，得分4.5'
    )
    print(f"订单创建: {order1.order_id}")
    print(f"订单状态: {order1.status.value}")
    print(f"订单股数: {order1.shares}股")
    
    # 执行买入
    success = executor.execute_buy_order(order1, current_price=20.85)
    print(f"执行结果: {'成功' if success else '失败'}")
    
    # 2. 查看持仓
    print("\n【持仓情况】")
    summary = executor.get_portfolio_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # 3. 风险告警测试
    print("\n【风险告警测试】")
    # 模拟价格下跌触发止损
    executor.check_risk_alerts('600031', current_price=20.20)  # 低于止损价
    
    # 模拟价格上涨触发止盈
    executor.check_risk_alerts('600031', current_price=22.10)  # 触发第一档止盈
    
    # 4. 卖出测试
    print("\n【卖出测试】")
    position = executor.portfolio.get_position('600031')
    sell_shares = int(position.shares * 0.3)  # 卖出30%
    
    order2 = executor.create_sell_order(
        symbol='600031',
        shares=sell_shares,
        price=22.10,
        reason='触发第一档止盈（+6%）'
    )
    
    success = executor.execute_sell_order(order2, current_price=22.10)
    print(f"卖出订单: {order2.order_id}")
    print(f"执行结果: {'成功' if success else '失败'}")
    print(f"卖出股数: {order2.shares}股")
    print(f"成交价格: ¥{order2.filled_price:.2f}")
    
    # 5. 最终持仓
    print("\n【最终持仓】")
    summary = executor.get_portfolio_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # 6. 交易历史
    print("\n【交易历史】")
    history = executor.get_trade_history()
    for trade in history:
        print(f"{trade['order_type'].upper()}: {trade['symbol']} "
              f"{trade['shares']}股 @ ¥{trade['filled_price']:.2f}")
