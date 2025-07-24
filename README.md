# DeFi Credit Scoring using Aave V2 Protocol

## 🔍 Overview

This project assigns a **credit score between 0 and 1000** to DeFi wallets based solely on their historical transaction behavior on the Aave V2 protocol. The goal is to identify **responsible**, **risky**, or **bot-like** wallets using a feature-rich ML pipeline.

> **Higher scores = more reliable users**,  
> **Lower scores = suspicious or exploitative behavior**.

---

## 🧠 Approach

1. **Data Source**:  
   Raw transaction-level JSON data from Aave V2 (100K records).

2. **Preprocessing**:
   - Converted timestamps
   - Cleaned nested JSON fields
   - Standardized numerical columns
   - Computed USD value of transactions

3. **Feature Engineering**:
   - Aggregated borrow behavior: sums, averages, max
   - Interaction behavior with `toId`:
     - Average time spacing
     - Count of repeated interactions
     - Interaction with top 10 most common `toId`s
   - Lag features: time difference between transaction and `createdAt`, `updatedAt`
   - Borrow collateral & debt metrics
   - Action type counts (`borrow`, `repay`, `liquidation`, etc.)

4. **Scoring Logic**:
   - Applied **MinMaxScaler** on selected features
   - Weights manually assigned based on financial intuition
   - Custom formula used to compute `credit_score_raw`
   - Final score scaled to range **0–1000**
   - Categorized into `low`, `medium`, `high` risk classes

5. **Model Prediction** *(optional)*:
   - Trained ensemble (StackingRegressor) using selected features
   - Stored as `stacked_model.pkl` with corresponding `scaler.pkl`
   - Used in prediction script for automatic scoring

---

## 🛠️ File Structure

