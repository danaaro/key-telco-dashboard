"""
lib/carriers/globe.py — Globe Telecom (Philippines) carrier module
Sources: Globe Telecom IR, SEC (Philippines), PSE filings, press releases
Latest:  Q3 2025 (9M 2025 results; Q4 2025 expected Q1 2026)
Note:    Listed on Philippine Stock Exchange (PSE) as GLO; yfinance ticker GLO.PS
         Key differentiator: ~12% equity stake in GCash/Mynt (leading super-app)
         All values in PHP billions unless stated. FX: ~57.5 PHP/USD (Apr 2026)
"""
import os

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

# ── Carrier identity ──────────────────────────────────────────────────────────
ID      = "globe"
ACCENT  = "#0066CC"   # Globe Blue
PHP_USD = 0.0174      # Approximate PHP/USD — used for landing page summary (~57.5 PHP/USD)

# ══════════════════════════════════════════════════════════════════════════════
#  DATA  (PHP billions unless stated)
#  Source: Globe Telecom Investor Relations, PSE filings, press releases
# ══════════════════════════════════════════════════════════════════════════════

ANN = ['FY2023', 'FY2024', 'FY2025']
A = dict(
    rev    = [164.0, 168.7, 178.2],    # Service Revenue ₱B
    ebitda = [ 81.0,  86.8,  87.0],    # Adj. EBITDA ₱B (FY2025 est.)
    capex  = [ 49.6,  56.2,  46.2],    # CapEx ₱B
    mob    = [ 57.8,  60.9,  65.8],    # M mobile subscribers
    cov5g  = [  82,    85,    87],     # % coverage 5G (est.)
    gcash  = [  2.8,   3.8,   6.1],   # GCash/Mynt equity earnings ₱B
)
A['margin'] = [round(e/r*100, 1) for e, r in zip(A['ebitda'], A['rev'])]

# Quarterly data (₱B)
QTRS     = ["Q1'24", "Q2'24", "Q3'24", "Q4'24", "Q1'25", "Q2'25", "Q3'25"]
Q = dict(
    rev    = [39.5, 39.9, 40.9, 44.7, 39.9, 39.8, 42.4],   # Service Revenue ₱B
    ebitda = [20.2, 20.8, 22.4, 23.4, 20.6, 20.7, 22.9],   # EBITDA ₱B
)
Q['margin'] = [round(e/r*100, 1) for e, r in zip(Q['ebitda'], Q['rev'])]

# Subscriber detail
SUB_LABELS  = ["FY2023", "FY2024", "FY2025 (est.)"]
MOB_SUBS    = [57.8, 60.9, 65.8]       # M total mobile subs
SUBS_5G     = [ 6.0,  9.0, 12.5]       # M 5G subs (FY2025 = 9M 2025 reported + est.)
HOME_BB     = [ 3.0,  3.2,  3.4]       # M Home broadband/fiber subs (est.)

# Revenue segments ₱B (FY2024 vs FY2025)
SEG_LABELS  = ['Mobile Data', 'Mobile Voice/SMS', 'Home Broadband', 'Enterprise / Other']
SEG_FY2024  = [75.2, 39.6, 28.1, 25.8]
SEG_FY2025  = [82.3, 37.8, 30.4, 27.7]
SEG_COLORS  = [ACCENT, TEA, BLU, PRP]

# ── KPI summary block (Q3 2025 vs Q3 2024) ───────────────────────────────────
KPI_DATA = [
    ("Service Revenue", Q['rev'][6],   Q['rev'][2],   "₱B", "rev"),
    ("EBITDA",          Q['ebitda'][6],Q['ebitda'][2],"₱B", "ebitda"),
    ("EBITDA Margin",   Q['margin'][6],Q['margin'][2],"%" , "margin"),
    ("Mobile Subs",     65.8,          60.9,          "M",  "subs"),
    ("5G Coverage",     87.0,          85.0,          "%" , "coverage"),
    ("GCash Eq. Earn.", 6.1,           3.8,           "₱B", "gcash"),
]


# ══════════════════════════════════════════════════════════════════════════════
#  CHART BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _chart_quarterly() -> str:
    """Quarterly Service Revenue + EBITDA trend with margin line."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=QTRS, y=Q['rev'], name="Service Revenue",
        marker_color=ACCENT, opacity=0.85,
        text=[f"₱{v:.1f}B" for v in Q['rev']],
        textposition="outside", cliponaxis=False,
    ), secondary_y=False)

    fig.add_trace(go.Bar(
        x=QTRS, y=Q['ebitda'], name="EBITDA",
        marker_color=TEA, opacity=0.85,
        text=[f"₱{v:.1f}B" for v in Q['ebitda']],
        textposition="outside", cliponaxis=False,
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=QTRS, y=Q['margin'], name="EBITDA Margin %",
        mode="lines+markers",
        line=dict(color=YLW, width=2.5),
        marker=dict(size=7),
        text=[f"{v:.1f}%" for v in Q['margin']],
        textposition="top center",
    ), secondary_y=True)

    layout = base_layout(ACCENT, title="Quarterly Service Revenue & EBITDA (₱B)")
    layout.update(barmode="group", height=370,
                  margin=dict(l=65, r=65, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(title_text="₱ Billions", secondary_y=False, range=[0, 60])
    fig.update_yaxes(title_text="Margin %", secondary_y=True,
                     range=[40, 65], showgrid=False, ticksuffix="%")

    return fig_to_div(fig, "globe-chart-quarterly")


def _chart_annual() -> str:
    """Annual revenue, EBITDA, and CapEx grouped bars."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=ANN, y=A['rev'], name="Service Revenue",
        marker_color=ACCENT, opacity=0.85,
        text=[f"₱{v:.1f}B" for v in A['rev']],
        textposition="outside", cliponaxis=False,
    ))
    fig.add_trace(go.Bar(
        x=ANN, y=A['ebitda'], name="EBITDA",
        marker_color=TEA, opacity=0.85,
        text=[f"₱{v:.1f}B" for v in A['ebitda']],
        textposition="outside", cliponaxis=False,
    ))
    fig.add_trace(go.Bar(
        x=ANN, y=A['capex'], name="CapEx",
        marker_color=PRP, opacity=0.75,
        text=[f"₱{v:.1f}B" for v in A['capex']],
        textposition="outside", cliponaxis=False,
    ))

    layout = base_layout(ACCENT, title="Annual Financials (₱B) — FY2023–FY2025")
    layout.update(barmode="group", height=360,
                  margin=dict(l=65, r=50, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(range=[0, 220])

    return fig_to_div(fig, "globe-chart-annual")


def _chart_segments() -> str:
    """Revenue segment mix: FY2024 vs FY2025."""
    fig = go.Figure()

    for i, (label, color) in enumerate(zip(SEG_LABELS, SEG_COLORS)):
        fig.add_trace(go.Bar(
            x=["FY2024", "FY2025"],
            y=[SEG_FY2024[i], SEG_FY2025[i]],
            name=label,
            marker_color=color, opacity=0.85,
            text=[f"₱{SEG_FY2024[i]:.1f}B", f"₱{SEG_FY2025[i]:.1f}B"],
            textposition="inside", cliponaxis=False,
        ))

    layout = base_layout(ACCENT, title="Revenue Segment Mix (₱B) — FY2024 vs FY2025")
    layout.update(barmode="stack", height=360,
                  margin=dict(l=65, r=50, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(range=[0, 210])

    return fig_to_div(fig, "globe-chart-segments")


def _chart_subscribers() -> str:
    """Subscriber growth: Mobile total, 5G subs, Home broadband."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=SUB_LABELS, y=MOB_SUBS, name="Total Mobile Subs",
        marker_color=ACCENT, opacity=0.85,
        text=[f"{v:.1f}M" for v in MOB_SUBS],
        textposition="outside", cliponaxis=False,
    ))
    fig.add_trace(go.Bar(
        x=SUB_LABELS, y=SUBS_5G, name="5G Subscribers",
        marker_color=BLU, opacity=0.85,
        text=[f"{v:.1f}M" for v in SUBS_5G],
        textposition="outside", cliponaxis=False,
    ))
    fig.add_trace(go.Bar(
        x=SUB_LABELS, y=HOME_BB, name="Home Broadband",
        marker_color=TEA, opacity=0.85,
        text=[f"{v:.1f}M" for v in HOME_BB],
        textposition="outside", cliponaxis=False,
    ))

    layout = base_layout(ACCENT, title="Subscriber Metrics (Millions) — FY2023–FY2025")
    layout.update(barmode="group", height=360,
                  margin=dict(l=65, r=50, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(range=[0, 80])

    return fig_to_div(fig, "globe-chart-subscribers")


def _chart_gcash() -> str:
    """GCash/Mynt equity earnings trend — strategic differentiator."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=ANN, y=A['gcash'], name="GCash/Mynt Equity Earnings",
        marker_color=YLW, opacity=0.9,
        text=[f"₱{v:.1f}B" for v in A['gcash']],
        textposition="outside", cliponaxis=False,
    ))

    # Add annotation for FY2025
    fig.add_annotation(
        x="FY2025", y=6.1,
        text="+61% YoY<br>₱6.1B",
        showarrow=True, arrowhead=2,
        arrowcolor=YLW,
        font=dict(color=YLW, size=11),
        bgcolor=CARD_BG, bordercolor=YLW, borderwidth=1,
        ay=-40,
    )

    layout = base_layout(ACCENT, title="GCash / Mynt Equity Earnings (₱B) — Key Digital Asset")
    layout.update(height=340, margin=dict(l=65, r=50, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(range=[0, 8.5])

    return fig_to_div(fig, "globe-chart-gcash")


def _chart_stock() -> str:
    """GLO.PS vs PLDT (TEL.PS) and sector — 3-year performance."""
    try:
        import yfinance as yf
        import pandas as pd
        try:
            from curl_cffi import requests as cffi_requests
            session = cffi_requests.Session(impersonate="chrome")
        except ImportError:
            session = None

        tickers = {
            "Globe (GLO)":  "GLO.PS",
            "PLDT (TEL)":   "TEL.PS",
        }

        dfs = {}
        for label, sym in tickers.items():
            try:
                kwargs = {"period": "3y", "interval": "1wk", "auto_adjust": True}
                if session:
                    kwargs["session"] = session
                t = yf.Ticker(sym)
                hist = t.history(**kwargs)
                if hist.empty:
                    hist = yf.download(sym, period="3y", interval="1wk",
                                       auto_adjust=True, progress=False)
                if not hist.empty:
                    dfs[label] = hist["Close"]
            except Exception:
                pass

        if not dfs:
            raise ValueError("No stock data retrieved")

        base_date = None
        for ser in dfs.values():
            if base_date is None or ser.index[0] < base_date:
                base_date = ser.index[0]

        fig = go.Figure()
        colors = [ACCENT, BLU]
        for (label, ser), color in zip(dfs.items(), colors):
            base_val = ser.iloc[0]
            norm = (ser / base_val * 100).round(2)
            fig.add_trace(go.Scatter(
                x=norm.index, y=norm.values, name=label,
                line=dict(color=color, width=2.5),
                mode="lines",
            ))

        layout = base_layout(ACCENT, title="GLO vs PLDT — 3-Year Normalized Performance (Base=100)")
        layout.update(height=360, margin=dict(l=65, r=50, t=70, b=50))
        fig.update_layout(**layout)
        apply_axes(fig, ACCENT)
        fig.update_yaxes(ticksuffix="")
        fig.add_hline(y=100, line_dash="dot", line_color=MUTED, opacity=0.5)

        return fig_to_div(fig, "globe-chart-stock")

    except Exception as e:
        return f"""
        <div class='chart-wrap'>
          <div style='padding:32px;color:{MUTED};text-align:center;font-size:13px'>
            <div style='font-size:20px;margin-bottom:8px'>📊</div>
            Stock chart unavailable (PSE data): {e}<br>
            <small>GLO.PS trades on the Philippine Stock Exchange (PSE).</small>
          </div>
        </div>"""


# ══════════════════════════════════════════════════════════════════════════════
#  INITIATIVE CARDS
# ══════════════════════════════════════════════════════════════════════════════

def _initiatives_div() -> str:
    cards = [
        initiative_card("💰", "GCash / Mynt",
                        "Digital Financial Super-App — ~12% equity stake",
                        [
                            "FY2025 equity earnings: ₱6.1B (+61% YoY)",
                            "GCash: #1 e-wallet in Philippines, 94M+ registered users",
                            "Mynt fintech: expanding lending, insurance, investments",
                            "Growing to be a major earnings driver beyond telecom",
                        ], YLW),
        initiative_card("📡", "5G Leadership",
                        "87% population coverage — ahead of regional peers",
                        [
                            "12.5M 5G subscribers (9M 2025 data)",
                            "5G SA (Standalone) core deployed in key cities",
                            "5G mmWave trials for enterprise/venue use cases",
                            "Globe Business: 5G private network deployments",
                        ], ACCENT),
        initiative_card("🏠", "Home Broadband",
                        "Fiber-to-the-Home (FTTH) expansion",
                        [
                            "3.4M home broadband subscribers (FY2025 est.)",
                            "GoFiber rollout targeting underserved areas",
                            "FTTH now covers majority of new installs",
                            "Broadband ARPU uplift driving revenue mix shift",
                        ], TEA),
        initiative_card("🤖", "AI & Digital Transformation",
                        "Globe iQ — AI-driven network & customer ops",
                        [
                            "AI-powered network optimization reducing opex",
                            "Conversational AI for customer care (Globe One app)",
                            "Predictive maintenance reducing network downtime",
                            "Enterprise AI solutions via Globe Business",
                        ], BLU),
        initiative_card("🌏", "Enterprise & B2B",
                        "Globe Business — fastest-growing segment",
                        [
                            "ICT services: cloud, cybersecurity, data center",
                            "Partnership with Google Cloud, AWS",
                            "Philippine offshore BPO sector key enterprise target",
                            "5G private networks for manufacturing & logistics",
                        ], PRP),
        initiative_card("♻️", "Sustainability & ESG",
                        "Net Zero target 2050; renewable energy focus",
                        [
                            "RE100 commitment — 100% renewable energy target",
                            "E-waste program: 1,000+ tonnes collected",
                            "Digital inclusion: free connectivity for schools",
                            "MSCI ESG Rating: BBB (improving trajectory)",
                        ], GRN),
    ]
    return f'<div class="init-grid">{"".join(cards)}</div>'


# ══════════════════════════════════════════════════════════════════════════════
#  GUIDANCE / OUTLOOK
# ══════════════════════════════════════════════════════════════════════════════

def _guidance_div() -> str:
    cards = [
        guidance_card("FY2025 Service Revenue", "₱178B+",
                      "Driven by data monetization & enterprise growth", ACCENT),
        guidance_card("FY2025 EBITDA", "~₱87B",
                      "Margin ~52–53%; efficiency program offsetting rising costs", TEA),
        guidance_card("FY2025 CapEx", "~₱46B",
                      "Down from ₱56B in FY2024; network capex normalization", YLW),
        guidance_card("5G Subscribers", "12–15M",
                      "FY2025 target; monetization through premium plans", BLU),
        guidance_card("GCash Equity Earnings", "₱6B+",
                      "Structural earnings driver; Mynt IPO potential medium-term", PRP),
        guidance_card("Home Broadband", "3.5M+",
                      "FTTH expansion; GoFiber targeting 1M new passes/year", GRN),
    ]
    return f'<div class="guide-grid">{"".join(cards)}</div>'


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN BUILD FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def generate(output_dir: str) -> None:
    """Generate Globe Telecom dashboard HTML and write to output_dir."""
    import os as _os
    out_path = _os.path.join(output_dir, "globe.html")

    # ── KPI cards ─────────────────────────────────────────────────────────────
    kpi_html = '<div class="kpi-grid">'
    for label, val, prior, unit, slug in KPI_DATA:
        if unit == "₱B":
            # Extend kpi_card logic for PHP
            pct = (val - prior) / prior * 100
            arrow = "▲" if pct > 0 else "▼"
            good_up = slug not in ("churn", "capex")
            from lib.base import GRN, RED
            color = GRN if (pct > 0) == good_up else RED
            v_str = f"₱{val:.1f}B"
            kpi_html += f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{v_str}</div>
      <div class="kpi-delta" style="color:{color}">
        {arrow} {abs(pct):.1f}% vs prior year Q
      </div>
    </div>"""
        elif unit == "M":
            pct = (val - prior) / prior * 100
            arrow = "▲" if pct > 0 else "▼"
            good_up = True
            from lib.base import GRN, RED
            color = GRN if pct > 0 else RED
            v_str = f"{val:.1f}M"
            kpi_html += f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{v_str}</div>
      <div class="kpi-delta" style="color:{color}">
        {arrow} {abs(pct):.1f}% vs prior year
      </div>
    </div>"""
        else:
            kpi_html += kpi_card(label, val, prior, unit, slug, ACCENT)
    kpi_html += '</div>'

    # ── Estimate note ─────────────────────────────────────────────────────────
    est_note = """
    <div class="est-note">
      <strong>Data Note:</strong> Q3 2025 = 9-month 2025 results. FY2025 annual figures partially estimated
      (Globe reports semi-annually). Q4 2024 vs Q3 2024 used for YoY comparison. All values in Philippine
      Peso (₱). USD equivalents use ~57.5 PHP/USD (April 2026 rate).
    </div>"""

    # ── Charts ────────────────────────────────────────────────────────────────
    chart_quarterly  = _chart_quarterly()
    chart_annual     = _chart_annual()
    chart_segments   = _chart_segments()
    chart_subscribers = _chart_subscribers()
    chart_gcash      = _chart_gcash()
    chart_stock      = _chart_stock()

    # ── Body HTML ─────────────────────────────────────────────────────────────
    body = f"""
<!-- KPIs -->
<section class="section" id="kpis">
  <div class="section-title"><span class="dot"></span>Key Performance Indicators — Q3 2025 vs Q3 2024</div>
  <div class="section-sub">Quarterly snapshot · PHP values · YoY delta</div>
  {est_note}
  {kpi_html}
</section>

<!-- Revenue Analysis -->
<section class="section" id="revenue">
  <div class="section-title"><span class="dot"></span>Revenue Analysis</div>
  <div class="section-sub">Service Revenue & EBITDA trend (₱B)</div>
  <div class="chart-wrap">{chart_quarterly}
    <div class="chart-note">Quarterly Service Revenue and EBITDA (₱B). Q2–Q3 2025 = 9M 2025 partial data. EBITDA margin on right axis.</div>
  </div>
  <div class="chart-wrap">{chart_annual}
    <div class="chart-note">Annual financials FY2023–FY2025. FY2025 EBITDA partially estimated. CapEx declined in FY2025 post peak investment cycle.</div>
  </div>
  <div class="chart-wrap">{chart_segments}
    <div class="chart-note">Revenue segment mix FY2024 vs FY2025. Mobile Data growing as share; Voice/SMS declining structurally. Home Broadband expanding.</div>
  </div>
</section>

<!-- Network Domain -->
<section class="section" id="network">
  <div class="section-title"><span class="dot"></span>Network Domain &amp; 5G Leadership</div>
  <div class="section-sub">Subscriber growth · 5G adoption · Broadband expansion</div>
  <div class="chart-wrap">{chart_subscribers}
    <div class="chart-note">Subscriber base growth. Total mobile subs 65.8M (FY2025); 5G subs accelerating to 12.5M; Home broadband steady expansion via FTTH.</div>
  </div>
</section>

<!-- GCash / Digital -->
<section class="section" id="digital">
  <div class="section-title"><span class="dot"></span>GCash &amp; Digital Ecosystem</div>
  <div class="section-sub">Strategic fintech stake — fastest-growing earnings driver</div>
  <div class="chart-wrap">{chart_gcash}
    <div class="chart-note">Globe holds ~12% equity in Mynt (GCash parent). FY2025 equity earnings of ₱6.1B (+61% YoY) represent a growing non-telecom profit stream.</div>
  </div>
</section>

<!-- Strategic Initiatives -->
<section class="section" id="initiatives">
  <div class="section-title"><span class="dot"></span>Strategic Initiatives</div>
  <div class="section-sub">Network · Digital · Enterprise · Sustainability</div>
  {_initiatives_div()}
</section>

<!-- Stock Performance -->
<section class="section" id="stock">
  <div class="section-title"><span class="dot"></span>Stock Performance</div>
  <div class="section-sub">GLO.PS vs PLDT (TEL.PS) — Philippine Stock Exchange · 3-Year Normalized</div>
  <div class="chart-wrap">{chart_stock}
    <div class="chart-note">Normalized to 100 at start of period. Globe (GLO.PS) vs PLDT (TEL.PS). Data via Yahoo Finance / PSE. Weekly intervals.</div>
  </div>
</section>

<!-- Outlook -->
<section class="section" id="outlook">
  <div class="section-title"><span class="dot"></span>FY2025 Guidance &amp; Targets</div>
  <div class="section-sub">Management guidance as of Q3 2025 earnings</div>
  {_guidance_div()}
</section>
"""

    sources = """
<strong>Sources:</strong> Globe Telecom Investor Relations (globe.com.ph/ir) ·
Philippine Stock Exchange (PSE) filings · Globe press releases (9M 2025, FY2024 Annual Report) ·
Yahoo Finance (GLO.PS, TEL.PS) · GCash/Mynt press releases · Telecompaper ·
<a href="https://ir.globe.com.ph" target="_blank">ir.globe.com.ph</a><br>
"""

    carrier_meta = {
        "name":           "Globe Telecom",
        "ticker":         "GLO.PS",
        "accent":         ACCENT,
        "flag":           "🇵🇭",
        "region":         "APAC",
        "latest_quarter": "Q3 2025",
        "stock_period":   "3-Year (PSE)",
    }

    nav_links = [
        ("kpis",        "KPIs"),
        ("revenue",     "Revenue"),
        ("network",     "Network"),
        ("digital",     "GCash"),
        ("initiatives", "Initiatives"),
        ("stock",       "Stock"),
        ("outlook",     "Outlook"),
    ]

    html = page_shell(carrier_meta, nav_links, body, sources)
    _os.makedirs(_os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [Globe] Written -> {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
#  SUMMARY (used by generate_all.py landing page)
# ══════════════════════════════════════════════════════════════════════════════

def get_summary() -> dict:
    """Return landing-page summary metrics (USD-converted where needed)."""
    usd = PHP_USD
    q_rev_latest  = Q['rev'][6]    # Q3'25 ₱B
    q_rev_prior   = Q['rev'][2]    # Q3'24 ₱B
    ebitda_latest = Q['ebitda'][6]
    ebitda_prior  = Q['ebitda'][2]

    return {
        "id":            ID,
        "svc_rev":       round(q_rev_latest * usd, 2),    # Q3'25 revenue in $B
        "ebitda_margin": Q['margin'][6],                   # %
        "fcf_annual":    None,                             # FCF not separately disclosed by Globe
        "subscribers":   65.8,                             # M mobile subs FY2025
        "coverage_5g":   87,                               # % population 5G coverage
        "latest_q":      "Q3 2025",
        "rev_yoy_pct":   round((q_rev_latest - q_rev_prior) / q_rev_prior * 100, 1),
        "ebitda_yoy_pct":round((ebitda_latest - ebitda_prior) / ebitda_prior * 100, 1),
    }
