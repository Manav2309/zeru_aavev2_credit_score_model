import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import MinMaxScaler
import joblib

from pandas import json_normalize
json_path= r"C:\Users\vaish\Assessment_zeru\user-wallet-transactions.json"
with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
clean_data = json_normalize(data)    
df = pd.DataFrame(clean_data)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
df['createdAt'] = pd.to_datetime(df['createdAt.$date'])
df['updatedAt'] = pd.to_datetime(df['updatedAt.$date'])


df.drop(columns=['_id.$oid', '__v'], inplace=True, errors='ignore')

df['actionData.amount'] = pd.to_numeric(df['actionData.amount'], errors='coerce')
df['actionData.assetPriceUSD'] = pd.to_numeric(df['actionData.assetPriceUSD'], errors='coerce')

df['usd_value']= df['actionData.amount']* df['actionData.assetPriceUSD']

df_sorted = df.sort_values(['userWallet', 'actionData.toId', 'timestamp'])

df_sorted['toId_time_diff'] = df_sorted.groupby(['userWallet', 'actionData.toId'])['timestamp'].diff()

avg_toid_spacing = (
    df_sorted.groupby('userWallet')['toId_time_diff']
    .mean()
    .fillna(0)
    .rename('avg_toId_spacing_secs')
)
df_sorted['toId_time_diff'] = df_sorted['toId_time_diff'].fillna(0)

df_sorted["borrowRate"] = pd.to_numeric(df_sorted["actionData.borrowRate"], errors='coerce') / 1e27


fill_zero_cols = [
    "actionData.borrowRate", 
    "actionData.stableTokenDebt", 
    "actionData.variableTokenDebt", 
    "actionData.collateralAmount", 
    "actionData.collateralAssetPriceUSD", 
    "actionData.principalAmount", 
    "actionData.borrowAssetPriceUSD"
]

df_sorted[fill_zero_cols] = df_sorted[fill_zero_cols].fillna(0.0)

# Optional: convert ID columns to string 'none'
id_cols = [
    "actionData.liquidatorId", 
    "actionData.repayerId", 
    "actionData.callerId"
]
df_sorted[id_cols] = df_sorted[id_cols].fillna("none")

for col in fill_zero_cols:
    df_sorted[col] = pd.to_numeric(df_sorted[col], errors='coerce')
    
df_sorted[fill_zero_cols] = df_sorted[fill_zero_cols].fillna(0.0)
    
credit_features = df_sorted.groupby("userWallet")[fill_zero_cols].agg("sum").reset_index()
    
df_sorted["actionData.borrowRateMode"].value_counts()
df_sorted.drop(columns=['actionData.borrowRateMode'], inplace=True, errors='ignore')

df_sorted = df.sort_values(by=['userWallet', 'actionData.toId', 'timestamp'])

cols_to_convert = [
    "actionData.borrowRate",
    "actionData.stableTokenDebt",
    "actionData.variableTokenDebt",
    "actionData.collateralAmount",
    "actionData.collateralAssetPriceUSD",
    "actionData.principalAmount",
    "actionData.borrowAssetPriceUSD"
]

df_sorted[cols_to_convert] = df_sorted[cols_to_convert].apply(pd.to_numeric, errors='coerce')



borrow_agg = (
    df_sorted.groupby("userWallet")[cols_to_convert]
    .agg(["sum", "mean", "max", "count"])
    .fillna(0)
)
# Flatten multi-index column names
borrow_agg.columns = ['_'.join(col) for col in borrow_agg.columns]
borrow_agg = borrow_agg.reset_index()

# Compute time difference per wallet + toId group
df['toId_time_diff'] = df.groupby(['userWallet', 'actionData.toId'])['timestamp'].diff().dt.total_seconds()

# Compute per-wallet average spacing
avg_toid_spacing = (
    df.groupby('userWallet')['toId_time_diff']
    .mean()
    .fillna(0)
    .rename('avg_toId_spacing_secs')
)

# Count repeated toIds per userWallet
repeat_toid_count = (
    df.groupby(['userWallet', 'actionData.toId'])
    .size()
    .reset_index(name='tx_count')
    .query('tx_count > 1')
    .groupby('userWallet')
    .size()
    .rename('repeat_toId_interaction_count')
)
# Step 1: Find top 10 toIds overall
top_10_toids = df['actionData.toId'].value_counts().head(10).index

# Step 2: Flag if toId is in top 10
df['to_common_toId'] = df['actionData.toId'].isin(top_10_toids).astype(int)

# Step 3: Aggregate per wallet
tx_to_common_toid = (
    df.groupby('userWallet')['to_common_toId']
    .sum()
    .rename('tx_to_common_toId')
)
# Combine all features
wallet_features = pd.DataFrame(df['userWallet'].unique(), columns=['userWallet'])

wallet_features = (
    wallet_features
    .merge(avg_toid_spacing, on='userWallet', how='left')
    .merge(repeat_toid_count, on='userWallet', how='left')
    .merge(tx_to_common_toid, on='userWallet', how='left')
)

# Fill any remaining NaNs (wallets without repeated toIds, etc.)
wallet_features.fillna(0, inplace=True)
wallet_base = df.groupby('userWallet').agg(
    tx_count=('txHash', 'count'),
    total_usd_value=('usd_value', 'sum'),
    avg_usd_value=('usd_value', 'mean'),
    active_days=('timestamp', lambda x: (x.max() - x.min()).days),
    num_borrows=('action', lambda x: (x == 'borrow').sum()),
    num_repays=('action', lambda x: (x == 'repay').sum()),
    num_liquidations=('action', lambda x: (x == 'liquidationcall').sum()),
    num_deposits=('action', lambda x: (x == 'deposit').sum())
).reset_index()


final_df = (
    wallet_base
    .merge(wallet_features, on='userWallet', how='left')
)

df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize(None)
df['createdAt'] = pd.to_datetime(df['createdAt']).dt.tz_localize(None)
df['updatedAt'] = pd.to_datetime(df['updatedAt']).dt.tz_localize(None)

# Compute lag features
df['created_lag'] = (df['createdAt'] - df['timestamp']).dt.total_seconds()
df['updated_lag'] = (df['updatedAt'] - df['timestamp']).dt.total_seconds()

# Aggregate lag features per wallet
lag_features = df.groupby('userWallet').agg(
    avg_created_lag=('created_lag', 'mean'),
    max_created_lag=('created_lag', 'max'),
    avg_updated_lag=('updated_lag', 'mean'),
    max_updated_lag=('updated_lag', 'max')
).reset_index()

# Merge into final_df
final_df = final_df.merge(lag_features, on='userWallet', how='left')  
final_df = final_df.merge(borrow_agg, on="userWallet", how="left").fillna(0)

score_features = [
    'tx_count', 'total_usd_value', 'avg_usd_value',
    'num_borrows', 'num_repays', 'num_liquidations',
    'avg_toId_spacing_secs', 'repeat_toId_interaction_count',
    'tx_to_common_toId', 'avg_created_lag', 'max_created_lag',
    'actionData.borrowRate_mean', 'actionData.variableTokenDebt_sum',
    'actionData.collateralAmount_sum', 'actionData.principalAmount_sum'
]

scaler = MinMaxScaler()
scaled_feats = scaler.fit_transform(final_df[score_features])
scaled_df = pd.DataFrame(scaled_feats, columns=score_features)

# Replace or concatenate with final_df
for col in score_features:
    final_df[f'scaled_{col}'] = scaled_df[col]
    
    

df['has_borrow_rate'] = df['actionData.borrowRate'].notna().astype(int)

    
borrow_presence = df.groupby('userWallet')['has_borrow_rate'].sum().reset_index()
borrow_presence.rename(columns={'has_borrow_rate': 'borrow_rate_presence'}, inplace=True)

borrow_presence['borrow_rate_presence'] = (borrow_presence['borrow_rate_presence'] > 0).astype(int)

final_df = final_df.merge(borrow_presence, on='userWallet', how='left')
final_df['borrow_rate_presence'] = final_df['borrow_rate_presence'].fillna(0).astype(int)


cols = [
    'actionData.collateralAmount',
    'actionData.variableTokenDebt',
    'actionData.stableTokenDebt',
    'actionData.principalAmount',
    'actionData.borrowRate'
]

# Create binary flags
for col in cols:
    flag_col = f'has_{col.split(".")[-1]}'
    df[flag_col] = df[col].notna().astype(int)

# Group by wallet and sum flags
activity_flags = df.groupby('userWallet')[[f'has_{col.split(".")[-1]}' for col in cols]].sum().reset_index()

# Convert counts > 0 into 1 (i.e., presence flags)
for col in activity_flags.columns:
    if col != 'userWallet':
        activity_flags[col] = (activity_flags[col] > 0).astype(int)

final_df = final_df.merge(activity_flags, on='userWallet', how='left')

x = final_df.drop(columns=['userWallet'])


model= joblib.load('stacked_model.pkl')
scaler = joblib.load('scaler.pkl')

x_scaled = scaler.transform(x)
predictions = model.predict(x_scaled)

final_df['predicted_credit_score'] = predictions

def get_score_band(score):
    if 0 <= score <= 100:
        return 'Extremely risky / suspicious'
    elif score <= 200:
        return 'High risk'
    elif score <= 300:
        return 'Above-average risk'
    elif score <= 400:
        return 'Moderate risk'
    elif score <= 500:
        return 'Slightly below average'
    elif score <= 600:
        return 'Average'
    elif score <= 700:
        return 'low risk'
    elif score <= 800:
        return 'Very low risk'
    elif score <= 900:
        return 'Responsible, frequent activity'
    else:
        return 'Ideal behavior / top-tier wallets'

# Apply to each wallet's predicted score
final_df['score_band'] = final_df['predicted_credit_score'].apply(get_score_band)

# Export final output
final_df[['userWallet', 'predicted_credit_score', 'score_band']].to_csv("wallet_scores.csv", index=False)
