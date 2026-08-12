# 📊 CampaignIQ — Marketing Campaign Attribution & ROI Analytics

**CampaignIQ** is a production-style analytics package that turns raw campaign rows into **attribution**, **ROI**, **segment insights**, **statistical testing**, and **budget reallocation** guidance — plus an interactive **Streamlit** dashboard for ongoing monitoring.

---

## ⚡ Quick start — run the dashboard

```bash
git clone https://github.com/ashritkvs/campaigniq-marketing-analytics.git
cd campaigniq-marketing-analytics
pip install -r requirements.txt
streamlit run dashboard.py
```

This opens automatically in your browser at `http://localhost:8501`. Upload `marketing_data.csv` via the sidebar file uploader to populate it (the raw CSV isn't committed to this repo — bring your own copy or export one matching the schema below).

---

## 🎯 Business problem

Marketing teams need to know **which channels and campaigns actually fund growth**, not just which ones spend the most. Weak attribution creates three expensive failures: budgets follow habit instead of performance, high-value audiences stay under-invested, and leadership sees activity metrics instead of profit logic. CampaignIQ connects **spend → modeled revenue → ROI → segments → tests → budget scenarios** so decisions are evidence-led and finance-ready.

---

## 🔎 Verified findings (from executing the notebook on the full 200,000-row dataset)

| Metric | Actual result |
| --- | --- |
| Dataset scale | **200,000 campaigns** across **6 channels** (Email, Facebook, Google Ads, Instagram, Website, YouTube), **5 campaign types**, **5 customer segments** |
| Overall ROI | **~5.0%** per channel — tightly clustered (4.99%–5.03% range), not a large spread |
| Best channel | **Facebook** (5.03% ROI), then Website (5.01%); Instagram lowest (4.99%) |
| Email vs. Search proxy test | Conversion rates 7.98% vs 8.01%; two-proportion z-test **p = 0.00029** (statistically significant) but **Cohen's h = 0.001** (practically negligible effect size) — significance here is driven by the very large sample (22M+ clicks), not a meaningful real-world difference |
| Segment ROI | All five segments cluster between 4.998%–5.012% ROI; Foodies highest |
| Reallocation lift | **+0.00%** — efficiency-weighted budget reallocation finds no meaningful gain, because channel efficiency is already nearly uniform across the dataset |

> These numbers come from actually executing `CampaignIQ_Analysis.ipynb` end-to-end against `marketing_data.csv`, not illustrative placeholders.

---

## 🧰 Tools & stack

| Layer | Tooling |
| --- | --- |
| Data prep | `pandas`, `numpy` |
| Analysis & statistics | `scipy`, `statsmodels` |
| Static storytelling | `matplotlib`, `seaborn` |
| Interactive BI | `plotly`, `streamlit` |
| Notebook | `jupyter`, `ipykernel` |

---

## 🚀 How to run

### 1) Environment

```bash
cd campaigniq-marketing-analytics
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Data

Place **`marketing_data.csv`** next to the notebook and dashboard (this repo ships a copy sourced from the workspace marketing extract).

**Columns used (actual schema):**  
`Campaign_ID`, `Company`, `Campaign_Type`, `Target_Audience`, `Duration`, `Channel_Used`, `Conversion_Rate`, `Acquisition_Cost`, `ROI`, `Location`, `Language`, `Clicks`, `Impressions`, `Engagement_Score`, `Customer_Segment`, `Date`

Engineered fields: **Spend** (cleaned `Acquisition_Cost`), **Revenue** = `Spend × (1 + ROI/100)`, **Conversions** = `Conversion_Rate × Clicks`.

### 3) Notebook

```bash
jupyter notebook CampaignIQ_Analysis.ipynb
```

### 4) Dashboard

```bash
streamlit run dashboard.py
```

Open the local URL Streamlit prints (defaults to **http://localhost:8501**).

---

## 📁 Project structure

```
campaigniq-marketing-analytics/
├── CampaignIQ_Analysis.ipynb   # End-to-end analysis + executive narrative
├── dashboard.py                # Streamlit monitoring app
├── requirements.txt            # Locked dependency baseline (semver ranges)
├── README.md                   # You are here
└── marketing_data.csv          # Campaign-level marketing dataset
```

---

## 🧭 What the dashboard shows

- **Sidebar filters:** campaign type, date range, channels, audience segment  
- **KPI row:** total spend, total revenue, overall ROI %, best channel by ROI  
- **Charts:** channel ROI bars, spend vs revenue scatter (bubble = conversions), monthly trends, segment×channel heatmap, budget mix (current vs recommended), top campaigns table  

---

## 📝 Notes for stakeholders

- ROI and revenue are **modeled from the dataset’s ROI definition** to enable consistent channel comparisons; finance should align definitions with accounting before using outputs as official targets.
- A/B testing uses a **practical proxy** when explicit experiment flags are absent (two campaign types compared with a two-proportion z-test on pooled clicks).
- Budget “lift” is a **scenario model**, not a promise — validate with incrementality or geo holdouts before large reallocations.

---

Built for marketing, analytics, and growth teams who want **one coherent story** from spreadsheet to dashboard.
