"""
lib/carriers/vf_germany.py — Vodafone Germany carrier module
Sources: Vodafone Group IR (investors.vodafone.com), annual/semi-annual reports
Latest:  H1 FY2026 (April–September 2025, reported November 2025)
Note:    Vodafone uses Apr–Mar fiscal year. Germany is ~35% of Group service revenue.
         Stock chart uses parent Vodafone Group (VOD) on LSE/NASDAQ.
         All values in EUR billions unless stated.
         FY2025 included €4.35B impairment charge and TV-law headwinds (now abating).
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
ID      = "vf_germany"
ACCENT  = "#E60000"   # Vodafone Red
EUR_USD = 1.09        # Approximate EUR/USD — used for landing page summary

# ══════════════════════════════════════════════════════════════════════════════
#  DATA  (EUR billions unless stated; Vodafone fiscal year Apr-Mar)
#  FY2024 = Apr 2023–Mar 2024 | FY2025 = Apr 2024–Mar 2025
#  H1 FY2026 = Apr–Sep 2025 (latest reported)
#  Source: Vodafone Group annual/semi-annual results, Germany segment
# ══════════════════════════════════════════════════════════════════════════════

# Annual periods (Vodafone fiscal year)
ANN = ['FY2024', 'FY2025', 'H1 FY2026\n(6-month)']
A = dict(
    rev   = [11.5,  11.0,  6.0],    # Revenue €B (H1 FY2026 = 6-month figure)
    ebitda= [ 3.20,  2.80, 1.80],   # Adj. EBITDAaL €B
    mob   = [40.0,  39.5,  39.0],   # M mobile customers (est.)
    bb    = [ 2.80,  2.70,  2.60],  # M broadband/cable subscribers (est.)
    cov5g = [90,    92,    95],      # % Germany population 5G coverage (est.)
)
A['margin'] = [round(e/r*100, 1) for e, r in zip(A['ebitda'], A['rev'])]

# Half-year periods for trend chart
PERIODS = ["H1 FY2024", "H2 FY2024", "H1 FY2025", "H2 FY2025", "H1 FY2026"]
P = dict(
    rev   = [5.80, 5.70, 5.60, 5.40, 6.00],   # Revenue €B
    ebitda= [1.65, 1.55, 1.50, 1.30, 1.80],   # EBITDAaL €B (H2 FY2025 = TV law hit peak)
    svc_gr= [0.0, -2.5, -5.0, -5.0, 0.5],     # Service revenue YoY growth %
)
P['margin'] = [round(e/r*100, 1) for e, r in zip(P['ebitda'], P['rev'])]

KPI_DATA = [
    # H1 FY2026 vs H1 FY2025
    ("Revenue (6-month)",   6.00, 5.60, "€B", "svc_rev"),
    ("Adj. EBITDAaL",       1.80, 1.50, "€B", "ebitda"),
    ("EBITDAaL Margin",    30.0, 26.8,  "%",  "margin"),
    ("Mobile Customers",   39.0, 39.5,  "M",  "adds"),
    ("Broadband/Cable",     2.60, 2.70, "M",  "broadband"),
    ("5G Coverage",         95,   92,   "%",  "coverage"),
]


def get_summary():
    return {
        "id":             ID,
        "svc_rev":        round(6.0 * EUR_USD / 2, 1),  # H1 FY2026 annualized quarterly in USD
        "ebitda_margin":  30.0,                           # % H1 FY2026
        "fcf_annual":     None,                             # Germany FCF not reported separately from Vodafone Group
        "subscribers":    39.0,                           # M mobile customers
        "coverage_5g":    95,                             # % Germany pop (est.)
        "latest_q":       "H1 FY2026",
        "capex_pct":      0.0,
    }


def generate(output_dir):
    print(f"  [VF Germany] Building charts...")
    divs = {
        "trend":        _chart_trend(),
        "annual":       _chart_annual(),
        "subscribers":  _chart_subscribers(),
        "coverage":     _chart_coverage(),
        "stock":        _chart_stock(),
    }
    html = _build_html(divs)
    out_path = os.path.join(output_dir, "vf_germany.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [VF Germany] Written -> {out_path}")
    return out_path


# ── Charts ────────────────────────────────────────────────────────────────────

def _chart_trend():
    """Half-yearly revenue/EBITDA trend including inflection in H1 FY2026."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    clrs = [hex_alpha(ACCENT, 0.5), hex_alpha(ACCENT, 0.5),
            hex_alpha(ACCENT, 0.7), hex_alpha(ACCENT, 0.7),
            ACCENT]
    fig.add_trace(go.Bar(
        x=PERIODS, y=P['rev'], name="Revenue (€B)",
        marker_color=clrs, cliponaxis=False,
        text=[f"€{v:.2f}B" for v in P['rev']],
        textposition="outside", textfont=dict(size=10, color=TXT),
        hovertemplate="<b>%{x}</b><br>Revenue: €%{y:.2f}B<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=PERIODS, y=P['margin'], name="EBITDAaL Margin %",
        mode="lines+markers",
        line=dict(color=TEA, width=2.5, dash="dot"),
        marker=dict(size=7, color=TEA),
        hovertemplate="<b>%{x}</b><br>EBITDAaL Margin: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)
    fig.update_layout(**base_layout(ACCENT, "Semi-Annual Revenue & EBITDAaL Margin Trend"))
    apply_axes(fig)
    fig.update_yaxes(title_text="EUR Billions", secondary_y=False, tickprefix="€")
    fig.update_yaxes(title_text="EBITDAaL Margin %", secondary_y=True,
                     ticksuffix="%", range=[20, 40], showgrid=False)
    fig.add_vrect(x0="H1 FY2026", x1="H1 FY2026", fillcolor=GRN, opacity=0.10, line_width=0)
    fig.add_annotation(x="H1 FY2026", y=6.5,
                       text="Inflection:<br>+0.5% svc rev growth<br>(TV law abating)",
                       showarrow=True, arrowhead=2, arrowcolor=GRN,
                       font=dict(size=9, color=GRN), bgcolor=CARD_BG,
                       bordercolor=GRN, borderwidth=1, xref="x", yref="y")
    fig.add_annotation(x="H2 FY2025", y=1.5,
                       text="TV law hit peak<br>(-7.5pp EBITDA impact)",
                       showarrow=True, arrowhead=2, arrowcolor=RED,
                       font=dict(size=9, color=RED), bgcolor=CARD_BG,
                       bordercolor=RED, borderwidth=1, xref="x", yref="y")
    return fig_to_div(fig, "vfde_chart_trend")


def _chart_annual():
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ANN, y=A['ebitda'], name="Adj. EBITDAaL",
                         marker_color=ACCENT, cliponaxis=False,
                         text=[f"€{v:.2f}B" for v in A['ebitda']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>EBITDAaL: €%{y:.2f}B<extra></extra>"))
    fig.add_trace(go.Bar(x=ANN, y=A['rev'], name="Total Revenue",
                         marker_color=hex_alpha(ACCENT, 0.45), cliponaxis=False,
                         text=[f"€{v:.1f}B" for v in A['rev']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>Revenue: €%{y:.1f}B<extra></extra>"))
    fig.update_layout(**base_layout(ACCENT, "Annual Revenue & EBITDAaL (EUR, Vodafone FY)"),
                      barmode="group")
    apply_axes(fig)
    fig.update_yaxes(title_text="EUR Billions", tickprefix="€", range=[0, 15])
    for i, (yr, m) in enumerate(zip(ANN, A['margin'])):
        fig.add_annotation(x=yr, y=A['ebitda'][i] + 0.4,
                           text=f"{m}%", showarrow=False,
                           font=dict(size=9, color=TEA), xref="x", yref="y")
    fig.add_annotation(x="FY2025", y=6.0,
                       text="€4.35B impairment<br>charge taken FY2025\n(not in EBITDAaL)",
                       showarrow=True, arrowhead=2, arrowcolor=RED,
                       font=dict(size=9, color=RED), bgcolor=CARD_BG,
                       bordercolor=RED, borderwidth=1)
    return fig_to_div(fig, "vfde_chart_annual")


def _chart_subscribers():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=ANN, y=A['mob'], name="Mobile Customers (M)",
                         marker_color=ACCENT, cliponaxis=False,
                         text=[f"{v:.1f}M" for v in A['mob']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>Mobile: %{y:.1f}M<extra></extra>"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=ANN, y=A['bb'], name="Broadband/Cable (M)",
                             mode="lines+markers+text",
                             line=dict(color=TEA, width=2.5),
                             marker=dict(size=9, color=TEA),
                             text=[f"{v:.2f}M" for v in A['bb']],
                             textposition="top center", textfont=dict(size=9, color=TEA),
                             hovertemplate="<b>%{x}</b><br>Broadband: %{y:.2f}M<extra></extra>"),
                  secondary_y=True)
    fig.update_layout(**base_layout(ACCENT, "Subscriber Metrics — Mobile & Broadband"))
    apply_axes(fig)
    fig.update_yaxes(title_text="Mobile Customers (M)", secondary_y=False,
                     ticksuffix="M", range=[37, 42])
    fig.update_yaxes(title_text="Broadband/Cable Subs (M)", secondary_y=True,
                     ticksuffix="M", range=[2.3, 3.1], showgrid=False)
    fig.add_annotation(x="FY2025", y=40.5,
                       text="Sub pressure from\n1&1 / O2 competition",
                       showarrow=True, arrowhead=2, arrowcolor=YLW,
                       font=dict(size=9, color=YLW), bgcolor=CARD_BG,
                       bordercolor=YLW, borderwidth=1)
    return fig_to_div(fig, "vfde_chart_subs")


def _chart_coverage():
    fig = go.Figure()
    clrs = [ORG, YLW, ACCENT]
    for yr, cov, clr in zip(ANN, A['cov5g'], clrs):
        fig.add_trace(go.Bar(
            x=[yr], y=[cov], name=yr, marker_color=clr,
            cliponaxis=False, showlegend=False,
            text=[f"{cov}%"], textposition="outside",
            textfont=dict(color=TXT, size=12),
            hovertemplate=f"<b>{yr}</b><br>5G Coverage: {cov}%<extra></extra>",
        ))
    fig.add_hline(y=95, line_dash="dot", line_color=GRN, line_width=1.5,
                  annotation_text="95% Germany target (H1 FY2026)",
                  annotation_position="right",
                  annotation_font=dict(color=GRN, size=9))
    fig.update_layout(**base_layout(ACCENT, "5G Network Coverage — % Germany Population"),
                      height=280)
    apply_axes(fig)
    fig.update_yaxes(title_text="% Germany Population", ticksuffix="%", range=[0, 115])
    return fig_to_div(fig, "vfde_chart_cov")


def _chart_stock():
    """Stock chart uses parent Vodafone Group (VOD)."""
    if not HAS_YF:
        return "<div class='chart-placeholder'>Stock chart unavailable - install yfinance</div>"

    print("    Fetching 3-year stock data (VOD, TEF, DTEGY, IYZ)...")
    end   = date.today()
    start = date(end.year - 3, end.month, end.day)
    tickers = {"VOD":   (ACCENT, "Vodafone Group (VOD) — Parent"),
               "TEF":   (BLU,    "Telefonica (TEF)"),
               "DTEGY": (ORG,    "Deutsche Telekom (DTEGY)"),
               "ORAN":  (TEA,    "Orange (ORAN)")}

    ssl_session = curl_requests.Session(verify=False, impersonate="chrome") if HAS_CURL else None
    traces, returns = [], {}
    for tkr, (clr, lbl) in tickers.items():
        try:
            obj = yf.Ticker(tkr, session=ssl_session) if ssl_session else yf.Ticker(tkr)
            raw = obj.history(start=str(start), end=str(end), auto_adjust=True)
            if raw.empty:
                continue
            prices  = raw['Close'].squeeze().dropna()
            norm    = (prices / prices.iloc[0]) * 100
            ret3y   = prices.iloc[-1] / prices.iloc[0] * 100 - 100
            ytd_st  = prices[prices.index >= f"{end.year}-01-01"]
            ret_ytd = (ytd_st.iloc[-1] / ytd_st.iloc[0] * 100 - 100) if len(ytd_st) > 1 else 0
            returns[tkr] = (ret3y, ret_ytd)
            traces.append(go.Scatter(
                x=norm.index, y=norm.values, name=lbl,
                line=dict(color=clr, width=2.5 if tkr == "VOD" else 1.8),
                hovertemplate=f"<b>{lbl}</b><br>%{{x|%b %Y}}<br>Indexed: %{{y:.1f}}<extra></extra>",
            ))
        except Exception as e:
            print(f"    Warning: {tkr}: {e}")

    if not traces:
        return "<div class='chart-placeholder'>Could not fetch stock data.</div>"

    fig = go.Figure(traces)
    fig.add_hline(y=100, line_dash="dot", line_color=MUTED, line_width=1,
                  annotation_text="Base (3yr ago = 100)", annotation_position="left",
                  annotation_font=dict(color=MUTED, size=9))
    events = [
        ("2024-05-14", "FY2024 results\nGermany -5% svc rev"),
        ("2024-09-16", "1&1 migration\ncompleted (12M cust.)"),
        ("2025-05-13", "FY2025 results\n€4.35B impairment"),
        ("2025-11-12", "H1 FY2026\nGermany inflection"),
    ]
    for ev_date, ev_text in events:
        try:
            ev_dt = pd.Timestamp(ev_date)
            if ev_dt > pd.Timestamp(str(end)):
                continue
            fig.add_vline(x=ev_dt, line_dash="dot",
                          line_color=hex_alpha(ACCENT, 0.40), line_width=1)
            fig.add_annotation(x=ev_dt, y=175, text=ev_text,
                               showarrow=False, textangle=-90,
                               font=dict(size=8, color=hex_alpha(ACCENT, 0.80)),
                               xref="x", yref="y")
        except Exception:
            pass

    ret_text = "  |  ".join(
        f"<b>{t}</b>: 3Y {r[0]:+.0f}%  YTD {r[1]:+.0f}%"
        for t, r in returns.items()
    )
    fig.update_layout(
        **base_layout(ACCENT, "3-Year Stock — Vodafone Group (VOD) vs European Telecom Peers"),
        annotations=[a for a in fig.layout.annotations] + [
            dict(text=ret_text, showarrow=False,
                 xref="paper", yref="paper", x=0.01, y=-0.12,
                 font=dict(size=10, color=MUTED), align="left")
        ]
    )
    apply_axes(fig)
    fig.update_yaxes(title_text="Indexed Price (base=100)")
    return fig_to_div(fig, "vfde_chart_stock")


def _build_html(divs):
    kpi_html = "".join(kpi_card(lbl, val, prior, unit, slug, ACCENT)
                       for lbl, val, prior, unit, slug in KPI_DATA)

    initiatives = [
        ("🔴", "Market Stabilisation", "Returning to growth in H1 FY2026",
         ["H1 FY2026 service revenue +0.5% YoY — first positive print in 2+ years",
          "TV-law (MDU regulation) negative impact now abating",
          "1&1 network migration completed (12M customers moved to Vodafone)",
          "Wholesale revenue growing at higher margins vs retail ARPU"], ACCENT),
        ("🌐", "5G Network Leadership", "~95% Germany population coverage",
         ["95% Germany population 5G coverage target (H1 FY2026)",
          "5G Standalone deployment for network slicing / low-latency",
          "C-band spectrum (3.6 GHz) mid-band densification ongoing",
          "5G FWA (GigaCube) gaining traction in rural areas"], BLU),
        ("🔗", "OXG Fiber JV", "Fiber expansion via joint venture",
         ["OXG JV with Telefónica Germany — shared fiber build",
          "1M+ households now commercially available on fiber (FY2025)",
          "Asset-light model: reduces Vodafone DE CapEx burden",
          "Targets 7M+ homes passed by end of 2030"], GRN),
        ("🏭", "Enterprise & IoT", "B2B and private 5G networks",
         ["Largest enterprise customer base in Germany (~250K business customers)",
          "Private 5G networks: manufacturing, logistics, smart factories",
          "IoT connections: 100M+ globally; Germany a key hub",
          "SD-WAN and SASE (managed networking) fast-growing"], TEA),
        ("🤖", "Network AI & Automation", "Group-wide Gigabit Operations",
         ["Vodafone Group 'Gigabit Operations' programme targets 30% opex savings",
          "AI-powered network self-healing and proactive fault management",
          "RAN optimization using ML for interference management",
          "Customer-facing AI (TOBi chatbot) reducing contact centre load"], ORG),
        ("💡", "Fixed-Mobile Convergence", "GigaKombi bundle strategy",
         ["GigaKombi (cable/DSL + mobile) bundle drives ARPA growth",
          "Convergence customers have materially lower churn",
          "DSL + cable footprint: ~2.6M broadband customers",
          "TV/entertainment remains a differentiator vs pure-play mobile"], PRP),
    ]
    init_html = "".join(initiative_card(*args) for args in initiatives)

    guide_data = [
        ("H1 FY2026 Revenue",  "€6.0B",  "+7% vs H1 FY2025", ACCENT),
        ("EBITDAaL Margin",    "30%",     "Recovery from 25.5% trough", TEA),
        ("5G Coverage",        "~95%",    "Germany population", GRN),
        ("Broadband/Cable",    "~2.6M",   "Stable; fiber JV ramping", BLU),
    ]
    guide_html = "".join(guidance_card(*args) for args in guide_data)

    body_html = f"""
<div class="section" id="kpis">
  <div class="section-title"><span class="dot"></span>H1 FY2026 Key Performance Indicators</div>
  <div class="section-sub">H1 FY2026 (Apr–Sep 2025) vs H1 FY2025 (Apr–Sep 2024). Source: Vodafone Group H1 FY2026 results (November 2025).</div>
  <div class="kpi-grid">{kpi_html}</div>
  <div class="est-note">
    <strong>Segment note:</strong> Vodafone Germany is a segment within Vodafone Group plc (VOD: LSE/NASDAQ).
    Fiscal year Apr–Mar. H1 FY2026 = Apr–Sep 2025. Germany CapEx/FCF not separately disclosed from Group.
    €4.35B impairment charge was taken in FY2025 due to competitive headwinds (excluded from EBITDAaL).
    Values in EUR. Approx. USD at €1 = ${EUR_USD:.2f} noted in footer.
  </div>
</div>

<div class="section" id="revenue">
  <div class="section-title"><span class="dot"></span>Revenue & EBITDAaL Trend</div>
  <div class="section-sub">Semi-annual trend FY2024 through H1 FY2026. H1 FY2026 shows first revenue growth inflection after 2+ years of declines.</div>
  <div class="chart-wrap">
    {divs['trend']}
    <div class="chart-note">TV-law (MDU regulation) impacted revenue H2 FY2024–H2 FY2025. Impact now abating in H1 FY2026. 1&1 migration completed Sep 2024 adding wholesale revenue. Vodafone FY = Apr–Mar.</div>
  </div>
</div>

<div class="section" id="financials">
  <div class="section-title"><span class="dot"></span>Annual Financial Performance</div>
  <div class="section-sub">FY2024–H1 FY2026 annual figures. EBITDAaL margin recovering after TV-law trough. H1 FY2026 is 6-month figure.</div>
  <div class="chart-grid-2">
    <div class="chart-wrap">
      {divs['annual']}
      <div class="chart-note">FY2025 included €4.35B impairment (not in EBITDAaL). EBITDAaL declined due to TV-law regulation and mobile ARPU pressure. Recovery visible in H1 FY2026.</div>
    </div>
    <div class="chart-wrap">
      {divs['coverage']}
      <div class="chart-note">5G coverage reaching ~95% Germany population by H1 FY2026. Mid-band 3.6 GHz densification ongoing. OXG fiber JV expanding fixed network.</div>
    </div>
  </div>
</div>

<div class="section" id="network">
  <div class="section-title"><span class="dot"></span>Network Domain — 5G, Fiber JV & Strategic Initiatives</div>
  <div class="section-sub">Vodafone Germany: Europe's largest B2B telecom + second-largest mobile operator in Germany. Key initiatives: 5G densification, OXG fiber JV, enterprise private networks.</div>
  <div class="chart-grid-2" style="margin-bottom:16px">
    <div class="chart-wrap">
      {divs['subscribers']}
      <div class="chart-note">Mobile sub decline reflects competition from 1&1 (new entrant), O2/TEF, and Telekom. Broadband steady; OXG fiber JV to address fixed growth gap.</div>
    </div>
    <div class="chart-wrap">
      {divs['stock']}
      <div class="chart-note">Stock shows Vodafone Group (parent VOD) vs European telecom peers. Germany represents ~35% of Group service revenue. VOD undergoes portfolio transformation (Vantage Towers, Indus Towers).</div>
    </div>
  </div>
  <div class="init-grid">{init_html}</div>
</div>

<div class="section" id="outlook">
  <div class="section-title"><span class="dot"></span>H1 FY2026 Performance & Outlook</div>
  <div class="section-sub">From Vodafone Group H1 FY2026 results (November 2025). Germany on path to return to growth; TV-law headwinds abating; 1&1 migration complete.</div>
  <div class="guide-grid">{guide_html}</div>
  <div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div class="init-card" style="border-left:3px solid {ACCENT}">
      <div class="init-title" style="margin-bottom:10px">FY2026 Strategic Priorities</div>
      <ul class="init-bullets">
        <li>Return Germany service revenue to sustained growth</li>
        <li>Scale OXG fiber JV to 2M+ homes commercially available</li>
        <li>5G Advanced deployment for enterprise private networks</li>
        <li>Drive EBITDAaL margin back toward 30%+ by FY2027</li>
      </ul>
    </div>
    <div class="init-card" style="border-left:3px solid {TEA}">
      <div class="init-title" style="margin-bottom:10px">Market Position (Germany)</div>
      <ul class="init-bullets">
        <li>#2 mobile operator in Germany (~26% market share)</li>
        <li>Largest enterprise B2B telecoms provider in Germany</li>
        <li>5G coverage ~95% Germany — competitive with Telekom</li>
        <li>OXG JV: shared fiber build reduces standalone CapEx need</li>
      </ul>
    </div>
  </div>
</div>
"""

    sources_html = f"""
<strong>Data Sources:</strong>
Vodafone Group Investor Relations (investors.vodafone.com) &middot;
Vodafone FY2025 Full Year Results (May 2025) &middot;
Vodafone H1 FY2026 Results (November 2025) &middot;
Vodafone Group Annual Report FY2025.<br>
<strong>FX Note:</strong> All financials in EUR (Vodafone Group reports in EUR). Approx. USD: EUR/USD ~{EUR_USD:.2f} (April 2026).
H1 FY2026 revenue €6.0B ≈ ${6.0*EUR_USD:.1f}B USD. Germany EBITDAaL €1.80B ≈ ${1.80*EUR_USD:.2f}B USD.<br>
<strong>Note:</strong> Vodafone Germany is a subsidiary segment; Germany CapEx/FCF not separately disclosed.
€4.35B goodwill impairment in FY2025 reflects competitive pressure and lower-than-expected EBITDAaL — excluded from EBITDAaL metric.
Stock chart uses parent Vodafone Group (VOD) on LSE/NASDAQ, not a Germany-specific listing.<br>
"""

    nav_links = [
        ("kpis",       "KPIs"),
        ("revenue",    "Revenue Trend"),
        ("financials", "Financials"),
        ("network",    "Network Domain"),
        ("outlook",    "Outlook"),
    ]
    carrier_meta = {
        "name":           "Vodafone Germany",
        "ticker":         "VOD (parent)",
        "accent":         ACCENT,
        "flag":           "🇩🇪",
        "region":         "Europe",
        "latest_quarter": "H1 FY2026",
        "stock_period":   "3-Year (VOD)",
    }
    return page_shell(carrier_meta, nav_links, body_html, sources_html)
