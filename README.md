# T-Mobile (TMUS) — Executive Financial Dashboard

An interactive financial analysis dashboard for T-Mobile US, built for executive management and network software/services strategy teams serving Tier-1/Tier-2 CSPs.

**Live dashboard →** [danaaro.github.io/tmobile-dashboard](https://danaaro.github.io/tmobile-dashboard/)

---

## What's Inside

| Section | Content |
|---|---|
| **KPI Cards** | Q4 2025 vs Q4 2024 — 8 key metrics with YoY deltas |
| **Revenue** | Quarterly service revenue trend + EBITDA margin |
| **Annual Financials** | FY2022–FY2025 actuals + FY2026 guidance |
| **Network CapEx** | Annual CapEx trend with Sprint integration & 5G Advanced annotations |
| **5G Broadband** | Customer trajectory 4.7M → 9.4M + 12M target |
| **Network AI/Software** | AI-RAN, IntentCX (OpenAI), Customer Driven Coverage, 5G Advanced, T-Satellite, Fiber |
| **Subscribers** | Postpaid phone net adds + churn trend |
| **Capital Allocation** | FCF vs CapEx vs shareholder returns |
| **Stock (3-Year)** | TMUS vs AT&T, Verizon, Telecom ETF — live data, event annotations |
| **FY2026 Outlook** | Guidance cards + 2027 long-range targets |

---

## Data Sources

All financial data sourced from verified public filings:
- [T-Mobile Investor Relations](https://investor.t-mobile.com) — quarterly earnings press releases
- SEC EDGAR — 10-K / 10-Q filings
- Yahoo Finance — stock price data (live, via `yfinance`)
- T-Mobile 2024 Capital Markets Day presentation

> **Latest data:** Q4 2025 / FY2025 (fully reported). Q1 2026 earnings call: April 28, 2026.

---

## Regenerate with Fresh Data

```bash
pip install plotly yfinance pandas numpy curl_cffi
python generate_dashboard.py
```

Output: `index.html` — a single self-contained file, no server required.

---

## Network Domain Focus

Built with a **network software & services lens** for companies serving Global Tier-1/Tier-2 CSPs:
- Network CapEx trends and investment signals
- 5G Advanced deployment progress
- AI-RAN and network software initiatives
- Fixed wireless / fiber expansion trajectory
- Venue and small cell densification context
