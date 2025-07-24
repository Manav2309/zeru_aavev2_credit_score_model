# 📊 Wallet Credit Score Analysis (Aave V2)

## 🔍 Overview

This document presents an analytical summary of the credit scoring model developed for wallets interacting with the Aave V2 protocol. Based on transaction-level behavioral signals, each wallet is assigned a **credit score between 0 and 1000**, with higher scores indicating healthier, more responsible financial behavior.

The model is designed to aid DeFi risk assessment, incentivization, and credit underwriting decisions.

---

## 📈 Score Distribution

![Score Distribution](./score_distribution.png)

### Key Observations:
- The score distribution is **right-skewed**, with a majority of wallets concentrated in the **0–200** range.
- A secondary peak around **400–500** indicates a population of moderately active wallets.
- The presence of extreme low scores signals potential **bot activity**, **one-time usage**, or **exploit patterns**.

---

## 📊 Model Evaluation: Predicted vs Actual Scores

![Actual vs Predicted Scores](./actual_vs_predicted.png)

### Model Insights:
- The stacked model demonstrates **high predictive alignment**, with most predictions tightly clustered around the diagonal.
- A few visible outliers may represent wallets with **abnormal feature combinations** (e.g., high USD volume but minimal interaction diversity).
- The model generalizes well across different behavioral patterns, ensuring reliable scoring across heterogeneous users.

---

## 🎯 Score Band Behavior Breakdown

| Score Range | Label                          | Behavioral Pattern Summary                                                                 |
|-------------|----------------------------------|---------------------------------------------------------------------------------------------|
| 0–100       | Extremely risky / suspicious    | Short lifespan, liquidation-prone, high bot-like or flash-loan behavior                    |
| 101–200     | High risk                       | Minimal repayments, collateral misuse, repeated single-pool interaction                    |
| 201–300     | Above-average risk              | Low transaction value, inconsistent activity, skewed borrow/repay ratio                    |
| 301–400     | Moderate risk                   | Improved diversity and frequency, limited liquidation, average duration                    |
| 401–500     | Slightly below average          | Balanced, mid-range activity with consistent but conservative DeFi usage                   |
| 501–600     | Average                         | Stable borrowing behavior, low liquidation, long engagement duration                       |
| 601–700     | Low risk                        | Strong borrow-repay patterns, frequent deposits, responsible risk management               |
| 701–800     | Very low risk                   | High value activity, frequent participation across lending and liquidity provisioning      |
| 801–900     | Responsible / frequent          | Long-term users with reliable credit footprint and frequent protocol interaction           |
| 901–1000    | Ideal / elite wallets           | Top-tier users with high value, no liquidations, and strong long-term behavioral signals   |

---

## 📌 Strategic Insights

### Protocol-Level Use Cases:
- **Risk-Based Lending**: Offer better terms to wallets in the 700+ range.
- **Liquidation Risk Flagging**: Actively monitor 0–200 wallets for toxic behavior.
- **User Incentives**: Target 800+ wallets for loyalty campaigns and airdrops.

### Fraud & Automation Detection:
- Repetitive interactions with top `toIds`, frequent zero-collateral borrows, and high liquidation rates correlate with exploitative patterns.
- The system flags such wallets even with limited transaction counts by tracking time-based and interaction-based signals.

### Model Extensibility:
- The score bands are **transparent** and **auditable**, and the system can be adapted to:
  - Integrate token balance or staking features.
  - Factor in on-chain identity indicators (ENS, POAP, Gitcoin).
  - Apply temporal weighting to favor recent activity trends.

---

## 🔄 Conclusion

This credit scoring model enables transparent, data-driven segmentation of wallet risk profiles on DeFi protocols. The system effectively captures behavioral nuances while remaining extensible for future on-chain credit primitives.

---
