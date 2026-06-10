# Adaptive Multi-Asset Trading Model

## Purpose

I built this project to practice applying Python to systematic trading research. The goal was not to create a production trading bot, but to better understand how signal logic, risk controls, position sizing, drawdown limits, and backtesting structure fit together in a multi-asset strategy.

This project helped me think through the difference between a strategy that looks good in theory and one that needs to survive realistic market conditions, changing regimes, and risk constraints.

## What It Does

The model is designed as a research framework for testing trading logic across multiple asset types.

Core components include:

- Multi-asset strategy logic
- Rule-based signal generation
- Backtesting workflow
- Position sizing and risk controls
- Drawdown and performance tracking
- Strategy evaluation metrics
- Optional experimental modules for sentiment or expectancy modeling

The project is intended for research and learning, not live trading.

## Project Structure

```text
adaptive-multi-asset-trading-model/
│
├── adaptive_multi_asset_trading_model.py
├── requirements.txt
├── .gitignore
├── .env.example
├── LICENSE
└── README.md
```

## How to Run

Clone the repository:

```bash
git clone https://github.com/williamtbon/adaptive-multi-asset-trading-model.git
cd adaptive-multi-asset-trading-model
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the model:

```bash
python adaptive_multi_asset_trading_model.py
```

If command-line options are available:

```bash
python adaptive_multi_asset_trading_model.py --help
```

## Configuration

If the model uses API keys or environment variables, create a local `.env` file based on `.env.example`.

Example:

```text
API_KEY=your_api_key_here
```

Do not upload real API keys, tokens, account credentials, or private data to GitHub.

## Example Use Cases

This project can be used to study:

- How a strategy performs under different market regimes
- How risk limits affect drawdowns
- How position sizing changes total return and volatility
- How adding more filters can improve or overcomplicate a model
- How backtest assumptions influence results

## What I Learned

While building this project, I learned that:

- Backtest results can change significantly when assumptions around sizing, exits, costs, or data handling change.
- Risk controls are just as important as entry signals.
- A model can become harder to interpret as more filters and asset classes are added.
- Good documentation matters because a complex script is difficult to review without a clear explanation of the workflow.
- Strategy performance should be evaluated through both return and downside-risk metrics, not returns alone.

## Limitations

This project has several important limitations:

- It is not a live trading system.
- Backtested results do not guarantee future performance.
- Market frictions such as slippage, liquidity, fees, and execution quality may not be fully reflected.
- Some assumptions may be simplified for educational purposes.
- The model should be reviewed carefully before any serious financial use.

## Future Improvements

Possible future improvements include:

- Splitting the main script into separate modules for data, signals, risk, backtesting, and reporting
- Adding cleaner configuration files
- Improving logging and error handling
- Adding more detailed performance reports
- Testing the model across different time periods and market environments
- Adding unit tests for major functions

## Disclaimer

This project is for educational and research purposes only. It is not financial advice, investment advice, or a recommendation to trade any security, cryptocurrency, derivative, or financial instrument.
