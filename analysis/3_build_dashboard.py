"""
Bank Churn – Step 3: Single-page interactive dashboard
=======================================================
Builds a self-contained (offline) BI-style HTML dashboard: a KPI card strip plus
six interactive Plotly charts on one page, styled like Power BI / Tableau.

Output: deliverables/dashboard.html   (open in any browser; no internet needed)
"""
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

BASE = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE / "deliverables" / "bank_churn_clean.csv")

# palette
NAVY, TEAL, RED, GREY, AMBER, BG = "#1f3a5f", "#2a9d8f", "#e63946", "#8d99ae", "#e9c46a", "#eef2f7"
baseline = df.Exited.mean()

# features
df["AgeGroup"] = pd.cut(df.Age, [17,30,40,50,60,100], labels=["18–30","31–40","41–50","51–60","60+"])

def rate(col, order=None, observed=True):
    g = df.groupby(col, observed=observed).Exited.agg(["mean","size","sum"])
    if order: g = g.reindex(order)
    return g

LAYOUT = dict(template="plotly_white", margin=dict(l=50,r=20,t=56,b=40),
              font=dict(family="Segoe UI, Helvetica, Arial", size=13, color="#2b2b2b"),
              title=dict(font=dict(size=17, color=NAVY)), showlegend=False,
              height=330, paper_bgcolor="white", plot_bgcolor="white")

def pct_axis(fig): fig.update_yaxes(tickformat=".0%")

# 1) Geography
g = rate("Geography", ["France","Germany","Spain"])
f1 = go.Figure(go.Bar(x=g.index, y=g["mean"], marker_color=[GREY,RED,GREY],
        text=[f"{v:.1%}" for v in g["mean"]], textposition="outside",
        hovertemplate="%{x}<br>Churn %{y:.1%}<br>%{customdata:,} customers<extra></extra>",
        customdata=g["size"]))
f1.add_hline(y=baseline, line_dash="dash", line_color=NAVY,
             annotation_text=f"avg {baseline:.0%}", annotation_position="top left")
f1.update_layout(LAYOUT, title="Churn by Geography — Germany is 2× the rest"); pct_axis(f1)
f1.update_yaxes(range=[0,0.40])

# 2) Products
g = rate("NumOfProducts", [1,2,3,4])
f2 = go.Figure(go.Bar(x=[str(i) for i in g.index], y=g["mean"], marker_color=[TEAL,TEAL,RED,RED],
        text=[f"{v:.0%}" for v in g["mean"]], textposition="outside",
        hovertemplate="%{x} product(s)<br>Churn %{y:.1%}<br>%{customdata:,} customers<extra></extra>",
        customdata=g["size"]))
f2.update_layout(LAYOUT, title="Churn by # Products — 3–4 products ≈ total churn",
                 xaxis_title="Number of products"); pct_axis(f2)
f2.update_yaxes(range=[0,1.1])

# 3) Age
g = rate("AgeGroup", ["18–30","31–40","41–50","51–60","60+"])
f3 = go.Figure(go.Bar(x=g.index.astype(str), y=g["mean"], marker_color=NAVY,
        text=[f"{v:.0%}" for v in g["mean"]], textposition="outside",
        hovertemplate="Age %{x}<br>Churn %{y:.1%}<extra></extra>"))
f3.add_hline(y=baseline, line_dash="dash", line_color=RED)
f3.update_layout(LAYOUT, title="Churn by Age — peaks at 51–60", xaxis_title="Age group"); pct_axis(f3)
f3.update_yaxes(range=[0,0.65])

# 4) Activity & Gender grouped
act = rate("IsActiveMember", [0,1]); gen = rate("Gender")
f4 = go.Figure()
f4.add_bar(x=["Inactive","Active"], y=act["mean"], marker_color=[RED,TEAL],
           text=[f"{v:.1%}" for v in act["mean"]], textposition="outside", name="Activity")
f4.add_bar(x=["Female","Male"], y=gen.reindex(["Female","Male"])["mean"], marker_color=[AMBER,GREY],
           text=[f"{v:.1%}" for v in gen.reindex(['Female','Male'])['mean']], textposition="outside", name="Gender")
f4.update_layout(LAYOUT, title="Churn by Activity & Gender"); pct_axis(f4)
f4.update_yaxes(range=[0,0.34])

# 5) Balance at risk by geography
risk = df[df.Exited==1].groupby("Geography", observed=True).Balance.sum().reindex(["France","Germany","Spain"])/1e6
f5 = go.Figure(go.Bar(x=risk.index, y=risk.values, marker_color=[GREY,RED,GREY],
        text=[f"€{v:.0f}M" for v in risk.values], textposition="outside",
        hovertemplate="%{x}<br>€%{y:.1f}M at risk<extra></extra>"))
f5.update_layout(LAYOUT, title="Balance at Risk by Geography (€M held by churners)",
                 yaxis_title="€ millions")
f5.update_yaxes(range=[0,max(risk.values)*1.2])

# 6) Heatmap Geography × Age churn rate
piv = (df.pivot_table(index="Geography", columns="AgeGroup", values="Exited",
                      observed=True, aggfunc="mean")
       .reindex(["France","Germany","Spain"])[["18–30","31–40","41–50","51–60","60+"]])
f6 = go.Figure(go.Heatmap(z=piv.values, x=list(piv.columns), y=list(piv.index),
        colorscale=[[0,"#e8f3f1"],[0.5,AMBER],[1,RED]], zmin=0, zmax=0.8,
        text=[[f"{v:.0%}" for v in row] for row in piv.values],
        texttemplate="%{text}", textfont=dict(size=12),
        hovertemplate="%{y}, age %{x}<br>Churn %{z:.1%}<extra></extra>",
        colorbar=dict(tickformat=".0%", title="Churn", len=0.8)))
f6.update_layout(LAYOUT, title="Churn Hotspots: Geography × Age", showlegend=False)

figs = [f1,f2,f3,f4,f5,f6]
cfg = {"displayModeBar": False, "responsive": True}
divs = [f.to_html(full_html=False, include_plotlyjs=False, config=cfg,
                  div_id=f"chart{i}") for i,f in enumerate(figs)]

# KPI cards
churned = df[df.Exited==1]
tb = df.Balance.sum(); bar = churned.Balance.sum(); NIM = 0.025
hi = df[df.Balance > 100000]
cards = [
    ("Churn rate", f"{baseline:.1%}", "PRIMARY · target ≤ 15%", RED),
    ("Retention rate", f"{1-baseline:.1%}", "target ≥ 85%", TEAL),
    ("Deposits under mgmt", f"€{tb/1e6:.0f}M", "total deposit book", NAVY),
    ("Deposits at risk", f"€{bar/1e6:.0f}M", f"{bar/tb:.0%} of all deposits", RED),
    ("Revenue at risk", f"≈€{bar*NIM/1e6:.1f}M", "per yr · ~2.5% NIM (illustrative)", RED),
    ("Active members", f"{df.IsActiveMember.mean():.0%}", "target ≥ 60%", NAVY),
    ("Avg balance / cust.", f"€{df.Balance.mean()/1e3:.0f}K", "across all 10,000", NAVY),
    ("High-balance churn", f"{hi.Exited.mean():.1%}", f"&gt;€100k · {len(hi):,} customers", RED),
]
card_html = "".join(
    f'<div class="card"><div class="card-label">{l}</div>'
    f'<div class="card-value" style="color:{c}">{v}</div>'
    f'<div class="card-sub">{s}</div></div>' for l,v,s,c in cards)

html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Bank Customer Retention Dashboard</title>
<script>{get_plotlyjs()}</script>
<style>
 *{{box-sizing:border-box}} body{{margin:0;background:{BG};font-family:'Segoe UI',Helvetica,Arial,sans-serif;color:#222}}
 .wrap{{max-width:1320px;margin:0 auto;padding:20px 26px 40px}}
 header{{background:linear-gradient(110deg,{NAVY},#2c5a8f);color:#fff;border-radius:14px;padding:22px 28px;box-shadow:0 4px 14px rgba(31,58,95,.25)}}
 header h1{{margin:0;font-size:26px;letter-spacing:.3px}}
 header p{{margin:6px 0 0;opacity:.9;font-size:14px}}
 .kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:18px 0}}
 .card{{background:#fff;border-radius:12px;padding:16px 18px;box-shadow:0 2px 8px rgba(0,0,0,.06);border-top:4px solid {NAVY}}}
 .card-label{{font-size:12px;text-transform:uppercase;letter-spacing:.6px;color:#7a869a;font-weight:600}}
 .card-value{{font-size:28px;font-weight:800;margin:6px 0 2px;line-height:1}}
 .card-sub{{font-size:11.5px;color:#8a93a3}}
 .grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
 .panel{{background:#fff;border-radius:12px;padding:6px 10px 4px;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
 footer{{margin-top:18px;font-size:12px;color:#8a93a3;text-align:center}}
 .note{{font-size:12.5px;color:#5b6675;margin:2px 0 12px}}
 @media(max-width:980px){{.kpis{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap">
<header>
 <h1>🏦 Bank Customer Retention Dashboard</h1>
 <p>10,000 retail-banking customers across France, Germany &amp; Spain · Goal: reduce customer churn and protect deposits</p>
</header>
<div class="kpis">{card_html}</div>
<div class="note">📊 Interactive — hover any bar for exact figures, zoom by dragging, double-click to reset. Charts are colour-coded <span style="color:{TEAL};font-weight:700">healthy</span> vs <span style="color:{RED};font-weight:700">at-risk</span>.</div>
<div class="grid">
 <div class="panel">{divs[0]}</div>
 <div class="panel">{divs[1]}</div>
 <div class="panel">{divs[2]}</div>
 <div class="panel">{divs[3]}</div>
 <div class="panel">{divs[4]}</div>
 <div class="panel">{divs[5]}</div>
</div>
<footer>Bank Churn Analysis · Data Analyst Program · built from bank_churn_clean.csv (validated, 0 missing values)</footer>
</div></body></html>"""

out = BASE / "deliverables" / "dashboard.html"
out.write_text(html)
print(f"Dashboard → {out}  ({out.stat().st_size/1e6:.1f} MB, self-contained)")
