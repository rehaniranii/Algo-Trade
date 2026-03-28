# 📈 Multi-Asset Algorithmic Trading Backtester

A scalable, rule-based **algorithmic trading backtesting engine** built in Python that supports multiple assets, advanced technical indicators, and portfolio-level risk management.

Designed for **quant experimentation, strategy validation, and rapid prototyping**, this project simulates realistic trading conditions using historical data.

---

## 🚀 Features

### 📂 Dynamic Multi-Asset Support

* Automatically loads all CSV datasets from a `/datasets` folder
* Handles multiple assets simultaneously
* No hardcoding required

---

### 📊 Technical Indicators

The strategy combines multiple indicators for robust signal generation:

* **MACD + Signal Line** → Momentum detection
* **EMA (20) vs SMA (50)** → Trend identification
* **RSI** → Overbought/Oversold conditions
* **Bollinger Bands** → Volatility + mean reversion
* **Fibonacci Retracement** → Key support/resistance levels

---

### 🧠 Smart Signal Engine

Each indicator contributes to a **scoring system**:

* Bullish signals → +1
* Bearish signals → -1

#### Trade Logic:

* **Buy** → Score ≥ 3
* **Sell** → Score ≤ -3

#### Exit Conditions:

* Stop-loss
* Trailing stop-loss
* Trend or momentum reversal

---

### 💼 Portfolio Management

* Initial capital: ₹10,00,000
* Position sizing: **30% capital per trade**
* Supports multiple concurrent positions
* Real-time portfolio valuation

---

### 🛡️ Risk Management

* **Hard Stop-Loss** (2%)
* **Trailing Stop-Loss** (dynamic)
* **Max Drawdown Tracking**

---

### 📈 Backtesting Metrics

At the end of the simulation, the system outputs:

* Final portfolio value
* Total profit/loss
* Return (%)
* Maximum drawdown
* Total trades executed
* Win rate (%)
* Average win / loss
* Trade-by-trade performance

---

### 🇮🇳 Indian Financial Formatting

All outputs are formatted in Indian number style:
`10,00,000.00` instead of `1,000,000.00`

---

## 🛠️ Installation

```bash
pip install pandas numpy
```



---

## ▶️ Usage

1. Add your datasets to the `/datasets` folder
2. Ensure each CSV contains required columns:

   * `close`, `high`, `low`
   * `rsi`, `macd`, `ema_20`, `sma_50`
3. Run the script:

```bash
python main.py
```

---

## 📌 Example Strategy Flow

1. Load datasets
2. Compute indicators
3. Generate signals
4. Execute trades
5. Manage portfolio
6. Track performance
7. Output final analytics

---

## ⚠️ Disclaimer

This project is intended for:

* Educational purposes
* Strategy research
* Backtesting experiments

**Not financial advice. Do not use directly for live trading without further validation.**

---

## 🔮 Future Improvements

* 🔹 Machine Learning-based signal optimization
* 🔹 Live trading integration (Zerodha Kite, Alpaca, etc.)
* 🔹 Parameter tuning / optimization engine
* 🔹 Visualization dashboard (Matplotlib / Plotly)
* 🔹 Transaction cost & slippage modeling

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork the repo and submit a pull request.

---

## ⭐ If you like this project

Give it a star ⭐ and consider building on top of it!

---

<img width="1200" height="600" alt="image" src="https://github.com/user-attachments/assets/7f7993fe-371f-4cf0-8e24-eb200536a378" />
<img width="1200" height="600" alt="image" src="https://github.com/user-attachments/assets/9f3fcebe-ec36-4c0e-b21c-1b18e6a9ed33" />
<img width="1000" height="500" alt="image" src="https://github.com/user-attachments/assets/20f1a143-652f-4fa3-a718-1583f7e427c4" />



