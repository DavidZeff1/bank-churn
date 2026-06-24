"""
Bank Churn – Step 2: EDA, KPIs & Deep-Dive Analysis
====================================================
Loads the clean dataset, engineers analysis features, computes the bank's
retention KPIs and every segment churn table, prints an evidence-backed findings
report, and renders presentation-quality charts (PNG) used by the deck.

Outputs:
  deliverables/kpis.json            – headline KPIs + segment tables (for the deck)
  deliverables/findings.md          – written findings with evidence
  deliverables/segment_tables.xlsx  – all churn-by-segment tables
  deliverables/charts/*.png         – static charts
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, FuncFormatter

BASE = Path(__file__).resolve().parent.parent
CLEAN = BASE / "deliverables" / "bank_churn_clean.csv"
CHARTS = BASE / "deliverables" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

# ---- house style -------------------------------------------------------
NAVY, TEAL, RED, GREY, AMBER = "#1f3a5f", "#2a9d8f", "#e63946", "#8d99ae", "#e9c46a"
RETAINED, CHURNED = "#4c72b0", "#e63946"
plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 150, "font.size": 12,
    "font.family": "DejaVu Sans", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25,
    "axes.titlesize": 15, "axes.titleweight": "bold", "axes.titlecolor": NAVY,
})
def pct(ax): ax.yaxis.set_major_formatter(PercentFormatter(1.0))
def save(fig, name):
    fig.tight_layout(); fig.savefig(CHARTS / name, bbox_inches="tight"); plt.close(fig)
def barlabels(ax, fmt="{:.1%}", off=0.01, color=NAVY):
    for p in ax.patches:
        h = p.get_height()
        if np.isfinite(h):
            ax.annotate(fmt.format(h), (p.get_x()+p.get_width()/2, h+off),
                        ha="center", va="bottom", fontweight="bold",
                        fontsize=11, color=color)

df = pd.read_csv(CLEAN)
N = len(df)

# ---- feature engineering ----------------------------------------------
df["AgeGroup"] = pd.cut(df["Age"], [17,30,40,50,60,100],
                        labels=["18–30","31–40","41–50","51–60","60+"])
df["TenureGroup"] = pd.cut(df["Tenure"], [-1,2,5,8,10],
                           labels=["0–2","3–5","6–8","9–10"])
df["BalanceBand"] = pd.cut(df["Balance"], [-1,0,50000,100000,150000,1e9],
                           labels=["Zero","€0–50k","€50–100k","€100–150k","€150k+"])
df["CreditBand"] = pd.cut(df["CreditScore"], [349,580,670,740,851],
                          labels=["Poor (<580)","Fair (580–669)","Good (670–739)","Excellent (740+)"])
df["ProductGroup"] = df["NumOfProducts"].map({1:"1",2:"2",3:"3",4:"4"})
df["HasBalance"] = (df["Balance"] > 0).astype(int)

baseline = df["Exited"].mean()

def churn_by(col, order=None):
    g = df.groupby(col, observed=True).agg(
        customers=("Exited","size"),
        churned=("Exited","sum"),
        churn_rate=("Exited","mean"),
        balance=("Balance","sum")).reset_index()
    g["lift_vs_avg"] = g["churn_rate"] / baseline
    if order is not None:
        g[col] = pd.Categorical(g[col], order); g = g.sort_values(col)
    return g

# ====================================================== KPIs
churned = df[df.Exited == 1]
retained = df[df.Exited == 0]
NIM = 0.025                       # illustrative net-interest-margin on deposits (revenue proxy)
HI_THRESH = 100_000               # "high-balance" customer threshold
hi = df[df.Balance > HI_THRESH]
kpis = {
    # ---- base counts ----
    "total_customers": int(N),
    "churned_customers": int(df.Exited.sum()),
    "inactive_customers": int((df.IsActiveMember == 0).sum()),
    # ---- success-metric rates ----
    "churn_rate": float(baseline),
    "retention_rate": float(1 - baseline),
    "active_member_rate": float(df.IsActiveMember.mean()),
    "cross_sell_rate": float((df.NumOfProducts >= 2).mean()),
    "single_product_share": float((df.NumOfProducts == 1).mean()),
    "avg_products": float(df.NumOfProducts.mean()),
    # ---- deposits & value ----
    "total_balance": float(df.Balance.sum()),
    "balance_at_risk": float(churned.Balance.sum()),
    "balance_at_risk_share": float(churned.Balance.sum()/df.Balance.sum()),
    "stable_deposits": float(retained.Balance.sum()),
    "avg_balance_per_customer": float(df.Balance.mean()),
    "avg_balance_churned": float(churned.Balance.mean()),
    "avg_balance_retained": float(retained.Balance.mean()),
    # ---- high-value churn ----
    "high_balance_threshold": HI_THRESH,
    "high_balance_customers": int(len(hi)),
    "high_balance_churn_rate": float(hi.Exited.mean()),
    # ---- revenue proxy (illustrative, NIM assumption) ----
    "nim_assumption": NIM,
    "revenue_proxy_annual": float(df.Balance.sum() * NIM),
    "revenue_at_risk_annual": float(churned.Balance.sum() * NIM),
}
# success-metric targets (direction-aware for status colouring)
targets = {
    "churn_rate":        {"target": 0.15, "lower_is_better": True},
    "retention_rate":    {"target": 0.85, "lower_is_better": False},
    "active_member_rate":{"target": 0.60, "lower_is_better": False},
    "cross_sell_rate":   {"target": 0.60, "lower_is_better": False},
}

print("="*64); print("HEADLINE KPIs"); print("="*64)
print(f"Customers ................. {kpis['total_customers']:,}")
print(f"Churn rate (PRIMARY) ...... {kpis['churn_rate']:.1%}  ({kpis['churned_customers']:,} lost)")
print(f"Retention rate ............ {kpis['retention_rate']:.1%}")
print(f"Balance at risk ........... €{kpis['balance_at_risk']:,.0f}  "
      f"({kpis['balance_at_risk_share']:.1%} of all deposits)")
print(f"Active-member rate ........ {kpis['active_member_rate']:.1%}")
print(f"Avg products / customer ... {kpis['avg_products']:.2f}  "
      f"(single-product: {kpis['single_product_share']:.1%})")
print("-"*64)
print(f"Deposits under mgmt ....... €{kpis['total_balance']/1e6:,.0f}M")
print(f"Avg balance / customer .... €{kpis['avg_balance_per_customer']:,.0f}")
print(f"Stable deposits ........... €{kpis['stable_deposits']/1e6:,.0f}M")
print(f"Cross-sell rate (2+ prod).. {kpis['cross_sell_rate']:.1%}")
print(f"High-balance churn (>€100k) {kpis['high_balance_churn_rate']:.1%}  "
      f"({kpis['high_balance_customers']:,} customers)")
print(f"Revenue at risk (~{NIM:.1%} NIM) €{kpis['revenue_at_risk_annual']/1e6:.1f}M / yr "
      f"of €{kpis['revenue_proxy_annual']/1e6:.1f}M total")

# ====================================================== segment tables
tables = {
    "Geography": churn_by("Geography", ["France","Germany","Spain"]),
    "Gender":    churn_by("Gender"),
    "AgeGroup":  churn_by("AgeGroup", ["18–30","31–40","41–50","51–60","60+"]),
    "NumOfProducts": churn_by("ProductGroup", ["1","2","3","4"]),
    "IsActiveMember": churn_by("IsActiveMember"),
    "BalanceBand": churn_by("BalanceBand", ["Zero","€0–50k","€50–100k","€100–150k","€150k+"]),
    "TenureGroup": churn_by("TenureGroup", ["0–2","3–5","6–8","9–10"]),
    "CreditBand": churn_by("CreditBand", ["Poor (<580)","Fair (580–669)","Good (670–739)","Excellent (740+)"]),
    "HasCrCard": churn_by("HasCrCard"),
}
for name, t in tables.items():
    print("\n" + "-"*64 + f"\nChurn by {name}\n" + "-"*64)
    show = t.copy()
    show["churn_rate"] = (show["churn_rate"]*100).round(1).astype(str)+"%"
    show["lift_vs_avg"] = show["lift_vs_avg"].round(2).astype(str)+"x"
    show["balance"] = (show["balance"]/1e6).round(1).astype(str)+"M"
    print(show.to_string(index=False))

# Germany high-balance combo
ger = df[df.Geography=="Germany"]
print("\n" + "-"*64 + "\nGermany focus\n" + "-"*64)
print(f"Germany churn {ger.Exited.mean():.1%} vs rest {df[df.Geography!='Germany'].Exited.mean():.1%}")
print(f"Germany avg balance €{ger.Balance.mean():,.0f} vs rest €{df[df.Geography!='Germany'].Balance.mean():,.0f}")

# Inactive + single-product combo (actionable segment)
seg = df[(df.IsActiveMember==0) & (df.NumOfProducts==1)]
print(f"\nInactive & single-product segment: {len(seg):,} customers, churn {seg.Exited.mean():.1%}")

# correlations with churn (numeric)
corr = df[["Exited","Age","Balance","NumOfProducts","IsActiveMember",
           "CreditScore","Tenure","HasCrCard","EstimatedSalary"]].corr()["Exited"].drop("Exited")
print("\nCorrelation with Exited:\n", corr.sort_values(key=abs, ascending=False).round(3).to_string())

# ====================================================== CHARTS
# 1) Overall churn donut
fig, ax = plt.subplots(figsize=(6,6))
ax.pie([1-baseline, baseline], labels=["Retained","Churned"],
       colors=[RETAINED, CHURNED], autopct="%1.1f%%", startangle=90,
       wedgeprops=dict(width=0.42, edgecolor="white"), textprops=dict(fontsize=14))
ax.text(0,0, f"{baseline:.1%}\nchurn", ha="center", va="center",
        fontsize=20, fontweight="bold", color=NAVY)
ax.set_title("1 in 5 customers churned"); save(fig, "01_overall_donut.png")

# 2) Geography
t = tables["Geography"]
fig, ax = plt.subplots(figsize=(8,5))
bars = ax.bar(t.Geography, t.churn_rate, color=[GREY if g!="Germany" else RED for g in t.Geography])
ax.axhline(baseline, ls="--", color=NAVY, lw=1.5)
ax.text(2.4, baseline+0.005, f"avg {baseline:.0%}", color=NAVY, fontweight="bold")
pct(ax); barlabels(ax); ax.set_ylim(0,0.40); ax.set_title("Germany churns at ~2× France & Spain")
ax.set_ylabel("Churn rate"); save(fig, "02_geography.png")

# 3) Products (the dramatic driver)
t = tables["NumOfProducts"]
fig, ax = plt.subplots(figsize=(8,5))
ax.bar(t.ProductGroup, t.churn_rate, color=[TEAL, TEAL, RED, RED])
pct(ax); barlabels(ax); ax.set_ylim(0,1.08)
ax.set_title("3–4 products = near-total churn"); ax.set_xlabel("Number of products")
ax.set_ylabel("Churn rate"); save(fig, "03_products.png")

# 4) Age group
t = tables["AgeGroup"]
fig, ax = plt.subplots(figsize=(8,5))
ax.bar(t.AgeGroup, t.churn_rate, color=NAVY)
ax.axhline(baseline, ls="--", color=RED, lw=1.5)
pct(ax); barlabels(ax); ax.set_ylim(0,0.62)
ax.set_title("Churn climbs with age, peaks at 51–60"); ax.set_xlabel("Age group")
ax.set_ylabel("Churn rate"); save(fig, "04_age.png")

# 5) Activity + Gender (grouped small multiples)
fig, axes = plt.subplots(1,2, figsize=(11,4.6))
ta = tables["IsActiveMember"]; ta["lbl"] = ta.IsActiveMember.map({0:"Inactive",1:"Active"})
axes[0].bar(ta.lbl, ta.churn_rate, color=[RED, TEAL]); pct(axes[0]); barlabels(axes[0])
axes[0].set_ylim(0,0.35); axes[0].set_title("Activity")
tg = tables["Gender"]
axes[1].bar(tg.Gender, tg.churn_rate, color=[RED, GREY]); pct(axes[1]); barlabels(axes[1])
axes[1].set_ylim(0,0.35); axes[1].set_title("Gender")
fig.suptitle("Inactive members and women churn more", fontsize=15, fontweight="bold", color=NAVY)
save(fig, "05_activity_gender.png")

# 6) Balance at risk by geography (€)
t = tables["Geography"].copy()
risk = churned.groupby("Geography", observed=True).Balance.sum().reindex(["France","Germany","Spain"])
fig, ax = plt.subplots(figsize=(8,5))
ax.bar(risk.index, risk.values/1e6, color=[GREY, RED, GREY])
for i,v in enumerate(risk.values):
    ax.annotate(f"€{v/1e6:.0f}M", (i, v/1e6+3), ha="center", fontweight="bold", color=NAVY)
ax.set_ylabel("Balance held by churned customers (€M)")
ax.set_title("Germany holds most of the balance walking out the door")
save(fig, "06_balance_at_risk.png")

# 7) Balance distribution churned vs retained
fig, ax = plt.subplots(figsize=(8,5))
for lab, sub, c in [("Retained", df[df.Exited==0], RETAINED), ("Churned", churned, CHURNED)]:
    ax.hist(sub.Balance/1000, bins=40, alpha=0.6, label=lab, color=c)
ax.set_xlabel("Balance (€000s)"); ax.set_ylabel("Customers")
ax.legend(); ax.set_title("Churners skew toward high balances (esp. the €120k+ cluster)")
save(fig, "07_balance_dist.png")

# ====================================================== persist
out = {"kpis": kpis, "targets": targets, "baseline": baseline,
       "tables": {k: v.assign(**{c: v[c] for c in v.columns}).to_dict(orient="list")
                  for k, v in tables.items()},
       "germany": {"churn": float(ger.Exited.mean()),
                   "avg_balance": float(ger.Balance.mean())},
       "corr": corr.round(4).to_dict()}
(BASE/"deliverables"/"kpis.json").write_text(json.dumps(out, indent=2, default=float))

with pd.ExcelWriter(BASE/"deliverables"/"segment_tables.xlsx") as xw:
    for k, t in tables.items():
        t.to_excel(xw, sheet_name=k[:31], index=False)

print("\nSaved kpis.json, segment_tables.xlsx and", len(list(CHARTS.glob('*.png'))), "charts.")
