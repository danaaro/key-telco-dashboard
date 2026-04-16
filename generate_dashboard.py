#!/usr/bin/env python3
"""
T-Mobile Executive Financial Dashboard Generator
─────────────────────────────────────────────────
Sources : T-Mobile Investor Relations (investor.t-mobile.com), SEC EDGAR
          Stock data: Yahoo Finance via yfinance
Latest  : Q4 2025 / FY2025 (fully reported)
Note    : Q1 2026 earnings call scheduled April 28, 2026 — not yet reported
Run     : python generate_dashboard.py
Output  : tmobile_dashboard.html
"""

import sys, os
from datetime import datetime, date

# Force UTF-8 stdout so emoji/Unicode in print() works on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
except ImportError:
    sys.exit("ERROR: plotly not found.  Run:  pip install plotly")

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    HAS_YF = True
except ImportError:
    HAS_YF = False
    print("WARNING: yfinance/pandas not installed -- stock chart will be skipped.\n"
          "         Run: pip install yfinance pandas numpy")

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL = True
except ImportError:
    HAS_CURL = False

GENERATED  = datetime.now().strftime("%B %d, %Y  %H:%M")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT     = os.path.join(SCRIPT_DIR, "index.html")

def hex_alpha(hex_color, alpha):
    """Convert #RRGGBB + alpha float → rgba() string for Plotly compatibility."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

# ── Colour palette ───────────────────────────────────────────────────────────
MAG  = "#E20074"   # T-Mobile magenta
MAG2 = "#ff4da6"   # lighter accent
BG   = "#0a0e1a"
CARD = "#111827"
TXT  = "#f1f5f9"
MUTED= "#94a3b8"
GRID = "#1e2940"
GRN  = "#22c55e"
RED  = "#ef4444"
YLW  = "#f59e0b"
BLU  = "#3b82f6"
PRP  = "#8b5cf6"
TEA  = "#14b8a6"
ORG  = "#f97316"

def _base(title="", **kw):
    """Return base layout dict. Does NOT include xaxis/yaxis — set those via update_xaxes/update_yaxes."""
    d = dict(
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(color=TXT, family="'Inter','Segoe UI',Arial,sans-serif", size=12),
        title=dict(text=title, font=dict(size=14, color=TXT), x=0.01, xanchor="left"),
        margin=dict(l=65, r=50, t=55, b=50),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID,
                    borderwidth=1, font=dict(size=11)),
        hoverlabel=dict(bgcolor="#1e293b", font_size=12,
                        font_family="'Inter',Arial,sans-serif"),
    )
    d.update(kw)
    return d

def _apply_axes(fig):
    """Apply standard dark-theme axis styling to all axes."""
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont=dict(size=11))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont=dict(size=11))

def fig_to_div(fig, div_id):
    return pio.to_html(
        fig, include_plotlyjs=False, full_html=False,
        div_id=div_id,
        config={"displayModeBar": True, "displaylogo": False,
                "modeBarButtonsToRemove": ["select2d","lasso2d"],
                "responsive": True}
    )

# ══════════════════════════════════════════════════════════════════════════════
#  DATA  (all $ billions unless stated; source: T-Mobile IR / SEC EDGAR)
# ══════════════════════════════════════════════════════════════════════════════

ANN = ['FY2022','FY2023','FY2024','FY2025']
A = dict(
    svc  = [61.3, 63.2, 66.2, 71.3],
    ebitda=[26.4, 29.1, 31.8, 33.9],
    ni   = [ 2.6,  8.3, 11.3, 11.0],
    capex= [14.0,  9.8,  8.8, 10.0],
    fcf  = [ 7.7, 13.6, 17.0, 18.0],
    opcf = [16.8, 18.6, 22.3, 28.0],
    debt = [72.1, 76.4, 79.0, 80.5],   # long-term debt estimate FY2025
    shr  = [ 7.7, 14.0, 14.4,  None],  # shareholder returns
    adds = [ 3.1,  3.1,  3.1,  3.3],   # M postpaid phone net adds
    conn = [113.6,119.7,129.5,142.4],  # M total customer connections
)
A['margin'] = [round(e/s*100,1) for e,s in zip(A['ebitda'], A['svc'])]
A['capex_pct'] = [round(c/s*100,1) for c,s in zip(A['capex'], A['svc'])]

# FY2026 guidance (from Q4 2025 earnings release)
G26 = dict(ebitda_lo=37.0, ebitda_hi=37.5, fcf_lo=18.0, fcf_hi=18.7, capex=10.0)

# Quarterly  (* = derived from FY2025 total minus Q1+Q4 reported)
QTRS = ["Q4'23","Q1'24","Q2'24","Q3'24","Q4'24","Q1'25","Q2'25*","Q3'25*","Q4'25"]
Q = dict(
    svc  = [16.0, 16.1, 16.4, 16.7, 16.9, 16.9, 17.7, 18.0, 18.7],
    ebitda=[ 7.2,  7.6,  8.0,  8.2,  7.9,  8.3,  8.6,  8.6,  8.4],
    ni   = [ 2.0,  2.4,  2.9,  3.1,  3.0,  3.0, 2.95, 2.95,  2.1],
    capex= [ 1.6,  2.6,  2.0,  2.0,  2.2,  2.5,  2.5,  2.5,  2.5],
    fcf  = [ 4.3,  3.3,  3.5,  5.2,  4.1,  4.4,  4.7,  4.7,  4.2],
    adds = [  934,  532,  738,  865,  903,  495,  900,  943,  962],  # K
    churn= [ 0.96, 0.86, 0.86, 0.86, 0.92, 0.91, 0.90, 0.92, 1.02],
    bb   = [  4.7,  5.2,  5.6,  6.0,  6.4,  6.9,  7.5, 8.85,  9.4],  # M broadband
    est  = [False,False,False,False,False,False,True, True,False],
)
Q['margin']    = [round(e/s*100,1) for e,s in zip(Q['ebitda'], Q['svc'])]
Q['capex_pct'] = [round(c/s*100,1) for c,s in zip(Q['capex'],  Q['svc'])]

# Bar colours: full magenta for actuals, semi-transparent for estimates
MAG_DIM = hex_alpha(MAG, 0.40)
BAR_CLR = [MAG if not e else MAG_DIM for e in Q['est']]

# KPI deltas  Q4'25 vs Q4'24
KPI = [
    ("Service Revenue", 18.7, 16.9, "$B", "svc_rev"),
    ("Core Adj. EBITDA", 8.4,  7.9,  "$B", "ebitda"),
    ("Net Income",        2.1,  3.0,  "$B", "net_income"),
    ("Adj. Free Cash Flow", 4.2, 4.1, "$B", "fcf"),
    ("CapEx",             2.5,  2.2,  "$B", "capex"),
    ("Phone Net Adds",    962,  903,  "K",  "adds"),
    ("5G Broadband Cust.",9.4,  6.4,  "M",  "broadband"),
    ("Postpaid Churn",   1.02, 0.92,  "%",  "churn"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  CHART 1 – Quarterly Service Revenue + EBITDA Margin
# ══════════════════════════════════════════════════════════════════════════════
def chart_revenue():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Revenue bars
    fig.add_trace(go.Bar(
        x=QTRS, y=Q['svc'],
        name="Service Revenue ($B)",
        marker_color=BAR_CLR,
        text=[f"${v:.1f}B" for v in Q['svc']],
        textposition="outside", textfont=dict(size=10, color=TXT),
        hovertemplate="<b>%{x}</b><br>Service Rev: $%{y:.2f}B<extra></extra>",
    ), secondary_y=False)
    # EBITDA margin line
    fig.add_trace(go.Scatter(
        x=QTRS, y=Q['margin'],
        name="EBITDA Margin %",
        mode="lines+markers",
        line=dict(color=TEA, width=2.5, dash="dot"),
        marker=dict(size=7, color=TEA),
        hovertemplate="<b>%{x}</b><br>EBITDA Margin: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)
    fig.update_layout(**_base("Quarterly Service Revenue & EBITDA Margin"))
    _apply_axes(fig)
    fig.update_yaxes(title_text="USD Billions", secondary_y=False, tickprefix="$")
    fig.update_yaxes(title_text="EBITDA Margin %", secondary_y=True,
                     ticksuffix="%", range=[40, 55], showgrid=False)
    # Highlight latest quarter
    fig.add_vrect(x0="Q3'25*", x1="Q4'25", fillcolor=MAG, opacity=0.07, line_width=0)
    fig.add_annotation(x="Q4'25", y=max(Q['svc'])*1.08, text="◀ Latest Quarter",
                       showarrow=False, font=dict(color=MAG, size=10), xref="x", yref="y")
    return fig_to_div(fig, "chart_revenue")

# ══════════════════════════════════════════════════════════════════════════════
#  CHART 2 – Annual Financial Performance (EBITDA + Net Income + FCF)
# ══════════════════════════════════════════════════════════════════════════════
def chart_annual_financials():
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ANN, y=A['ebitda'], name="Core Adj. EBITDA",
        marker_color=MAG,
        text=[f"${v:.1f}B" for v in A['ebitda']],
        textposition="outside", textfont=dict(size=10, color=TXT),
        hovertemplate="<b>%{x}</b><br>EBITDA: $%{y:.1f}B<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=ANN, y=A['ni'], name="Net Income",
        marker_color=BLU,
        text=[f"${v:.1f}B" for v in A['ni']],
        textposition="outside", textfont=dict(size=10, color=TXT),
        hovertemplate="<b>%{x}</b><br>Net Income: $%{y:.1f}B<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=ANN, y=A['fcf'], name="Adj. Free Cash Flow",
        marker_color=GRN,
        text=[f"${v:.1f}B" for v in A['fcf']],
        textposition="outside", textfont=dict(size=10, color=TXT),
        hovertemplate="<b>%{x}</b><br>FCF: $%{y:.1f}B<extra></extra>",
    ))
    # Add FY2026 EBITDA guidance bar (dashed outline)
    fig.add_trace(go.Bar(
        x=['FY2026E'], y=[G26['ebitda_lo']],
        name="FY2026E EBITDA (guidance low)",
        marker_color=hex_alpha(MAG, 0.15),
        marker_line_color=MAG, marker_line_width=2,
        hovertemplate="FY2026E EBITDA Guidance: $37.0–$37.5B<extra></extra>",
        showlegend=True,
    ))
    fig.update_layout(**_base("Annual Financial Performance"), barmode="group")
    _apply_axes(fig)
    fig.update_yaxes(title_text="USD Billions", tickprefix="$")
    # EBITDA margin annotation
    for i, (yr, m) in enumerate(zip(ANN, A['margin'])):
        fig.add_annotation(x=yr, y=A['ebitda'][i] + 1.5,
                           text=f"{m}%", showarrow=False,
                           font=dict(size=9, color=TEA), xref="x", yref="y")
    fig.add_annotation(x=2.5, y=31, text="EBITDA Margin (above bars)",
                       showarrow=False, font=dict(size=9, color=TEA, style="italic"))
    return fig_to_div(fig, "chart_annual")

# ══════════════════════════════════════════════════════════════════════════════
#  CHART 3 – Network CapEx: Annual Trend + % of Service Revenue
# ══════════════════════════════════════════════════════════════════════════════
def chart_capex():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=ANN, y=A['capex'], name="Annual CapEx ($B)",
        marker_color=[ORG, TEA, GRN, MAG],
        text=[f"${v:.1f}B" for v in A['capex']],
        textposition="outside", textfont=dict(size=11, color=TXT),
        hovertemplate="<b>%{x}</b><br>CapEx: $%{y:.1f}B<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=ANN, y=A['capex_pct'],
        name="CapEx % of Svc Revenue",
        mode="lines+markers+text",
        line=dict(color=YLW, width=2.5),
        marker=dict(size=9, color=YLW),
        text=[f"{v}%" for v in A['capex_pct']],
        textposition="top center", textfont=dict(size=10, color=YLW),
        hovertemplate="<b>%{x}</b><br>CapEx/Svc Rev: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)
    # FY2026 guidance
    fig.add_trace(go.Bar(
        x=['FY2026E'], y=[G26['capex']], name="FY2026E CapEx (guidance)",
        marker_color=hex_alpha(MAG, 0.25),
        marker_line_color=MAG, marker_line_width=2,
        hovertemplate="FY2026E CapEx Guidance: ~$10.0B<extra></extra>",
    ), secondary_y=False)
    fig.update_layout(**_base("Network CapEx — Annual Trend & Efficiency"))
    _apply_axes(fig)
    fig.update_yaxes(title_text="USD Billions", secondary_y=False, tickprefix="$", range=[0, 18])
    fig.update_yaxes(title_text="CapEx as % of Service Revenue", secondary_y=True,
                     ticksuffix="%", showgrid=False, range=[0, 30])
    # Annotations
    annotations = [
        (0, 14.0, "Sprint integration<br>peak investment", ORG),
        (1,  9.8, "Network<br>normalization", TEA),
        (2,  8.8, "CapEx efficiency<br>record low", GRN),
        (3, 10.0, "5G Advanced<br>ramp-up", MAG),
    ]
    for i, yv, lbl, clr in annotations:
        fig.add_annotation(x=ANN[i], y=yv - 2.2, text=lbl, showarrow=True,
                           arrowhead=2, arrowcolor=clr, font=dict(size=9, color=clr),
                           bgcolor=CARD, bordercolor=clr, borderwidth=1,
                           xref="x", yref="y")
    return fig_to_div(fig, "chart_capex")

# ══════════════════════════════════════════════════════════════════════════════
#  CHART 4 – 5G Broadband Customer Trajectory
# ══════════════════════════════════════════════════════════════════════════════
def chart_broadband():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Area fill under broadband line
    fig.add_trace(go.Scatter(
        x=QTRS, y=Q['bb'],
        name="5G Broadband Customers (M)",
        mode="lines+markers",
        fill="tozeroy",
        fillcolor=hex_alpha(TEA, 0.14),
        line=dict(color=TEA, width=3),
        marker=dict(size=8, color=[TEA if not e else YLW for e in Q['est']],
                    symbol=["circle" if not e else "diamond" for e in Q['est']]),
        text=[f"{v:.2f}M" for v in Q['bb']],
        textposition="top center", textfont=dict(size=9, color=TEA),
        hovertemplate="<b>%{x}</b><br>Broadband Customers: %{y:.2f}M<extra></extra>",
    ), secondary_y=False)
    # Net adds bars (quarterly delta)
    bb_adds = [Q['bb'][0]] + [Q['bb'][i]-Q['bb'][i-1] for i in range(1, len(Q['bb']))]
    bb_clr = [TEA if not e else hex_alpha(YLW, 0.55) for e in Q['est']]
    fig.add_trace(go.Bar(
        x=QTRS, y=bb_adds, name="Net Adds per Quarter (M)",
        marker_color=bb_clr, opacity=0.7,
        hovertemplate="<b>%{x}</b><br>Net Adds: +%{y:.2f}M<extra></extra>",
    ), secondary_y=True)
    # Target line 12M by 2028
    fig.add_hline(y=12, line_dash="dot", line_color=MAG, line_width=1.5,
                  annotation_text="12M target (2028)", annotation_position="right",
                  annotation_font=dict(color=MAG, size=10),
                  secondary_y=False)
    fig.update_layout(**_base("5G Broadband Customer Growth Trajectory"))
    _apply_axes(fig)
    fig.update_yaxes(title_text="Total Customers (Millions)", secondary_y=False,
                     ticksuffix="M", range=[0, 14])
    fig.update_yaxes(title_text="Quarterly Net Adds (M)", secondary_y=True,
                     ticksuffix="M", showgrid=False, range=[0, 3])
    fig.add_annotation(x=8, y=9.8, text="9.4M total<br>(8.5M 5G BB)",
                       showarrow=True, arrowhead=2, arrowcolor=TEA,
                       font=dict(color=TEA, size=10), bgcolor=CARD,
                       bordercolor=TEA, borderwidth=1, xref="x", yref="y")
    return fig_to_div(fig, "chart_broadband")

# ══════════════════════════════════════════════════════════════════════════════
#  CHART 5 – Subscriber Metrics: Phone Net Adds + Churn
# ══════════════════════════════════════════════════════════════════════════════
def chart_subscribers():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    add_clr = [GRN if not e else hex_alpha(GRN, 0.40) for e in Q['est']]
    fig.add_trace(go.Bar(
        x=QTRS, y=Q['adds'], name="Postpaid Phone Net Adds (K)",
        marker_color=add_clr,
        text=[f"{v}K" for v in Q['adds']],
        textposition="outside", textfont=dict(size=9, color=TXT),
        hovertemplate="<b>%{x}</b><br>Phone Net Adds: %{y:,}K<extra></extra>",
    ), secondary_y=False)
    churn_clr = [GRN if c <= 0.90 else (YLW if c <= 0.95 else RED) for c in Q['churn']]
    fig.add_trace(go.Scatter(
        x=QTRS, y=Q['churn'],
        name="Postpaid Phone Churn %",
        mode="lines+markers",
        line=dict(color=YLW, width=2.5),
        marker=dict(size=9, color=churn_clr, line=dict(color=TXT, width=1)),
        hovertemplate="<b>%{x}</b><br>Churn: %{y:.2f}%<extra></extra>",
    ), secondary_y=True)
    fig.update_layout(**_base("Subscriber Metrics — Postpaid Net Adds & Churn"))
    _apply_axes(fig)
    fig.update_yaxes(title_text="Phone Net Adds (Thousands)", secondary_y=False, range=[0, 1200])
    fig.update_yaxes(title_text="Postpaid Phone Churn %", secondary_y=True,
                     ticksuffix="%", showgrid=False, range=[0.7, 1.2])
    fig.add_hline(y=0.90, line_dash="dot", line_color=GRN, line_width=1,
                  annotation_text="0.90% benchmark", annotation_position="right",
                  annotation_font=dict(color=GRN, size=9), secondary_y=True)
    return fig_to_div(fig, "chart_subscribers")

# ══════════════════════════════════════════════════════════════════════════════
#  CHART 6 – Capital Allocation: FCF vs CapEx vs Shareholder Returns
# ══════════════════════════════════════════════════════════════════════════════
def chart_capital():
    shr_vals = [v if v is not None else 0 for v in A['shr']]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ANN, y=A['fcf'], name="Adj. Free Cash Flow",
                         marker_color=GRN,
                         text=[f"${v:.1f}B" for v in A['fcf']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>FCF: $%{y:.1f}B<extra></extra>"))
    fig.add_trace(go.Bar(x=ANN, y=A['capex'], name="CapEx (Network Investment)",
                         marker_color=ORG,
                         text=[f"${v:.1f}B" for v in A['capex']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>CapEx: $%{y:.1f}B<extra></extra>"))
    fig.add_trace(go.Bar(x=ANN[:3], y=shr_vals[:3], name="Shareholder Returns",
                         marker_color=PRP,
                         text=[f"${v:.1f}B" for v in shr_vals[:3]],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>Shareholder Returns: $%{y:.1f}B<extra></extra>"))
    # FY2026 guidance bars
    fig.add_trace(go.Bar(x=['FY2026E'], y=[(G26['fcf_lo']+G26['fcf_hi'])/2],
                         name="FY2026E FCF (guidance mid)",
                         marker_color=hex_alpha(GRN, 0.25), marker_line_color=GRN, marker_line_width=2,
                         hovertemplate="FY2026E FCF Guidance: $18.0–$18.7B<extra></extra>"))
    fig.update_layout(**_base("Capital Allocation — FCF vs CapEx vs Shareholder Returns"),
                      barmode="group")
    _apply_axes(fig)
    fig.update_yaxes(title_text="USD Billions", tickprefix="$")
    # Program-to-date annotation
    fig.add_annotation(x=1, y=18, text="$31.4B program-to-date<br>shareholder returns (thru Q4'24)",
                       showarrow=False, font=dict(color=PRP, size=9, style="italic"),
                       bgcolor=CARD, bordercolor=PRP, borderwidth=1)
    return fig_to_div(fig, "chart_capital")

# ══════════════════════════════════════════════════════════════════════════════
#  CHART 7 – 3-Year Stock Performance vs Peers
# ══════════════════════════════════════════════════════════════════════════════
def chart_stock():
    if not HAS_YF:
        return "<div class='chart-placeholder'>⚠ Stock chart unavailable — install yfinance: <code>pip install yfinance pandas</code></div>"

    print("  Fetching 3-year stock data (TMUS, T, VZ, IYZ)...")
    end   = date.today()
    start = date(end.year - 3, end.month, end.day)
    tickers = {"TMUS": (MAG, "T-Mobile (TMUS)"),
               "T":    (BLU, "AT&T (T)"),
               "VZ":   (ORG, "Verizon (VZ)"),
               "IYZ":  (PRP, "Telecom ETF (IYZ)")}

    # Build an SSL-bypassing curl_cffi session (handles corporate proxy / self-signed cert)
    ssl_session = curl_requests.Session(verify=False, impersonate="chrome") if HAS_CURL else None

    traces, returns = [], {}
    for tkr, (clr, lbl) in tickers.items():
        try:
            ticker_obj = yf.Ticker(tkr, session=ssl_session) if ssl_session else yf.Ticker(tkr)
            raw = ticker_obj.history(start=str(start), end=str(end), auto_adjust=True)
            if raw.empty:
                print(f"    Warning: no data returned for {tkr}")
                continue
            prices = raw['Close'].squeeze().dropna()
            if len(prices) < 2:
                continue
            norm    = (prices / prices.iloc[0]) * 100
            ret3y   = prices.iloc[-1] / prices.iloc[0] * 100 - 100
            ytd_st  = prices[prices.index >= f"{end.year}-01-01"]
            ret_ytd = (ytd_st.iloc[-1] / ytd_st.iloc[0] * 100 - 100) if len(ytd_st) > 1 else 0
            returns[tkr] = (ret3y, ret_ytd)
            traces.append(go.Scatter(
                x=norm.index, y=norm.values, name=lbl,
                line=dict(color=clr, width=2.5 if tkr == "TMUS" else 1.8),
                hovertemplate=f"<b>{lbl}</b><br>%{{x|%b %Y}}<br>Indexed: %{{y:.1f}}<extra></extra>",
            ))
            print(f"    {tkr}: {len(prices)} data points, 3Y return {ret3y:+.1f}%")
        except Exception as e:
            print(f"    Warning: could not fetch {tkr}: {e}")

    if not traces:
        return "<div class='chart-placeholder'>⚠ Could not fetch stock data. Check internet connection.</div>"

    fig = go.Figure(traces)
    fig.add_hline(y=100, line_dash="dot", line_color=MUTED, line_width=1,
                  annotation_text="Base (3yr ago = 100)", annotation_position="left",
                  annotation_font=dict(color=MUTED, size=9))

    # Key event annotations (TMUS)
    events = [
        ("2023-10-25", "Capital Markets Day<br>raised 2027 targets"),
        ("2024-01-29", "FY2023 earnings<br>record FCF"),
        ("2025-01-29", "FY2024 earnings<br>best-ever net income"),
        ("2025-04-28", "Q1 2025<br>best-ever Q1"),
        ("2026-01-28", "FY2025 earnings<br>broadband 9.4M"),
        ("2026-04-28", "Q1 2026<br>earnings call →"),
    ]
    for ev_date, ev_text in events:
        try:
            ev_dt = pd.Timestamp(ev_date)
            if ev_dt > pd.Timestamp(str(end)):
                continue
            fig.add_vline(x=ev_dt, line_dash="dot",
                          line_color=hex_alpha(MAG, 0.40), line_width=1)
            fig.add_annotation(x=ev_dt, y=175, text=ev_text,
                               showarrow=False, textangle=-90,
                               font=dict(size=8, color=hex_alpha(MAG, 0.80)),
                               xref="x", yref="y")
        except Exception:
            pass

    # Returns summary table
    ret_text = "  |  ".join(
        f"<b>{t}</b>: 3Y {r[0]:+.0f}%  YTD {r[1]:+.0f}%"
        for t, r in returns.items()
    )

    fig.update_layout(
        **_base("3-Year Stock Performance vs Peers (Indexed to 100)"),
        annotations=[a for a in fig.layout.annotations] + [
            dict(text=ret_text, showarrow=False,
                 xref="paper", yref="paper", x=0.01, y=-0.12,
                 font=dict(size=10, color=MUTED), align="left")
        ]
    )
    _apply_axes(fig)
    fig.update_yaxes(title_text="Indexed Price (base=100)")
    fig.update_xaxes(title_text="")
    return fig_to_div(fig, "chart_stock")

# ══════════════════════════════════════════════════════════════════════════════
#  CHART 8 – Quarterly FCF vs CapEx
# ══════════════════════════════════════════════════════════════════════════════
def chart_fcf_capex_quarterly():
    fig = go.Figure()
    fcf_clr  = [GRN if not e else hex_alpha(GRN, 0.40) for e in Q['est']]
    capex_clr= [ORG if not e else hex_alpha(ORG, 0.40) for e in Q['est']]
    fig.add_trace(go.Bar(x=QTRS, y=Q['fcf'],  name="Adj. Free Cash Flow",
                         marker_color=fcf_clr,
                         hovertemplate="<b>%{x}</b><br>FCF: $%{y:.2f}B<extra></extra>"))
    fig.add_trace(go.Bar(x=QTRS, y=Q['capex'], name="CapEx",
                         marker_color=capex_clr,
                         hovertemplate="<b>%{x}</b><br>CapEx: $%{y:.2f}B<extra></extra>"))
    # FCF - CapEx = residual cash
    residual = [f - c for f, c in zip(Q['fcf'], Q['capex'])]
    fig.add_trace(go.Scatter(
        x=QTRS, y=residual, name="FCF − CapEx (cash after network spend)",
        mode="lines+markers",
        line=dict(color=TEA, width=2, dash="dot"),
        marker=dict(size=7, color=TEA),
        hovertemplate="<b>%{x}</b><br>FCF−CapEx: $%{y:.2f}B<extra></extra>",
    ))
    fig.update_layout(**_base("Quarterly FCF vs CapEx — Cash Generation vs Network Investment"),
                      barmode="group")
    _apply_axes(fig)
    fig.update_yaxes(title_text="USD Billions", tickprefix="$")
    fig.add_vrect(x0="Q3'25*", x1="Q4'25", fillcolor=MAG, opacity=0.07, line_width=0)
    return fig_to_div(fig, "chart_fcf_capex")

# ══════════════════════════════════════════════════════════════════════════════
#  HTML ASSEMBLY
# ══════════════════════════════════════════════════════════════════════════════

def kpi_card(label, val, prior, unit, slug):
    pct = (val - prior) / prior * 100
    arrow = "▲" if pct > 0 else "▼"
    # For churn and CapEx, up is bad; for net income Q4 variance, explain separately
    good_up = slug not in ("churn", "capex")
    color   = GRN if (pct > 0) == good_up else RED
    # Format value
    if unit == "$B":
        v_str = f"${val:.1f}B"
    elif unit == "K":
        v_str = f"{val:,.0f}K"
    elif unit == "M":
        v_str = f"{val:.1f}M"
    else:
        v_str = f"{val:.2f}%"
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{v_str}</div>
      <div class="kpi-delta" style="color:{color}">
        {arrow} {abs(pct):.1f}% vs Q4'24
      </div>
    </div>"""

def network_initiative_card(icon, title, subtitle, bullets, color=MAG):
    b_html = "".join(f"<li>{b}</li>" for b in bullets)
    return f"""
    <div class="init-card" style="border-left:3px solid {color}">
      <div class="init-header">
        <span class="init-icon" style="color:{color}">{icon}</span>
        <div>
          <div class="init-title">{title}</div>
          <div class="init-subtitle">{subtitle}</div>
        </div>
      </div>
      <ul class="init-bullets">{b_html}</ul>
    </div>"""

def build_html(divs):
    kpi_html = "".join(kpi_card(*k) for k in KPI)

    initiatives = [
        ("🧠", "AI-RAN Innovation Center",
         "Partners: NVIDIA · Ericsson · Nokia",
         ["Industry-first AI + RAN integration lab",
          "Brings AI inference to the Radio Access Network",
          "Targets real-time network optimization via AI",
          "Accelerates 5G Advanced performance gains"],
         MAG),
        ("🤝", "IntentCX — AI Customer Platform",
         "Partner: OpenAI",
         ["Predictive AI platform for customer engagement",
          "Target: 75% reduction in inbound care contacts",
          "Powered by OpenAI LLMs on T-Mobile network data",
          "Redefines Care operations across enterprise segment"],
         BLU),
        ("📡", "Customer Driven Coverage",
         "AI-driven network site prioritization",
         ["AI algorithmic model ranks tens of thousands of pending sites",
          "Prioritizes builds based on specific customer demand signals",
          "Enables higher ROI per network dollar spent",
          "Part of $9.5B FY2025 CapEx investment strategy"],
         TEA),
        ("🌐", "5G Advanced — Standalone Core",
         "Only US carrier with nationwide SA 5G core",
         ["US-first 5G Advanced broad deployment",
          "Record 6.3 Gbps downlink speeds achieved",
          "Voice over New Radio (VoNR) in production",
          "4-carrier aggregation + Massive MIMO rollout"],
         GRN),
        ("🛰️", "T-Satellite (Direct-to-Device)",
         "Satellite network on modern smartphones",
         ["Only US satellite service on most modern smartphones",
          "Over 1 million messages delivered",
          "Hundreds of thousands of active customers",
          "Eliminates dead zones without new hardware"],
         PRP),
        ("🏠", "Fiber & Fixed Wireless (5G Home)",
         "Fastest-growing broadband in the US",
         ["9.4M total broadband customers (Q4 2025)",
          "8.5M on 5G broadband specifically",
          "Target: 12M broadband by 2028",
          "Fiber: 12–15M households passed by 2030 (~20% IRR)"],
         ORG),
    ]
    init_html = "".join(network_initiative_card(*args) for args in initiatives)

    guidance_cards = [
        ("Core Adj. EBITDA", "$37.0–$37.5B", f"+{(37.25/33.9*100-100):.0f}% YoY", MAG),
        ("Adj. Free Cash Flow", "$18.0–$18.7B", f"+{(18.35/18.0*100-100):.0f}% YoY", GRN),
        ("CapEx", "~$10.0B", "5G Advanced ramp", ORG),
        ("Postpaid Net Adds", "TBD (2026)", "Based on Q1 2026 guidance", BLU),
    ]
    guide_html = ""
    for lbl, val, note, clr in guidance_cards:
        guide_html += f"""
        <div class="guide-card" style="border-top:3px solid {clr}">
          <div class="guide-label">{lbl}</div>
          <div class="guide-value" style="color:{clr}">{val}</div>
          <div class="guide-note">{note}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>T-Mobile Executive Financial Dashboard — Q4 2025</title>
<script src="https://cdn.plot.ly/plotly-3.0.0.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg:    {BG};
    --card:  {CARD};
    --mag:   {MAG};
    --text:  {TXT};
    --muted: {MUTED};
    --grid:  {GRID};
    --grn:   {GRN};
    --red:   {RED};
    --ylw:   {YLW};
    --blu:   {BLU};
    --tea:   {TEA};
  }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: 'Inter','Segoe UI',Arial,sans-serif;
    background: var(--bg); color: var(--text);
    line-height: 1.5; font-size: 14px;
  }}
  /* ── NAV ── */
  nav {{
    position: sticky; top: 0; z-index: 100;
    background: rgba(10,14,26,0.95);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--grid);
    display: flex; align-items: center;
    padding: 0 24px; height: 52px; gap: 4px;
    overflow-x: auto;
  }}
  .nav-brand {{
    font-weight: 700; font-size: 15px;
    color: var(--mag); margin-right: 16px;
    white-space: nowrap; letter-spacing: -0.3px;
  }}
  nav a {{
    color: var(--muted); text-decoration: none;
    font-size: 12px; font-weight: 500;
    padding: 6px 12px; border-radius: 6px;
    white-space: nowrap; transition: all .2s;
  }}
  nav a:hover {{ color: var(--text); background: var(--grid); }}
  .nav-print {{
    margin-left: auto;
    background: var(--mag); color: white;
    border: none; padding: 6px 14px;
    border-radius: 6px; cursor: pointer;
    font-size: 12px; font-weight: 600;
    white-space: nowrap; transition: opacity .2s;
  }}
  .nav-print:hover {{ opacity: 0.85; }}
  /* ── HERO ── */
  .hero {{
    background: linear-gradient(135deg, {CARD} 0%, #1a0a14 60%, {BG} 100%);
    border-bottom: 1px solid var(--grid);
    padding: 36px 32px 28px;
  }}
  .hero-badge {{
    display: inline-block; background: var(--mag);
    color: white; font-size: 10px; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    padding: 3px 10px; border-radius: 4px; margin-bottom: 12px;
  }}
  .hero h1 {{ font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }}
  .hero h1 span {{ color: var(--mag); }}
  .hero-meta {{
    margin-top: 8px; color: var(--muted); font-size: 12px;
    display: flex; gap: 24px; flex-wrap: wrap;
  }}
  .hero-meta strong {{ color: var(--text); }}
  /* ── SECTIONS ── */
  .section {{
    padding: 32px 24px;
    border-bottom: 1px solid var(--grid);
  }}
  .section-title {{
    font-size: 18px; font-weight: 700;
    color: var(--text); margin-bottom: 6px;
    display: flex; align-items: center; gap: 10px;
  }}
  .section-title .dot {{
    width: 4px; height: 20px;
    background: var(--mag); border-radius: 2px;
  }}
  .section-sub {{
    color: var(--muted); font-size: 12px; margin-bottom: 20px;
  }}
  /* ── KPI CARDS ── */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(175px, 1fr));
    gap: 12px; margin-bottom: 8px;
  }}
  .kpi-card {{
    background: var(--card); border: 1px solid var(--grid);
    border-radius: 10px; padding: 16px;
    transition: border-color .2s;
  }}
  .kpi-card:hover {{ border-color: var(--mag); }}
  .kpi-label {{ font-size: 11px; color: var(--muted); font-weight: 500; margin-bottom: 6px; }}
  .kpi-value {{ font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }}
  .kpi-delta {{ font-size: 11px; font-weight: 600; margin-top: 4px; }}
  /* ── CHARTS ── */
  .chart-wrap {{
    background: var(--card); border: 1px solid var(--grid);
    border-radius: 12px; padding: 4px; overflow: hidden;
    margin-bottom: 16px;
  }}
  .chart-wrap .chart-note {{
    padding: 6px 16px 10px;
    font-size: 10px; color: var(--muted); font-style: italic;
  }}
  .chart-grid-2 {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
  }}
  @media (max-width: 860px) {{ .chart-grid-2 {{ grid-template-columns: 1fr; }} }}
  .chart-placeholder {{
    background: var(--card); border: 1px dashed var(--grid);
    border-radius: 12px; padding: 32px;
    color: var(--muted); text-align: center; font-size: 13px;
  }}
  /* ── NETWORK INITIATIVES ── */
  .init-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
  }}
  .init-card {{
    background: var(--card); border-radius: 10px;
    padding: 18px; border: 1px solid var(--grid);
    transition: border-color .2s;
  }}
  .init-card:hover {{ border-color: var(--mag); }}
  .init-header {{ display: flex; gap: 12px; align-items: flex-start; margin-bottom: 12px; }}
  .init-icon {{ font-size: 24px; line-height: 1; flex-shrink: 0; }}
  .init-title {{ font-size: 14px; font-weight: 700; }}
  .init-subtitle {{ font-size: 11px; color: var(--muted); margin-top: 2px; }}
  .init-bullets {{ font-size: 12px; color: var(--muted); padding-left: 18px; }}
  .init-bullets li {{ margin-bottom: 4px; }}
  /* ── GUIDANCE CARDS ── */
  .guide-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
  }}
  .guide-card {{
    background: var(--card); border-radius: 10px;
    padding: 18px; border: 1px solid var(--grid);
  }}
  .guide-label {{ font-size: 11px; color: var(--muted); font-weight: 500; margin-bottom: 8px; }}
  .guide-value {{ font-size: 20px; font-weight: 700; letter-spacing: -0.5px; }}
  .guide-note  {{ font-size: 11px; color: var(--muted); margin-top: 6px; }}
  /* ── DISCLAIMER ── */
  .est-note {{
    background: {CARD}; border: 1px solid rgba(245,158,11,0.25);
    border-radius: 8px; padding: 10px 16px;
    font-size: 11px; color: var(--muted); margin-bottom: 16px;
  }}
  .est-note strong {{ color: {YLW}; }}
  /* ── FOOTER ── */
  footer {{
    padding: 24px 32px; color: var(--muted);
    font-size: 11px; border-top: 1px solid var(--grid);
    line-height: 1.7;
  }}
  footer a {{ color: var(--mag); text-decoration: none; }}
  footer a:hover {{ text-decoration: underline; }}
  /* ── PRINT ── */
  @media print {{
    body {{ background: white; color: #111; }}
    nav, .nav-print {{ display: none !important; }}
    .hero {{ background: #f8f8f8; border-bottom: 2px solid #E20074; }}
    .kpi-card, .init-card, .guide-card, .chart-wrap {{
      background: white; border-color: #ddd;
      break-inside: avoid;
    }}
    .section {{ break-inside: avoid; }}
  }}
</style>
</head>
<body>

<!-- ── NAVIGATION ────────────────────────────────────────────────────── -->
<nav>
  <span class="nav-brand">T&#8209;Mobile Exec Dashboard</span>
  <a href="#kpis">KPIs</a>
  <a href="#revenue">Revenue</a>
  <a href="#financials">Financials</a>
  <a href="#network">Network Domain</a>
  <a href="#subscribers">Subscribers</a>
  <a href="#capital">Capital</a>
  <a href="#stock">Stock</a>
  <a href="#outlook">Outlook</a>
  <button class="nav-print" onclick="window.print()">⬇ Print / Save PDF</button>
</nav>

<!-- ── HERO ──────────────────────────────────────────────────────────── -->
<div class="hero">
  <div class="hero-badge">Executive Strategy Brief</div>
  <h1>T-Mobile US <span>(TMUS)</span> — Financial Dashboard</h1>
  <div class="hero-meta">
    <span><strong>Latest Quarter:</strong> Q4 2025 (vs Q4 2024)</span>
    <span><strong>Stock Period:</strong> 3-Year (Apr 2023 – Apr 2026)</span>
    <span><strong>Lens:</strong> Network Domain · 5G · Broadband · AI/Software</span>
    <span><strong>Generated:</strong> {GENERATED}</span>
    <span><strong>Sources:</strong> T-Mobile IR · SEC EDGAR · Yahoo Finance</span>
  </div>
</div>

<!-- ── SECTION 1: KPIs ───────────────────────────────────────────────── -->
<div class="section" id="kpis">
  <div class="section-title"><span class="dot"></span>Q4 2025 Key Performance Indicators</div>
  <div class="section-sub">Latest quarter vs Q4 2024 (1 year back). All values from T-Mobile IR press releases.</div>
  <div class="kpi-grid">{kpi_html}</div>
  <div class="est-note">
    <strong>⚠ Net Income note:</strong> Q4 2025 net income ($2.1B) declined vs Q4 2024 ($3.0B), though FY2025 full-year net income was $11.0B vs $11.3B in FY2024 (largely flat). EPS grew slightly YoY ($9.72 vs $9.66) due to share buybacks.
    Q1 2026 earnings are scheduled for <strong>April 28, 2026</strong>.
  </div>
</div>

<!-- ── SECTION 2: REVENUE ────────────────────────────────────────────── -->
<div class="section" id="revenue">
  <div class="section-title"><span class="dot"></span>Service Revenue & EBITDA Margin</div>
  <div class="section-sub">Quarterly service revenue trend Q4 2023 → Q4 2025. Bars with * are Q2/Q3 2025 estimates derived from FY2025 actuals.</div>
  <div class="est-note">
    <strong>* Estimated quarters</strong> (Q2'25, Q3'25): Derived from FY2025 reported totals ($71.3B svc rev, $33.9B EBITDA) minus Q1+Q4 reported actuals. Labeled with lighter shading.
  </div>
  <div class="chart-wrap">
    {divs['revenue']}
    <div class="chart-note">Source: T-Mobile IR quarterly earnings press releases · investor.t-mobile.com</div>
  </div>
</div>

<!-- ── SECTION 3: ANNUAL FINANCIALS ─────────────────────────────────── -->
<div class="section" id="financials">
  <div class="section-title"><span class="dot"></span>Annual Financial Performance</div>
  <div class="section-sub">FY2022–FY2025 actuals. EBITDA margin annotated above bars. FY2026 EBITDA guidance shown for context.</div>
  <div class="chart-grid-2">
    <div class="chart-wrap">
      {divs['annual']}
      <div class="chart-note">FY2022 net income impacted by Sprint merger integration costs. FY2026E = mid-point of guidance range.</div>
    </div>
    <div class="chart-wrap">
      {divs['fcf_capex']}
      <div class="chart-note">FCF−CapEx line shows residual cash available after network investment. Strong upward trend 2022→2025.</div>
    </div>
  </div>
</div>

<!-- ── SECTION 4: NETWORK DOMAIN ─────────────────────────────────────── -->
<div class="section" id="network">
  <div class="section-title"><span class="dot"></span>Network Domain — CapEx, 5G Broadband & AI Initiatives</div>
  <div class="section-sub">Primary lens: Network investment trends, 5G deployment, fixed wireless growth, and network AI/software strategy.</div>

  <div class="chart-grid-2" style="margin-bottom:16px">
    <div class="chart-wrap">
      {divs['capex']}
      <div class="chart-note">CapEx peaked at $14B in FY2022 (Sprint integration). Normalized to $8.8B in FY2024, now ramping to $9.5B–$10B for 5G Advanced. Annual CapEx guidance: ~$9–10B through 2027.</div>
    </div>
    <div class="chart-wrap">
      {divs['broadband']}
      <div class="chart-note">Total broadband: 9.4M customers (8.5M on 5G broadband) as of Q4 2025. Target: 12M by 2028. Fiber: 12–15M households passed by 2030 (~20% IRR). Diamond markers = estimated quarters.</div>
    </div>
  </div>

  <!-- Network AI & Software Initiatives -->
  <div class="section-title" style="margin-bottom:12px; font-size:15px;">
    <span class="dot"></span>Network AI, Software & Technology Initiatives
  </div>
  <div class="init-grid">{init_html}</div>
</div>

<!-- ── SECTION 5: SUBSCRIBERS ───────────────────────────────────────── -->
<div class="section" id="subscribers">
  <div class="section-title"><span class="dot"></span>Subscriber Metrics</div>
  <div class="section-sub">Postpaid phone net additions and churn. Q4 2025 delivered 962K postpaid phone net adds (+7% YoY). FY2025 total: 3.3M phone net adds (industry best).</div>
  <div class="chart-wrap">
    {divs['subscribers']}
    <div class="chart-note">Green marker = churn ≤ 0.90%; Yellow = 0.90–0.95%; Red = >0.95%. Churn ticked up in Q4'25 (1.02%) due to seasonal promotions — FY2025 full-year churn: 0.93%.</div>
  </div>
</div>

<!-- ── SECTION 6: CAPITAL ────────────────────────────────────────────── -->
<div class="section" id="capital">
  <div class="section-title"><span class="dot"></span>Capital Allocation & Leverage</div>
  <div class="section-sub">Free cash flow generation vs network investment (CapEx) vs shareholder returns. FY2025: $18B FCF, $10B CapEx. Long-term debt rose from $72B (2022) to ~$80B (2025), partly from US Cellular acquisition.</div>
  <div class="chart-wrap">
    {divs['capital']}
    <div class="chart-note">FY2025 shareholder returns not yet fully disclosed. Program-to-date (Q3 2022–Q4 2024): $31.4B returned. FY2026E FCF guidance: $18.0–$18.7B.</div>
  </div>
</div>

<!-- ── SECTION 7: STOCK ──────────────────────────────────────────────── -->
<div class="section" id="stock">
  <div class="section-title"><span class="dot"></span>Stock Performance — 3-Year vs Peers</div>
  <div class="section-sub">TMUS vs AT&T (T), Verizon (VZ), and iShares US Telecom ETF (IYZ). Normalized to 100 at start. Key event annotations on chart. Data: Yahoo Finance.</div>
  <div class="chart-wrap">
    {divs['stock']}
    <div class="chart-note">Live data via Yahoo Finance. Dashed vertical lines mark key T-Mobile events. ⚑ Q1 2026 earnings April 28, 2026.</div>
  </div>
</div>

<!-- ── SECTION 8: OUTLOOK ────────────────────────────────────────────── -->
<div class="section" id="outlook">
  <div class="section-title"><span class="dot"></span>FY2026 Guidance & Strategic Outlook</div>
  <div class="section-sub">From Q4 2025 earnings release. FY2026 targets reflect ~10% EBITDA growth. Q1 2026 results due April 28, 2026.</div>
  <div class="guide-grid">{guide_html}</div>

  <div style="margin-top:24px; display:grid; grid-template-columns:1fr 1fr; gap:16px;">
    <div class="init-card" style="border-left:3px solid {MAG}">
      <div class="init-title" style="margin-bottom:10px;">📈 2027 Long-Range Targets</div>
      <ul class="init-bullets">
        <li>Service Revenue: <strong>$75–76B</strong> (~5% CAGR from FY2023)</li>
        <li>Core Adj. EBITDA: <strong>$38–39B</strong> (~7% CAGR)</li>
        <li>Adj. Free Cash Flow: <strong>$18–19B</strong></li>
        <li>Stockholder returns through 2027: <strong>~$50B program</strong></li>
      </ul>
    </div>
    <div class="init-card" style="border-left:3px solid {TEA}">
      <div class="init-title" style="margin-bottom:10px;">🏆 Competitive Network Position</div>
      <ul class="init-bullets">
        <li>J.D. Power network quality sweep: 5 of 6 US regions (FY2025)</li>
        <li>Ookla Best Mobile Network: back-to-back years</li>
        <li>Opensignal Best Overall Experience: 4 consecutive years</li>
        <li>Only US carrier with nationwide standalone 5G core</li>
      </ul>
    </div>
  </div>
</div>

<!-- ── FOOTER ─────────────────────────────────────────────────────────── -->
<footer>
  <strong>Data Sources:</strong>
  T-Mobile Investor Relations (<a href="https://investor.t-mobile.com" target="_blank">investor.t-mobile.com</a>) ·
  T-Mobile Newsroom earnings press releases ·
  SEC EDGAR 10-K / 10-Q filings ·
  Yahoo Finance (stock data via yfinance) ·
  T-Mobile 2024 Capital Markets Day presentation.<br>
  <strong>Note:</strong> Q2 2025 and Q3 2025 quarterly figures marked with * are estimates derived from FY2025 reported totals minus Q1 and Q4 reported actuals.
  All financial data in USD billions unless stated. Q1 2026 results not yet reported (earnings call April 28, 2026).<br>
  <strong>Generated:</strong> {GENERATED}
</footer>

</body>
</html>"""
    return html


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("T-Mobile Executive Dashboard Generator")
    print("=" * 45)
    print("  Building charts…")

    divs = {}
    steps = [
        ("revenue",     chart_revenue,              "Revenue & EBITDA Margin"),
        ("annual",      chart_annual_financials,    "Annual Financials"),
        ("capex",       chart_capex,                "Network CapEx"),
        ("broadband",   chart_broadband,            "5G Broadband Trajectory"),
        ("subscribers", chart_subscribers,          "Subscriber Metrics"),
        ("capital",     chart_capital,              "Capital Allocation"),
        ("stock",       chart_stock,                "3-Year Stock Performance"),
        ("fcf_capex",   chart_fcf_capex_quarterly,  "Quarterly FCF vs CapEx"),
    ]
    for key, fn, label in steps:
        print(f"  [{steps.index((key,fn,label))+1}/{len(steps)}] {label}…")
        divs[key] = fn()

    print("  Assembling HTML…")
    html = build_html(divs)

    print(f"  Writing -> {OUTPUT}")
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"\n✅  Done!  File: {OUTPUT}")
    print(f"   Size: {size_kb:.0f} KB")
    print(f"   Open in any browser — no server required.")
    print(f"   Use 'Print / Save PDF' button for static report.")
