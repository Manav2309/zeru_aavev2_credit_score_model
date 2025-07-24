# Aave V2 Wallet Credit Scoring Model

## 📌 Objective

This project builds a machine learning pipeline that assigns a **credit score between 0 and 1000** to DeFi wallets using their historical transaction behavior on the **Aave V2 protocol**. The goal is to identify responsible users, detect risky or suspicious wallets, and enable smarter DeFi lending decisions.

---

## 🧠 Methodology

### 1. Data Ingestion
- Raw JSON file (~100K records) contains Aave V2 user transactions.
- Transactions include actions like `deposit`, `borrow`, `repay`, `redeem`, and `liquidationcall`.

### 2. Data Preprocessing
- Flattened nested JSON using `json_normalize`.
- Converted timestamp fields to readable datetime.
- Computed USD value for each transaction (`amount × assetPriceUSD`).
- **Missing value handling:**
  - `0` for missing numeric values (e.g., `collateralAmount`, `borrowRate`).
  - `"none"` for categorical fields (`liquidatorId`, `repayerId`).
  - Used **mean/median** imputation where `0` would introduce bias.
- Derived lag features between timestamps (`createdAt`, `updatedAt` vs `timestamp`).

### 3. Feature Engineering
- **Temporal behavior:** Time gaps between repeated `toId` interactions.
- **Financial metrics:** Aggregates (sum, mean, max, count) per wallet for loan-related fields.
- **Activity stats:** Borrow/repay/deposit frequency, transaction volume.
- **Lag analysis:** Delays between event creation/update and execution time.
- **Binary flags:** Indicators for presence of fields like `borrowRate`, `principalAmount`.
- **Behavioral patterns:** Interaction with popular `toIds`, repeated interaction count.

### 4. Credit Score Creation
- A **custom score** (our target) was created using the engineered wallet features.
- This raw score was scaled to a **0–1000** range using `MinMaxScaler`.

### 5. Model Training & Inference
- Used and compared multiple models:
  - `Linear Regression`
  - `Random Forest Regressor` (with tuned hyperparameters)
  - `Gradient Boosting Regressor`
- Built a **stacked ensemble model** using these as base learners.
- Final predictions were generated using `stacked_model.pkl` and scaled appropriately.

---

## 🏗️ Project Structure

```text
📦 main.py                     <- Main script to load data and generate scores
📄 user-wallet-transactions.json <- Input transaction data (excluded from repo)
📦 stacked_model.pkl           <- Trained ensemble model file
📦 scaler.pkl                  <- Scaler used for normalizing features
📄 sample.ipynb                <- Notebook with feature engineering + model training
📄 README.md                   <- This documentation
📄 analysis.md                 <- Score distribution analysis & behavioral insights
📄 wallet_scores.csv           <- Output: userWallet + credit_score + score_band
