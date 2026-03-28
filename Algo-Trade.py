import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

CONFIG = {
    "position_size": 0.30,
    "stop_loss": 0.02,
    "trailing_stop": 0.015,
    "buy_threshold": 3,
    "sell_threshold": -3
}

# DYNAMICALLY LOAD ALL DATASETS FROM FOLDER
datasets_folder = 'datasets'
csv_files = sorted(glob.glob(os.path.join(datasets_folder, '*.csv')))

if not csv_files:
    print(f'Error: No CSV files found in {datasets_folder} folder')
    exit(1)

# Load all dataframes into a dictionary
dataframes = {}
asset_names = []

for csv_file in csv_files:
    asset_name = os.path.basename(csv_file).replace('.csv', '')
    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.lower()
    dataframes[asset_name] = df
    asset_names.append(asset_name)

print(f'Loaded {len(asset_names)} datasets: {", ".join(asset_names)}')

# APPLY INDICATORS TO ALL DATAFRAMES
for asset_name, df in dataframes.items():
    # MACD SIGNAL LINE
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    # TREND (EMA20 vs SMA50)
    df['trend'] = 0
    df.loc[df['ema_20'] > df['sma_50'], 'trend'] = 1
    df.loc[df['ema_20'] < df['sma_50'], 'trend'] = -1
    
    # MOMENTUM (MACD crossover)
    df['momentum'] = 0
    df.loc[df['macd'] > df['macd_signal'], 'momentum'] = 1
    df.loc[df['macd'] < df['macd_signal'], 'momentum'] = -1
    
    # BOLLINGER BANDS
    df['bb_middle'] = df['close'].rolling(20).mean()
    df['bb_std'] = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + (2 * df['bb_std'])
    df['bb_lower'] = df['bb_middle'] - (2 * df['bb_std'])
    df['bb_signal'] = 0
    df.loc[df['close'] < df['bb_lower'], 'bb_signal'] = 1
    df.loc[df['close'] > df['bb_upper'], 'bb_signal'] = -1
    
    # FIBONACCI RETRACEMENT
    df['recent_high'] = df['high'].rolling(20).max()
    df['recent_low'] = df['low'].rolling(20).min()
    df['fib_50'] = df['recent_low'] + 0.5 * (df['recent_high'] - df['recent_low'])
    df['fib_618'] = df['recent_low'] + 0.618 * (df['recent_high'] - df['recent_low'])
    df['fib_signal'] = 0
    df.loc[df['close'] <= df['fib_618'], 'fib_signal'] = 1
    df.loc[df['close'] >= df['fib_50'], 'fib_signal'] = -1

def format_indian(value):
    """Format number in Indian numbering system (e.g., 10,00,000.00)"""
    s = f'{value:.2f}'
    parts = s.split('.')
    integer_part = parts[0]
    decimal_part = parts[1]
    
    # Remove negative sign if present
    is_negative = integer_part.startswith('-')
    if is_negative:
        integer_part = integer_part[1:]
    
    # Format integer part with Indian commas
    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        # Last 3 digits
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        
        # Add commas every 2 digits from right to left in the remaining part
        parts_list = []
        for i in range(len(remaining), 0, -2):
            start = max(0, i - 2)
            parts_list.insert(0, remaining[start:i])
        
        formatted = ','.join(parts_list) + ',' + last_three
    
    if is_negative:
        formatted = '-' + formatted
    
    return f'{formatted}.{decimal_part}'

class Portfolio:
    def __init__(self, initial_cash=1000000):
        self.cash = initial_cash
        self.initial_capital = initial_cash
        self.positions = {}
        self.trades = []
        self.history = []
        self.peak_value = initial_cash
        self.max_drawdown = 0.0

    def add_position(self, asset, price, index, reason):
        position_value = self.cash * CONFIG["position_size"]
        shares = int(position_value / price)
        if shares > 0:
            cost = shares * price
            self.cash -= cost
            self.positions[asset] = {
                'shares': shares,
                'entry_price': price,
                'entry_index': index,
                'entry_value': cost,
                'stop_loss': price * (1 - CONFIG["stop_loss"]),
                'trailing_stop': price * (1 - CONFIG["trailing_stop"]),
                'highest_price': price,
            }
            self.trades.append({
                'action': 'BUY', 'asset': asset, 'index': index, 'price': price,
                'shares': shares, 'value': cost, 'reason': reason
            })
            return True
        return False

    def close_position(self, asset, price, index, reason):
        if asset in self.positions:
            pos = self.positions[asset]
            proceeds = pos['shares'] * price
            profit = proceeds - pos['entry_value']
            self.cash += proceeds
            self.trades.append({
                'action': 'SELL', 'asset': asset, 'index': index, 'price': price,
                'entry_price': pos['entry_price'], 'shares': pos['shares'],
                'profit': profit, 'return_pct': (profit / pos['entry_value'] * 100),
                'value': proceeds, 'reason': reason
            })
            del self.positions[asset]
            return True
        return False

    def get_portfolio_value(self, prices_dict):
        value = self.cash
        for asset, pos in self.positions.items():
            value += pos['shares'] * prices_dict.get(asset, pos['entry_price'])
        return value

    def update_history(self, prices_dict):
        current_val = self.get_portfolio_value(prices_dict)
        self.history.append(current_val)
        if current_val > self.peak_value:
            self.peak_value = current_val
        dd = (self.peak_value - current_val) / self.peak_value
        if dd > self.max_drawdown:
            self.max_drawdown = dd

portfolio = Portfolio(initial_cash=1000000)

print('Starting backtest with 1,000,000 initial capital...')
print('Analyzing signals and executing trades...')

# Get maximum number of bars across all datasets
max_bars = max(len(df) for df in dataframes.values())

for i in range(max_bars):
    
    # UPDATE TRAILING STOPS FOR ALL POSITIONS
    for asset, pos in list(portfolio.positions.items()):
        if asset in dataframes and i < len(dataframes[asset]):
            price = dataframes[asset].iloc[i]['close']
            if price > pos['highest_price']:
                pos['highest_price'] = price
                pos['trailing_stop'] = price * (1 - CONFIG["trailing_stop"])
    
    # TRADING LOGIC FOR EACH ASSET
    for asset_name in asset_names:
        if i >= len(dataframes[asset_name]):
            continue
        
        df = dataframes[asset_name]
        trend = df.iloc[i]['trend']
        momentum = df.iloc[i]['momentum']
        rsi = df.iloc[i]['rsi']
        bb_signal = df.iloc[i]['bb_signal']
        fib_signal = df.iloc[i]['fib_signal']
        price = df.iloc[i]['close']
        
        # CALCULATE SCORE
        score = 0
        if trend == 1: score += 1
        elif trend == -1: score -= 1
        if momentum == 1: score += 1
        elif momentum == -1: score -= 1
        if rsi < 30: score += 1
        elif rsi > 70: score -= 1
        if bb_signal == 1: score += 1
        elif bb_signal == -1: score -= 1
        if fib_signal == 1: score += 1
        elif fib_signal == -1: score -= 1
        
        # BUY SIGNAL
        if score >= CONFIG["buy_threshold"] and asset_name not in portfolio.positions:
            portfolio.add_position(asset_name, price, i, f'BUY s={score}')
        
        # SELL SIGNAL
        elif score <= CONFIG["sell_threshold"] and asset_name in portfolio.positions:
            portfolio.close_position(asset_name, price, i, f'SELL s={score}')
        
        # EXIT CONDITIONS FOR OPEN POSITIONS
        elif asset_name in portfolio.positions:
            pos = portfolio.positions[asset_name]
            
            # Hard stop loss
            if price <= pos['stop_loss']:
                portfolio.close_position(asset_name, price, i, 'STOP LOSS')
            # Trailing stop
            elif price <= pos['trailing_stop']:
                portfolio.close_position(asset_name, price, i, 'TRAILING STOP')
            # Trend or momentum reversal
            elif trend == -1 or momentum == -1:
                portfolio.close_position(asset_name, price, i, f'EXIT t={trend} m={momentum}')
    
    # UPDATE PORTFOLIO HISTORY
    prices_dict = {}
    for asset_name in asset_names:
        if i < len(dataframes[asset_name]):
            prices_dict[asset_name] = dataframes[asset_name].iloc[i]['close']
    portfolio.update_history(prices_dict)

# CLOSE REMAINING OPEN POSITIONS
final_prices = {}
max_index = {}
for asset_name in asset_names:
    final_prices[asset_name] = dataframes[asset_name].iloc[-1]['close']
    max_index[asset_name] = len(dataframes[asset_name]) - 1

for asset_name in asset_names:
    if asset_name in portfolio.positions:
        portfolio.close_position(asset_name, final_prices[asset_name], max_index[asset_name], 'End')

print('='*80)
print('FINAL PORTFOLIO SUMMARY')
print('='*80)

final_value = portfolio.get_portfolio_value(final_prices)
profit = final_value - portfolio.initial_capital
return_pct = (profit / portfolio.initial_capital) * 100

print(f'Initial Capital:        {format_indian(portfolio.initial_capital)}')
print(f'Final Portfolio Value:  {format_indian(final_value)}')
print(f'Total Profit/Loss:      {format_indian(profit)}')
print(f'Return Pct:             {return_pct:.2f}%')
print(f'Max Drawdown:           {portfolio.max_drawdown*100:.2f}%')

buy_trades = [t for t in portfolio.trades if t['action'] == 'BUY']
sell_trades = [t for t in portfolio.trades if t['action'] == 'SELL']

print(f'\nTotal Trades:           {len(portfolio.trades)}')
print(f'Buy Trades:             {len(buy_trades)}')

if sell_trades:
    profits = [t['profit'] for t in sell_trades]
    winning = len([p for p in profits if p > 0])
    losing = len([p for p in profits if p < 0])
    win_rate = (winning / len(sell_trades)) * 100
    
    print(f'Winning Trades:         {winning}')
    print(f'Win Rate Pct:           {win_rate:.2f}%')
    print(f'Total Trade P/L:        {format_indian(sum(profits))}')
    
    if winning > 0:
        avg_win = sum([p for p in profits if p > 0]) / winning
        print(f'Average Win:            {format_indian(avg_win)}')
    if losing > 0:
        avg_loss = sum([p for p in profits if p < 0]) / losing
        print(f'Average Loss:           {format_indian(avg_loss)}')

# ================= PERFORMANCE METRICS =================
returns = np.diff(portfolio.history) / portfolio.history[:-1]

if len(returns) > 0:
    avg_return = np.mean(returns)
    std_return = np.std(returns)

    sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return != 0 else 0

    total_years = len(portfolio.history) / 252
    cagr = ((portfolio.history[-1] / portfolio.history[0]) ** (1 / total_years)) - 1 if total_years > 0 else 0

    downside = returns[returns < 0]
    sortino = (avg_return / np.std(downside)) * np.sqrt(252) if len(downside) > 0 else 0

    print('\n' + '='*80)
    print('ADVANCED PERFORMANCE METRICS')
    print('='*80)
    print(f'Sharpe Ratio:           {sharpe_ratio:.3f}')
    print(f'Sortino Ratio:          {sortino:.3f}')
    print(f'CAGR:                   {cagr*100:.2f}%')

print('='*80)

# EQUITY CURVE
plt.figure(figsize=(12,6))
plt.plot(portfolio.history)
plt.title('Portfolio Equity Curve')
plt.xlabel('Time Steps')
plt.ylabel('Portfolio Value')
plt.grid()

plt.savefig('equity_curve.png')
plt.show()

# DRAWDOWN CALCULATION
history = np.array(portfolio.history)
running_max = np.maximum.accumulate(history)
drawdown = (running_max - history) / running_max

plt.figure(figsize=(12,6))
plt.plot(drawdown)
plt.title('Drawdown Curve')
plt.xlabel('Time Steps')
plt.ylabel('Drawdown')
plt.grid()

plt.savefig('drawdown_curve.png')
plt.show()

# TRADE PNL DISTRIBUTION
profits = [t['profit'] for t in portfolio.trades if t['action'] == 'SELL']

if profits:
    plt.figure(figsize=(10,5))
    plt.hist(profits, bins=30)
    plt.title('Trade Profit Distribution')
    plt.xlabel('Profit')
    plt.ylabel('Frequency')
    plt.grid()

    plt.savefig('pnl_distribution.png')
    plt.show()
