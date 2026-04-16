"""
lib/registry.py — Carrier registry
To add a new carrier: add one entry to CARRIERS dict + create lib/carriers/<id>.py
"""

CARRIERS = {
    "tmobile": {
        "id":          "tmobile",
        "name":        "T-Mobile US",
        "short":       "TMUS",
        "ticker":      "TMUS",
        "exchange":    "NASDAQ",
        "currency":    "USD",
        "fx_pair":     None,
        "region":      "Americas",
        "flag":        "🇺🇸",
        "accent":      "#E20074",
        "status":      "active",
        "module":      "lib.carriers.tmobile",
        "out_file":    "carriers/tmobile.html",
        "latest_q":    "Q4 2025",
        "phase":       1,
    },
    "verizon": {
        "id":          "verizon",
        "name":        "Verizon",
        "short":       "VZ",
        "ticker":      "VZ",
        "exchange":    "NYSE",
        "currency":    "USD",
        "fx_pair":     None,
        "region":      "Americas",
        "flag":        "🇺🇸",
        "accent":      "#CD040B",
        "status":      "active",
        "module":      "lib.carriers.verizon",
        "out_file":    "carriers/verizon.html",
        "latest_q":    "Q4 2025",
        "phase":       1,
    },
    "att": {
        "id":          "att",
        "name":        "AT&T",
        "short":       "AT&T",
        "ticker":      "T",
        "exchange":    "NYSE",
        "currency":    "USD",
        "fx_pair":     None,
        "region":      "Americas",
        "flag":        "🇺🇸",
        "accent":      "#00A8E0",
        "status":      "active",
        "module":      "lib.carriers.att",
        "out_file":    "carriers/att.html",
        "latest_q":    "Q4 2025",
        "phase":       1,
    },
    "vmo2": {
        "id":          "vmo2",
        "name":        "Virgin Media O2",
        "short":       "VMO2",
        "ticker":      None,          # Private JV — Liberty Global + Telefonica
        "exchange":    "Private JV",
        "currency":    "GBP",
        "fx_pair":     "GBPUSD=X",
        "region":      "Europe",
        "flag":        "🇬🇧",
        "accent":      "#D0021B",
        "status":      "active",
        "module":      "lib.carriers.vmo2",
        "out_file":    "carriers/vmo2.html",
        "latest_q":    "Q2 2025",
        "phase":       2,
    },
    "odido": {
        "id":          "odido",
        "name":        "Odido",
        "short":       "Odido",
        "ticker":      None,          # Private — PE-backed (Warburg Pincus + Apax); IPO 2026
        "exchange":    "Private (IPO 2026)",
        "currency":    "EUR",
        "fx_pair":     "EURUSD=X",
        "region":      "Europe",
        "flag":        "🇳🇱",
        "accent":      "#FF6B00",
        "status":      "active",
        "module":      "lib.carriers.odido",
        "out_file":    "carriers/odido.html",
        "latest_q":    "FY2025",
        "phase":       2,
    },
    "vf_germany": {
        "id":          "vf_germany",
        "name":        "Vodafone Germany",
        "short":       "VF-DE",
        "ticker":      "VOD",         # Parent: Vodafone Group (LSE/NASDAQ)
        "exchange":    "LSE / NASDAQ",
        "currency":    "EUR",
        "fx_pair":     "EURUSD=X",
        "region":      "Europe",
        "flag":        "🇩🇪",
        "accent":      "#E60000",
        "status":      "active",
        "module":      "lib.carriers.vf_germany",
        "out_file":    "carriers/vf_germany.html",
        "latest_q":    "H1 FY2026",   # Vodafone uses Apr-Mar fiscal year
        "phase":       2,
    },
    "globe": {
        "id":          "globe",
        "name":        "Globe Telecom",
        "short":       "GLO",
        "ticker":      "GLO.PS",      # PSE listing; yfinance suffix .PS
        "exchange":    "PSE",
        "currency":    "PHP",
        "fx_pair":     "PHPUSD=X",
        "region":      "APAC",
        "flag":        "🇵🇭",
        "accent":      "#0066CC",
        "status":      "active",
        "module":      "lib.carriers.globe",
        "out_file":    "carriers/globe.html",
        "latest_q":    "Q3 2025",
        "phase":       3,
    },
}


def active_carriers():
    return {k: v for k, v in CARRIERS.items() if v["status"] == "active"}


def planned_carriers():
    return {k: v for k, v in CARRIERS.items() if v["status"] == "planned"}


def by_region(region):
    return {k: v for k, v in CARRIERS.items() if v["region"] == region}


def by_phase(phase):
    return {k: v for k, v in CARRIERS.items() if v["phase"] == phase}
