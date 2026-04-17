"""
generate_data.py
----------------
Generates a realistic synthetic poll dataset and saves it to data/poll_data.csv

Poll Topic: "Which political party / candidate do you support in the upcoming election?"
500 respondents across 5 regions, 4 age groups, 2 genders.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────────────
N = 500

REGIONS       = ["North", "South", "East", "West", "Central"]
AGE_GROUPS    = ["18-25", "26-35", "36-50", "51+"]
GENDERS       = ["Male", "Female", "Non-binary"]
OPTIONS       = ["Option A", "Option B", "Option C", "Option D"]
EDUCATION     = ["High School", "Bachelor's", "Master's", "PhD"]
EMPLOYMENT    = ["Employed", "Student", "Self-employed", "Unemployed"]

# Region-wise response biases (realistic skew)
REGION_BIAS = {
    "North":   [0.40, 0.30, 0.20, 0.10],
    "South":   [0.25, 0.40, 0.25, 0.10],
    "East":    [0.30, 0.25, 0.30, 0.15],
    "West":    [0.20, 0.25, 0.35, 0.20],
    "Central": [0.35, 0.30, 0.20, 0.15],
}

# Age group biases
AGE_BIAS = {
    "18-25": [0.20, 0.25, 0.40, 0.15],
    "26-35": [0.30, 0.30, 0.25, 0.15],
    "36-50": [0.40, 0.30, 0.20, 0.10],
    "51+":   [0.45, 0.30, 0.15, 0.10],
}

# ── Build rows ────────────────────────────────────────────────────────────────
def random_date(start_days_ago=90):
    base = datetime(2024, 1, 1)
    return base + timedelta(days=np.random.randint(0, start_days_ago))

rows = []
for i in range(1, N + 1):
    region     = np.random.choice(REGIONS)
    age_group  = np.random.choice(AGE_GROUPS, p=[0.25, 0.30, 0.27, 0.18])
    gender     = np.random.choice(GENDERS,    p=[0.48, 0.48, 0.04])
    education  = np.random.choice(EDUCATION,  p=[0.25, 0.45, 0.22, 0.08])
    employment = np.random.choice(EMPLOYMENT, p=[0.55, 0.20, 0.15, 0.10])

    # Combine region + age bias (weighted average)
    rb = np.array(REGION_BIAS[region])
    ab = np.array(AGE_BIAS[age_group])
    bias = (rb * 0.6 + ab * 0.4)
    bias = bias / bias.sum()

    selected_option = np.random.choice(OPTIONS, p=bias)
    date            = random_date(90)

    rows.append({
        "respondent_id":    f"R{i:04d}",
        "date":             date.strftime("%Y-%m-%d"),
        "question":         "Which option do you prefer for the upcoming election?",
        "selected_option":  selected_option,
        "region":           region,
        "age_group":        age_group,
        "gender":           gender,
        "education":        education,
        "employment":       employment,
    })

df = pd.DataFrame(rows)

# ── Add 2% noise (missing values) ────────────────────────────────────────────
noise_idx = np.random.choice(df.index, size=int(N * 0.02), replace=False)
df.loc[noise_idx, "selected_option"] = np.nan

# ── Save ──────────────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
df.to_csv("data/poll_data.csv", index=False)
print(f"✅  Dataset saved: data/poll_data.csv  ({len(df)} rows)")
print(df.head(10).to_string())
