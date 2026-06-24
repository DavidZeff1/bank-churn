# Bank Customer Churn — Final Project
**Data Analyst Program · Hebrew University of Jerusalem** — *A Business Perspective*

End-to-end churn & retention analysis of 10,000 retail-banking customers: messy data → clean dataset → KPIs → deep-dive analysis → interactive dashboard → presentation, all wrapped in a **multi-tab showcase website** (`index.html`).

## 🎯 Headline result
**20.4% churn (2,037 customers) = €186M of deposits at risk.** Concentrated in Germany, multi-product holders, older and inactive customers — and addressable.

## 🌐 Showcase website
`index.html` is a static, single-page site with a tab for every deliverable — **Overview · Dashboard · Presentation · Report · Data & Cleaning**. Open it locally by double-clicking `index.html`, or deploy it (see below). It references the files in `deliverables/` in place, so there is no duplication and no build step.

## 📦 Deliverables (`/deliverables`)
| File | What it is | Rubric step |
|---|---|---|
| `Bank_Churn_Analysis.pptx` | **12-min, 13-slide presentation** (editable) | 3.5 / 3.6 + Outcome |
| `dashboard.html` | **Interactive single-page BI dashboard** — open in any browser | 3.5 Dashboard |
| `Bank_Churn_Report.md` | Full written report: process, findings, recommendations | 3.6 Reporting |
| `bank_churn_clean.csv` | Cleaned, validated dataset (10,000 × 13, 0 missing) | 3.2 Cleaning |
| `cleaning_log.md` | Auditable record of every cleaning step + validation | 3.2 |
| `segment_tables.xlsx` | Churn-by-segment tables (geography, age, products, …) | 3.1 / 3.4 |
| `kpis.json` | Machine-readable KPIs & metrics | 3.3 |
| `charts/*.png` | Static charts used in the deck | 3.4 |

## ▶️ How to view
- **Dashboard:** double-click `deliverables/dashboard.html` (self-contained, works offline; hover/zoom interactive).
- **Presentation:** open `deliverables/Bank_Churn_Analysis.pptx` in PowerPoint/Keynote/Google Slides.
  - Two placeholders to fill on slide 2: **teammate names** and **mentor name**.
- **Report:** `deliverables/Bank_Churn_Report.md`.

## 🚀 Deploy to Vercel
The site is pure static files at the repo root, so **no configuration is needed**:
1. Push this folder to a GitHub repo.
2. In Vercel: **Add New → Project → Import** the repo.
3. Framework Preset: **Other** · Build Command: **none** · Output Directory: **leave empty (root)**.
4. **Deploy.** Vercel serves `index.html` at `/`.

(The deck's slide images are pre-rendered into `deliverables/slides/`, so the live site needs no build tools.)

## 🔁 Reproduce from scratch
```bash
pip install pandas numpy matplotlib seaborn openpyxl plotly python-pptx pillow markdown
python3 analysis/1_clean_data.py       # messy xlsx -> clean csv (+ validation)
python3 analysis/2_eda_analysis.py     # KPIs, segment tables, charts
python3 analysis/3_build_dashboard.py  # interactive dashboard.html
python3 analysis/4_build_deck.py       # presentation .pptx
python3 analysis/5_build_website.py    # index.html (the showcase site)
# slide images: soffice --headless --convert-to pdf deliverables/Bank_Churn_Analysis.pptx
#               pdftoppm -png -r 150 deliverables/Bank_Churn_Analysis.pdf deliverables/slides/slide
```

## 🗂 Structure
```
bank churn/
├─ index.html                      # showcase website (entry point)
├─ web/                            # styles.css + app.js (tabs & slide gallery)
├─ README.md
├─ Bank+Customer+Churn/            # raw inputs (messy xlsx, reference csv, dictionary)
├─ analysis/                       # reproducible Python pipeline (steps 1–5)
└─ deliverables/                   # all outputs (dashboard, deck, report, data, slides, charts)
```

## 🔑 Key findings
1. **Product paradox** — 2 products = 7.6% churn (sweet spot); 3–4 products = 83–100% churn; 51% of customers hold just one.
2. **Germany** — 32% churn (2× the rest) and ~2× the balance → €98M at risk.
3. **Age & engagement** — churn peaks at 56% for ages 51–60; inactive members churn ~2×; 2,521 inactive single-product customers churn at 37%.
4. **What doesn't matter** — tenure, credit score, credit-card ownership. *(Also caught a corrupted `HasCrCard` column in the raw data.)*

> Built with Python (pandas, matplotlib/seaborn), Plotly (dashboard) and python-pptx (deck).
