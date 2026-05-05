# 📈 Volatility-Filtered Momentum Algorithm
**Developer:** Carlo Ace Sagad  
**Program:** The Build Fellowship: Software Meets Wall Street (Spring 2026)

## 🚀 Project Overview
This repository contains my final project for the Open Avenues Build Fellowship. I engineered a regime-filtered trading algorithm using Python and the QuantConnect LEAN engine. 

**The Thesis:** Moving average crossovers perform well in trending markets but suffer severe drawdowns during market panic. By integrating external VIX data (Wall Street's Fear Gauge), the algorithm identifies regime changes and blocks trades or liquidates holdings when volatility spikes.

## 🛠️ Architecture & Failure Mode Defenses
To prepare this algorithm for live deployment, I implemented strict failure mode defenses:
* **External Data Pipeline:** Built a custom `PythonData` class to ingest remote CSV data for the VIX, allowing the algorithm to execute cross-asset logic.
* **Reality Modeling (Analytical Defense):** Injected `ConstantFeeModel` and `ConstantSlippageModel` to prevent the engine from making perfect-price assumptions.
* **State Persistence (Mechanical Defense):** Utilized QuantConnect's `self.object_store` to save the portfolio's `is_long` state to the cloud as a JSON object after every trade. Upon a server restart, the algorithm reads the object store to remember its position and avoid duplicate orders.

## 📊 Backtest Outcomes (2014 - 2017)
The final backtest resulted in a **-7.71% return**. While nominally negative, this outcome perfectly demonstrated the necessity of Reality Modeling. The raw strategy was highly profitable in a frictionless vacuum, but once real-world fees, slippage, and the "whipsaw" effect of the VIX emergency-sell filter were applied, the true operational cost was revealed. This confirms that failing to model reality leads to dangerous over-optimism in algorithmic trading.
