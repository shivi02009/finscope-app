import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests, math, json
from datetime import datetime

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinScope — Stock Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"], .stApp { font-family: 'Space Grotesk', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #080b12 !important; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1440px !important; }

/* ── Grid background ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(56,189,248,0.07) 0%, transparent 70%),
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 100% 100%, 48px 48px, 48px 48px;
}

/* ── All text visible ── */
p, li, div, span, label, .stMarkdown, .stText { color: #e2e8f0 !important; }
h1, h2, h3, h4, h5 { color: #f8fafc !important; font-family: 'Space Grotesk', sans-serif !important; font-weight: 700 !important; }

/* ── Input ── */
.stTextInput > div > div > input {
    background: #0f1520 !important;
    border: 1.5px solid rgba(148,163,184,0.2) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.15) !important;
    background: #0f1824 !important;
}
.stTextInput > div > div > input::placeholder { color: #475569 !important; }
.stTextInput label { display: none !important; }

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #38bdf8, #0ea5e9) !important;
    color: #0c1220 !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 14px 28px !important;
    width: 100% !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(56,189,248,0.25) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #7dd3fc, #38bdf8) !important;
    box-shadow: 0 4px 28px rgba(56,189,248,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(15,21,32,0.8) !important;
    border: 1px solid rgba(148,163,184,0.1) !important;
    border-radius: 14px !important;
    padding: 18px !important;
    backdrop-filter: blur(12px) !important;
}
[data-testid="metric-container"] label {
    color: #64748b !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-family: 'Space Grotesk', sans-serif !important; font-size: 20px !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15,21,32,0.6) !important;
    border: 1px solid rgba(148,163,184,0.1) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    padding: 8px 18px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(56,189,248,0.12) !important;
    color: #38bdf8 !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 22px !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #38bdf8 !important; }

/* ── Selectbox / dropdown ── */
.stSelectbox > div > div {
    background: #0f1520 !important;
    border-color: rgba(148,163,184,0.2) !important;
    color: #f1f5f9 !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #080b12; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }

/* ── Alerts ── */
.stAlert { border-radius: 12px !important; border: 1px solid rgba(248,113,113,0.3) !important; background: rgba(248,113,113,0.07) !important; }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ─────────────────────────────────────────────────────────────
PL = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='JetBrains Mono', color='#64748b', size=11),
    margin=dict(l=8, r=8, t=28, b=8),
    xaxis=dict(gridcolor='rgba(255,255,255,0.04)', linecolor='rgba(255,255,255,0.06)',
               tickfont=dict(size=10, color='#475569'), zeroline=False),
    yaxis=dict(gridcolor='rgba(255,255,255,0.04)', linecolor='rgba(255,255,255,0.06)',
               tickfont=dict(size=10, color='#475569'), zeroline=False),
)

# ── HELPERS ──────────────────────────────────────────────────────────────────
def fmt_large(n):
    if n is None or (isinstance(n, float) and math.isnan(n)): return "—"
    n = float(n)
    if abs(n) >= 1e12: return f"{n/1e12:.2f}T"
    if abs(n) >= 1e9:  return f"{n/1e9:.2f}B"
    if abs(n) >= 1e6:  return f"{n/1e6:.2f}M"
    return f"{n:.2f}"

def fmt_pct(n):
    if n is None or (isinstance(n, float) and math.isnan(n)): return "—"
    return f"{float(n)*100:.1f}%"

def safe(n, dec=2):
    if n is None or (isinstance(n, float) and math.isnan(n)): return "—"
    return f"{float(n):.{dec}f}"

def gv(info, key, default=None):
    v = info.get(key, default)
    if v is None: return default
    if isinstance(v, float) and math.isnan(v): return default
    return v

def kpi_card(label, value, sub="", value_color="#f1f5f9"):
    return f"""
    <div style="background:rgba(15,21,32,0.85);border:1px solid rgba(148,163,184,0.1);
                border-radius:14px;padding:18px 20px;backdrop-filter:blur(12px);
                transition:border 0.2s;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:1.5px;
                    text-transform:uppercase;color:#475569;margin-bottom:10px;">{label}</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;
                    color:{value_color};line-height:1;margin-bottom:4px;">{value}</div>
        <div style="font-size:11px;color:#334155;">{sub}</div>
    </div>"""

def ratio_card_open(title, accent="#38bdf8"):
    return f"""<div style="background:rgba(15,21,32,0.85);border:1px solid rgba(148,163,184,0.1);
        border-radius:14px;padding:20px;backdrop-filter:blur(12px);">
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:2px;
            color:{accent};text-transform:uppercase;margin-bottom:14px;padding-bottom:12px;
            border-bottom:1px solid rgba(148,163,184,0.08);">{title}</div>"""

def ratio_row(label, val, color="#94a3b8"):
    return f"""<div style="display:flex;justify-content:space-between;align-items:center;
        padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
        <span style="color:#64748b;font-size:13px;font-family:'Space Grotesk',sans-serif;">{label}</span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:500;color:{color};">{val}</span>
    </div>"""

def ratio_card_close():
    return "</div>"

# ── SESSION STATE ────────────────────────────────────────────────────────────
if "screen" not in st.session_state:
    st.session_state.screen = "search"
if "ticker" not in st.session_state:
    st.session_state.ticker = ""

def go_to_dashboard(sym):
    st.session_state.ticker = sym.strip().upper()
    st.session_state.screen = "dashboard"

def go_to_search():
    st.session_state.screen = "search"
    st.session_state.ticker = ""

# ── COMPANY SEARCH ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def search_companies(query):
    if len(query) < 2:
        return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={requests.utils.quote(query)}&quotesCount=8&newsCount=0&listsCount=0"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=6)
        data = r.json()
        results = []
        for q in data.get("quotes", []):
            if q.get("quoteType") in ("EQUITY", "ETF", "MUTUALFUND", "INDEX"):
                symbol   = q.get("symbol", "")
                name     = q.get("longname") or q.get("shortname") or symbol
                exchange = q.get("exchange", "")
                type_    = q.get("quoteType", "")
                results.append({"symbol": symbol, "name": name, "exchange": exchange, "type": type_})
        return results
    except:
        return []

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — SEARCH
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "search":

    # Logo
    st.markdown("""
    <style>@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}</style>
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding-bottom:24px;border-bottom:1px solid rgba(148,163,184,0.08);margin-bottom:48px;">
        <div style="display:flex;align-items:center;gap:14px;">
            <div style="width:38px;height:38px;border-radius:10px;
                        background:linear-gradient(135deg,#38bdf8,#0ea5e9);
                        display:flex;align-items:center;justify-content:center;
                        font-size:18px;box-shadow:0 4px 20px rgba(56,189,248,0.35);">📈</div>
            <div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;
                            color:#f8fafc;letter-spacing:-0.5px;line-height:1;">
                    Fin<span style='color:#38bdf8'>Scope</span></div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                            color:#334155;letter-spacing:2px;margin-top:1px;">STOCK INTELLIGENCE</div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:7px;height:7px;border-radius:50%;background:#4ade80;
                        box-shadow:0 0 10px #4ade80;animation:pulse 2s infinite;"></div>
            <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#334155;letter-spacing:1px;">LIVE DATA</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero text
    st.markdown("""
    <div style="text-align:center;margin-bottom:36px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:3px;
                    color:#38bdf8;text-transform:uppercase;margin-bottom:14px;">Real-Time Financial Analysis</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:52px;font-weight:700;
                    color:#f8fafc;letter-spacing:-2px;line-height:1.05;margin-bottom:12px;">
            Analyse Any Stock<br><span style='color:#38bdf8'>Instantly</span>
        </div>
        <div style="font-size:16px;color:#475569;max-width:440px;margin:0 auto;line-height:1.6;">
            DCF valuation · 30+ ratios · Buy/Sell signals<br>for any stock globally — free, live, automated
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search bar
    _, sc, _ = st.columns([1, 3, 1])
    with sc:
        query = st.text_input("", placeholder="🔍  Apple, Tesla, RELIANCE.NS, NVDA, Bitcoin…", key="search_query")
        search_clicked = st.button("Search →", key="search_btn", use_container_width=True)

        # Live results dropdown
        if query and len(query) >= 2:
            results = search_companies(query)
            if results:
                st.markdown("""
                <div style="background:rgba(10,14,22,0.98);border:1px solid rgba(56,189,248,0.15);
                            border-radius:12px;padding:6px;margin-top:4px;backdrop-filter:blur(20px);">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:2px;
                                color:#334155;text-transform:uppercase;padding:6px 10px 2px;">Results</div>
                </div>""", unsafe_allow_html=True)

                for r in results:
                    label = f"{r['name']}  ·  **{r['symbol']}**  ·  {r['exchange']}"
                    if st.button(f"{r['name']}   {r['symbol']}   {r['exchange']}", key=f"res_{r['symbol']}", use_container_width=True):
                        go_to_dashboard(r['symbol'])
                        st.rerun()

                st.markdown("""
                <style>
                div[data-testid="stVerticalBlock"] > div:has(button[kind="secondary"]) button {
                    background: rgba(15,21,32,0.7) !important;
                    border: 1px solid rgba(148,163,184,0.08) !important;
                    border-radius: 10px !important;
                    color: #cbd5e1 !important;
                    font-family: 'Space Grotesk', sans-serif !important;
                    font-size: 13px !important;
                    font-weight: 400 !important;
                    text-align: left !important;
                    padding: 10px 16px !important;
                    box-shadow: none !important;
                    margin-bottom: 2px !important;
                }
                div[data-testid="stVerticalBlock"] > div:has(button[kind="secondary"]) button:hover {
                    background: rgba(56,189,248,0.08) !important;
                    border-color: rgba(56,189,248,0.2) !important;
                    color: #38bdf8 !important;
                }
                </style>""", unsafe_allow_html=True)

            elif len(query) >= 2:
                st.markdown('<div style="color:#475569;font-family:JetBrains Mono,monospace;font-size:12px;padding:8px 0;text-align:center;">No results — try the ticker directly e.g. AAPL</div>', unsafe_allow_html=True)

        # Direct ticker fallback
        if search_clicked and query:
            go_to_dashboard(query)
            st.rerun()

    # Quick picks
    st.markdown("<div style='margin:36px 0 12px;text-align:center;font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:2px;color:#334155;text-transform:uppercase;'>Quick picks</div>", unsafe_allow_html=True)
    qc = st.columns(10)
    quick_tickers = [("AAPL","Apple"),("MSFT","Microsoft"),("NVDA","Nvidia"),("TSLA","Tesla"),
                     ("GOOGL","Google"),("AMZN","Amazon"),("RELIANCE.NS","Reliance"),
                     ("TCS.NS","TCS"),("INFY.NS","Infosys"),("BTC-USD","Bitcoin")]
    for col, (sym, lbl) in zip(qc, quick_tickers):
        with col:
            if st.button(lbl, key=f"q_{sym}"):
                go_to_dashboard(sym)
                st.rerun()

    # Feature cards
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:48px;">
        <div style="background:rgba(15,21,32,0.5);border:1px solid rgba(148,163,184,0.07);border-radius:14px;padding:24px;text-align:center;">
            <div style="font-size:26px;margin-bottom:10px;">📊</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:600;color:#e2e8f0;margin-bottom:6px;">30+ Financial Ratios</div>
            <div style="font-size:12px;color:#475569;line-height:1.6;">P/E, ROE, margins, liquidity, growth metrics and more</div>
        </div>
        <div style="background:rgba(15,21,32,0.5);border:1px solid rgba(148,163,184,0.07);border-radius:14px;padding:24px;text-align:center;">
            <div style="font-size:26px;margin-bottom:10px;">🎯</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:600;color:#e2e8f0;margin-bottom:6px;">DCF + Graham Valuation</div>
            <div style="font-size:12px;color:#475569;line-height:1.6;">Fair value estimates with buy / hold / sell scoring</div>
        </div>
        <div style="background:rgba(15,21,32,0.5);border:1px solid rgba(148,163,184,0.07);border-radius:14px;padding:24px;text-align:center;">
            <div style="font-size:26px;margin-bottom:10px;">🌍</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:14px;font-weight:600;color:#e2e8f0;margin-bottom:6px;">Global Markets</div>
            <div style="font-size:12px;color:#475569;line-height:1.6;">US, India, UK, Europe, crypto and ETFs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

# ── BACK BUTTON STYLE (scoped to key) ────────────────────────────────────────
st.markdown("""
<style>
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
button[kind="secondary"]#back_btn_widget,
div[data-testid="column"]:first-child button {
    background: rgba(15,21,32,0.7) !important;
    border: 1px solid rgba(148,163,184,0.12) !important;
    border-radius: 8px !important;
    color: #64748b !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
    box-shadow: none !important;
    width: auto !important;
    letter-spacing: 0.2px !important;
}
div[data-testid="column"]:first-child button:hover {
    border-color: rgba(56,189,248,0.3) !important;
    color: #38bdf8 !important;
    background: rgba(56,189,248,0.05) !important;
}
</style>
""", unsafe_allow_html=True)

# ── DASHBOARD HEADER — single unified row ─────────────────────────────────────
back_col, logo_col, live_col = st.columns([1, 7, 1])

with back_col:
    if st.button("← Back", key="back_btn"):
        go_to_search()
        st.rerun()

with logo_col:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;gap:10px;padding:6px 0;">
        <div style="width:28px;height:28px;border-radius:7px;background:linear-gradient(135deg,#38bdf8,#0ea5e9);
                    display:flex;align-items:center;justify-content:center;font-size:14px;
                    box-shadow:0 2px 12px rgba(56,189,248,0.3);">📈</div>
        <span style="font-family:'Space Grotesk',sans-serif;font-size:19px;font-weight:700;
                     color:#f8fafc;letter-spacing:-0.5px;">
            Fin<span style='color:#38bdf8'>Scope</span>
        </span>
    </div>""", unsafe_allow_html=True)

with live_col:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:flex-end;gap:6px;padding:10px 0;">
        <div style="width:6px;height:6px;border-radius:50%;background:#4ade80;
                    box-shadow:0 0 8px #4ade80;animation:pulse 2s infinite;"></div>
        <span style="font-family:'JetBrains Mono',monospace;font-size:10px;
                     color:#334155;letter-spacing:1px;">LIVE</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='border-top:1px solid rgba(148,163,184,0.08);margin:4px 0 24px;'></div>",
            unsafe_allow_html=True)

# ── FETCH DATA ───────────────────────────────────────────────────────────────
ticker = st.session_state.ticker

with st.spinner(f"Loading {ticker}…"):
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info
        hist  = stock.history(period="6mo")
        fin   = stock.financials
        recs  = stock.recommendations
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

price = gv(info,"currentPrice") or gv(info,"regularMarketPrice")
if not price:
    st.error(f"No data for '{ticker}'. Try searching the company name above.")
    st.stop()

currency   = gv(info,"currency","USD")
prev_close = gv(info,"previousClose", price)
change     = price - prev_close
change_pct = change / prev_close * 100 if prev_close else 0
name       = gv(info,"longName", ticker)
shares     = gv(info,"sharesOutstanding", 1) or 1

# ── VALUATION ────────────────────────────────────────────────────────────────
eps    = gv(info,"trailingEps", 0) or 0
bv     = gv(info,"bookValue", 0) or 0
graham = math.sqrt(22.5 * eps * bv) if eps > 0 and bv > 0 else None
fcf    = gv(info,"freeCashflow", 0) or 0
cash   = gv(info,"totalCash", 0) or 0
debt   = gv(info,"totalDebt", 0) or 0
eg     = gv(info,"earningsGrowth", 0.05) or 0.05
dcf    = None
if fcf and shares:
    mult = 10 + min(max(eg, -0.1), 0.3) * 100
    dcf  = fcf / shares * mult + cash / shares - debt / shares

analyst_mean = gv(info,"targetMeanPrice")
analyst_high = gv(info,"targetHighPrice")
analyst_low  = gv(info,"targetLowPrice")
fair_value   = dcf or analyst_mean or graham
upside_pct   = (fair_value - price) / price * 100 if fair_value and price else None

# ── SCORE ────────────────────────────────────────────────────────────────────
score = 50; reasons = []
pe         = gv(info,"trailingPE", 0) or 0
margin     = gv(info,"profitMargins", 0) or 0
roe        = gv(info,"returnOnEquity", 0) or 0
rev_growth = gv(info,"revenueGrowth", 0) or 0
peg        = gv(info,"pegRatio", 0) or 0

if fair_value and price:
    up = (fair_value - price) / price
    if up > 0.2:     score += 20; reasons.append("undervalued vs fair value")
    elif up > 0.05:  score += 10
    elif up < -0.15: score -= 20; reasons.append("overvalued vs fair value")
    elif up < 0:     score -= 5
if pe:
    if pe < 15:  score += 10; reasons.append("low P/E ratio")
    elif pe > 40: score -= 10; reasons.append("elevated P/E ratio")
if margin:
    if margin > 0.15:  score += 10; reasons.append("strong profit margins")
    elif margin < 0:   score -= 15; reasons.append("negative margins")
if roe > 0.15:       score += 8;  reasons.append("strong ROE")
if rev_growth > 0.1: score += 8;  reasons.append("solid revenue growth")
if peg and 0 < peg < 1: score += 10; reasons.append("attractive PEG ratio")
if analyst_mean and price:
    aup = (analyst_mean - price) / price
    if aup > 0.1:    score += 8; reasons.append("analyst consensus bullish")
    elif aup < -0.05: score -= 8; reasons.append("analyst consensus bearish")

score = max(0, min(100, score))
if score >= 65:   signal, sig_color, sig_bg = "BUY",  "#4ade80", "rgba(74,222,128,0.08)"
elif score <= 35: signal, sig_color, sig_bg = "SELL", "#f87171", "rgba(248,113,113,0.08)"
else:             signal, sig_color, sig_bg = "HOLD", "#fbbf24", "rgba(251,191,36,0.08)"

sig_border = sig_color.replace(")", ",0.25)").replace("#4ade80","rgba(74,222,128").replace("#f87171","rgba(248,113,113").replace("#fbbf24","rgba(251,191,36")
upside_color = "#4ade80" if (upside_pct or 0) >= 0 else "#f87171"
upside_str   = f"{'+' if (upside_pct or 0)>=0 else ''}{upside_pct:.1f}%" if upside_pct else "—"
change_color = "#4ade80" if change >= 0 else "#f87171"

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

# ── COMPANY HEADER ────────────────────────────────────────────────────────────
hc1, hc2 = st.columns([3,1])
with hc1:
    tags = [t for t in [ticker, gv(info,"exchange",""), gv(info,"sector",""), gv(info,"country","")] if t]
    tag_html = "".join([f'<span style="background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.18);border-radius:6px;padding:3px 10px;font-size:11px;color:#7dd3fc;font-family:JetBrains Mono,monospace;letter-spacing:0.5px;">{t}</span>' for t in tags])
    st.markdown(f"""
    <div style="margin-bottom:4px;">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:30px;font-weight:700;
                    color:#f8fafc;letter-spacing:-0.5px;margin-bottom:10px;">{name}</div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;">{tag_html}</div>
    </div>""", unsafe_allow_html=True)

with hc2:
    st.markdown(f"""
    <div style="text-align:right;padding-top:4px;">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:36px;font-weight:700;
                    color:#f8fafc;letter-spacing:-1px;line-height:1;">{currency} {price:,.2f}</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:{change_color};margin-top:4px;">
            {'+' if change>=0 else ''}{change:.2f} ({'+' if change_pct>=0 else ''}{change_pct:.2f}%)
        </div>
        <div style="font-size:11px;color:#334155;margin-top:4px;font-family:'JetBrains Mono',monospace;">
            {datetime.now().strftime('%d %b %Y')}
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin:20px 0;border-top:1px solid rgba(148,163,184,0.08);'></div>", unsafe_allow_html=True)

# ── VERDICT BANNER ───────────────────────────────────────────────────────────
reason_text = ("Key factors: " + ", ".join(reasons[:3]) + ".") if reasons else "Insufficient data for full analysis."

v1, v2, v3, v4, v5 = st.columns([1, 2.5, 1.1, 1.1, 1])
verdict_style = f"background:{sig_bg};border:1px solid {sig_border};border-radius:14px;padding:20px;height:100%;backdrop-filter:blur(12px);"

with v1:
    st.markdown(f"""
    <div style="{verdict_style}text-align:center;">
        <div style="width:62px;height:62px;border-radius:50%;border:2.5px solid {sig_color};
                    display:flex;align-items:center;justify-content:center;margin:0 auto 10px;
                    background:rgba(0,0,0,0.3);">
            <span style="font-family:'Space Grotesk',sans-serif;font-weight:800;font-size:14px;
                         color:{sig_color};letter-spacing:1px;">{signal}</span>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#475569;letter-spacing:1px;">SIGNAL</div>
    </div>""", unsafe_allow_html=True)

with v2:
    st.markdown(f"""
    <div style="{verdict_style}">
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#334155;letter-spacing:2px;
                    text-transform:uppercase;margin-bottom:8px;">Analysis Summary</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:600;
                    color:{sig_color};margin-bottom:6px;">
            {"Strong Buy Signal" if signal=="BUY" else "Sell / Avoid" if signal=="SELL" else "Hold & Watch"}
        </div>
        <div style="font-size:13px;color:#64748b;line-height:1.6;">{reason_text}</div>
    </div>""", unsafe_allow_html=True)

for label, val, col in [
    ("Fair Value",  f"{currency} {fair_value:.2f}" if fair_value else "—", "#e2e8f0"),
    ("Upside",      upside_str, upside_color),
    ("Score",       f"{score}/100", sig_color),
]:
    idx = ["Fair Value","Upside","Score"].index(label)
    with [v3,v4,v5][idx]:
        st.markdown(f"""
        <div style="{verdict_style}text-align:center;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#334155;
                        letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">{label}</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;font-weight:700;color:{col};">{val}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

# ── KPI CARDS ────────────────────────────────────────────────────────────────
kc = st.columns(8)
kpis = [
    ("Market Cap",   fmt_large(gv(info,"marketCap")),         "Capitalization"),
    ("Revenue TTM",  fmt_large(gv(info,"totalRevenue")),      "Annual Revenue"),
    ("Net Income",   fmt_large(gv(info,"netIncomeToCommon")), "TTM"),
    ("P/E Ratio",    safe(gv(info,"trailingPE"),1)+"x",       "Trailing"),
    ("EPS TTM",      safe(gv(info,"trailingEps")),            "Per Share"),
    ("Div Yield",    fmt_pct(gv(info,"dividendYield")),       "Annual"),
    ("52W High",     f"{currency} {safe(gv(info,'fiftyTwoWeekHigh'))}", ""),
    ("52W Low",      f"{currency} {safe(gv(info,'fiftyTwoWeekLow'))}", ""),
]
for col, (label, val, sub) in zip(kc, kpis):
    with col:
        st.markdown(kpi_card(label, val, sub), unsafe_allow_html=True)

st.markdown("<div style='margin:24px 0;'></div>", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊  Overview", "💰  Valuation", "📋  Key Ratios", "📈  Charts"])

# ─── TAB 1: OVERVIEW ─────────────────────────────────────────────────────────
with tab1:
    oc1, oc2 = st.columns(2)
    def chart_label(text):
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;letter-spacing:2px;color:#334155;text-transform:uppercase;margin-bottom:10px;">{text}</div>', unsafe_allow_html=True)

    with oc1:
        chart_label("Price History — 6 Months")
        if not hist.empty:
            lc = "#4ade80" if hist["Close"].iloc[-1] >= hist["Close"].iloc[0] else "#f87171"
            fc = "rgba(74,222,128,0.07)" if lc=="#4ade80" else "rgba(248,113,113,0.07)"
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"].round(2), mode="lines",
                line=dict(color=lc, width=2), fill="tozeroy", fillcolor=fc,
                hovertemplate=f"{currency} %{{y:,.2f}}<extra></extra>"
            ))
            fig.update_layout(**{**PL, "height":240})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with oc2:
        chart_label("Revenue vs Net Income (Billions)")
        if fin is not None and not fin.empty:
            rev_row = next((r for r in fin.index if "Total Revenue" in str(r)), None)
            ni_row  = next((r for r in fin.index if "Net Income" in str(r)), None)
            if rev_row and ni_row:
                cols_s = sorted(fin.columns)[:4]
                yr = [str(c.year) for c in cols_s]
                rv = [round(float(fin.loc[rev_row,c])/1e9,2) if pd.notna(fin.loc[rev_row,c]) else 0 for c in cols_s]
                nv = [round(float(fin.loc[ni_row,c])/1e9,2)  if pd.notna(fin.loc[ni_row,c]) else 0  for c in cols_s]
                fig2 = go.Figure(data=[
                    go.Bar(name="Revenue",    x=yr, y=rv, marker_color="rgba(56,189,248,0.8)", marker_line_width=0),
                    go.Bar(name="Net Income", x=yr, y=nv, marker_color="rgba(74,222,128,0.8)", marker_line_width=0),
                ])
                fig2.update_layout(**{**PL, "height":240, "barmode":"group",
                    "legend":dict(font=dict(size=10,color="#64748b"), bgcolor="rgba(0,0,0,0)")})
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    st.markdown("<div style='margin:8px 0;'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;letter-spacing:2px;color:#334155;text-transform:uppercase;margin-bottom:16px;">Performance Gauges</div>', unsafe_allow_html=True)

    # Pull values with multiple field fallbacks
    raw_pe     = gv(info,"trailingPE") or gv(info,"forwardPE")
    raw_margin = gv(info,"profitMargins") or gv(info,"netMargins") or gv(info,"returnOnAssets")
    raw_roe    = gv(info,"returnOnEquity")
    raw_de     = gv(info,"debtToEquity")

    def stat_gauge_html(title, raw_val, display_val, bar_pct, bar_color, sub_label, rating, rating_color):
        """A clean horizontal-bar stat card that always renders."""
        pct = max(0, min(bar_pct, 100))
        return f"""
        <div style="background:rgba(15,21,32,0.85);border:1px solid rgba(148,163,184,0.1);
                    border-radius:14px;padding:22px 20px;backdrop-filter:blur(12px);">
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:2px;
                        text-transform:uppercase;color:#475569;margin-bottom:14px;">{title}</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:34px;font-weight:700;
                        color:#f1f5f9;line-height:1;margin-bottom:6px;">{display_val}</div>
            <div style="font-size:11px;color:#475569;margin-bottom:14px;">{sub_label}</div>
            <div style="background:rgba(255,255,255,0.05);border-radius:4px;height:6px;overflow:hidden;margin-bottom:10px;">
                <div style="width:{pct}%;height:100%;background:{bar_color};border-radius:4px;
                            transition:width 1s ease;box-shadow:0 0 8px {bar_color}55;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#334155;">0 — {int(pct)}% of range</div>
                <div style="background:rgba(0,0,0,0.3);border:1px solid {rating_color}44;border-radius:6px;
                            padding:2px 10px;font-family:'JetBrains Mono',monospace;font-size:10px;
                            color:{rating_color};letter-spacing:1px;">{rating}</div>
            </div>
        </div>"""

    def get_rating(val, thresholds, labels, invert=False):
        """Return (rating_text, color) based on value."""
        if val is None: return "N/A", "#475569"
        lo, hi = thresholds
        if invert:
            if val <= lo:   return labels[0], "#4ade80"
            elif val <= hi: return labels[1], "#fbbf24"
            else:           return labels[2], "#f87171"
        else:
            if val >= hi:   return labels[0], "#4ade80"
            elif val >= lo: return labels[1], "#fbbf24"
            else:           return labels[2], "#f87171"

    gc = st.columns(4)

    # ── P/E Ratio ──
    with gc[0]:
        v = raw_pe
        rating, rc = get_rating(v, (15, 25), ["CHEAP", "FAIR", "PRICEY"], invert=True)
        display = f"{v:.1f}x" if v else "—"
        pct = (1 - min((v or 0)/60, 1)) * 100 if v else 0
        bar_c = rc
        sub = "Trailing P/E — lower is cheaper"
        st.markdown(stat_gauge_html("P/E Ratio", v, display, pct, bar_c, sub, rating, rc), unsafe_allow_html=True)

    # ── Net Margin ──
    with gc[1]:
        v = raw_margin
        vp = (v or 0) * 100
        rating, rc = get_rating(vp, (5, 15), ["STRONG", "MODERATE", "WEAK"])
        display = f"{vp:.1f}%" if v is not None else "—"
        pct = min(max(vp / 40 * 100, 0), 100)
        sub = "Net profit as % of revenue"
        st.markdown(stat_gauge_html("Net Margin", v, display, pct, rc, sub, rating, rc), unsafe_allow_html=True)

    # ── Return on Equity ──
    with gc[2]:
        v = raw_roe
        vp = (v or 0) * 100
        rating, rc = get_rating(vp, (10, 20), ["STRONG", "MODERATE", "WEAK"])
        display = f"{vp:.1f}%" if v is not None else "—"
        pct = min(max(vp / 50 * 100, 0), 100)
        sub = "Profit generated per equity dollar"
        st.markdown(stat_gauge_html("Return on Equity", v, display, pct, rc, sub, rating, rc), unsafe_allow_html=True)

    # ── Debt / Equity ──
    with gc[3]:
        v = raw_de
        vr = (v or 0) / 100  # yfinance gives D/E * 100
        rating, rc = get_rating(vr, (0.5, 1.5), ["LOW", "MODERATE", "HIGH"], invert=True)
        display = f"{vr:.2f}" if v is not None else "—"
        pct = min(max(vr / 3 * 100, 0), 100)
        sub = "Total debt relative to equity"
        st.markdown(stat_gauge_html("Debt / Equity", v, display, pct, rc, sub, rating, rc), unsafe_allow_html=True)

# ─── TAB 2: VALUATION ────────────────────────────────────────────────────────
with tab2:
    vc1, vc2 = st.columns(2)
    with vc1:
        dcf_col = "#4ade80" if dcf and dcf > price else "#f87171"
        gr_col  = "#4ade80" if graham and graham > price else "#f87171"
        html = ratio_card_open("Valuation Multiples", "#38bdf8")
        for lbl, val in [
            ("P/E Ratio (TTM)",   safe(gv(info,"trailingPE"),2)+"x"),
            ("Forward P/E",       safe(gv(info,"forwardPE"),2)+"x"),
            ("PEG Ratio",         safe(gv(info,"pegRatio"),2)),
            ("Price / Book",      safe(gv(info,"priceToBook"),2)+"x"),
            ("Price / Sales",     safe(gv(info,"priceToSalesTrailing12Months"),2)+"x"),
            ("EV / EBITDA",       safe(gv(info,"enterpriseToEbitda"),2)+"x"),
            ("EV / Revenue",      safe(gv(info,"enterpriseToRevenue"),2)+"x"),
        ]:
            html += ratio_row(lbl, val)
        html += ratio_card_close()
        st.markdown(html, unsafe_allow_html=True)

    with vc2:
        html = ratio_card_open("Price Targets", "#a78bfa")
        for lbl, val, col in [
            ("Current Price",     f"{currency} {price:,.2f}", "#e2e8f0"),
            ("DCF Fair Value",    f"{currency} {dcf:.2f}" if dcf else "—", dcf_col),
            ("Graham Number",     f"{currency} {graham:.2f}" if graham else "—", gr_col),
            ("Analyst Mean",      f"{currency} {analyst_mean:.2f}" if analyst_mean else "—", "#e2e8f0"),
            ("Analyst High",      f"{currency} {analyst_high:.2f}" if analyst_high else "—", "#4ade80"),
            ("Analyst Low",       f"{currency} {analyst_low:.2f}" if analyst_low else "—", "#f87171"),
            ("Margin of Safety",  upside_str, upside_color),
        ]:
            html += ratio_row(lbl, val, col)
        html += ratio_card_close()
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("<div style='margin:16px 0;'></div>", unsafe_allow_html=True)
    val_items = {"Current\nPrice": price}
    if dcf:          val_items["DCF\nEst."]    = round(dcf,2)
    if graham:       val_items["Graham\nNo."]  = round(graham,2)
    if analyst_mean: val_items["Analyst\nMean"]= round(analyst_mean,2)

    if len(val_items) > 1:
        chart_label("Valuation Comparison")
        colors = ["rgba(56,189,248,0.85)","rgba(74,222,128,0.85)","rgba(251,191,36,0.85)","rgba(167,139,250,0.85)"]
        fig_v = go.Figure(go.Bar(
            x=list(val_items.values()), y=list(val_items.keys()), orientation="h",
            marker_color=colors[:len(val_items)], marker_line_width=0,
            text=[f"{currency} {v:,.2f}" for v in val_items.values()],
            textposition="outside", textfont=dict(color="#94a3b8", size=11, family="JetBrains Mono"),
        ))
        fig_v.update_layout(**{**PL, "height":180,
            "xaxis": dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(size=10,color="#475569")),
            "yaxis": dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11,family="JetBrains Mono",color="#64748b"))})
        st.plotly_chart(fig_v, use_container_width=True, config={"displayModeBar":False})

# ─── TAB 3: KEY RATIOS ───────────────────────────────────────────────────────
with tab3:
    rc1, rc2 = st.columns(2)
    with rc1:
        html = ratio_card_open("Profitability", "#4ade80")
        for lbl, val in [
            ("Gross Margin",       fmt_pct(gv(info,"grossMargins"))),
            ("Operating Margin",   fmt_pct(gv(info,"operatingMargins"))),
            ("Net Profit Margin",  fmt_pct(gv(info,"profitMargins"))),
            ("EBITDA Margin",      fmt_pct(gv(info,"ebitdaMargins"))),
            ("Return on Assets",   fmt_pct(gv(info,"returnOnAssets"))),
            ("Return on Equity",   fmt_pct(gv(info,"returnOnEquity"))),
        ]:
            html += ratio_row(lbl, val)
        html += ratio_card_close()
        st.markdown(html, unsafe_allow_html=True)

        st.markdown("<div style='margin:14px 0;'></div>", unsafe_allow_html=True)

        html = ratio_card_open("Growth", "#fbbf24")
        for lbl, val in [
            ("Revenue Growth YoY",    fmt_pct(gv(info,"revenueGrowth"))),
            ("Earnings Growth YoY",   fmt_pct(gv(info,"earningsGrowth"))),
            ("EPS Growth (Qtr)",      fmt_pct(gv(info,"earningsQuarterlyGrowth"))),
            ("Revenue / Share",       safe(gv(info,"revenuePerShare"))),
            ("Book Value / Share",    safe(gv(info,"bookValue"))),
            ("Operating Cash Flow",   fmt_large(gv(info,"operatingCashflow"))),
        ]:
            html += ratio_row(lbl, val)
        html += ratio_card_close()
        st.markdown(html, unsafe_allow_html=True)

    with rc2:
        html = ratio_card_open("Liquidity & Solvency", "#f87171")
        for lbl, val in [
            ("Current Ratio",    safe(gv(info,"currentRatio"))),
            ("Quick Ratio",      safe(gv(info,"quickRatio"))),
            ("Debt / Equity",    safe((gv(info,"debtToEquity",0) or 0)/100)),
            ("Total Debt",       fmt_large(gv(info,"totalDebt"))),
            ("Total Cash",       fmt_large(gv(info,"totalCash"))),
            ("Free Cash Flow",   fmt_large(gv(info,"freeCashflow"))),
        ]:
            html += ratio_row(lbl, val)
        html += ratio_card_close()
        st.markdown(html, unsafe_allow_html=True)

        st.markdown("<div style='margin:14px 0;'></div>", unsafe_allow_html=True)

        html = ratio_card_open("Dividends & Ownership", "#a78bfa")
        for lbl, val in [
            ("Dividend Yield",        fmt_pct(gv(info,"dividendYield"))),
            ("Dividend Rate",         safe(gv(info,"dividendRate"))),
            ("Payout Ratio",          fmt_pct(gv(info,"payoutRatio"))),
            ("Shares Outstanding",    fmt_large(gv(info,"sharesOutstanding"))),
            ("Insider Ownership",     fmt_pct(gv(info,"heldPercentInsiders"))),
            ("Institutional Own.",    fmt_pct(gv(info,"heldPercentInstitutions"))),
        ]:
            html += ratio_row(lbl, val)
        html += ratio_card_close()
        st.markdown(html, unsafe_allow_html=True)

# ─── TAB 4: CHARTS ───────────────────────────────────────────────────────────
with tab4:
    def get_series(df, keyword):
        if df is None or df.empty: return [], []
        row = next((r for r in df.index if keyword.lower() in str(r).lower()), None)
        if not row: return [], []
        cols = sorted(df.columns)[:4]
        return [str(c.year) for c in cols], \
               [round(float(df.loc[row,c])/1e9,2) if pd.notna(df.loc[row,c]) else 0 for c in cols]

    tc1, tc2 = st.columns(2)
    with tc1:
        chart_label("Revenue Trend (Billions)")
        rl, rv = get_series(fin, "Total Revenue")
        if rl:
            fig = go.Figure(go.Bar(x=rl, y=rv, marker_color="rgba(56,189,248,0.8)", marker_line_width=0,
                text=[f"{v:.1f}B" for v in rv], textposition="outside",
                textfont=dict(color="#94a3b8", size=10, family="JetBrains Mono")))
            fig.update_layout(**{**PL, "height":230})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with tc2:
        chart_label("EPS Trend")
        nl, nv = get_series(fin, "Net Income")
        if nl and shares:
            ev = [round(v*1e9/shares,2) for v in nv]
            fig = go.Figure(go.Scatter(x=nl, y=ev, mode="lines+markers",
                line=dict(color="#4ade80", width=2.5),
                marker=dict(color="#4ade80", size=8, line=dict(color="#080b12",width=2)),
                text=[f"{v:.2f}" for v in ev], textposition="top center",
                textfont=dict(color="#94a3b8",size=10,family="JetBrains Mono")))
            fig.update_layout(**{**PL, "height":230})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    tc3, tc4 = st.columns(2)
    with tc3:
        chart_label("Margin Analysis (%)")
        mv = [(gv(info,k) or 0)*100 for k in ["grossMargins","operatingMargins","profitMargins","ebitdaMargins"]]
        mc = ["rgba(74,222,128,0.85)" if v>=0 else "rgba(248,113,113,0.85)" for v in mv]
        fig = go.Figure(go.Bar(x=["Gross","Operating","Net","EBITDA"], y=[round(v,1) for v in mv],
            marker_color=mc, marker_line_width=0,
            text=[f"{v:.1f}%" for v in mv], textposition="outside",
            textfont=dict(color="#94a3b8",size=10,family="JetBrains Mono")))
        fig.update_layout(**{**PL, "height":230,
            "yaxis":dict(ticksuffix="%",gridcolor="rgba(255,255,255,0.04)",tickfont=dict(size=10,color="#475569"))})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with tc4:
        chart_label("Analyst Recommendations")
        rec_data = {"Strong Buy":0,"Buy":0,"Hold":0,"Sell":0,"Strong Sell":0}
        if recs is not None and not recs.empty:
            latest = recs.iloc[-1]
            for k2,l in [("strongBuy","Strong Buy"),("buy","Buy"),("hold","Hold"),("sell","Sell"),("strongSell","Strong Sell")]:
                if k2 in latest: rec_data[l] = int(latest[k2])
        if any(v>0 for v in rec_data.values()):
            fig = go.Figure(go.Pie(
                labels=list(rec_data.keys()), values=list(rec_data.values()),
                marker_colors=["#4ade80","#86efac","#fbbf24","#fca5a5","#f87171"],
                hole=0.5, textfont=dict(color="#94a3b8",size=10,family="JetBrains Mono"),
                hovertemplate="%{label}: %{value}<extra></extra>"
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=230, margin=dict(l=10,r=10,t=10,b=10),
                legend=dict(font=dict(size=10,color="#64748b"),bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:rgba(15,21,32,0.6);border:1px solid rgba(148,163,184,0.08);
            border-radius:12px;padding:14px 20px;margin-top:32px;
            font-family:'JetBrains Mono',monospace;font-size:11px;color:#334155;line-height:1.7;">
    ⚠ <strong style="color:#475569;">Disclaimer</strong> — For educational purposes only.
    Data via yfinance / Yahoo Finance. Buy/Sell signals are algorithmic estimates
    and do <strong style="color:#475569;">not</strong> constitute financial advice.
    Always consult a qualified financial advisor before investing.
</div>
""", unsafe_allow_html=True)
