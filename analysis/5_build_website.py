"""
Bank Churn – Step 5: Static showcase website (Vercel-ready)
============================================================
Generates index.html — a single-page, multi-tab site that showcases every
deliverable. No build step, no framework: just static files served from the
repo root, so Vercel hosts it with zero configuration.

  index.html            (generated here)
  web/styles.css        (hand-written)
  web/app.js            (hand-written)
  deliverables/...       (referenced in place — dashboard, slides, charts, downloads)
"""
from pathlib import Path
import json
import markdown
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
D = BASE / "deliverables"
K = json.loads((D / "kpis.json").read_text())["kpis"]
md = lambda t: markdown.markdown(t, extensions=["tables", "fenced_code", "sane_lists"])

# ---- dynamic values ----
churn = f"{K['churn_rate']:.1%}"
ret = f"{1-K['churn_rate']:.1%}"
lost = f"{K['churned_customers']:,}"
risk = f"€{K['balance_at_risk']/1e6:.0f}M"
risk_share = f"{K['balance_at_risk_share']:.0%}"
active = f"{K['active_member_rate']:.0%}"
prod = f"{K['avg_products']:.2f}"
single = f"{K['single_product_share']:.0%}"

n_slides = len(list((D / "slides").glob("slide-*.png")))

# ---- rendered report + log ----
report_html = md((D / "Bank_Churn_Report.md").read_text())
log_html = md((D / "cleaning_log.md").read_text())

# ---- clean data preview ----
dfp = pd.read_csv(D / "bank_churn_clean.csv").head(12).copy()
for c in ["Balance", "EstimatedSalary"]:
    dfp[c] = dfp[c].map("€{:,.0f}".format)
preview_html = dfp.to_html(classes="data", index=False, border=0)

# ---- chart gallery ----
charts = [
    ("03_products.png", "The product paradox — 2 products is the retention sweet spot"),
    ("02_geography.png", "Germany churns at roughly twice the rate of France & Spain"),
    ("04_age.png", "Churn climbs with age and peaks at 51–60"),
    ("05_activity_gender.png", "Inactive members and women churn more"),
    ("06_balance_at_risk.png", "Where the at-risk deposits sit, by geography"),
    ("07_balance_dist.png", "Churners skew toward higher balances"),
]
gallery = '<h2 style="color:#1f3a5f;margin-top:34px">Analysis charts</h2><div class="grid gallery">' + "".join(
    f'<figure><img src="deliverables/charts/{f}" alt="{c}" loading="lazy"><figcaption>{c}</figcaption></figure>'
    for f, c in charts) + "</div>"

# ---- findings (overview) ----
findings = [
    ("🔀", "The product paradox",
     'Two products = <b>7.6%</b> churn (the sweet spot), but <b>3–4 products = 83–100%</b> churn. '
     'Half the base sits on a single product at <span class="stat">27.7%</span>.'),
    ("🇩🇪", "Germany & the deposit drain",
     'Germany churns at <span class="stat">32%</span> — about 2× the rest — while holding ~2× the balance: '
     '<b>€98M</b> of deposits at risk.'),
    ("📈", "Age & engagement",
     'Churn peaks at <span class="stat">56%</span> for ages 51–60. The <b>2,521</b> inactive single-product '
     'customers churn at <b>37%</b> — the clearest at-risk segment.'),
    ("🧭", "What does NOT drive churn",
     'Tenure, credit score and credit-card ownership have <b>no real effect</b> — so retention budget can be '
     'aimed precisely. (We also caught a corrupted column in the raw data.)'),
]
find_cards = "".join(
    f'<div class="card find"><h3><span class="em">{e}</span>{t}</h3><p>{b}</p></div>'
    for e, t, b in findings)

# ---- deliverable launchers ----
launchers = [
    ("📊", "Interactive Dashboard", "Six churn lenses + KPI cards on one page. Hover, zoom, explore.", "dashboard"),
    ("🖥️", "Presentation", f"{n_slides}-slide, 12-minute deck — the full story, ready to present.", "presentation"),
    ("📄", "Full Report", "Process, findings and recommendations, with evidence.", "report"),
    ("🧹", "Data & Cleaning", "From a messy workbook to a validated, analysis-ready dataset.", "data"),
]
launch_cards = "".join(
    f'<div class="card launch" data-tab="{tab}"><div class="ic">{e}</div>'
    f'<h3>{t}</h3><p>{d}</p><div class="go">Open →</div></div>'
    for e, t, d, tab in launchers)

# ===================================================================== assemble
HEAD = f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bank Customer Churn — Analysis Showcase</title>
<meta name="description" content="Churn & retention analysis of 10,000 retail-banking customers: dashboard, presentation, report and data.">
<link rel="stylesheet" href="web/styles.css">
</head><body>
<header class="nav"><div class="nav-inner">
  <div class="brand">🏦 Bank Churn<span class="dot"> · </span><span style="color:#6b7686;font-weight:600">Analysis Showcase</span></div>
  <nav class="tabs">
    <a class="tab-link" data-tab="overview" href="#overview">Overview</a>
    <a class="tab-link" data-tab="dashboard" href="#dashboard">Dashboard</a>
    <a class="tab-link" data-tab="presentation" href="#presentation">Presentation</a>
    <a class="tab-link" data-tab="report" href="#report">Report</a>
    <a class="tab-link" data-tab="data" href="#data">Data &amp; Cleaning</a>
  </nav>
</div></header><main>"""

OVERVIEW = f"""
<section id="tab-overview" class="tab">
  <div class="hero">
    <div class="kicker">Bank Churn · A Business Perspective</div>
    <h1>Why Are Our Customers Leaving?</h1>
    <div class="sub">A churn &amp; retention analysis of 10,000 retail-banking customers across France, Germany and Spain.</div>
    <div class="hero-stats">
      <div class="s red"><b>{churn}</b> customer churn</div>
      <div class="s amber"><b>{risk}</b> deposits at risk</div>
      <div class="s"><b>{lost}</b> customers lost</div>
    </div>
  </div>

  <div class="grid kpis">
    <div class="card kpi red"><div class="label">Churn rate</div><div class="value">{churn}</div><div class="sub">primary KPI · target ≤ 15%</div></div>
    <div class="card kpi teal"><div class="label">Retention rate</div><div class="value">{ret}</div><div class="sub">keep above 85%</div></div>
    <div class="card kpi red"><div class="label">Balance at risk</div><div class="value">{risk}</div><div class="sub">{risk_share} of all deposits</div></div>
    <div class="card kpi"><div class="label">Active members</div><div class="value">{active}</div><div class="sub">engagement lever</div></div>
    <div class="card kpi"><div class="label">Products / customer</div><div class="value">{prod}</div><div class="sub">{single} on a single product</div></div>
  </div>

  <div class="section-head"><h2>Key findings</h2><p>Churn is concentrated and addressable — driven by product fit, geography, age and engagement.</p></div>
  <div class="grid cards-2">{find_cards}</div>

  <div class="section-head" style="margin-top:30px"><h2>Explore the deliverables</h2><p>Each tab showcases one part of the project.</p></div>
  <div class="grid cards-2">{launch_cards}</div>
</section>"""

DASHBOARD = """
<section id="tab-dashboard" class="tab">
  <div class="section-head"><span class="kicker">BI tool · Plotly</span>
    <h2>Interactive Dashboard</h2>
    <p>One page, six lenses on churn, plus headline KPIs. Hover any bar for exact figures, drag to zoom, double-click to reset.</p></div>
  <div class="btnrow"><a class="btn outline" href="deliverables/dashboard.html" target="_blank">↗ Open full-screen in new tab</a></div>
  <div class="frame-wrap"><iframe id="dashFrame" class="dash" data-src="deliverables/dashboard.html" title="Bank churn dashboard"></iframe></div>
</section>"""

PRESENTATION = f"""
<section id="tab-presentation" class="tab">
  <div class="section-head"><span class="kicker">12-minute deck · {n_slides} slides</span>
    <h2>Presentation</h2>
    <p>The full narrative — domain, KPIs, data prep, deep-dive insights and recommendations. Use ← → keys or the thumbnails.</p></div>
  <div class="btnrow">
    <a class="btn" href="deliverables/Bank_Churn_Analysis.pptx" download>⬇ Download PowerPoint (.pptx)</a>
    <a class="btn navy" href="deliverables/Bank_Churn_Analysis.pdf" target="_blank">⬇ View / download PDF</a>
  </div>
  <div class="stage" id="slideStage" data-slides="{n_slides}">
    <button class="navbtn" id="prev" aria-label="Previous slide">‹</button>
    <img id="slideImg" src="deliverables/slides/slide-01.png" alt="Current slide">
    <button class="navbtn" id="next" aria-label="Next slide">›</button>
  </div>
  <div class="stage-meta"><span class="count" id="slideCount">Slide 1 / {n_slides}</span>
    <span style="color:#8d99ae;font-size:13px">Click a thumbnail to jump</span></div>
  <div class="thumbs" id="thumbs"></div>
</section>"""

REPORT_OPEN = """
<section id="tab-report" class="tab">
  <div class="section-head"><span class="kicker">Reporting</span><h2>Full Report</h2>
    <p>Process, findings and recommendations — documented and evidence-backed.</p></div>
  <article class="report">"""
REPORT_CLOSE = "</article>" + gallery + "</section>"

DATA = f"""
<section id="tab-data" class="tab">
  <div class="section-head"><span class="kicker">Data loading &amp; cleaning</span><h2>Data &amp; Cleaning</h2>
    <p>The raw workbook was intentionally messy. Below: a preview of the cleaned dataset, the full cleaning log, and downloads.</p></div>
  <div style="margin:6px 0 16px">
    <span class="pill">10,000 rows</span><span class="pill">13 columns</span>
    <span class="pill">0 missing values</span><span class="pill">validated vs reference ✓</span>
  </div>
  <div class="btnrow">
    <a class="btn" href="deliverables/bank_churn_clean.csv" download>⬇ Clean dataset (.csv)</a>
    <a class="btn navy" href="deliverables/segment_tables.xlsx" download>⬇ Segment tables (.xlsx)</a>
  </div>
  <h3 style="color:#1f3a5f">Cleaned data — first 12 rows</h3>
  <div class="table-scroll">{preview_html}</div>
  <h3 style="color:#1f3a5f;margin-top:30px">Cleaning log</h3>
  <article class="report" style="max-width:none">{log_html}</article>
</section>"""

FOOT = """<footer>Bank Customer Churn · Data Analyst Program, Hebrew University of Jerusalem ·
  built with Python, Plotly &amp; python-pptx</footer></main><script src="web/app.js"></script></body></html>"""

html = HEAD + OVERVIEW + DASHBOARD + PRESENTATION + REPORT_OPEN + report_html + REPORT_CLOSE + DATA + FOOT
(BASE / "index.html").write_text(html)
print(f"index.html written ({len(html)/1024:.0f} KB) · {n_slides} slides · references deliverables/ in place")
