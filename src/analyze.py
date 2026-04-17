"""
analyze.py
----------
Performs all analytical computations on the clean dataset and
prints a structured insights report.

Analyses:
  1.  Overall vote share (%)
  2.  Region-wise breakdown
  3.  Age-group breakdown
  4.  Gender breakdown
  5.  Education-level breakdown
  6.  Employment-status breakdown
  7.  Week-over-week trend
  8.  Cross-tab: Region × Option
  9.  Leading option detection
  10. Insights summary (text)
"""

import pandas as pd
import numpy as np

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("data/poll_data_clean.csv")
df["date"] = pd.to_datetime(df["date"])

OPTIONS  = sorted(df["selected_option"].unique())
TOTAL    = len(df)

print("=" * 60)
print("       POLL RESULTS VISUALIZER — ANALYSIS REPORT")
print("=" * 60)
print(f"\nTotal respondents : {TOTAL}")
print(f"Date range        : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"Options           : {OPTIONS}\n")

# ── 1. Overall vote share ─────────────────────────────────────────────────────
print("── 1. OVERALL VOTE SHARE ───────────────────────────────")
overall = (df["selected_option"]
           .value_counts()
           .reset_index()
           .rename(columns={"count": "votes"}))
overall["share_%"] = (overall["votes"] / TOTAL * 100).round(2)
print(overall.to_string(index=False))

# ── 2. Region-wise ────────────────────────────────────────────────────────────
print("\n── 2. REGION-WISE BREAKDOWN ────────────────────────────")
region_df = (df.groupby(["region", "selected_option"])
               .size()
               .reset_index(name="votes"))
region_total = df.groupby("region").size().reset_index(name="total")
region_df = region_df.merge(region_total, on="region")
region_df["share_%"] = (region_df["votes"] / region_df["total"] * 100).round(2)
print(region_df.to_string(index=False))

# ── 3. Age-group breakdown ────────────────────────────────────────────────────
print("\n── 3. AGE-GROUP BREAKDOWN ──────────────────────────────")
age_order = ["18-25", "26-35", "36-50", "51+"]
age_df = (df.groupby(["age_group", "selected_option"])
            .size()
            .reset_index(name="votes"))
age_total = df.groupby("age_group").size().reset_index(name="total")
age_df = age_df.merge(age_total, on="age_group")
age_df["share_%"] = (age_df["votes"] / age_df["total"] * 100).round(2)
print(age_df.to_string(index=False))

# ── 4. Gender breakdown ───────────────────────────────────────────────────────
print("\n── 4. GENDER BREAKDOWN ─────────────────────────────────")
gender_df = (df.groupby(["gender", "selected_option"])
               .size()
               .reset_index(name="votes"))
print(gender_df.to_string(index=False))

# ── 5. Education breakdown ────────────────────────────────────────────────────
print("\n── 5. EDUCATION BREAKDOWN ──────────────────────────────")
edu_df = (df.groupby(["education", "selected_option"])
            .size()
            .reset_index(name="votes"))
print(edu_df.to_string(index=False))

# ── 6. Employment breakdown ───────────────────────────────────────────────────
print("\n── 6. EMPLOYMENT BREAKDOWN ─────────────────────────────")
emp_df = (df.groupby(["employment", "selected_option"])
            .size()
            .reset_index(name="votes"))
print(emp_df.to_string(index=False))

# ── 7. Weekly trend ───────────────────────────────────────────────────────────
print("\n── 7. WEEKLY TREND ─────────────────────────────────────")
trend_df = (df.groupby(["week", "selected_option"])
              .size()
              .reset_index(name="votes"))
print(trend_df.head(20).to_string(index=False))

# ── 8. Cross-tab Region × Option ─────────────────────────────────────────────
print("\n── 8. CROSS-TAB: REGION × OPTION ──────────────────────")
xtab = pd.crosstab(df["region"], df["selected_option"], margins=True)
print(xtab)

# ── 9. Leading option per region ─────────────────────────────────────────────
print("\n── 9. LEADING OPTION PER REGION ────────────────────────")
leaders = (df.groupby(["region", "selected_option"])
             .size()
             .reset_index(name="votes")
             .sort_values("votes", ascending=False)
             .groupby("region")
             .first()
             .reset_index()[["region", "selected_option", "votes"]])
print(leaders.to_string(index=False))

# ── 10. Insights summary ──────────────────────────────────────────────────────
winner = overall.iloc[0]
runner = overall.iloc[1]
margin = round(winner["share_%"] - runner["share_%"], 2)

print("\n── 10. KEY INSIGHTS ────────────────────────────────────")
print(f"""
  ✅  Leading option   : {winner['selected_option']} with {winner['share_%']}% of votes ({winner['votes']} respondents)
  🥈  Runner-up        : {runner['selected_option']} with {runner['share_%']}% (margin: {margin}pp)
  🌍  Strongest region : {leaders.sort_values('votes', ascending=False).iloc[0]['region']} favours {leaders.sort_values('votes', ascending=False).iloc[0]['selected_option']}
  👥  Total responses  : {TOTAL}
  📅  Survey period    : {df['date'].min().strftime('%d %b %Y')} – {df['date'].max().strftime('%d %b %Y')}
""")

print("=" * 60)
print("Analysis complete. Run visualize.py to generate charts.")
print("=" * 60)
