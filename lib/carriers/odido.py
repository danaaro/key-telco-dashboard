"""
lib/carriers/odido.py — Odido (Netherlands) carrier module
Sources: Telecompaper, Odido press releases, company reports
Latest:  FY2025 (annual reporting; detailed quarterly not publicly available)
Note:    Private — PE-backed (Warburg Pincus + Apax Partners).
         Former T-Mobile Netherlands, rebranded to Odido September 2023.
         IPO planned 2026 on Euronext Amsterdam.
         All values in EUR millions/billions unless stated.
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
ID      = "odido"
ACCENT  = "#FF6B00"   # Odido Orange
EUR_USD = 1.09        # Approximate EUR/USD — used for landing page summary

# ══════════════════════════════════════════════════════════════════════════════
#  DATA  (EUR billions unless stated)
#  Source: Telecompaper (telecompaper.com), Odido press releases, company reports
#  Note: Odido is private; limited public disclosure. CapEx/FCF not published.
# ══════════════════════════════════════════════════════════════════════════════

ANN = ['FY2023', 'FY2024', 'FY2025']
A = dict(
    rev    = [2.29, 2.35, 2.38],     # Total Revenue €B
    ebitda = [0.85, 0.88, 0.91],     # Adj. EBITDA €B
    mob    = [3.05, 3.10, 3.15],     # M mobile subscribers (est.)
    bb     = [0.88, 0.95, 1.01],     # M fixed broadband subscribers (FWA + fiber)
    cov5g  = [85,   85,   86],       # % Netherlands population 5G coverage (est.)
)
A['margin'] = [round(e/r*100, 1) for e, r in zip(A['ebitda'], A['rev'])]

# Revenue segments €B
SEG_LABELS  = ['Mobile', 'Fixed Broadband', 'Business / Other']
SEG_FY2024  = [1.37, 0.50, 0.47]
SEG_FY2025  = [1.38, 0.56, 0.44]
SEG_COLORS  = [ACCENT, TEA, BLU]

KPI_DATA = [
    # FY2025 vs FY2024
    ("Total Revenue",     2.38, 2.35, "€B", "svc_rev"),
    ("Adj. EBITDA",       0.91, 0.88, "€B", "ebitda"),
    ("EBITDA Margin",    38.2, 37.5,  "%",  "margin"),
    ("Mobile Subscribers",3.15, 3.10, "M",  "adds"),
    ("Broadband Subs",   1.01, 0.95,  "M",  "broadband"),
    ("5G Coverage (NL)", 86,   85,    "%",  "coverage"),
]


def get_summary():
    return {
        "id":             ID,
        "svc_rev":        round(2.38 * EUR_USD / 4, 1),  # FY2025 quarterly equiv in USD
        "ebitda_margin":  38.2,
        "fcf_annual":     0.0,   # Not publicly disclosed
        "subscribers":    3.15,  # M mobile
        "coverage_5g":    86,    # % Netherlands pop
        "latest_q":       "FY2025",
        "capex_pct":      0.0,   # Not disclosed
    }


def generate(output_dir):
    print(f"  [Odido] Building charts...")
    divs = {
        "annual":       _chart_annual(),
        "segments":     _chart_segments(),
        "subscribers":  _chart_subscribers(),
        "coverage":     _chart_coverage(),
    }
    html = _build_html(divs)
    out_path = os.path.join(output_dir, "odido.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [Odido] Written -> {out_path}")
    return out_path


# ── Charts ────────────────────────────────────────────────────────────────────

def _chart_annual():
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ANN, y=A['rev'], name="Total Revenue",
                         marker_color=ACCENT, cliponaxis=False,
                         text=[f"€{v:.2f}B" for v in A['rev']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>Revenue: €%{y:.2f}B<extra></extra>"))
    fig.add_trace(go.Bar(x=ANN, y=A['ebitda'], name="Adj. EBITDA",
                         marker_color=TEA, cliponaxis=False,
                         text=[f"€{v:.2f}B" for v in A['ebitda']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>EBITDA: €%{y:.2f}B<extra></extra>"))
    fig.update_layout(**base_layout(ACCENT, "Annual Revenue & EBITDA (EUR)"), barmode="group")
    apply_axes(fig)
    fig.update_yaxes(title_text="EUR Billions", tickprefix="€", range=[0, 3.2])
    for i, (yr, m) in enumerate(zip(ANN, A['margin'])):
        fig.add_annotation(x=yr, y=A['ebitda'][i] + 0.08,
                           text=f"{m}%", showarrow=False,
                           font=dict(size=9, color=YLW), xref="x", yref="y")
    fig.add_annotation(x="FY2023", y=2.5,
                       text="Rebranded to<br>Odido Sep 2023",
                       showarrow=True, arrowhead=2, arrowcolor=ORG,
                       font=dict(size=9, color=ORG), bgcolor=CARD_BG,
                       bordercolor=ORG, borderwidth=1)
    return fig_to_div(fig, "odido_chart_annual")


def _chart_segments():
    fig = go.Figure()
    x = ['FY2024', 'FY2025']
    for seg, v24, v25, clr in zip(SEG_LABELS, SEG_FY2024, SEG_FY2025, SEG_COLORS):
        fig.add_trace(go.Bar(
            name=seg, x=x, y=[v24, v25],
            marker_color=clr, cliponaxis=False,
            text=[f"€{v:.2f}B" for v in [v24, v25]],
            textposition="outside", textfont=dict(size=10, color=TXT),
            hovertemplate=f"<b>{seg}</b> %{{x}}<br>€%{{y:.2f}}B<extra></extra>",
        ))
    fig.update_layout(**base_layout(ACCENT, "Revenue by Segment — FY2024 vs FY2025"), barmode="group")
    apply_axes(fig)
    fig.update_yaxes(title_text="EUR Billions", tickprefix="€", range=[0, 1.8])
    fig.add_annotation(x="FY2025", y=0.62,
                       text="Fixed broadband<br>+11% YoY<br>(FWA growth)",
                       showarrow=True, arrowhead=2, arrowcolor=TEA,
                       font=dict(size=9, color=TEA), bgcolor=CARD_BG,
                       bordercolor=TEA, borderwidth=1)
    return fig_to_div(fig, "odido_chart_segments")


def _chart_subscribers():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=ANN, y=A['bb'], name="Broadband Subscribers (M)",
                         marker_color=ACCENT, cliponaxis=False,
                         text=[f"{v:.2f}M" for v in A['bb']],
                         textposition="outside", textfont=dict(size=10, color=TXT),
                         hovertemplate="<b>%{x}</b><br>Broadband: %{y:.2f}M<extra></extra>"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=ANN, y=A['mob'], name="Mobile Subscribers (M)",
                             mode="lines+markers+text",
                             line=dict(color=BLU, width=2.5),
                             marker=dict(size=9, color=BLU),
                             text=[f"{v:.2f}M" for v in A['mob']],
                             textposition="top center", textfont=dict(size=9, color=BLU),
                             hovertemplate="<b>%{x}</b><br>Mobile: %{y:.2f}M<extra></extra>"),
                  secondary_y=True)
    fig.add_hline(y=1.0, line_dash="dot", line_color=GRN, line_width=1.5,
                  annotation_text="1M broadband milestone (Q1 2025)",
                  annotation_position="right",
                  annotation_font=dict(color=GRN, size=9), secondary_y=False)
    fig.update_layout(**base_layout(ACCENT, "Subscriber Growth — Broadband & Mobile"))
    apply_axes(fig)
    fig.update_yaxes(title_text="Broadband Subscribers (M)", secondary_y=False,
                     ticksuffix="M", range=[0, 1.4])
    fig.update_yaxes(title_text="Mobile Subscribers (M)", secondary_y=True,
                     ticksuffix="M", range=[2.8, 3.5], showgrid=False)
    return fig_to_div(fig, "odido_chart_subs")


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
    fig.add_hline(y=86, line_dash="dot", line_color=GRN, line_width=1.5,
                  annotation_text="86% NL pop — fastest speeds in Netherlands (Opensignal)",
                  annotation_position="right",
                  annotation_font=dict(color=GRN, size=9))
    fig.update_layout(**base_layout(ACCENT, "5G Network Coverage — % Netherlands Population"),
                      height=280)
    apply_axes(fig)
    fig.update_yaxes(title_text="% Netherlands Population", ticksuffix="%", range=[0, 110])
    return fig_to_div(fig, "odido_chart_cov")


def _build_html(divs):
    kpi_html = "".join(kpi_card(lbl, val, prior, unit, slug, ACCENT)
                       for lbl, val, prior, unit, slug in KPI_DATA)

    initiatives = [
        ("🔶", "Odido Brand & Relaunch", "T-Mobile Netherlands → Odido (Sep 2023)",
         ["Rebranded Sept 2023 from T-Mobile Netherlands",
          "Fresh brand identity: 'Odido' = everyone together",
          "Customer-focused positioning in competitive Dutch market",
          "Growing brand awareness driving NPS improvement"], ACCENT),
        ("🏠", "Fixed Wireless Access (FWA)", "'Klik&Klaar' home internet",
         ["FWA launched 2024 — 'Klik&Klaar' (plug-and-play) product",
          "Key driver of crossing 1M broadband milestone (Q1 2025)",
          "Broadband revenue up +11% YoY in FY2025",
          "Now ~24% of total revenue and growing"], TEA),
        ("📡", "5G Network Leadership", "Fastest 5G speeds in the Netherlands",
         ["86% Netherlands population covered with 5G",
          "Averaging 331.9 Mbps — highest in Netherlands (Opensignal)",
          "3.5 GHz spectrum deployment complete (80% network modernized)",
          "SA 5G core roadmap underway for network slicing"], BLU),
        ("📊", "IPO Preparation (2026)", "PE exit via Euronext Amsterdam",
         ["Warburg Pincus + Apax Partners (PE owners) targeting IPO",
          "Expected ~€1B valuation at listing",
          "Strengthening financial disclosure ahead of IPO",
          "Revenue and EBITDA growth trajectory supports valuation"], GRN),
        ("🤖", "Network Automation & AI", "Intelligent network operations",
         ["AI-driven network self-optimization deployed on 3.5 GHz layer",
          "Automated fault detection and remediation",
          "Smart CapEx allocation based on customer demand signals",
          "Data analytics platform for customer experience improvement"], ORG),
        ("💼", "Business/Enterprise Strategy", "Corporate segment revival",
         ["Business segment under pressure (-6% FY2025 est.)",
          "Focus: SME and mid-market with bundled 5G + connectivity",
          "Government and public sector contracts growing",
          "SD-WAN and managed network services for enterprise"], PRP),
    ]
    init_html = "".join(initiative_card(*args) for args in initiatives)

    guide_data = [
        ("Total Revenue (FY2025)", "€2.38B", "+1.3% YoY", ACCENT),
        ("EBITDA Margin",          "38.2%",  "+0.7pp YoY", TEA),
        ("Fixed Broadband",        "1.01M",  "Crossed 1M milestone", GRN),
        ("5G Coverage",            "86%",    "Fastest in Netherlands", BLU),
    ]
    guide_html = "".join(guidance_card(*args) for args in guide_data)

    body_html = f"""
<div class="section" id="kpis">
  <div class="section-title"><span class="dot"></span>FY2025 Key Performance Indicators</div>
  <div class="section-sub">FY2025 vs FY2024 full-year comparison. Source: Odido company reports / Telecompaper.</div>
  <div class="kpi-grid">{kpi_html}</div>
  <div class="est-note">
    <strong>Private Company:</strong> Odido is PE-backed (Warburg Pincus + Apax Partners); not publicly listed as of April 2026.
    IPO on Euronext Amsterdam planned for 2026. CapEx and FCF data not publicly disclosed.
    Approx. USD equiv. at €1 = ${EUR_USD:.2f} noted in footer. Former name: T-Mobile Netherlands (rebranded Sep 2023).
  </div>
</div>

<div class="section" id="financials">
  <div class="section-title"><span class="dot"></span>Annual Financial Performance</div>
  <div class="section-sub">FY2023–FY2025 actuals. EBITDA margin improving toward 38%+. CapEx/FCF not publicly disclosed.</div>
  <div class="chart-grid-2">
    <div class="chart-wrap">
      {divs['annual']}
      <div class="chart-note">Steady revenue growth (+4% over 2yr). EBITDA margin expanding as fixed broadband scales. Source: Telecompaper / Odido press releases.</div>
    </div>
    <div class="chart-wrap">
      {divs['segments']}
      <div class="chart-note">Fixed broadband was the standout growth segment in FY2025 (+11% YoY) driven by FWA "Klik&Klaar" launch.</div>
    </div>
  </div>
</div>

<div class="section" id="network">
  <div class="section-title"><span class="dot"></span>Network Domain — 5G, FWA & Strategic Initiatives</div>
  <div class="section-sub">Odido operates the Netherlands' fastest 5G network (Opensignal). Fixed broadband now a key growth pillar through FWA.</div>
  <div class="chart-grid-2" style="margin-bottom:16px">
    <div class="chart-wrap">
      {divs['coverage']}
      <div class="chart-note">86% 5G population coverage. Odido ranked #1 in Netherlands for 5G download speeds (331.9 Mbps avg, Opensignal 2025).</div>
    </div>
    <div class="chart-wrap">
      {divs['subscribers']}
      <div class="chart-note">Broadband crossed 1M milestone in Q1 2025 — driven by FWA "Klik&Klaar" launch. Mobile base stable at ~3.1M.</div>
    </div>
  </div>
  <div class="init-grid">{init_html}</div>
</div>

<div class="section" id="outlook">
  <div class="section-title"><span class="dot"></span>FY2025 Results & Strategic Outlook</div>
  <div class="section-sub">Revenue and EBITDA growth on track for IPO. Fixed broadband scaling rapidly; mobile stable; 5G leadership sustained.</div>
  <div class="guide-grid">{guide_html}</div>
  <div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div class="init-card" style="border-left:3px solid {ACCENT}">
      <div class="init-title" style="margin-bottom:10px">Strategic Priorities 2026</div>
      <ul class="init-bullets">
        <li>Scale fixed broadband to 1.5M+ (FWA + fiber)</li>
        <li>Maintain 5G speed leadership via SA core rollout</li>
        <li>Drive EBITDA margin toward 40% via operational efficiency</li>
        <li>Complete IPO preparation and Euronext Amsterdam listing</li>
      </ul>
    </div>
    <div class="init-card" style="border-left:3px solid {TEA}">
      <div class="init-title" style="margin-bottom:10px">Market Position (Netherlands)</div>
      <ul class="init-bullets">
        <li>#3 mobile operator in Netherlands (~19% market share)</li>
        <li>Fastest 5G network by speed (Opensignal 2025)</li>
        <li>Growing fixed broadband challenger to KPN and Ziggo</li>
        <li>Strong SME/enterprise presence via former T-Mobile B2B</li>
      </ul>
    </div>
  </div>
</div>
"""

    sources_html = f"""
<strong>Data Sources:</strong>
Odido company press releases (odido.nl) &middot;
Telecompaper industry reports &middot;
Opensignal Netherlands Mobile Network Experience (2025) &middot;
Company financial disclosures.<br>
<strong>FX Note:</strong> All financials in EUR. Approx. USD: EUR/USD ~{EUR_USD:.2f} (April 2026).
FY2025 revenue €2.38B ≈ ${2.38*EUR_USD:.2f}B USD · EBITDA €0.91B ≈ ${0.91*EUR_USD:.2f}B USD.<br>
<strong>Note:</strong> Odido is private (PE-backed); detailed CapEx, FCF, and sub-quarterly financials not publicly disclosed.
Data based on public press releases and industry reports. IPO expected Euronext Amsterdam 2026.<br>
"""

    nav_links = [
        ("kpis",       "KPIs"),
        ("financials", "Financials"),
        ("network",    "Network"),
        ("outlook",    "Outlook"),
    ]
    carrier_meta = {
        "name":           "Odido",
        "ticker":         "Private",
        "accent":         ACCENT,
        "flag":           "🇳🇱",
        "region":         "Europe",
        "latest_quarter": "FY2025",
        "stock_period":   "N/A",
    }
    return page_shell(carrier_meta, nav_links, body_html, sources_html)
