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
   - Filled missing values for financial fields (`borrowRate`, `collateralAmount`, etc.) with 0 or "none".

3. **Feature Engineering:**
   - **Temporal Behavior:** Time gaps between repeated `toId` interactions.
   - **Financial Metrics:** Aggregates (sum, mean, max, count) of loan-related fields per wallet.
   - **Activity Stats:** Borrow/repay/deposit frequency, total and average transaction value.
   - **Lag Analysis:** Delay between creation/update timestamps and actual interaction time.
   - **Binary Flags:** Indicators for presence of key fields (e.g., `has_borrowRate`, `has_collateralAmount`).
   - **Behavioral Metrics:** Interaction with most common `toIds`, count of repeated `toIds`.

4. **Model Inference:**
   - Models used:
     `Linear Regression`
     `Random Forest Regression`
     ``
   - Pre-trained stacking regression model (`stacked_model.pkl`) loaded via `joblib`.
   - Model predicts a raw `credit_score_raw` between 0 and 1.
   - This score is scaled to a 0–1000 range using `MinMaxScaler`.

---

## 🏗️ Architecture

```text
📦 main.py               <- One-step script to load JSON and generate scores
📦 stacked_model.pkl     <- Trained ensemble model
📦 scaler.pkl            <- Scaler used for feature normalization
📄 user-wallet-transactions.json <- Input data (not committed due to file size)
📦 sample.ipynb          <- Where the model was created, trained and tested on the preprocessed data with scores
