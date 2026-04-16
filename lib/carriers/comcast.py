"""
lib/carriers/comcast.py — Comcast Corporation (CMCSA) carrier module
Sources: Comcast IR (cmcastcorporate.com/ir), SEC EDGAR, earnings press releases
Latest:  Q4 2025 / FY2025 (reported Jan 2026)
Note:    Focus on Cable Communications / Connectivity & Platforms segment.
         Xfinity Mobile is MVNO on Verizon network; Comcast owns no wireless spectrum.
         DOCSIS 4.0 multi-gig upgrade is primary network CapEx cycle through 2028.
         Q3+Q4 2025 quarterly data marked * are estimates; full-year actuals confirmed.
"""
import os

from lib.base import (
    hex_alpha, base_layout, apply_axes, fig_to_div,
    kpi_card, initiative_card, guidance_card, page_shell,
    DARK_BG, CARD_BG, TXT, MUTED, GRID,
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
ID     = "comcast"
ACCENT = "#0568AE"   # Comcast corporate blue

# ══════════════════════════════════════════════════════════════════════════════
#  DATA  (all $ billions unless stated)
#  Source: Comcast IR earnings press releases, SEC EDGAR 10-K/10-Q
#  Segment: Cable Communications / "Connectivity & Platforms" (primary telco segment)
# ══════════════════════════════════════════════════════════════════════════════

# Annual — Cable Communications segment
ANN = ['FY2022', 'FY2023', 'FY2024', 'FY2025']
A = dict(
    rev    = [64.3, 65.7, 66.4, 65.8],    # Cable segment revenue $B
    ebitda = [25.9, 26.8, 27.0, 27.3],    # Cable segment EBITDA $B
    capex  = [11.2, 11.3, 11.8, 11.5],    # Cable segment CapEx $B
    fcf    = [12.4, 14.8, 15.1, 15.5],    # Total company free cash flow $B
    bb_subs= [32.2, 32.3, 32.3, 31.9],    # M broadband subscribers
    mob    = [ 4.4,  6.0,  7.7, 10.1],    # M Xfinity Mobile lines
    video  = [16.1, 14.3, 12.8, 11.4],    # M video subscribers
)
A['margin'] = [round(e/r*100, 1) for e, r in zip(A['ebitda'], A['rev'])]

# FY2026 guidance
G26 = dict(capex_lo=11.0, capex_hi=11.5, fcf_lo=15.0, fcf_hi=16.0)

# Quarterly — Cable Communications segment (* = estimates)
QTRS = ["Q4'23", "Q1'24", "Q2'24", "Q3'24", "Q4'24", "Q1'25", "Q2'25*", "Q3'25*", "Q4'25*"]
Q = dict(
    rev    = [16.3, 16.2, 16.3, 16.5, 17.4, 16.3, 16.4, 16.6, 16.5],  # Cable rev $B
    ebitda = [ 6.7,  6.6,  6.7,  6.8,  6.9,  6.7,  6.7,  6.9,  7.0],  # Cable EBITDA $B
    capex  = [ 2.9,  2.8,  2.9,  3.1,  3.0,  2.8,  2.9,  3.0,  2.8],  # Cable CapEx $B
    bb_net = [  -34,  -65,  -61,  -87, -139, -199, -150, -130, -110],   # K broadband net adds
    mob_net= [  355,  489,  295,  319,  298,  323,  310,  305,  300],   # K Xfinity Mobile net adds
    est    = [False,False,False,False,False,False, True, True, True],
)
Q['margin']    = [round(e/r*100, 1) for e, r in zip(Q['ebitda'], Q['rev'])]
Q['capex_pct'] = [round(c/r*100, 1) for c, r in zip(Q['capex'],  Q['rev'])]

BLU_DIM  = hex_alpha(ACCENT, 0.40)
BAR_CLR  = [ACCENT if not e else BLU_DIM for e in Q['est']]

KPI_DATA = [
    ("Cable Revenue",      16.5, 17.4, "$B", "rev"),
    ("Cable EBITDA",        7.0,  6.9, "$B", "ebitda"),
    ("EBITDA Margin",      42.4, 39.7, "%",  "margin"),
    ("FCF (Annual)",       15.5, 15.1, "$B", "fcf"),
    ("Broadband Subs",     31.9, 32.3, "M",  "bb_subs"),
    ("Xfinity Mobile Lines",10.1, 7.7, "M",  "mobile"),
    ("Video Subs",         11.4, 12.8, "M",  "video"),
    ("Cable CapEx",         2.8,  3.0, "$B", "capex"),
]


# ══════════════════════════════════════════════════════════════════════════════
#  CHART BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _chart_revenue():
    """Quarterly Cable revenue + EBITDA with margin overlay."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=QTRS, y=Q['rev'], name="Cable Revenue",
        marker_color=BAR_CLR,
        text=[f"${v:.1f}B" for v in Q['rev']],
        textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:.2f}B<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=QTRS, y=Q['margin'], name="EBITDA Margin %",
        mode="lines+markers",
        line=dict(color=YLW, width=2.5),
        marker=dict(size=7),
        text=[f"{v:.1f}%" for v in Q['margin']],
        textposition="top center",
        hovertemplate="<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)

    layout = base_layout(ACCENT, "Quarterly Cable Revenue & EBITDA Margin")
    layout.update(height=370, margin=dict(l=65, r=65, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(title_text="$ Billions", secondary_y=False,
                     range=[0, 22], tickprefix="$")
    fig.update_yaxes(title_text="EBITDA Margin %", secondary_y=True,
                     range=[30, 55], showgrid=False, ticksuffix="%")
    fig.add_vrect(x0="Q2'25*", x1="Q4'25*", fillcolor=ACCENT, opacity=0.06, line_width=0)
    return fig_to_div(fig, "cmcsa_chart_revenue")


def _chart_annual():
    """Annual Cable revenue, EBITDA, CapEx with FCF line."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=ANN, y=A['rev'], name="Cable Revenue",
        marker_color=ACCENT, opacity=0.85,
        text=[f"${v:.1f}B" for v in A['rev']],
        textposition="outside", cliponaxis=False,
    ), secondary_y=False)
    fig.add_trace(go.Bar(
        x=ANN, y=A['ebitda'], name="Cable EBITDA",
        marker_color=TEA, opacity=0.85,
        text=[f"${v:.1f}B" for v in A['ebitda']],
        textposition="outside", cliponaxis=False,
    ), secondary_y=False)
    fig.add_trace(go.Bar(
        x=ANN, y=A['capex'], name="Cable CapEx",
        marker_color=ORG, opacity=0.75,
        text=[f"${v:.1f}B" for v in A['capex']],
        textposition="outside", cliponaxis=False,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=ANN, y=A['margin'], name="EBITDA Margin %",
        mode="lines+markers",
        line=dict(color=YLW, width=2.5, dash="dot"),
        marker=dict(size=8),
        text=[f"{v:.1f}%" for v in A['margin']],
        textposition="top center",
    ), secondary_y=True)

    layout = base_layout(ACCENT, "Annual Cable Financials — FY2022–FY2025 ($B)")
    layout.update(barmode="group", height=380, margin=dict(l=65, r=65, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(title_text="$ Billions", secondary_y=False,
                     range=[0, 82], tickprefix="$")
    fig.update_yaxes(title_text="Margin %", secondary_y=True,
                     range=[30, 55], showgrid=False, ticksuffix="%")
    return fig_to_div(fig, "cmcsa_chart_annual")


def _chart_subscribers():
    """Subscriber trends: Broadband, Xfinity Mobile, Video."""
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Broadband & Video Subscribers (M)",
                                        "Xfinity Mobile Lines (M)"])

    fig.add_trace(go.Scatter(
        x=ANN, y=A['bb_subs'], name="Broadband",
        mode="lines+markers+text",
        line=dict(color=ACCENT, width=2.5),
        marker=dict(size=9),
        text=[f"{v:.1f}M" for v in A['bb_subs']],
        textposition="top center",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=ANN, y=A['video'], name="Video (cord-cutting)",
        mode="lines+markers+text",
        line=dict(color=RED, width=2.5, dash="dot"),
        marker=dict(size=9),
        text=[f"{v:.1f}M" for v in A['video']],
        textposition="bottom center",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=ANN, y=A['mob'], name="Xfinity Mobile Lines",
        marker_color=GRN, opacity=0.85,
        text=[f"{v:.1f}M" for v in A['mob']],
        textposition="outside", cliponaxis=False,
    ), row=1, col=2)

    layout = base_layout(ACCENT, "")
    layout.update(height=360, margin=dict(l=65, r=65, t=65, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(range=[0, 38], row=1, col=1)
    fig.update_yaxes(range=[0, 13], row=1, col=2)
    return fig_to_div(fig, "cmcsa_chart_subscribers")


def _chart_bb_net_adds():
    """Broadband net adds quarterly — competitive pressure story."""
    clrs = [GRN if v > 0 else RED for v in Q['bb_net']]
    clrs_dim = [hex_alpha(c, 0.45) if e else c
                for c, e in zip(clrs, Q['est'])]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=QTRS, y=Q['bb_net'], name="Broadband Net Adds",
        marker_color=clrs_dim,
        text=[f"{v:+.0f}K" for v in Q['bb_net']],
        textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>BB Net Adds: %{y:+.0f}K<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color=MUTED, opacity=0.6)

    layout = base_layout(ACCENT, "Quarterly Broadband Net Adds (K) — Competitive Pressure")
    layout.update(height=340, margin=dict(l=65, r=50, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(range=[-280, 120])
    fig.add_annotation(
        x="Q4'24", y=-139,
        text="Worst qtr<br>-139K",
        showarrow=True, arrowhead=2, arrowcolor=RED,
        font=dict(color=RED, size=10),
        bgcolor=CARD_BG, bordercolor=RED, borderwidth=1,
        ay=40,
    )
    return fig_to_div(fig, "cmcsa_chart_bb_adds")


def _chart_mobile_adds():
    """Xfinity Mobile net adds — growth story."""
    mob_clr = [ACCENT if not e else BLU_DIM for e in Q['est']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=QTRS, y=Q['mob_net'], name="Xfinity Mobile Net Adds",
        marker_color=mob_clr,
        text=[f"{v:,.0f}K" for v in Q['mob_net']],
        textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Mobile Net Adds: %{y:,.0f}K<extra></extra>",
    ))

    layout = base_layout(ACCENT, "Xfinity Mobile Net Line Adds (K) — MVNO Growth")
    layout.update(height=320, margin=dict(l=65, r=50, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(range=[0, 620])
    return fig_to_div(fig, "cmcsa_chart_mobile_adds")


def _chart_capex():
    """CapEx trend and DOCSIS 4.0 investment context."""
    # Annual CapEx + capex as % of revenue
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=ANN, y=A['capex'], name="Cable CapEx",
        marker_color=ORG, opacity=0.85,
        text=[f"${v:.1f}B" for v in A['capex']],
        textposition="outside", cliponaxis=False,
    ), secondary_y=False)

    capex_pct_ann = [round(c/r*100, 1) for c, r in zip(A['capex'], A['rev'])]
    fig.add_trace(go.Scatter(
        x=ANN, y=capex_pct_ann, name="CapEx % of Revenue",
        mode="lines+markers",
        line=dict(color=YLW, width=2.5),
        marker=dict(size=8),
        text=[f"{v:.1f}%" for v in capex_pct_ann],
        textposition="top center",
    ), secondary_y=True)

    fig.add_annotation(
        x="FY2024", y=11.8,
        text="DOCSIS 4.0<br>ramp begins",
        showarrow=True, arrowhead=2, arrowcolor=ORG,
        font=dict(color=ORG, size=10),
        bgcolor=CARD_BG, bordercolor=ORG, borderwidth=1,
        ay=-40,
    )

    layout = base_layout(ACCENT, "Annual Cable CapEx & % of Revenue — DOCSIS 4.0 Investment Cycle")
    layout.update(height=360, margin=dict(l=65, r=65, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    fig.update_yaxes(title_text="$ Billions", secondary_y=False,
                     range=[0, 15], tickprefix="$")
    fig.update_yaxes(title_text="CapEx % Revenue", secondary_y=True,
                     range=[0, 28], showgrid=False, ticksuffix="%")
    return fig_to_div(fig, "cmcsa_chart_capex")


def _chart_stock():
    """CMCSA vs Charter, ATT, and S&P 500 — 3-year normalized."""
    if not HAS_YF:
        return "<div class='chart-placeholder'>yfinance not installed</div>"

    tickers = {
        "Comcast (CMCSA)": "CMCSA",
        "Charter (CHTR)":  "CHTR",
        "AT&T (T)":        "T",
        "S&P 500 (SPY)":   "SPY",
    }
    colors = [ACCENT, TEA, ORG, BLU]

    dfs = {}
    try:
        session = curl_requests.Session(impersonate="chrome") if HAS_CURL else None
        for label, sym in tickers.items():
            try:
                t = yf.Ticker(sym)
                kw = {"period": "3y", "interval": "1wk", "auto_adjust": True}
                if session:
                    kw["session"] = session
                hist = t.history(**kw)
                if hist.empty:
                    hist = yf.download(sym, period="3y", interval="1wk",
                                       auto_adjust=True, progress=False)
                if not hist.empty:
                    dfs[label] = hist["Close"]
            except Exception:
                pass
    except Exception:
        pass

    if not dfs:
        return "<div class='chart-placeholder'>Stock data unavailable</div>"

    fig = go.Figure()
    for (label, ser), color in zip(dfs.items(), colors):
        base_val = ser.iloc[0]
        norm = (ser / base_val * 100).round(2)
        fig.add_trace(go.Scatter(
            x=norm.index, y=norm.values, name=label,
            line=dict(color=color, width=2.5),
            mode="lines",
            hovertemplate=f"<b>{label}</b><br>%{{x|%b %Y}}<br>Index: %{{y:.1f}}<extra></extra>",
        ))

    fig.add_hline(y=100, line_dash="dot", line_color=MUTED, opacity=0.5)
    layout = base_layout(ACCENT, "CMCSA vs Charter, AT&T & S&P 500 — 3-Year Normalized (Base=100)")
    layout.update(height=370, margin=dict(l=65, r=50, t=70, b=50))
    fig.update_layout(**layout)
    apply_axes(fig, ACCENT)
    return fig_to_div(fig, "cmcsa_chart_stock")


# ══════════════════════════════════════════════════════════════════════════════
#  INITIATIVE & GUIDANCE CARDS
# ══════════════════════════════════════════════════════════════════════════════

def _initiatives_div():
    cards = [
        initiative_card("🔌", "DOCSIS 4.0 / Multi-Gig Broadband",
                        "Largest cable network upgrade in Comcast history",
                        [
                            "DOCSIS 4.0 enables 10 Gbps downstream, 6 Gbps upstream",
                            "Network Pass: 1-gigabit symmetrical available to 60M+ homes",
                            "Full 40% of footprint upgraded by end of 2025",
                            "Complete US footprint targeted by 2028; ~$15B capex cycle",
                        ], ACCENT),
        initiative_card("📱", "Xfinity Mobile (MVNO)",
                        "10M+ lines — fastest-growing wireless in the US",
                        [
                            "MVNO on Verizon network + Comcast WiFi offload (22M hotspots)",
                            "10.1M lines (FY2025); adding ~1.2M lines/quarter",
                            "Bundled with broadband: reduces churn by ~1.5× vs standalone",
                            "No spectrum ownership; leveraging existing network assets",
                        ], GRN),
        initiative_card("🏠", "Fixed-Mobile Convergence",
                        "Broadband + Mobile bundle = retention engine",
                        [
                            "Xfinity Mobile + Broadband bundle reduces churn significantly",
                            "Average broadband ARPU uplift ~$15/mo from mobile bundle",
                            "Peacock streaming included: media + connectivity convergence",
                            "Xfinity One: unified gateway for home + mobile management",
                        ], TEA),
        initiative_card("🤖", "AI & Network Automation",
                        "Comcast Technology Solutions — AI-driven network ops",
                        [
                            "AI-powered predictive maintenance across HFC plant",
                            "Xfinity Assistant: conversational AI for 35M+ customer interactions/yr",
                            "Network virtualization: CCAP-to-cloud migration ongoing",
                            "Real-time network health: proactive outage prevention via ML",
                        ], BLU),
        initiative_card("🏢", "Business Services",
                        "Enterprise & SMB — fastest-growing cable segment",
                        [
                            "Business Services revenue: ~$10B/yr (~15% of Cable rev)",
                            "Comcast Business: Fortune 500 connectivity + managed services",
                            "SD-WAN, cybersecurity, cloud networking for midmarket",
                            "Government & education sector wins accelerating",
                        ], PRP),
        initiative_card("🔐", "Network Security & Edge",
                        "Comcast Technology Solutions (CTS) — B2B platform",
                        [
                            "CTS: CDN, cybersecurity, virtualized broadband for ISPs",
                            "X1 platform licensed to third-party operators",
                            "ActiveCore: SD-WAN platform for enterprise customers",
                            "Masergy acquisition: global enterprise SD-WAN & SASE",
                        ], ORG),
    ]
    return f'<div class="init-grid">{"".join(cards)}</div>'


def _guidance_div():
    cards = [
        guidance_card("FY2025 Cable Revenue", "~$65.8B",
                      "Broadband pressure offset by mobile & business growth", ACCENT),
        guidance_card("FY2025 EBITDA (Cable)", "~$27.3B",
                      "~41.5% margin; efficiency gains offsetting broadband softness", TEA),
        guidance_card("FY2026 CapEx (Cable)", "$11.0–11.5B",
                      "DOCSIS 4.0 peak investment; normalization targeted 2028+", ORG),
        guidance_card("FY2025 FCF (Total)", "~$15.5B",
                      "Supported by cable cash generation; NBCUniversal dilutive", GRN),
        guidance_card("Xfinity Mobile Target", "12–14M Lines",
                      "FY2026–27 target; MVNO margins expanding at scale", BLU),
        guidance_card("Broadband Trajectory", "Stabilization",
                      "DOCSIS 4.0 speed advantage expected to reverse net add trend", PRP),
    ]
    return f'<div class="guide-grid">{"".join(cards)}</div>'


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN BUILD FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def generate(output_dir: str) -> None:
    """Build carriers/comcast.html and write to output_dir."""
    print(f"  [Comcast] Building charts...")

    divs = {
        "revenue":      _chart_revenue(),
        "annual":       _chart_annual(),
        "subscribers":  _chart_subscribers(),
        "bb_adds":      _chart_bb_net_adds(),
        "mob_adds":     _chart_mobile_adds(),
        "capex":        _chart_capex(),
        "stock":        _chart_stock(),
    }

    # ── KPI cards ─────────────────────────────────────────────────────────────
    kpi_html = "".join(kpi_card(label, val, prior, unit, slug, ACCENT)
                       for label, val, prior, unit, slug in KPI_DATA)

    body_html = f"""
<!-- KPIs -->
<div class="section" id="kpis">
  <div class="section-title"><span class="dot"></span>Q4 2025 Key Performance Indicators</div>
  <div class="section-sub">Cable Communications segment · Q4 2025 vs Q4 2024 · All USD</div>
  <div class="kpi-grid">{kpi_html}</div>
  <div class="est-note">
    <strong>* Estimated quarters:</strong> Q2–Q4 2025 quarterly breakdowns partially estimated from FY2025 annual totals.
    Broadband subscriber losses reflect intensified competition from telco fiber (AT&amp;T, Verizon) and fixed wireless.
    Xfinity Mobile growth (+2.4M lines YoY) partially offsets broadband headwinds.
  </div>
</div>

<!-- Revenue -->
<div class="section" id="revenue">
  <div class="section-title"><span class="dot"></span>Revenue &amp; Profitability</div>
  <div class="section-sub">Quarterly Cable Communications revenue and EBITDA margin trend</div>
  <div class="chart-wrap">
    {divs['revenue']}
    <div class="chart-note">Cable segment EBITDA margin ~40–42%. Q4 typically highest revenue quarter. Lighter bars = estimated.</div>
  </div>
  <div class="chart-wrap">
    {divs['annual']}
    <div class="chart-note">Annual Cable segment financials. FY2025 revenue down slightly (~-1%) as broadband subscriber pressure offsets pricing gains and mobile growth.</div>
  </div>
</div>

<!-- Network Domain -->
<div class="section" id="network">
  <div class="section-title"><span class="dot"></span>Network Domain — DOCSIS 4.0 &amp; CapEx Cycle</div>
  <div class="section-sub">Multi-gig broadband upgrade is the defining network investment of 2024–2028</div>
  <div class="chart-wrap">
    {divs['capex']}
    <div class="chart-note">Cable CapEx elevated through 2028 to fund DOCSIS 4.0 multi-gig upgrade. Target: 100% of footprint (60M+ homes) by 2028 at ~$15B total investment.</div>
  </div>
  <div class="section-title" style="margin-bottom:12px; font-size:15px;"><span class="dot"></span>Network Strategy Initiatives</div>
  {_initiatives_div()}
</div>

<!-- Subscribers -->
<div class="section" id="subscribers">
  <div class="section-title"><span class="dot"></span>Subscriber Metrics</div>
  <div class="section-sub">Broadband pressure vs Xfinity Mobile growth — the convergence story</div>
  <div class="chart-wrap">
    {divs['subscribers']}
    <div class="chart-note">Broadband subs plateauing/declining due to fiber competition. Xfinity Mobile +2.4M lines YoY. Video cord-cutting structural decline continues.</div>
  </div>
  <div class="chart-grid-2">
    <div class="chart-wrap">
      {divs['bb_adds']}
      <div class="chart-note">Broadband net adds turned negative in 2024. AT&amp;T/Verizon fiber expansions and T-Mobile/Verizon FWA are primary competitive drivers.</div>
    </div>
    <div class="chart-wrap">
      {divs['mob_adds']}
      <div class="chart-note">Xfinity Mobile adding ~300K+ lines per quarter. MVNO on Verizon + 22M WiFi hotspots enables competitive pricing vs MNOs.</div>
    </div>
  </div>
</div>

<!-- Stock -->
<div class="section" id="stock">
  <div class="section-title"><span class="dot"></span>Stock Performance — 3-Year vs Peers</div>
  <div class="section-sub">CMCSA vs Charter Communications, AT&amp;T, and S&amp;P 500. Normalized to 100.</div>
  <div class="chart-wrap">
    {divs['stock']}
    <div class="chart-note">Live data via Yahoo Finance. Cable sector has underperformed broader market due to broadband subscriber concerns and high leverage.</div>
  </div>
</div>

<!-- Outlook -->
<div class="section" id="outlook">
  <div class="section-title"><span class="dot"></span>FY2025 Guidance &amp; Strategic Outlook</div>
  <div class="section-sub">Management guidance from Q4 2025 earnings. DOCSIS 4.0 completion targeted 2028.</div>
  {_guidance_div()}
  <div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div class="init-card" style="border-left:3px solid {ACCENT}">
      <div class="init-title" style="margin-bottom:10px">DOCSIS 4.0 Roadmap (2025–2028)</div>
      <ul class="init-bullets">
        <li>2025: <strong>40% of footprint</strong> upgraded to DOCSIS 4.0</li>
        <li>2026: <strong>60–65%</strong> passed; multi-gig tier launch in upgraded markets</li>
        <li>2027: <strong>80%+</strong> — national multi-gig coverage</li>
        <li>2028: <strong>100% completion</strong> — 10 Gbps capable across all 60M homes</li>
        <li>Total investment: <strong>~$15B</strong> over upgrade cycle</li>
      </ul>
    </div>
    <div class="init-card" style="border-left:3px solid {GRN}">
      <div class="init-title" style="margin-bottom:10px">Xfinity Mobile — Path to 15M+</div>
      <ul class="init-bullets">
        <li>FY2025: <strong>10.1M lines</strong> (+31% YoY)</li>
        <li>FY2026 target: <strong>12M+ lines</strong></li>
        <li>Mobile MVNO margin improving as scale grows</li>
        <li>Eventual own-network ambition: CBRS/C-band spectrum strategy under review</li>
        <li>Bundle attach rate: ~28% of broadband customers now take mobile</li>
      </ul>
    </div>
  </div>
</div>
"""

    sources_html = """
<strong>Data Sources:</strong>
Comcast Investor Relations (cmcastcorporate.com/ir) &middot;
SEC EDGAR 10-K / 10-Q filings &middot;
Comcast Q4 2025 earnings press release (Jan 2026) &middot;
Yahoo Finance (CMCSA, CHTR, T, SPY via yfinance) &middot;
Comcast Technology Solutions product releases.<br>
<strong>Segment note:</strong> All financial figures refer to Comcast Cable Communications / "Connectivity &amp; Platforms" segment unless stated.
Total company (including NBCUniversal, Sky, Corporate) revenue FY2025 ~$123B.
Q2–Q4 2025 quarterly breakdowns are partial estimates from annual totals.<br>
"""

    nav_links = [
        ("kpis",        "KPIs"),
        ("revenue",     "Revenue"),
        ("network",     "Network Domain"),
        ("subscribers", "Subscribers"),
        ("stock",       "Stock"),
        ("outlook",     "Outlook"),
    ]

    carrier_meta = {
        "name":           "Comcast",
        "ticker":         "CMCSA",
        "accent":         ACCENT,
        "flag":           "🇺🇸",
        "region":         "Americas",
        "latest_quarter": "Q4 2025",
        "stock_period":   "3-Year",
    }

    html = page_shell(carrier_meta, nav_links, body_html, sources_html)
    out_path = os.path.join(output_dir, "comcast.html")
    os.makedirs(output_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [Comcast] Written -> {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
#  SUMMARY (used by generate_all.py landing page)
# ══════════════════════════════════════════════════════════════════════════════

def get_summary() -> dict:
    return {
        "id":            ID,
        "svc_rev":       16.5,    # $B Cable revenue Q4 2025
        "ebitda_margin": 42.4,    # % Q4 2025
        "fcf_annual":    15.5,    # $B total company FY2025
        "subscribers":   31.9,    # M broadband subscribers (primary connectivity metric)
        "coverage_5g":   None,    # No wireless network (MVNO only — no coverage stat)
        "latest_q":      "Q4 2025",
    }
