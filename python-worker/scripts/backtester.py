# python-worker/scripts/backtester.py
"""
Event-driven backtesting engine with:
- Multiple strategy support
- Slippage modeling
- Commission calculations
"""
import pandas as pd
from typing import Callable, Dict
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    MARKET = 1
    LIMIT = 2

@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    side: str  # 'long' or 'short'

class Backtester:
    def __init__(self, data: pd.DataFrame, initial_balance: float = 10000):
        self.data = data
        self.balance = initial_balance
        self.position = 0
        self.trades: list[Trade] = []
        self.current_bar = 0
        self.commission = 0.0005  # 0.05% per trade
        self.slippage = 0.0003    # 0.03% slippage

    def next(self) -> bool:
        """Move to next bar"""
        if self.current_bar >= len(self.data) - 1:
            return False
        self.current_bar += 1
        return True

    def execute_order(self, size: float, order_type: OrderType = OrderType.MARKET) -> float:
        """Execute order with slippage and commission"""
        current_price = self.data.iloc[self.current_bar]['close']
        slippage = current_price * self.slippage * (1 if size > 0 else -1)
        fill_price = current_price + slippage
        cost = abs(size) * fill_price * self.commission
        self.balance -= cost
        return fill_price

    def enter_long(self, size_pct: float = 0.1):
        """Open long position"""
        if self.position != 0:
            return
        size = self.balance * size_pct
        price = self.execute_order(size)
        self.position = size / price
        self.trades.append(Trade(
            entry_time=self.data.iloc[self.current_bar].name,
            exit_time=None,
            entry_price=price,
            exit_price=None,
            size=size,
            pnl=None,
            side='long'
        ))

    def exit_position(self):
        """Close current position"""
        if self.position == 0:
            return
        price = self.execute_order(-self.position)
        trade = next(t for t in reversed(self.trades) if t.exit_time is None)
        trade.exit_time = self.data.iloc[self.current_bar].name
        trade.exit_price = price
        trade.pnl = (trade.exit_price - trade.entry_price) * trade.size
        self.balance += trade.pnl
        self.position = 0

    def run_strategy(self, strategy: Callable):
        """Run custom strategy function"""
        while self.next():
            strategy(self)

    def get_performance(self) -> Dict:
        """Calculate key metrics"""
        winning_trades = [t for t in self.trades if t.pnl > 0]
        return {
            'final_balance': self.balance,
            'total_trades': len(self.trades),
            'win_rate': len(winning_trades) / len(self.trades) if self.trades else 0,
            'max_drawdown': self._calculate_drawdown()
        }

    def _calculate_drawdown(self) -> float:
        equity_curve = []
        balance = self.balance
        for trade in self.trades:
            balance += trade.pnl
            equity_curve.append(balance)
        peak = max(equity_curve)
        trough = min(equity_curve)
        return (peak - trough) / peak
    
# Run Backtest:
# # Example strategy
# def moving_average_cross(bt: Backtester):
#     data = bt.data.iloc[:bt.current_bar+1]
#     if len(data) < 50:
#         return
    
#     short_ma = data['close'].rolling(10).mean().iloc[-1]
#     long_ma = data['close'].rolling(50).mean().iloc[-1]
    
#     if short_ma > long_ma and bt.position <= 0:
#         bt.exit_position()
#         bt.enter_long()
#     elif short_ma < long_ma and bt.position >= 0:
#         bt.exit_position()

# # Execute
# data = pd.read_csv('data/ETH-USDT_15m.csv', index_col='timestamp')
# backtester = Backtester(data)
# backtester.run_strategy(moving_average_cross)
# print(backtester.get_performance())
