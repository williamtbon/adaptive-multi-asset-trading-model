# Adaptive Multi-Asset Trading Model

## Purpose

I built this project to practice turning trading ideas into a structured Python model. The main goal was not to create a production trading system, but to better understand how signal logic, position sizing, risk controls, and backtesting assumptions all interact.

One thing I learned from working on this model is that backtest results can change a lot from small changes in exits, sizing, or risk rules. That made the project useful because it forced me to think beyond just “does the strategy make money?” and focus more on how the model behaves under different assumptions.

## What This Project Does

This project tests trading logic across multiple asset types and evaluates the results through a backtesting workflow.

Main features include:

* Multi-asset trading logic
* Rule-based signal generation
* Position sizing rules
* Risk controls and drawdown tracking
* Backtesting and performance review
* Basic performance metrics
* Optional experimental sentiment or expectancy-modeling components

The project is meant for research, learning, and portfolio demonstration.

## Project Structure

```text
adaptive-multi-asset-trading-model/
│
├── adaptive_multi_asset_trading_model.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## How to Run

Clone the repository:

```bash
git clone https://github.com/williamtbon/adaptive-multi-asset-trading-model.git
cd adaptive-multi-asset-trading-model
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the model:

```bash
python adaptive_multi_asset_trading_model.py
```

To check available command-line options:

```bash
python adaptive_multi_asset_trading_model.py --help
```

## Configuration

If the model uses API keys or environment variables, create a local `.env` file using `.env.example` as a guide.

Example:

```text
API_KEY=your_api_key_here
```

Real API keys, tokens, account credentials, or private data should not be uploaded to GitHub.

## Notes From Building This

This project helped me understand that a trading model is more than just entry signals. The risk framework, sizing rules, and exit assumptions can have just as much impact as the signal itself.

A challenge I ran into was keeping the model understandable as more features were added. It is easy to keep adding filters, but that can make the system harder to interpret. Because of that, I tried to keep the project focused on learning how the full workflow fits together: data, signals, sizing, risk, backtesting, and review.

## Example Use Cases

This project can be used to study:

* How different risk rules affect backtest results
* How position sizing changes return and drawdown behavior
* How performance changes across market conditions
* How a strategy responds when assumptions are adjusted
* How downside-risk metrics can give more context than return alone

## Limitations

This project has important limitations:

* It is not a live trading system.
* Backtested results do not guarantee future performance.
* Transaction costs, liquidity, slippage, and execution quality may not be fully modeled.
* Some assumptions are simplified for educational purposes.
* The model should be reviewed carefully before being used for any serious financial decision-making.

## Future Improvements

Future improvements could include:

* Splitting the main script into separate modules for data, signals, risk, backtesting, and reporting
* Adding more detailed logging
* Adding cleaner configuration files
* Improving performance reports
* Testing across more time periods and market environments
* Adding unit tests for important functions
* Improving documentation around assumptions

## Disclaimer

This project is for educational and research purposes only. It is not financial advice, investment advice, or a recommendation to trade any security, cryptocurrency, derivative, or financial instrument.
