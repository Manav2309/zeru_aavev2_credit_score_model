# Aave V2 Wallet Credit Scoring Model

## 📌 Objective

This project builds a machine learning pipeline that assigns a **credit score between 0 and 1000** to DeFi wallets using historical transaction behavior from the **Aave V2 protocol**. The goal is to detect and differentiate between responsible wallets and those exhibiting risky or bot-like behavior.

---

## 🧠 Methodology

1. **Data Ingestion:**
   - The input is a raw JSON file containing ~100K user transactions from the Aave V2 protocol.
   - Each transaction includes actions like `deposit`, `borrow`, `repay`, `liquidationcall`, etc.

2. **Data Preprocessing:**
   - Normalize nested JSON fields using `json_normalize`.
   - Convert timestamp fields to datetime.
   - Calculate USD value of transactions using `amount * assetPriceUSD`.
   - Filled missing values using a combination of strategies:
     - **0** for missing numeric values in financial columns.
     - **"none"** for categorical ID fields like `liquidatorId`, `repayerId`.
     - **Mean or median** imputation for selected features where 0 may bias the model.
   - Removed unnecessary columns and parsed timestamps into lag features.

3. **Feature Engineering:**
   - **Temporal Behavior:** Time gaps between repeated `toId` interactions.
   - **Financial Metrics:** Aggregates (sum, mean, max, count) of loan-related fields per wallet.
   - **Activity Stats:** Borrow/repay/deposit frequency, total and average transaction value.
   - **Lag Analysis:** Delay between creation/update timestamps and actual interaction time.
   - **Binary Flags:** Indicators for presence of key fields (e.g., `has_borrowRate`, `has_collateralAmount`).
   - **Behavioral Metrics:** Interaction with most common `toIds`, count of repeated `toIds`.

4. **Model Inference:**
   - Multiple base models were used:
     - `Linear Regression`
     - `Random Forest Regressor` (with tuned hyperparameters)
     - `Gradient Boosting Regressor`
   - These were stacked into a **meta-learner ensemble** and trained on the engineered features.
   - The final model (`stacked_model.pkl`) was loaded using `joblib`.
   - Predicted `credit_score_raw` (0 to 1) was scaled to the range **0–1000** using `MinMaxScaler`.

---

## 🏗️ Architecture

```text
📦 main.py                     <- One-step script to load JSON and generate scores
📄 user-wallet-transactions.json <- Input data (not committed due to size limits)
📦 stacked_model.pkl           <- Trained ensemble model
📦 scaler.pkl                  <- Scaler used for feature normalization
📄 sample.ipynb                <- Training notebook with model development
📄 README.md                   <- Project documentation
📄 analysis.md                 <- Detailed score band interpretation and analysis
📄 wallet_scores.csv           <- Output CSV with wallet credit scores (userWallet, score, label)
