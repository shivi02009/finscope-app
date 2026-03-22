import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import math, json
from datetime import datetime

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinScope — Financial Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;700;800&family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 3rem 3rem; max-width: 1400px; }

/* Background */
.stApp { background: #0a0c10; }

/* Grid overlay */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none; z-index: 0;
}

/* Text */
h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; color: #e8ecf4 !important; }
p, li, span, div { color: #e8ecf4; }
label { color: #8b92a5 !important; }

/* Input */
.stTextInput > div > div > input {
    background: #181c24 !important;
    border: 1px solid rgba(255,255,255,0.13) !important;
    border-radius: 10px !important;
    color: #e8ecf4 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 16px !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4ade80 !important;
    box-shadow: 0 0 0 3px rgba(74,222,128,0.12) !important;
}

/* Button */
.stButton > button {
    background: #4ade80 !important;
    color: #052e0a !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 12px 28px !important;
    width: 100% !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: #22c55e !important; }

/* Metrics */
[data-testid="metric-container"] {
    background: #111318 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 16px 18px !important;
}
[data-testid="metric-container"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    color: #555e72 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #e8ecf4 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #555e72 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    color: #4ade80 !important;
    border-bottom-color: #4ade80 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 20px !important;
}

/* Dividers */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Dataframe */
[data-testid="stDataFrame"] { background: #111318 !important; border-radius: 12px !important; }
.dvn-scroller { background: #111318 !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #111318 !important; border-right: 1px solid rgba(255,255,255,0.07) !important; }

/* Plotly charts transparent */
.js-plotly-plot .plotly { background: transparent !important; }

/* Selectbox */
.stSelectbox > div > div {
    background: #181c24 !important;
    border-color: rgba(255,255,255,0.13) !important;
    color: #e8ecf4 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ─────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Mono', color='#8b92a5', size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor='rgba(255,255,255,0.04)', linecolor='rgba(255,255,255,0.07)', tickfont=dict(size=10)),
    yaxis=dict(gridcolor='rgba(255,255,255,0.04)', linecolor='rgba(255,255,255,0.07)', tickfont=dict(size=10)),
)

# ── HELPERS ──────────────────────────────────────────────────────────────────
def fmt_large(n):
    if n is None or (isinstance(n, float) and math.isnan(n)): return "N/A"
    n = float(n)
    if abs(n) >= 1e12: return f"{n/1e12:.2f}T"
    if abs(n) >= 1e9:  return f"{n/1e9:.2f}B"
    if abs(n) >= 1e6:  return f"{n/1e6:.2f}M"
    return f"{n:.2f}"

def fmt_pct(n):
    if n is None or (isinstance(n, float) and math.isnan(n)): return "N/A"
    return f"{float(n)*100:.1f}%"

def safe(n, dec=2):
    if n is None or (isinstance(n, float) and math.isnan(n)): return "N/A"
    return f"{float(n):.{dec}f}"

def g(info, key, default=None):
    v = info.get(key, default)
    if v is None: return default
    if isinstance(v, float) and math.isnan(v): return default
    return v

def card_html(label, value, sub="", color="#e8ecf4"):
    return f"""
    <div style="background:#111318;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:16px 18px;">
        <div style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#555e72;margin-bottom:7px;">{label}</div>
        <div style="font-family:'Syne',sans-serif;font-size:21px;font-weight:700;color:{color};line-height:1;margin-bottom:3px;">{value}</div>
        <div style="font-size:11px;color:#555e72;">{sub}</div>
    </div>"""

def ratio_row_html(label, value, color="#e8ecf4"):
    return f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
        <span style="color:#8b92a5;font-size:13px;">{label}</span>
        <span style="font-family:'DM Mono',monospace;font-size:13px;color:{color};">{value}</span>
    </div>"""

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:24px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:28px;">
    <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:10px;height:10px;border-radius:50%;background:#4ade80;box-shadow:0 0 12px #4ade80;animation:pulse 2s infinite;"></div>
        <span style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#e8ecf4;letter-spacing:-0.5px;">Fin<span style='color:#4ade80'>Scope</span></span>
        <span style="font-family:'DM Mono',monospace;font-size:11px;color:#555e72;margin-left:8px;letter-spacing:1px;">FINANCIAL INTELLIGENCE</span>
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:11px;color:#555e72;">LIVE DATA · YAHOO FINANCE</div>
</div>
""", unsafe_allow_html=True)

# ── SEARCH BAR ───────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    ticker_input = st.text_input(
        "", placeholder="Enter ticker symbol — AAPL · TSLA · RELIANCE.NS · TCS.NS · NVDA · MSFT",
        label_visibility="collapsed", key="ticker_input"
    )
with col_btn:
    analyse_btn = st.button("Analyse →")

# Quick picks
st.markdown("""
<div style="display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 28px 0;">
    <span style="font-size:11px;color:#555e72;font-family:'DM Mono',monospace;padding-top:2px;">QUICK:</span>
""" + "".join([
    f'<span style="background:#181c24;border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:4px 12px;font-size:12px;color:#8b92a5;font-family:DM Mono,monospace;cursor:default;">{t}</span>'
    for t in ["AAPL","MSFT","GOOGL","TSLA","NVDA","AMZN","RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS"]
]) + "</div>", unsafe_allow_html=True)

# ── MAIN LOGIC ───────────────────────────────────────────────────────────────
ticker = ticker_input.strip().upper() if (analyse_btn or ticker_input) else None

if not ticker:
    st.markdown("""
    <div style="text-align:center;padding:80px 0 60px;border:1px solid rgba(255,255,255,0.05);border-radius:16px;background:#0d0f14;margin-top:20px;">
        <div style="font-family:'DM Mono',monospace;font-size:11px;letter-spacing:2px;color:#4ade80;margin-bottom:16px;text-transform:uppercase;">AI-Powered Financial Intelligence</div>
        <div style="font-family:'Syne',sans-serif;font-size:52px;font-weight:800;letter-spacing:-2px;color:#e8ecf4;line-height:1.05;margin-bottom:16px;">Analyse Any Stock<br><span style='color:#4ade80'>in Seconds</span></div>
        <div style="color:#555e72;font-size:16px;max-width:480px;margin:0 auto;line-height:1.6;">Real-time ratios · DCF valuation · Buy/Sell signals<br>Full dashboard for any global stock</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── FETCH ────────────────────────────────────────────────────────────────────
with st.spinner(f"Fetching data for {ticker}…"):
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info
        hist  = stock.history(period="6mo")
        fin   = stock.financials
        bal   = stock.balance_sheet
        cf    = stock.cashflow
        recs  = stock.recommendations
    except Exception as e:
        st.error(f"Error fetching {ticker}: {e}")
        st.stop()

price = g(info,"currentPrice") or g(info,"regularMarketPrice")
if not price:
    st.error(f"No data found for '{ticker}'. Check the symbol — Indian stocks need .NS suffix (e.g. RELIANCE.NS, TCS.NS)")
    st.stop()

currency    = g(info,"currency","USD")
prev_close  = g(info,"previousClose", price)
change      = price - prev_close
change_pct  = change / prev_close * 100 if prev_close else 0
name        = g(info,"longName", ticker)

# ── VALUATION CALCULATIONS ───────────────────────────────────────────────────
eps    = g(info,"trailingEps", 0) or 0
bv     = g(info,"bookValue", 0) or 0
graham = math.sqrt(22.5 * eps * bv) if eps > 0 and bv > 0 else None

fcf    = g(info,"freeCashflow", 0) or 0
shares = g(info,"sharesOutstanding", 1) or 1
cash   = g(info,"totalCash", 0) or 0
debt   = g(info,"totalDebt", 0) or 0
eg     = g(info,"earningsGrowth", 0.05) or 0.05
dcf    = None
if fcf and shares:
    mult = 10 + min(max(eg, -0.1), 0.3) * 100
    dcf  = fcf / shares * mult + cash / shares - debt / shares

analyst_mean = g(info,"targetMeanPrice")
analyst_high = g(info,"targetHighPrice")
analyst_low  = g(info,"targetLowPrice")
fair_value   = dcf or analyst_mean or graham
upside_pct   = (fair_value - price) / price * 100 if fair_value and price else None

# ── SIGNAL SCORE ─────────────────────────────────────────────────────────────
score = 50; reasons = []
pe         = g(info,"trailingPE", 0) or 0
margin     = g(info,"profitMargins", 0) or 0
roe        = g(info,"returnOnEquity", 0) or 0
rev_growth = g(info,"revenueGrowth", 0) or 0
peg        = g(info,"pegRatio", 0) or 0

if fair_value and price:
    up = (fair_value - price) / price
    if up > 0.2:   score += 20; reasons.append("undervalued vs fair value")
    elif up > 0.05: score += 10
    elif up < -0.15: score -= 20; reasons.append("overvalued vs fair value")
    elif up < 0: score -= 5

if pe:
    if pe < 15:  score += 10; reasons.append("low P/E")
    elif pe > 40: score -= 10; reasons.append("high P/E")

if margin:
    if margin > 0.15:  score += 10; reasons.append("strong profit margins")
    elif margin < 0:   score -= 15; reasons.append("negative margins")

if roe > 0.15:   score += 8;  reasons.append("strong ROE")
if rev_growth > 0.1: score += 8; reasons.append("strong revenue growth")
if peg and 0 < peg < 1: score += 10; reasons.append("attractive PEG ratio")

if analyst_mean and price:
    aup = (analyst_mean - price) / price
    if aup > 0.1:  score += 8; reasons.append("analysts bullish")
    elif aup < -0.05: score -= 8; reasons.append("analysts bearish")

score = max(0, min(100, score))
if score >= 65:   signal, sig_color = "BUY",  "#4ade80"
elif score <= 35: signal, sig_color = "SELL", "#f87171"
else:             signal, sig_color = "HOLD", "#fbbf24"

# ── COMPANY HEADER ───────────────────────────────────────────────────────────
ch_col1, ch_col2 = st.columns([3, 1])
with ch_col1:
    st.markdown(f"""
    <h1 style="font-size:28px;margin-bottom:8px;">{name}</h1>
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
        {"".join([f'<span style="background:#181c24;border:1px solid rgba(255,255,255,0.08);border-radius:6px;padding:3px 10px;font-size:11px;color:#8b92a5;font-family:DM Mono,monospace;">{v}</span>' for v in [ticker, g(info,"exchange",""), g(info,"sector","N/A"), g(info,"industry","N/A"), g(info,"country","")] if v])}
    </div>
    """, unsafe_allow_html=True)

with ch_col2:
    change_col = "#4ade80" if change >= 0 else "#f87171"
    st.markdown(f"""
    <div style="text-align:right;">
        <div style="font-family:'Syne',sans-serif;font-size:32px;font-weight:700;letter-spacing:-1px;">{currency} {price:.2f}</div>
        <div style="font-family:'DM Mono',monospace;font-size:14px;color:{change_col};">
            {'+' if change>=0 else ''}{change:.2f} ({'+' if change_pct>=0 else ''}{change_pct:.2f}%)
        </div>
        <div style="font-size:11px;color:#555e72;margin-top:3px;font-family:'DM Mono',monospace;">{currency} · {g(info,'quoteType','')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)

# ── VERDICT BANNER ───────────────────────────────────────────────────────────
verdict_bg   = {"BUY":"rgba(74,222,128,0.07)","SELL":"rgba(248,113,113,0.07)","HOLD":"rgba(251,191,36,0.07)"}[signal]
verdict_bdr  = {"BUY":"rgba(74,222,128,0.22)","SELL":"rgba(248,113,113,0.22)","HOLD":"rgba(251,191,36,0.22)"}[signal]
verdict_title= {"BUY":"Strong Buy Signal","SELL":"Sell / Avoid","HOLD":"Hold / Watch"}[signal]
reason_text  = ("Key factors: " + ", ".join(reasons[:3]) + ".") if reasons else "Based on available financial metrics."

upside_color = "#4ade80" if (upside_pct or 0) >= 0 else "#f87171"
upside_str   = f"{'+' if (upside_pct or 0)>=0 else ''}{upside_pct:.1f}%" if upside_pct else "N/A"

v1, v2, v3, v4, v5 = st.columns([1.2, 2.5, 1, 1, 1])
with v1:
    st.markdown(f"""
    <div style="background:{verdict_bg};border:1px solid {verdict_bdr};border-radius:14px;padding:20px;text-align:center;height:100%;">
        <div style="width:64px;height:64px;border-radius:50%;border:2.5px solid {sig_color};display:flex;align-items:center;justify-content:center;margin:0 auto 8px;background:rgba(0,0,0,0.3);">
            <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:14px;color:{sig_color};letter-spacing:1px;">{signal}</span>
        </div>
        <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:{sig_color};">{verdict_title}</div>
    </div>
    """, unsafe_allow_html=True)

with v2:
    st.markdown(f"""
    <div style="background:{verdict_bg};border:1px solid {verdict_bdr};border-radius:14px;padding:20px;height:100%;">
        <div style="font-family:'DM Mono',monospace;font-size:10px;color:#555e72;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">Analysis Summary</div>
        <div style="font-size:13px;color:#8b92a5;line-height:1.6;">{reason_text} Score based on valuation multiples, profitability, growth trajectory and analyst consensus.</div>
    </div>
    """, unsafe_allow_html=True)

for label, val, col in [
    ("Fair Value", f"{currency} {fair_value:.2f}" if fair_value else "N/A", "#e8ecf4"),
    ("Upside / Down", upside_str, upside_color),
    ("Score", f"{score}/100", sig_color),
]:
    with [v3, v4, v5][["Fair Value","Upside / Down","Score"].index(label)]:
        st.markdown(f"""
        <div style="background:{verdict_bg};border:1px solid {verdict_bdr};border-radius:14px;padding:20px;text-align:center;height:100%;">
            <div style="font-family:'DM Mono',monospace;font-size:10px;color:#555e72;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">{label}</div>
            <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:700;color:{col};">{val}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin:20px 0;'></div>", unsafe_allow_html=True)

# ── KPI CARDS ────────────────────────────────────────────────────────────────
k = st.columns(8)
kpis = [
    ("Market Cap",    fmt_large(g(info,"marketCap")),        "Capitalization"),
    ("Revenue TTM",   fmt_large(g(info,"totalRevenue")),     "Total Revenue"),
    ("Net Income",    fmt_large(g(info,"netIncomeToCommon")),"Net Income"),
    ("P/E Ratio",     safe(g(info,"trailingPE"),1)+"x",      "Trailing P/E"),
    ("EPS TTM",       safe(g(info,"trailingEps")),           "Earnings/Share"),
    ("Div Yield",     fmt_pct(g(info,"dividendYield")),      "Annual Yield"),
    ("52W High",      safe(g(info,"fiftyTwoWeekHigh")),      currency),
    ("52W Low",       safe(g(info,"fiftyTwoWeekLow")),       currency),
]
for col, (label, val, sub) in zip(k, kpis):
    with col:
        st.markdown(card_html(label, val, sub), unsafe_allow_html=True)

st.markdown("<div style='margin:24px 0;'></div>", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Valuation", "📋 Key Ratios", "📈 Charts"])

# ─── TAB 1: OVERVIEW ─────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:12px;font-weight:600;color:#555e72;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">Price History — 6 Months</div>', unsafe_allow_html=True)
        if not hist.empty:
            line_col = "#4ade80" if hist["Close"].iloc[-1] >= hist["Close"].iloc[0] else "#f87171"
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"].round(2),
                mode="lines", line=dict(color=line_col, width=2),
                fill="tozeroy",
                fillcolor=f"rgba({'74,222,128' if line_col=='#4ade80' else '248,113,113'},0.08)",
                hovertemplate=f"{currency} %{{y:.2f}}<extra></extra>"
            ))
            fig.update_layout(**PLOT_LAYOUT, height=240)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:12px;font-weight:600;color:#555e72;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">Revenue vs Net Income (Bn)</div>', unsafe_allow_html=True)
        if fin is not None and not fin.empty:
            rev_row = next((r for r in fin.index if "Total Revenue" in str(r)), None)
            ni_row  = next((r for r in fin.index if "Net Income" in str(r)), None)
            if rev_row and ni_row:
                cols_sorted = sorted(fin.columns)[:4]
                yr = [str(c.year) for c in cols_sorted]
                rv = [round(float(fin.loc[rev_row,c])/1e9,2) if pd.notna(fin.loc[rev_row,c]) else 0 for c in cols_sorted]
                nv = [round(float(fin.loc[ni_row,c])/1e9,2)  if pd.notna(fin.loc[ni_row,c]) else 0  for c in cols_sorted]
                fig2 = go.Figure(data=[
                    go.Bar(name="Revenue",    x=yr, y=rv, marker_color="rgba(96,165,250,0.8)",   marker_line_width=0),
                    go.Bar(name="Net Income", x=yr, y=nv, marker_color="rgba(74,222,128,0.8)", marker_line_width=0),
                ])
                fig2.update_layout(**PLOT_LAYOUT, height=240, barmode="group",
                    legend=dict(font=dict(size=10,color="#8b92a5"), bgcolor="rgba(0,0,0,0)"))
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin:8px 0;'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:15px;font-weight:700;color:#e8ecf4;margin-bottom:14px;display:flex;align-items:center;gap:8px;">Performance Gauges <span style="flex:1;height:1px;background:rgba(255,255,255,0.07);display:inline-block;"></span></div>', unsafe_allow_html=True)

    def make_gauge(val, title, suffix="", max_val=100, invert=False):
        if val is None: val = 0
        color = ("#f87171" if (val > max_val*0.66 if invert else val < max_val*0.33)
                 else "#fbbf24" if (val > max_val*0.33 if invert else val < max_val*0.66)
                 else "#4ade80")
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=round(val,1),
            number=dict(suffix=suffix, font=dict(color="#e8ecf4", family="Syne", size=22)),
            gauge=dict(
                axis=dict(range=[0, max_val], tickcolor="#555e72", tickfont=dict(color="#555e72",size=9)),
                bar=dict(color=color, thickness=0.7),
                bgcolor="rgba(255,255,255,0.03)",
                borderwidth=0,
                steps=[dict(range=[0,max_val*0.33],color="rgba(0,0,0,0)"),
                       dict(range=[max_val*0.33,max_val*0.66],color="rgba(0,0,0,0)"),
                       dict(range=[max_val*0.66,max_val],color="rgba(0,0,0,0)")],
            ),
            title=dict(text=title, font=dict(color="#555e72", size=10, family="DM Mono"))
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          height=170, margin=dict(l=20,r=20,t=30,b=10))
        return fig

    g1,g2,g3,g4 = st.columns(4)
    with g1:
        st.markdown('<div style="background:#111318;border:1px solid rgba(255,255,255,0.07);border-radius:13px;padding:4px;">', unsafe_allow_html=True)
        pe_val = g(info,"trailingPE") or 0
        st.plotly_chart(make_gauge(pe_val,"P/E RATIO","x",60,invert=True), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)
    with g2:
        st.markdown('<div style="background:#111318;border:1px solid rgba(255,255,255,0.07);border-radius:13px;padding:4px;">', unsafe_allow_html=True)
        st.plotly_chart(make_gauge((g(info,"profitMargins") or 0)*100,"NET MARGIN","%",40), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)
    with g3:
        st.markdown('<div style="background:#111318;border:1px solid rgba(255,255,255,0.07);border-radius:13px;padding:4px;">', unsafe_allow_html=True)
        st.plotly_chart(make_gauge((g(info,"returnOnEquity") or 0)*100,"RETURN ON EQUITY","%",50), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)
    with g4:
        st.markdown('<div style="background:#111318;border:1px solid rgba(255,255,255,0.07);border-radius:13px;padding:4px;">', unsafe_allow_html=True)
        de = (g(info,"debtToEquity") or 0)/100
        st.plotly_chart(make_gauge(de,"DEBT / EQUITY","",3,invert=True), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

# ─── TAB 2: VALUATION ────────────────────────────────────────────────────────
with tab2:
    va1, va2 = st.columns(2)
    with va1:
        st.markdown("""<div style="background:#111318;border:1px solid rgba(255,255,255,0.07);border-radius:13px;padding:18px;">
        <div style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:2px;color:#4ade80;text-transform:uppercase;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.05);">Valuation Multiples</div>
        """, unsafe_allow_html=True)
        for lbl, val in [
            ("P/E Ratio (TTM)",    safe(g(info,"trailingPE"),2)+"x"),
            ("Forward P/E",        safe(g(info,"forwardPE"),2)+"x"),
            ("PEG Ratio",          safe(g(info,"pegRatio"),2)),
            ("Price / Book",       safe(g(info,"priceToBook"),2)+"x"),
            ("Price / Sales",      safe(g(info,"priceToSalesTrailing12Months"),2)+"x"),
            ("EV / EBITDA",        safe(g(info,"enterpriseToEbitda"),2)+"x"),
            ("EV / Revenue",       safe(g(info,"enterpriseToRevenue"),2)+"x"),
        ]:
            st.markdown(ratio_row_html(lbl, val), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with va2:
        st.markdown("""<div style="background:#111318;border:1px solid rgba(255,255,255,0.07);border-radius:13px;padding:18px;">
        <div style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:2px;color:#4ade80;text-transform:uppercase;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.05);">Price Targets</div>
        """, unsafe_allow_html=True)
        dcf_col = "#4ade80" if dcf and dcf > price else "#f87171"
        gr_col  = "#4ade80" if graham and graham > price else "#f87171"
        for lbl, val, col in [
            ("Current Price",      f"{currency} {price:.2f}", "#e8ecf4"),
            ("DCF Fair Value",     f"{currency} {dcf:.2f}" if dcf else "N/A", dcf_col),
            ("Graham Number",      f"{currency} {graham:.2f}" if graham else "N/A", gr_col),
            ("Analyst Mean",       f"{currency} {analyst_mean:.2f}" if analyst_mean else "N/A", "#e8ecf4"),
            ("Analyst High",       f"{currency} {analyst_high:.2f}" if analyst_high else "N/A", "#4ade80"),
            ("Analyst Low",        f"{currency} {analyst_low:.2f}" if analyst_low else "N/A", "#f87171"),
            ("Margin of Safety",   upside_str, upside_color),
        ]:
            st.markdown(ratio_row_html(lbl, val, col), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin:16px 0;'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:12px;font-weight:600;color:#555e72;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">Valuation Comparison</div>', unsafe_allow_html=True)
    val_items = {"Current\nPrice": price}
    if dcf:          val_items["DCF\nEstimate"] = round(dcf,2)
    if graham:       val_items["Graham\nNumber"] = round(graham,2)
    if analyst_mean: val_items["Analyst\nTarget"] = round(analyst_mean,2)
    if len(val_items) > 1:
        fig_v = go.Figure(go.Bar(
            x=list(val_items.values()), y=list(val_items.keys()),
            orientation="h",
            marker_color=["rgba(96,165,250,0.85)","rgba(74,222,128,0.85)","rgba(251,191,36,0.85)","rgba(167,139,250,0.85)"][:len(val_items)],
            marker_line_width=0,
            text=[f"{currency} {v:.2f}" for v in val_items.values()],
            textposition="outside", textfont=dict(color="#8b92a5", size=11, family="DM Mono"),
        ))
        fig_v.update_layout(**PLOT_LAYOUT, height=180,
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(size=10)),
            yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=11,family="DM Mono",color="#8b92a5")))
        st.plotly_chart(fig_v, use_container_width=True, config={"displayModeBar":False})

# ─── TAB 3: KEY RATIOS ───────────────────────────────────────────────────────
with tab3:
    r1, r2, r3, r4 = st.columns(2), st.columns(2), st.columns(2), st.columns(2)
    groups = [
        ("PROFITABILITY", [
            ("Gross Margin",      fmt_pct(g(info,"grossMargins"))),
            ("Operating Margin",  fmt_pct(g(info,"operatingMargins"))),
            ("Net Profit Margin", fmt_pct(g(info,"profitMargins"))),
            ("Return on Assets",  fmt_pct(g(info,"returnOnAssets"))),
            ("Return on Equity",  fmt_pct(g(info,"returnOnEquity"))),
            ("EBITDA Margin",     fmt_pct(g(info,"ebitdaMargins"))),
        ]),
        ("LIQUIDITY & SOLVENCY", [
            ("Current Ratio",     safe(g(info,"currentRatio"))),
            ("Quick Ratio",       safe(g(info,"quickRatio"))),
            ("Debt / Equity",     safe((g(info,"debtToEquity",0) or 0)/100,2)),
            ("Total Debt",        fmt_large(g(info,"totalDebt"))),
            ("Total Cash",        fmt_large(g(info,"totalCash"))),
            ("Free Cash Flow",    fmt_large(g(info,"freeCashflow"))),
        ]),
        ("GROWTH", [
            ("Revenue Growth YoY",   fmt_pct(g(info,"revenueGrowth"))),
            ("Earnings Growth YoY",  fmt_pct(g(info,"earningsGrowth"))),
            ("EPS Growth (Qtr)",     fmt_pct(g(info,"earningsQuarterlyGrowth"))),
            ("Book Value / Share",   safe(g(info,"bookValue"))),
            ("Revenue / Share",      safe(g(info,"revenuePerShare"))),
            ("Operating Cash Flow",  fmt_large(g(info,"operatingCashflow"))),
        ]),
        ("DIVIDENDS & OWNERSHIP", [
            ("Dividend Yield",        fmt_pct(g(info,"dividendYield"))),
            ("Dividend Rate",         safe(g(info,"dividendRate"))),
            ("Payout Ratio",          fmt_pct(g(info,"payoutRatio"))),
            ("Shares Outstanding",    fmt_large(g(info,"sharesOutstanding"))),
            ("Insider Ownership",     fmt_pct(g(info,"heldPercentInsiders"))),
            ("Institutional Own.",    fmt_pct(g(info,"heldPercentInstitutions"))),
        ]),
    ]
    cols_pairs = [(r1[0],r1[1]),(r2[0],r2[1]),(r3[0],r3[1]),(r4[0],r4[1])]
    for i, (group_title, rows) in enumerate(groups):
        col = [r1,r2,r3,r4][i//2][i%2]
        with col:
            st.markdown(f"""<div style="background:#111318;border:1px solid rgba(255,255,255,0.07);border-radius:13px;padding:18px;margin-bottom:14px;">
            <div style="font-family:'DM Mono',monospace;font-size:10px;letter-spacing:2px;color:#4ade80;text-transform:uppercase;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.05);">{group_title}</div>
            {"".join([ratio_row_html(l,v) for l,v in rows])}
            </div>""", unsafe_allow_html=True)

# ─── TAB 4: CHARTS ───────────────────────────────────────────────────────────
with tab4:
    ch1, ch2 = st.columns(2)

    def get_fin_series(df, keyword):
        if df is None or df.empty: return [], []
        row = next((r for r in df.index if keyword.lower() in str(r).lower()), None)
        if not row: return [], []
        cols = sorted(df.columns)[:4]
        return [str(c.year) for c in cols], [round(float(df.loc[row,c])/1e9,2) if pd.notna(df.loc[row,c]) else 0 for c in cols]

    with ch1:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:12px;font-weight:600;color:#555e72;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">Revenue Trend (Bn)</div>', unsafe_allow_html=True)
        rl, rv = get_fin_series(fin, "Total Revenue")
        if rl:
            fig = go.Figure(go.Bar(x=rl,y=rv,marker_color="rgba(96,165,250,0.8)",marker_line_width=0,
                                   text=[f"{v:.1f}B" for v in rv],textposition="outside",textfont=dict(color="#8b92a5",size=10)))
            fig.update_layout(**PLOT_LAYOUT, height=220)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with ch2:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:12px;font-weight:600;color:#555e72;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">EPS Trend</div>', unsafe_allow_html=True)
        nl, nv = get_fin_series(fin, "Net Income")
        if nl and shares:
            ev = [round(v*1e9/shares,2) for v in nv]
            fig = go.Figure(go.Scatter(x=nl,y=ev,mode="lines+markers",
                line=dict(color="#4ade80",width=2.5),
                marker=dict(color="#4ade80",size=8,line=dict(color="#0a0c10",width=2)),
                text=[f"{v:.2f}" for v in ev],textposition="top center",textfont=dict(color="#8b92a5",size=10)))
            fig.update_layout(**PLOT_LAYOUT, height=220)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    ch3, ch4 = st.columns(2)
    with ch3:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:12px;font-weight:600;color:#555e72;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">Margin Analysis</div>', unsafe_allow_html=True)
        m_vals = [(g(info,"grossMargins") or 0)*100,(g(info,"operatingMargins") or 0)*100,
                  (g(info,"profitMargins") or 0)*100,(g(info,"ebitdaMargins") or 0)*100]
        m_cols = ["rgba(74,222,128,0.85)" if v>=0 else "rgba(248,113,113,0.85)" for v in m_vals]
        fig = go.Figure(go.Bar(x=["Gross","Operating","Net","EBITDA"],y=[round(v,1) for v in m_vals],
            marker_color=m_cols,marker_line_width=0,
            text=[f"{v:.1f}%" for v in m_vals],textposition="outside",textfont=dict(color="#8b92a5",size=10)))
        fig.update_layout(**PLOT_LAYOUT, height=220,
            yaxis=dict(ticksuffix="%",gridcolor="rgba(255,255,255,0.04)",tickfont=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with ch4:
        st.markdown('<div style="font-family:Syne,sans-serif;font-size:12px;font-weight:600;color:#555e72;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">Analyst Recommendations</div>', unsafe_allow_html=True)
        rec_data = {"Strong Buy":0,"Buy":0,"Hold":0,"Sell":0,"Strong Sell":0}
        if recs is not None and not recs.empty:
            latest = recs.iloc[-1]
            for k2,l in [("strongBuy","Strong Buy"),("buy","Buy"),("hold","Hold"),("sell","Sell"),("strongSell","Strong Sell")]:
                if k2 in latest: rec_data[l] = int(latest[k2])
        if any(v>0 for v in rec_data.values()):
            fig = go.Figure(go.Pie(
                labels=list(rec_data.keys()), values=list(rec_data.values()),
                marker_colors=["rgba(74,222,128,0.9)","rgba(74,222,128,0.6)","rgba(251,191,36,0.7)","rgba(248,113,113,0.6)","rgba(248,113,113,0.9)"],
                hole=0.45, textfont=dict(color="#8b92a5",size=10,family="DM Mono"),
                hovertemplate="%{label}: %{value}<extra></extra>"
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                height=220,margin=dict(l=10,r=10,t=10,b=10),
                legend=dict(font=dict(size=10,color="#8b92a5"),bgcolor="rgba(0,0,0,0)",x=1))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        else:
            st.markdown('<div style="color:#555e72;font-family:DM Mono,monospace;font-size:12px;padding:40px 0;text-align:center;">No analyst data available</div>', unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#111318;border:1px solid rgba(255,255,255,0.07);border-radius:11px;padding:14px 18px;margin-top:28px;font-size:11px;color:#555e72;line-height:1.6;font-family:'DM Mono',monospace;">
⚠ DISCLAIMER — For educational purposes only. Data sourced via yfinance / Yahoo Finance. 
Buy/Sell signals are algorithmic estimates only and do NOT constitute financial advice. 
Always consult a qualified financial advisor before making investment decisions.
</div>
""", unsafe_allow_html=True)
