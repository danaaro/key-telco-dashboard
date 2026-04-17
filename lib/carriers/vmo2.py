"""
lib/carriers/vmo2.py — Virgin Media O2 (VMO2, UK) carrier module
Sources: Liberty Global IR (libertyglobal.com), VMO2 press releases
Latest:  Q2 2025 (quarterly reporting); FY2025 annual estimated
Note:    Private JV — Liberty Global (50%) + Telefónica (50%).
         No stock listing. Parent context: LBTYA (NASDAQ) + TEF (NYSE/BME).
         All values in GBP billions unless stated. FX conversion to USD noted in footer.
"""
import os
from datetime import date

from lib.base import (
    hex_alpha, base_layout, apply_axes, fig_to_div,
    kpi_card, initiative_card, guidance_card, page_shell,
    CARD_BG, TXT, MUTED, GRID,
    GRN, RED, YLW, BLU, PRP, TEA, ORG,
)

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    raise ImportError("plotly not found.  Run:  pip install plotly")

try:
    import yfinance as yf
    import pandas as pd
    HAS_YF = True
except ImportError:
    HAS_YF = False

try:
    from curl_cffi import requests as curl_requests
    HAS_CURL = True
except ImportError:
    HAS_CURL = False

# ── Carrier identity ──────────────────────────────────────────────────────────
ID      = "vmo2"
ACCENT  = "#D0021B"   # Virgin Red
GBP_USD = 1.27        # Approximate GBP/USD — used for landing page summary

# ══════════════════════════════════════════════════════════════════════════════
#  DATA  (£ billions unless stated)
#  Source: Liberty Global Q4 2025 results; VMO2 press releases
# ══════════════════════════════════════════════════════════════════════════════

ANN = ['FY2023', 'FY2024', 'FY2025']
A = dict(
    rev   = [10.91, 10.68, 10.42],   # Total Revenue £B
    ebitda= [ 4.06,  3.98,  3.89],   # Adj. EBITDA £B
    capex = [ 2.00,  2.00,  2.10],   # CapEx £B
    fcf   = [ 0.72,  0.67,  0.39],   # Adj. FCF £B
    mob   = [23.0,  23.0,  23.1],    # M O2 mobile connections
    bb    = [ 5.75,  5.69,  5.62],   # M Virgin Media broadband subscribers
    cov5g = [60,    75,    87],      # % UK population 5G coverage
    fiber = [5.8,   6.9,   8.3],    # M full-fiber premises passed
)
A['margin']    = [round(e/r*100, 1) for e, r in zip(A['ebitda'], A['rev'])]
A['capex_pct'] = [round(c/r*100, 1) for c, r in zip(A['capex'],  A['rev'])]

# Quarterly data (FY2024 Q1-Q4, FY2025 Q1-Q2 — latest available)
QTRS = ["Q1'24", "Q2'24", "Q3'24", "Q4'24", "Q1'25", "Q2'25"]
Q = dict(
    rev   = [2.67, 2.67, 2.63, 2.72, 2.59, 2.53],   # Revenue £B
    ebitda= [1.00, 0.99, 0.98, 1.01, 0.95, 0.94],   # Adj. EBITDA £B
    capex = [0.50, 0.50, 0.50, 0.50, 0.53, 0.53],   # CapEx £B (derived)
    mob   = [23.2, 23.1, 23.0, 23.0, 23.0, 23.1],   # M mobile connections
    bb    = [5.75, 5.73, 5.71, 5.69, 5.66, 5.62],   # M broadband subs
)
Q['margin'] = [round(e/r*100, 1) for e, r in zip(Q['ebitda'], Q['rev'])]

KPI_DATA = [
    # (label, val_latest, val_prior, unit, slug)  — Q2'25 vs Q2'24
    ("Total Revenue",       2.53, 2.67, "£B", "svc_rev"),
    ("Adj. EBITDA",         0.94, 0.99, "£B", "ebitda"),
    ("CapEx",               0.53, 0.50, "£B", "capex"),
    ("O2 Mobile Connections",23.1, 23.1, "M",  "adds"),
    ("VM Broadband Subs",   5.62, 5.73, "M",  "broadband"),
    ("5G Coverage (UK Pop.)", 87,   75, "%",  "coverage"),
]


def get_summary():
    return {
        "id":             ID,
        "svc_rev":        round(2.53 * GBP_USD, 1),   # Q2 2025 rev in USD
        "ebitda_margin":  37.2,                         # % Q2 2025
        "fcf_annual":     None,                             # Private JV — FCF not publicly disclosed
        "subscribers":    23.1,                         # M mobile connections
        "coverage_5g":    87,                           # % UK pop
        "latest_q":       "Q2 2025",
        "capex_pct":      20.2,                         # FY2025 CapEx/Rev %
    }


def generate(output_dir):
    print(f"  [VMO2] Building charts...")
    divs = {
        "revenue":     _chart_revenue(),
        "annual":      _chart_annual(),
        "subscribers": _chart_subscribers(),
        "5g_rollout":  _chart_5g_rollout(),
        "parents":     _parent_context_div(),
    }
    html = _build_html(divs)
    out_path = os.path.join(output_dir, "vmo2.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [VMO2] Written -> {out_path}")
    return out_path


# ── Charts ────────────────────────────────────────────────────────────────────

def _chart_revenue():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    bar_clr = [ACCENT] * 4 + [hex_alpha(ACCENT, 0.55)] * 2
    fig.add_trace(go.Bar(
        x=QTRS, y=Q['rev'], name="Total Revenue (£B)",
        marker_color=bar_clr, cliponaxis=False,
        text=[f"£{v:.2f}B" for v in Q['rev']],
        textposition="outside", textfont=dict(size=10, color=TXT),
        hovertemplate="<b>%{x}</b><br>Revenue: £%{y:.2f}B<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=QTRS, y=Q['margin'], name="EBITDA Margin %",
        mode="lines+markers",
        line=dict(color=TEA, width=2.5, dash="dot"),
        marker=dict(size=7, color=TEA),
        hovertemplate="<b>%{x}</b><br>EBITDA Margin: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)
    fig.update_layout(**base_layout(ACCENT, "Quarterly Revenue & EBITDA Margin"))
    apply_axes(fig)
    fig.update_yaxes(title_text="GBP Billions", secondary_y=False, tickprefix="£")
    fig.update_yaxes(title_text="EBITDA Margin %", secondary_y=True,
                     ticksuffix="%", range=[30, 45], showgrid=False)
    fig.add_vrect(x0="Q1'25", x1="Q2'25", fillcolor=ACCENT, opacity=0.07, line_width=0)
    fig.add_annotation(x="Q2'25", y=max(Q['rev'])*1.1, text="Latest",
                       showarrow=False, font=dict(color=ACCENT, size=10), xref="x", yref="y")
    return fig_to_div(fig, "vmo2_chart_revenue")


def _chart_annual():
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ANN, y=A['ebitda'], name="Adj. EBITDA",
                         marker_color=ACCENT, cliponaxis=False,
                         text=[f"£{v:.2f}B" for v in A['ebitda']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>EBITDA: £%{y:.2f}B<extra></extra>"))
    fig.add_trace(go.Bar(x=ANN, y=A['fcf'], name="Adj. FCF",
                         marker_color=GRN, cliponaxis=False,
                         text=[f"£{v:.2f}B" for v in A['fcf']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>FCF: £%{y:.2f}B<extra></extra>"))
    fig.add_trace(go.Bar(x=ANN, y=A['capex'], name="CapEx",
                         marker_color=ORG, cliponaxis=False,
                         text=[f"£{v:.2f}B" for v in A['capex']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>CapEx: £%{y:.2f}B<extra></extra>"))
    fig.update_layout(**base_layout(ACCENT, "Annual Financial Performance (GBP)"), barmode="group")
    apply_axes(fig)
    fig.update_yaxes(title_text="GBP Billions", tickprefix="£", range=[0, 5.5])
    for i, (yr, m) in enumerate(zip(ANN, A['margin'])):
        fig.add_annotation(x=yr, y=A['ebitda'][i] + 0.3,
                           text=f"{m}%", showarrow=False,
                           font=dict(size=9, color=TEA), xref="x", yref="y")
    fig.add_annotation(x="FY2025", y=1.2,
                       text="FCF impacted by<br>Daisy transaction<br>financing requirements",
                       showarrow=True, arrowhead=2, arrowcolor=YLW,
                       font=dict(size=9, color=YLW), bgcolor=CARD_BG,
                       bordercolor=YLW, borderwidth=1)
    return fig_to_div(fig, "vmo2_chart_annual")


def _chart_subscribers():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=QTRS, y=Q['bb'], name="VM Broadband Subscribers (M)",
        mode="lines+markers",
        fill="tozeroy", fillcolor=hex_alpha(ACCENT, 0.12),
        line=dict(color=ACCENT, width=3),
        marker=dict(size=8, color=ACCENT),
        hovertemplate="<b>%{x}</b><br>Broadband: %{y:.2f}M<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=QTRS, y=Q['mob'], name="O2 Mobile Connections (M)",
        mode="lines+markers",
        line=dict(color=BLU, width=2.5, dash="dot"),
        marker=dict(size=7, color=BLU),
        hovertemplate="<b>%{x}</b><br>Mobile: %{y:.1f}M<extra></extra>",
    ), secondary_y=True)
    fig.update_layout(**base_layout(ACCENT, "Subscriber Metrics — Broadband & Mobile"))
    apply_axes(fig)
    fig.update_yaxes(title_text="VM Broadband Subs (M)", secondary_y=False,
                     ticksuffix="M", range=[5.4, 6.0])
    fig.update_yaxes(title_text="O2 Mobile Connections (M)", secondary_y=True,
                     ticksuffix="M", range=[22.5, 23.8], showgrid=False)
    return fig_to_div(fig, "vmo2_chart_subs")


def _chart_5g_rollout():
    fig = make_subplots(rows=1, cols=2,
                        column_widths=[0.55, 0.45],
                        specs=[[{"type": "bar"}, {"type": "bar"}]],
                        subplot_titles=["5G Population Coverage (%)", "Full-Fiber Premises (M homes)"])
    years = ANN
    for i, (yr, cov, clr) in enumerate(zip(years, A['cov5g'], [ORG, YLW, ACCENT])):
        fig.add_trace(go.Bar(
            x=[yr], y=[cov], name=yr, marker_color=clr, showlegend=False,
            cliponaxis=False,
            text=[f"{cov}%"], textposition="outside",
            textfont=dict(color=TXT, size=11),
            hovertemplate=f"<b>{yr}</b><br>5G Coverage: {cov}%<extra></extra>",
        ), row=1, col=1)
    for i, (yr, fp, clr) in enumerate(zip(years, A['fiber'], [ORG, YLW, ACCENT])):
        fig.add_trace(go.Bar(
            x=[yr], y=[fp], name=yr, marker_color=clr, showlegend=False,
            cliponaxis=False,
            text=[f"{fp:.1f}M"], textposition="outside",
            textfont=dict(color=TXT, size=11),
            hovertemplate=f"<b>{yr}</b><br>Fiber premises: {fp:.1f}M<extra></extra>",
        ), row=1, col=2)
    fig.update_layout(**base_layout(ACCENT, "5G Coverage & Fiber Footprint Expansion"),
                      height=300, barmode="group")
    apply_axes(fig)
    fig.update_yaxes(range=[0, 115], ticksuffix="%", row=1, col=1)
    fig.update_yaxes(range=[0, 11], ticksuffix="M", row=1, col=2)
    return fig_to_div(fig, "vmo2_chart_5g")


def _parent_context_div():
    """Replace stock chart with private JV ownership context."""
    lbtya_clr = BLU
    tef_clr   = PRP
    return f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:0">
  <div class="init-card" style="border-left:3px solid {lbtya_clr}">
    <div class="init-title" style="margin-bottom:10px">Liberty Global (LBTYA) — 50% Owner</div>
    <ul class="init-bullets">
      <li>Listed: NASDAQ (LBTYA/LBTYB/LBTYK)</li>
      <li>Liberty Global holds 50% of VMO2 JV</li>
      <li>Also owns Sunrise (Switzerland), Telenet (Belgium)</li>
      <li>Strategy: cable/fiber broadband + content bundles</li>
      <li>VMO2 is Liberty Global's largest single asset</li>
    </ul>
  </div>
  <div class="init-card" style="border-left:3px solid {tef_clr}">
    <div class="init-title" style="margin-bottom:10px">Telefónica (TEF) — 50% Owner</div>
    <ul class="init-bullets">
      <li>Listed: BME (TEF) + NYSE ADR</li>
      <li>Telefónica holds 50% via O2 UK contribution</li>
      <li>Also owns O2 Germany, Movistar (Spain/LATAM)</li>
      <li>Strategy: asset-light; JV cash generation</li>
      <li>VMO2 contributes to Telefónica Europe cash flow</li>
    </ul>
  </div>
</div>"""


def _build_html(divs):
    kpi_html = "".join(kpi_card(lbl, val, prior, unit, slug, ACCENT)
                       for lbl, val, prior, unit, slug in KPI_DATA)

    initiatives = [
        ("📡", "5G Network Expansion", "O2 network — 87% UK pop coverage (2025)",
         ["87% UK population 5G coverage achieved FY2025 (+12pp YoY)",
          "O2 operates the UK's most widely deployed 5G network",
          "5G Standalone (SA) core deployment underway",
          "Network sharing with Vodafone UK (CTIL) maximises coverage"], ACCENT),
        ("🔵", "Full-Fiber Acceleration", "Virgin Media next-gen network build",
         ["8.3M full-fiber premises passed by end FY2025",
          "+1.4M homes passed YoY — fastest expansion rate",
          "Target: cover all 17M VM cable homes with fiber",
          "Gigabit speeds on upgraded HFC and FTTP"], BLU),
        ("📱", "O2 Mobile Strategy", "UK's largest mobile network by connections",
         ["23M+ mobile connections including MVNO base",
          "O2 Priority perks platform drives loyalty and ARPU",
          "Business segment: enterprise 5G and IoT growing",
          "MVNO partnerships (Sky, Tesco, Lycamobile) add scale"], TEA),
        ("🏠", "Convergence (Fixed + Mobile)", "UK's leading converged operator",
         ["Only UK operator with national cable broadband + mobile",
          "Volt bundle (VM broadband + O2 mobile) — key differentiator",
          "Convergence drives lower churn vs. single-play",
          "Cross-sell penetration growing in both subscriber bases"], GRN),
        ("🤖", "AI & Network Automation", "Smart operations and customer experience",
         ["AI-powered network fault detection and self-healing",
          "Virtual assistant (Aura) handling customer care",
          "Dynamic network management reducing manual intervention",
          "Predictive CapEx allocation based on demand signals"], ORG),
        ("📊", "DAISY Transaction", "O2 infrastructure monetisation",
         ["O2 tower/infrastructure assets sold to DAISY (est.)",
          "Sale-leaseback improves near-term balance sheet",
          "Lease costs impact FY2026 FCF (~£200M guided)",
          "Unlocks capital for network reinvestment"], YLW),
    ]
    init_html = "".join(initiative_card(*args) for args in initiatives)

    guide_data = [
        ("Adj. EBITDA (FY2025)", "£3.89B", "-2.3% YoY", ACCENT),
        ("Adj. FCF (FY2025)",    "£0.39B", "Daisy-impacted", GRN),
        ("CapEx",                "~£2.1B", "Fiber acceleration", ORG),
        ("5G Coverage",          "87%",    "+12pp YoY", BLU),
    ]
    guide_html = "".join(guidance_card(*args) for args in guide_data)

    body_html = f"""
<div class="section" id="kpis">
  <div class="section-title"><span class="dot"></span>Q2 2025 Key Performance Indicators</div>
  <div class="section-sub">Q2 2025 vs Q2 2024. Source: VMO2 quarterly press release / Liberty Global Q2 2025 results.</div>
  <div class="kpi-grid">{kpi_html}</div>
  <div class="est-note">
    <strong>Private JV:</strong> Virgin Media O2 is a private joint venture (Liberty Global 50% + Telefónica 50%, formed June 2021).
    Financials reported quarterly via Liberty Global IR. Values in GBP. Approx. USD equiv. at £1 = ${GBP_USD:.2f} noted in footer.
  </div>
</div>

<div class="section" id="revenue">
  <div class="section-title"><span class="dot"></span>Revenue & EBITDA Margin</div>
  <div class="section-sub">Quarterly revenue trend FY2024–FY2025 (Q2 2025 is latest available). Lighter bars = FY2025.</div>
  <div class="chart-wrap">
    {divs['revenue']}
    <div class="chart-note">Source: Liberty Global quarterly results / VMO2 press releases. All values in GBP billions.</div>
  </div>
</div>

<div class="section" id="financials">
  <div class="section-title"><span class="dot"></span>Annual Financial Performance</div>
  <div class="section-sub">FY2023–FY2025 actuals. EBITDA margin annotated above bars. FCF decline in FY2025 driven by Daisy transaction financing.</div>
  <div class="chart-grid-2">
    <div class="chart-wrap">
      {divs['annual']}
      <div class="chart-note">FCF pressure in FY2025 (£0.39B vs £0.67B) reflects Daisy financing requirements; FY2026 guided at ~£200M.</div>
    </div>
    <div class="chart-wrap">
      {divs['5g_rollout']}
      <div class="chart-note">5G coverage +12pp to 87% in FY2025. Full-fiber footprint expanded to 8.3M homes (+1.4M YoY).</div>
    </div>
  </div>
</div>

<div class="section" id="network">
  <div class="section-title"><span class="dot"></span>Network Domain — 5G, Fiber & Strategic Initiatives</div>
  <div class="section-sub">UK's only national converged operator — O2 mobile + Virgin Media cable/fiber. Network investment focus: 5G densification and full-fiber upgrade.</div>
  <div class="init-grid">{init_html}</div>
</div>

<div class="section" id="subscribers">
  <div class="section-title"><span class="dot"></span>Subscriber Metrics</div>
  <div class="section-sub">O2 mobile connections (~23M) and Virgin Media broadband subscribers (5.6M). Broadband faces competitive pressure from BT/Sky; mobile stable.</div>
  <div class="chart-wrap">
    {divs['subscribers']}
    <div class="chart-note">Broadband subscriber loss (-130K FY2024) reflects competitive broadband market. O2 mobile stable at 23M connections including MVNO partners.</div>
  </div>
</div>

<div class="section" id="outlook">
  <div class="section-title"><span class="dot"></span>FY2025 Performance & Outlook</div>
  <div class="section-sub">From FY2025 results and Liberty Global IR. FY2026 FCF guidance ~£200M impacted by Daisy lease costs.</div>
  <div class="guide-grid">{guide_html}</div>
  <div style="margin-top:24px">
    <div class="section-title" style="font-size:15px;margin-bottom:12px"><span class="dot"></span>Parent Company Context</div>
    <div class="section-sub">VMO2 is 100% privately held. For investors, exposure is via parent companies below.</div>
    {divs['parents']}
  </div>
</div>
"""

    sources_html = f"""
<strong>Data Sources:</strong>
Liberty Global Investor Relations (libertyglobal.com/investors) &middot;
VMO2 press releases (news.virginmediao2.co.uk) &middot;
Ofcom UK telecoms data.<br>
<strong>FX Note:</strong> All financials in GBP. Approx. USD: GBP/USD ~{GBP_USD:.2f} (April 2026).
Q2 2025 revenue £2.53B ≈ ${2.53*GBP_USD:.1f}B USD · FY2025 EBITDA £3.89B ≈ ${3.89*GBP_USD:.1f}B USD.<br>
<strong>Note:</strong> VMO2 is a private JV (Liberty Global 50% + Telefónica 50%); no standalone stock listing.
Financials reported quarterly via Liberty Global results. Semi-annual consolidated view also available via Liberty Global Annual Report.<br>
"""

    nav_links = [
        ("kpis",        "KPIs"),
        ("revenue",     "Revenue"),
        ("financials",  "Financials"),
        ("network",     "Network"),
        ("subscribers", "Subscribers"),
        ("outlook",     "Outlook"),
    ]
    carrier_meta = {
        "name":           "Virgin Media O2",
        "ticker":         "Private JV",
        "accent":         ACCENT,
        "flag":           "🇬🇧",
        "region":         "Europe",
        "latest_quarter": "Q2 2025",
        "stock_period":   "N/A",
    }
    return page_shell(carrier_meta, nav_links, body_html, sources_html)
