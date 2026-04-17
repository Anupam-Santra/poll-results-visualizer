"""
visualize.py
------------
Generates 7 publication-quality charts from the clean poll dataset.
All charts are saved to outputs/ as PNG files (300 dpi).

Charts produced:
  1.  Overall vote share — horizontal bar chart
  2.  Overall vote share — donut / pie chart
  3.  Region-wise comparison — grouped bar chart
  4.  Age-group comparison — stacked bar chart
  5.  Gender breakdown — clustered bar chart
  6.  Weekly trend — multi-line chart
  7.  Heatmap: Region × Option
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

# ── Setup ─────────────────────────────────────────────────────────────────────
os.makedirs("outputs", exist_ok=True)
df = pd.read_csv("data/poll_data_clean.csv")
df["date"] = pd.to_datetime(df["date"])

PALETTE    = ["#2563EB", "#16A34A", "#DC2626", "#D97706"]   # A, B, C, D
OPTION_CLR = {opt: PALETTE[i] for i, opt in enumerate(sorted(df["selected_option"].unique()))}
TOTAL      = len(df)
FONT       = "DejaVu Sans"

plt.rcParams.update({
    "font.family":      FONT,
    "axes.spines.top":  False,
    "axes.spines.right": False,
    "axes.grid":        True,
    "grid.color":       "#E5E7EB",
    "grid.linewidth":   0.8,
    "figure.dpi":       150,
})

# ── Helper: annotate bars ─────────────────────────────────────────────────────
def annotate_bars(ax, fmt="{:.1f}%", offset=0.3):
    for bar in ax.patches:
        h = bar.get_height()
        if h > 0.5:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + offset,
                fmt.format(h),
                ha="center", va="bottom", fontsize=8, color="#374151"
            )

def save(fig, name):
    path = f"outputs/{name}.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✅  Saved: {path}")

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 1 — Horizontal bar: Overall vote share
# ═══════════════════════════════════════════════════════════════════════════════
def chart1_overall_bar():
    data = (df["selected_option"]
            .value_counts()
            .reset_index()
            .rename(columns={"count": "votes"}))
    data["share"] = data["votes"] / TOTAL * 100
    data = data.sort_values("share", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 4))
    colors = [OPTION_CLR[o] for o in data["selected_option"]]
    bars = ax.barh(data["selected_option"], data["share"], color=colors,
                   height=0.55, edgecolor="white")
    for bar, val in zip(bars, data["share"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=11, fontweight="bold")

    ax.set_xlabel("Vote Share (%)", fontsize=11)
    ax.set_title("Overall Poll Results — Vote Share by Option",
                 fontsize=14, fontweight="bold", pad=14)
    ax.set_xlim(0, data["share"].max() + 10)
    ax.axvline(25, color="#9CA3AF", linestyle="--", linewidth=0.8, label="25% line")
    ax.legend(fontsize=9)
    fig.tight_layout()
    save(fig, "chart1_overall_bar")

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 2 — Donut chart: Overall vote share
# ═══════════════════════════════════════════════════════════════════════════════
def chart2_donut():
    data = df["selected_option"].value_counts()
    colors = [OPTION_CLR[o] for o in data.index]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        data.values,
        labels=data.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        pctdistance=0.82,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    )
    for t in autotexts:
        t.set_fontsize(12)
        t.set_fontweight("bold")
        t.set_color("white")

    centre = plt.Circle((0, 0), 0.45, color="white")
    ax.add_artist(centre)
    ax.text(0, 0.06, f"{TOTAL}", ha="center", va="center",
            fontsize=22, fontweight="bold", color="#111827")
    ax.text(0, -0.14, "Responses", ha="center", va="center",
            fontsize=11, color="#6B7280")
    ax.set_title("Overall Vote Share — Donut Chart",
                 fontsize=14, fontweight="bold", pad=16)
    save(fig, "chart2_donut")

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 3 — Grouped bar: Region-wise
# ═══════════════════════════════════════════════════════════════════════════════
def chart3_region_grouped():
    pivot = (df.groupby(["region", "selected_option"])
               .size()
               .unstack(fill_value=0))
    pct   = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(11, 5))
    pct.plot(kind="bar", ax=ax, color=PALETTE, width=0.75,
             edgecolor="white", linewidth=0.5)
    annotate_bars(ax, fmt="{:.0f}%", offset=0.4)
    ax.set_xlabel("Region", fontsize=11)
    ax.set_ylabel("Vote Share (%)", fontsize=11)
    ax.set_title("Region-wise Poll Results — Vote Share per Option",
                 fontsize=14, fontweight="bold", pad=14)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=10)
    ax.legend(title="Option", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    fig.tight_layout()
    save(fig, "chart3_region_grouped")

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 4 — Stacked bar: Age-group
# ═══════════════════════════════════════════════════════════════════════════════
def chart4_age_stacked():
    age_order = ["18-25", "26-35", "36-50", "51+"]
    pivot = (df.groupby(["age_group", "selected_option"])
               .size()
               .unstack(fill_value=0))
    pivot = pivot.reindex(age_order)
    pct   = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = np.zeros(len(pct))
    for i, col in enumerate(pct.columns):
        bars = ax.bar(pct.index, pct[col], bottom=bottom, color=PALETTE[i],
                      label=col, edgecolor="white", linewidth=0.5)
        for bar, val in zip(bars, pct[col]):
            if val > 5:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_y() + bar.get_height() / 2,
                        f"{val:.0f}%", ha="center", va="center",
                        fontsize=9, color="white", fontweight="bold")
        bottom += pct[col].values

    ax.set_xlabel("Age Group", fontsize=11)
    ax.set_ylabel("Vote Share (%)", fontsize=11)
    ax.set_title("Age-Group Breakdown — Stacked Vote Share",
                 fontsize=14, fontweight="bold", pad=14)
    ax.legend(title="Option", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    ax.set_ylim(0, 105)
    fig.tight_layout()
    save(fig, "chart4_age_stacked")

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 5 — Clustered bar: Gender
# ═══════════════════════════════════════════════════════════════════════════════
def chart5_gender():
    pivot = (df.groupby(["gender", "selected_option"])
               .size()
               .unstack(fill_value=0))
    pct   = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(9, 5))
    pct.plot(kind="bar", ax=ax, color=PALETTE, width=0.7,
             edgecolor="white", linewidth=0.5)
    annotate_bars(ax, fmt="{:.0f}%", offset=0.4)
    ax.set_xlabel("Gender", fontsize=11)
    ax.set_ylabel("Vote Share (%)", fontsize=11)
    ax.set_title("Gender-wise Poll Results",
                 fontsize=14, fontweight="bold", pad=14)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=10)
    ax.legend(title="Option", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
    fig.tight_layout()
    save(fig, "chart5_gender")

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 6 — Line chart: Weekly trend
# ═══════════════════════════════════════════════════════════════════════════════
def chart6_trend():
    trend = (df.groupby(["week", "selected_option"])
               .size()
               .reset_index(name="votes"))
    total_per_week = df.groupby("week").size().reset_index(name="total")
    trend = trend.merge(total_per_week, on="week")
    trend["share"] = trend["votes"] / trend["total"] * 100

    fig, ax = plt.subplots(figsize=(11, 5))
    for option in sorted(df["selected_option"].unique()):
        sub = trend[trend["selected_option"] == option].sort_values("week")
        ax.plot(sub["week"], sub["share"], marker="o", markersize=5,
                linewidth=2, label=option, color=OPTION_CLR[option])

    ax.set_xlabel("Week Number (2024)", fontsize=11)
    ax.set_ylabel("Vote Share (%)", fontsize=11)
    ax.set_title("Weekly Trend — Vote Share Over Time",
                 fontsize=14, fontweight="bold", pad=14)
    ax.legend(title="Option", fontsize=9)
    fig.tight_layout()
    save(fig, "chart6_weekly_trend")

# ═══════════════════════════════════════════════════════════════════════════════
# Chart 7 — Heatmap: Region × Option
# ═══════════════════════════════════════════════════════════════════════════════
def chart7_heatmap():
    pivot = (df.groupby(["region", "selected_option"])
               .size()
               .unstack(fill_value=0))
    pct   = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(
        pct, annot=True, fmt=".1f", cmap="Blues",
        linewidths=0.5, linecolor="#E5E7EB",
        cbar_kws={"label": "Vote Share (%)"},
        ax=ax
    )
    ax.set_title("Heatmap: Region × Option — Vote Share (%)",
                 fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Option", fontsize=11)
    ax.set_ylabel("Region", fontsize=11)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()
    save(fig, "chart7_heatmap")

# ═══════════════════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n🎨  Generating charts...\n")
    chart1_overall_bar()
    chart2_donut()
    chart3_region_grouped()
    chart4_age_stacked()
    chart5_gender()
    chart6_trend()
    chart7_heatmap()
    print("\n✅  All 7 charts saved to outputs/\n")
