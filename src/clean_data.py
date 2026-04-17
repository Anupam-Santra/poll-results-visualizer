"""
clean_data.py
-------------
Loads raw poll_data.csv, cleans it, and saves a clean version.
"""

import pandas as pd
import numpy as np
import os

df = pd.read_csv("data/poll_data.csv")
print(f"Raw shape: {df.shape}")
print(f"Missing values before cleaning:\n{df.isnull().sum()}\n")

# 1. Drop duplicates
before = len(df)
df = df.drop_duplicates(subset=["respondent_id"])
print(f"Dropped {before - len(df)} duplicate rows.")

# 2. Impute missing selected_option using region mode (safe approach)
region_modes = (df.dropna(subset=["selected_option"])
                  .groupby("region")["selected_option"]
                  .agg(lambda x: x.mode()[0]))
missing_mask = df["selected_option"].isna()
df.loc[missing_mask, "selected_option"] = df.loc[missing_mask, "region"].map(region_modes)
# Fallback global mode
global_mode = df["selected_option"].mode()[0]
df["selected_option"] = df["selected_option"].fillna(global_mode)
print(f"Missing values after imputation: {df['selected_option'].isnull().sum()}")

# 3. Standardise text columns
text_cols = ["selected_option", "region", "age_group", "gender", "education", "employment"]
for col in text_cols:
    df[col] = df[col].astype(str).str.strip().str.title()

# 4. Parse dates
df["date"] = pd.to_datetime(df["date"])

# 5. Week and month
df["week"] = df["date"].dt.isocalendar().week.astype(int)
df["month"] = df["date"].dt.month_name()

# 6. Age as ordered categorical
age_order = ["18-25", "26-35", "36-50", "51+"]
df["age_group"] = pd.Categorical(df["age_group"], categories=age_order, ordered=True)

os.makedirs("data", exist_ok=True)
df.to_csv("data/poll_data_clean.csv", index=False)
print(f"\n✅  Clean dataset saved: data/poll_data_clean.csv  ({len(df)} rows)")
print(df.dtypes)
print("\nSample:\n", df.head())
