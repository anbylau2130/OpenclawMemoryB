"""
《交易策略评估与优化》策略实现
"""

import pandas as pd
import numpy as np


class StrategyEvaluation:
    """策略评估"""

    @staticmethod
    def sharpe_ratio_optimization(df: pd.DataFrame) -> pd.DataFrame:
        """夏普比率优化"""
        df = df.copy()
        df['return'] = df['close'].pct_change()
        df['vol'] = df['return'].rolling(20).std()
        df['sharpe'] = df['return'].rolling(20).mean() / df['vol']
        df['signal'] = 0
        df.loc[df['sharpe'] > df['sharpe'].quantile(0.7), 'signal'] = 1
        return df

    @staticmethod
    def max_drawdown_control(df: pd.DataFrame, limit: float = 0.1) -> pd.DataFrame:
        """最大回撤控制"""
        df = df.copy()
        df['cummax'] = df['close'].cummax()
        df['drawdown'] = (df['close'] - df['cummax']) / df['cummax']
        df['signal'] = 0
        df.loc[df['drawdown'] > -limit, 'signal'] = 1
        return df

    @staticmethod
    def calmar_ratio(df: pd.DataFrame) -> pd.DataFrame:
        """卡玛比率"""
        df = df.copy()
        df['return'] = df['close'].pct_change(252)
        df['drawdown'] = (df['close'] - df['close'].cummax()) / df['close'].cummax()
        df['calmar'] = df['return'] / df['drawdown'].abs()
        df['signal'] = 0
        df.loc[df['calmar'] > df['calmar'].quantile(0.7), 'signal'] = 1
        return df

    @staticmethod
    def information_ratio(df: pd.DataFrame) -> pd.DataFrame:
        """信息比率"""
        df = df.copy()
        df['return'] = df['close'].pct_change()
        df['benchmark'] = df['return'].rolling(60).mean()
        df['active_return'] = df['return'] - df['benchmark']
        df['tracking_error'] = df['active_return'].rolling(60).std()
        df['ir'] = df['active_return'].rolling(60).mean() / df['tracking_error']
        df['signal'] = 0
        df.loc[df['ir'] > 0, 'signal'] = 1
        return df

    @staticmethod
    def sortino_ratio(df: pd.DataFrame) -> pd.DataFrame:
        """索提诺比率"""
        df = df.copy()
        df['return'] = df['close'].pct_change()
        df['downside'] = df['return'][df['return'] < 0].rolling(20).std()
        df['sortino'] = df['return'].rolling(20).mean() / df['downside']
        df['signal'] = 0
        df.loc[df['sortino'] > df['sortino'].quantile(0.7), 'signal'] = 1
        return df


class StrategyOptimization:
    """策略优化"""

    @staticmethod
    def parameter_optimization(df: pd.DataFrame) -> pd.DataFrame:
        """参数优化"""
        df = df.copy()
        best_sharpe = -999
        best_signal = 0

        for window in [5, 10, 20, 30]:
            df['ma'] = df['close'].rolling(window).mean()
            df['test_signal'] = (df['close'] > df['ma']).astype(int)
            df['test_return'] = df['close'].pct_change() * df['test_signal'].shift(1)
            sharpe = df['test_return'].mean() / df['test_return'].std()

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_signal = df['test_signal']

        df['signal'] = best_signal
        return df

    @staticmethod
    def walk_forward_analysis(df: pd.DataFrame) -> pd.DataFrame:
        """滚动窗口分析"""
        df = df.copy()
        df['train_signal'] = 0
        df['test_signal'] = 0

        for i in range(60, len(df), 20):
            train = df.iloc[i-60:i]
            test = df.iloc[i:i+20]

            ma_window = 20 if train['close'].pct_change().std() < 0.02 else 10
            df.iloc[i:i+20, df.columns.get_loc('test_signal')] = (
                test['close'].rolling(ma_window).mean() < test['close']
            ).astype(int).values

        df['signal'] = df['test_signal']
        return df

    @staticmethod
    def cross_validation(df: pd.DataFrame) -> pd.DataFrame:
        """交叉验证"""
        df = df.copy()
        df['fold1'] = (df['close'].rolling(5).mean() > df['close'].rolling(20).mean()).astype(int)
        df['fold2'] = (df['close'].rolling(10).mean() > df['close'].rolling(30).mean()).astype(int)
        df['fold3'] = (df['close'].rolling(15).mean() > df['close'].rolling(40).mean()).astype(int)
        df['vote'] = df['fold1'] + df['fold2'] + df['fold3']
        df['signal'] = 0
        df.loc[df['vote'] >= 2, 'signal'] = 1
        return df

    @staticmethod
    def monte_carlo_simulation(df: pd.DataFrame) -> pd.DataFrame:
        """蒙特卡洛模拟"""
        df = df.copy()
        df['return'] = df['close'].pct_change()
        mean_return = df['return'].mean()
        std_return = df['return'].std()

        # 模拟100次
        simulations = []
        for _ in range(100):
            sim_return = np.random.normal(mean_return, std_return, len(df))
            sim_price = df['close'].iloc[0] * (1 + sim_return).cumprod()
            simulations.append(sim_price[-1])

        df['expected_price'] = np.mean(simulations)
        df['signal'] = 0
        df.loc[df['expected_price'] > df['close'], 'signal'] = 1
        return df

    @staticmethod
    def sensitivity_analysis(df: pd.DataFrame) -> pd.DataFrame:
        """敏感性分析"""
        df = df.copy()
        # 测试不同参数的稳健性
        signals = []
        for window in [5, 10, 15, 20, 25]:
            signals.append((df['close'] > df['close'].rolling(window).mean()).astype(int))

        df['consensus'] = sum(signals) / len(signals)
        df['signal'] = 0
        df.loc[df['consensus'] > 0.7, 'signal'] = 1  # 70%以上一致
        return df


def test_strategy_evaluation():
    """测试策略评估"""
    import pandas as pd
    import numpy as np

    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 2)
    volume = np.random.randint(100000, 5000000, 200)
    df = pd.DataFrame({'close': close, 'volume': volume}, index=dates)

    print("夏普优化:", StrategyEvaluation.sharpe_ratio_optimization(df)['signal'].value_counts().to_dict())
    print("回撤控制:", StrategyEvaluation.max_drawdown_control(df)['signal'].value_counts().to_dict())
    print("卡玛比率:", StrategyEvaluation.calmar_ratio(df)['signal'].value_counts().to_dict())
    print("信息比率:", StrategyEvaluation.information_ratio(df)['signal'].value_counts().to_dict())
    print("索提诺:", StrategyEvaluation.sortino_ratio(df)['signal'].value_counts().to_dict())
    print("参数优化:", StrategyOptimization.parameter_optimization(df)['signal'].value_counts().to_dict())
    print("滚动窗口:", StrategyOptimization.walk_forward_analysis(df)['signal'].value_counts().to_dict())
    print("交叉验证:", StrategyOptimization.cross_validation(df)['signal'].value_counts().to_dict())
    print("蒙特卡洛:", StrategyOptimization.monte_carlo_simulation(df)['signal'].value_counts().to_dict())
    print("敏感性分析:", StrategyOptimization.sensitivity_analysis(df)['signal'].value_counts().to_dict())


if __name__ == '__main__':
    test_strategy_evaluation()
