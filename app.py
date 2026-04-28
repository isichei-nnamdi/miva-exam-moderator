#!/usr/bin/env python3
"""
Miva Open University - Exam Score Moderator
============================================
Streamlit application for exam result analysis, integrity-based
score adjustment, and LMS gradebook moderation.

Directory layout:
    app.py
    assets/
        miva_logo.png   ← transparent Miva "M" logo

Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

# ── stdlib ─────────────────────────────────────────────────────────────────
import base64
import io
import os

# ── third-party ────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from scipy import stats


# ═══════════════════════════════════════════════════════════════════════════
#  BRAND PALETTE
# ═══════════════════════════════════════════════════════════════════════════
NAVY    = "#0D2B4E"
NAVY_L  = "#16407A"
RED     = "#D93B2B"
GOLD    = "#C4A07D"
WHITE   = "#FFFFFF"
BG      = "#EEF2F7"
MUTED   = "#8597AD"
SUCCESS = "#27AE60"
WARNING = "#E67E22"
DANGER  = "#C0392B"
INFO    = "#2471A3"

PALETTE = [RED, NAVY_L, GOLD, SUCCESS, WARNING, INFO, MUTED, DANGER]
# ── Grade constants ──────────────────────────────────────────────────────
GRADE_ORDER = ["A", "B", "C", "D", "E", "F"]
GRADE_COLORS = {
    "A": SUCCESS,   # green  – distinction
    "B": INFO,      # blue   – credit
    "C": GOLD,      # gold   – pass
    "D": WARNING,   # orange – borderline pass
    "E": "#E05A2B", # amber-red – marginal fail
    "F": DANGER,    # red    – fail
}
GRADE_VARIANTS = {   # maps to KPI card accent class
    "A": "s", "B": "i", "C": "g", "D": "w", "E": "d", "F": "r"
}

LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "miva_logo.png")


# ═══════════════════════════════════════════════════════════════════════════
#  LOGO (computed once - no caching needed; file is local & tiny)
# ═══════════════════════════════════════════════════════════════════════════
def _encode_logo(path: str) -> str:
    """Return transparent Miva logo as a base-64 PNG string."""
    try:
        img = Image.open(path).convert("RGBA")
        arr = np.array(img)
        # Strip near-black pixels (logo background)
        black = (arr[..., 0] < 40) & (arr[..., 1] < 40) & (arr[..., 2] < 40)
        arr[black, 3] = 0
        buf = io.BytesIO()
        Image.fromarray(arr).save(buf, "PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


LOGO_B64 = _encode_logo(LOGO_PATH)
LOGO_SRC = f"data:image/png;base64,{LOGO_B64}" if LOGO_B64 else ""


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG  ← must be the very first Streamlit call
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Miva Exam Moderator",
    page_icon=LOGO_SRC if LOGO_SRC else "🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
/* ── Reset ──────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {{
    background: {BG};
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
}}
[data-testid="stHeader"],
[data-testid="stToolbar"],
footer {{ display: none !important; }}
.block-container {{ padding-top: 0 !important; max-width: 1400px; }}

/* ── Top header bar ─────────────────────────────────────────────── */
.mhdr {{
    background: {NAVY};
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 2rem;
    border-radius: 0 0 16px 16px;
    border-bottom: 3px solid {RED};
    margin-bottom: 1.8rem;
    box-shadow: 0 4px 20px rgba(13,43,78,.22);
}}
.mhdr img {{ height: 50px; width: auto; }}
.mhdr-text {{ display: flex; flex-direction: column; }}
.mhdr-text h1 {{
    color: {WHITE}; font-size: 1.25rem; font-weight: 800;
    margin: 0; letter-spacing: .3px;
}}
.mhdr-text small {{
    color: {GOLD}; font-size: .76rem; opacity: .92;
}}
.mhdr-badge {{
    margin-left: auto;
    background: rgba(255,255,255,.1);
    color: {GOLD};
    border: 1px solid {GOLD}55;
    border-radius: 20px;
    padding: .25rem .85rem;
    font-size: .75rem;
    font-weight: 600;
    letter-spacing: .5px;
}}

/* ── Tabs ────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {WHITE};
    border-radius: 12px;
    padding: 5px;
    gap: 5px;
    box-shadow: 0 2px 12px rgba(13,43,78,.09);
    border: 1px solid rgba(13,43,78,.08);
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: {MUTED};
    border: none;
    border-radius: 9px;
    font-weight: 600;
    font-size: .9rem;
    padding: .58rem 1.6rem;
    transition: all .18s ease;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: {NAVY}; background: {BG}; }}
.stTabs [aria-selected="true"] {{
    background: {NAVY} !important;
    color: {WHITE} !important;
    box-shadow: 0 2px 8px rgba(13,43,78,.25);
}}
.stTabs [data-baseweb="tab-panel"] {{ padding: 1.5rem 0 0; }}

/* ── KPI Card ───────────────────────────────────────────────────── */
.kpi {{
    background: {WHITE};
    border-radius: 14px;
    padding: 1.15rem 1.45rem;
    box-shadow: 0 2px 14px rgba(13,43,78,.08);
    border-left: 4px solid {RED};
    position: relative;
    overflow: hidden;
}}
.kpi::after {{
    content: '';
    position: absolute;
    top: -20px; right: -20px;
    width: 80px; height: 80px;
    border-radius: 50%;
    background: currentColor;
    opacity: .03;
}}
.kpi.g {{ border-left-color: {GOLD}; }}
.kpi.s {{ border-left-color: {SUCCESS}; }}
.kpi.w {{ border-left-color: {WARNING}; }}
.kpi.d {{ border-left-color: {DANGER}; }}
.kpi.i {{ border-left-color: {INFO}; }}
.kpi.n {{ border-left-color: {NAVY_L}; }}
.kpi.r {{ border-left-color: {RED}; }}
.kl {{
    font-size: .7rem; font-weight: 700; color: {MUTED};
    text-transform: uppercase; letter-spacing: .85px; margin-bottom: .3rem;
}}
.kv {{
    font-size: 1.85rem; font-weight: 800;
    color: {NAVY}; line-height: 1.1;
}}
.ks {{ font-size: .72rem; color: {MUTED}; margin-top: .25rem; }}

/* ── Section header ─────────────────────────────────────────────── */
.sec {{
    font-size: 1rem; font-weight: 700; color: {NAVY};
    padding: .5rem 0 .5rem 1rem;
    border-left: 4px solid {RED};
    background: linear-gradient(90deg, rgba(13,43,78,.05) 0%, transparent 80%);
    border-radius: 0 6px 6px 0;
    margin: 1.6rem 0 1rem;
}}

/* ── Chart wrapper card ─────────────────────────────────────────── */
.chart-wrap {{
    background: {WHITE};
    border-radius: 14px;
    padding: 1rem 1.2rem 0.5rem;
    box-shadow: 0 2px 12px rgba(13,43,78,.07);
    border: 1px solid rgba(13,43,78,.05);
}}

/* ── File uploader ──────────────────────────────────────────────── */
[data-testid="stFileUploader"] {{
    border: 2px dashed {NAVY_L}44;
    border-radius: 12px;
    background: {WHITE};
    padding: .85rem;
    transition: border-color .2s;
}}
[data-testid="stFileUploader"]:hover {{ border-color: {RED}; }}

/* ── Buttons ────────────────────────────────────────────────────── */
.stButton > button {{
    background: {NAVY};
    color: {WHITE};
    border: none;
    border-radius: 9px;
    font-weight: 700;
    font-size: .87rem;
    padding: .55rem 1.5rem;
    transition: all .18s ease;
    cursor: pointer;
    letter-spacing: .2px;
}}
.stButton > button:hover {{
    background: {NAVY_L};
    transform: translateY(-2px);
    box-shadow: 0 5px 16px rgba(13,43,78,.25);
}}
.stButton > button:active {{ transform: translateY(0); }}

.stDownloadButton > button {{
    background: {RED} !important;
    color: {WHITE} !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    font-size: .87rem !important;
    padding: .55rem 1.5rem !important;
    transition: all .18s ease !important;
}}
.stDownloadButton > button:hover {{
    background: #B83020 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 16px rgba(217,59,43,.3) !important;
}}

/* ── Callout / info box ─────────────────────────────────────────── */
.callout {{
    background: {NAVY}0D;
    border: 1px solid {NAVY}22;
    border-radius: 10px;
    padding: .8rem 1.1rem;
    font-size: .84rem;
    color: {NAVY};
    line-height: 1.55;
}}
.callout-warn {{
    background: {WARNING}18;
    border: 1px solid {WARNING}55;
    border-radius: 10px;
    padding: .8rem 1.1rem;
    font-size: .84rem;
    color: #7a4e00;
}}
.callout-success {{
    background: {SUCCESS}15;
    border: 1px solid {SUCCESS}55;
    border-radius: 10px;
    padding: .8rem 1.1rem;
    font-size: .84rem;
    color: #1a5e35;
}}

/* ── Data editor ────────────────────────────────────────────────── */
[data-testid="stDataFrame"],
[data-testid="data-grid-canvas"] {{
    border-radius: 10px !important;
    overflow: hidden;
}}

/* ── Sliders ────────────────────────────────────────────────────── */
[data-testid="stSlider"] {{ padding: .3rem 0; }}

/* ── Selectbox / multiselect ────────────────────────────────────── */
[data-baseweb="tag"] {{
    background: {NAVY} !important;
    border-radius: 6px !important;
}}
[data-baseweb="tag"] span {{ color: {WHITE} !important; }}

/* ── Expander ───────────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    border: 1px solid rgba(13,43,78,.1) !important;
    border-radius: 10px !important;
    background: {WHITE};
}}

/* ── Scrollbar ──────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {MUTED}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {NAVY_L}; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  TOP HEADER
# ═══════════════════════════════════════════════════════════════════════════
logo_img_tag = f'<img src="{LOGO_SRC}" alt="Miva Logo" />' if LOGO_SRC else ""
st.markdown(f"""
<div class="mhdr">
  {logo_img_tag}
  <div class="mhdr-text">
    <h1>Exam Score Moderator</h1>
    <small>Academic Quality Assurance Portal</small>
  </div>
  <span class="mhdr-badge">MIVA OPEN UNIVERSITY</span>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def convert_string_columns_to_numeric(df: "pd.DataFrame") -> "pd.DataFrame":
    """Convert string columns with '-' as empty to numeric."""
    for col in df.columns:
        # Check if column is string-like (object, str, string)
        if df[col].dtype.name in ("object", "string", "str"):
            # Replace '-' and empty strings with NaN, then try to convert to numeric
            replaced = df[col].replace(["-", ""], pd.NA)
            converted = pd.to_numeric(replaced, errors="coerce")
            
            # Count how many values are NOT '-' or empty originally
            valid_original = (df[col] != "-") & (df[col] != "") & (df[col].notna())
            valid_count = valid_original.sum()
            
            # Count how many successfully converted
            converted_count = converted.notna().sum()
            
            # If most of the non-missing values are numeric, convert the column
            if valid_count > 0 and converted_count >= valid_count * 0.9:
                df[col] = converted
    return df


def read_upload(f) -> "pd.DataFrame | None":
    """Read a CSV or Excel uploaded file into a DataFrame."""
    try:
        if f.name.lower().endswith(".csv"):
            df = pd.read_csv(f)
        else:
            df = pd.read_excel(f)
        # Convert columns with '-' as empty values to numeric
        return convert_string_columns_to_numeric(df)
    except Exception as e:
        st.error(f"⚠️ Cannot read **{f.name}**: {e}")
        return None


def kpi(label: str, value: str, sub: str = "", v: str = ""):
    """Render a KPI card via HTML."""
    st.markdown(
        f'<div class="kpi {v}">'
        f'  <div class="kl">{label}</div>'
        f'  <div class="kv">{value}</div>'
        f'  {"<div class=ks>" + sub + "</div>" if sub else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


def sec(title: str):
    """Render a section header."""
    st.markdown(f'<div class="sec">{title}</div>', unsafe_allow_html=True)


def hex_to_rgba(hex_color: str, alpha_hex: str) -> str:
    """Convert hex color with alpha to rgba format for Plotly."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    alpha = int(alpha_hex, 16) / 255
    return f"rgba({r}, {g}, {b}, {alpha:.3f})"


def apply_chart_theme(fig: go.Figure, height: int = 370) -> go.Figure:
    """Apply consistent Miva chart theme."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Segoe UI, Inter, Arial, sans-serif",
        font_color=NAVY,
        margin=dict(l=10, r=10, t=42, b=10),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        title_font=dict(size=14, color=NAVY),
        xaxis=dict(gridcolor=hex_to_rgba(MUTED, "22"), zerolinecolor=hex_to_rgba(MUTED, "33")),
        yaxis=dict(gridcolor=hex_to_rgba(MUTED, "22"), zerolinecolor=hex_to_rgba(MUTED, "33")),
    )
    return fig


def show_chart(fig: go.Figure, height: int = 370):
    """Apply theme and render a Plotly chart."""
    fig = apply_chart_theme(fig, height)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def detect_score_col(df: pd.DataFrame) -> "str | None":
    """Return the primary score column name."""
    for c in ["score", "score_percentage"]:
        if c in df.columns:
            return c
    return None


def get_suspicious_mask(
    df: pd.DataFrame,
    integrity_thresh: int,
    exam_thresh: int,
    flag_is_risk: bool,
    flag_high: bool,
    flag_medium: bool,
) -> pd.Series:
    """Boolean mask of rows that are suspicious by current criteria.
    
    Flags students with:
    - integrity_score <= integrity_thresh AND exam_score >= exam_thresh
    OR (if checkboxes are enabled):
    - is_risk = True
    - risk_level = High/Medium
    """
    mask = pd.Series(False, index=df.index)
    
    # Primary filter: integrity_score <= threshold AND exam_score >= threshold
    if "integrity_score" in df.columns:
        integrity = pd.to_numeric(df["integrity_score"], errors="coerce").fillna(100)
        
        # Find exam score column
        exam_col = None
        for col in ["score", "score_percentage", "exam_score"]:
            if col in df.columns:
                exam_col = col
                break
        
        if exam_col:
            exam_scores = pd.to_numeric(df[exam_col], errors="coerce").fillna(0)
            mask |= (integrity <= integrity_thresh) & (exam_scores >= exam_thresh)
    
    # Additional flags
    if flag_is_risk and "is_risk" in df.columns:
        mask |= df["is_risk"].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
    
    risk_vals: list[str] = []
    if flag_high:   risk_vals.append("high")
    if flag_medium: risk_vals.append("medium")
    if risk_vals and "risk_level" in df.columns:
        mask |= df["risk_level"].astype(str).str.strip().str.lower().isin(risk_vals)
    
    return mask


def score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade.
    A: 70+, B: 60-69, C: 50-59, D: 45-49, E: 40-44, F: <40
    """
    if pd.isna(score):
        return "N/A"
    score = float(score)
    if score >= 70:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 45:
        return "D"
    elif score >= 40:
        return "E"
    else:
        return "F"


def normality_report(series: pd.Series) -> "dict | None":
    """Run appropriate normality test; return stats dict or None."""
    clean = pd.to_numeric(series, errors="coerce").dropna()
    n = len(clean)
    if n < 8:
        return None
    if n <= 5000:
        stat, p = stats.shapiro(clean)
        test_name = "Shapiro-Wilk"
    else:
        stat, p = stats.normaltest(clean)
        test_name = "D'Agostino-Pearson"
    return {
        "test": test_name, "stat": float(stat), "p": float(p),
        "skew": float(clean.skew()), "kurt": float(clean.kurtosis()),
        "mean": float(clean.mean()), "std": float(clean.std()),
        "min": float(clean.min()), "max": float(clean.max()), "n": n,
    }

def suggest_adjustment(rpt: dict) -> dict:
    """
    Estimate the optimal uniform mark shift to reduce skewness toward zero.

    Heuristic:  suggested = round(|skew| × σ × 0.45, nearest 0.5)
    Direction:  positive skew → add marks (pulls left tail up)
                negative skew → subtract marks (pulls right tail down)
    """
    skew = rpt["skew"]
    std  = rpt["std"]
    mean = rpt["mean"]
    mn   = rpt["min"]
    mx   = rpt["max"]

    raw       = abs(skew) * std * 0.45
    suggested = max(0.5, min(round(round(raw / 0.5) * 0.5, 1), 20.0))
    sign      = 1 if skew > 0 else -1
    direction = "add" if skew > 0 else "subtract"

    return {
        "direction":    direction,
        "sign":         sign,
        "suggested":    suggested,
        "proj_mean":    round(mean + sign * suggested, 2),
        "proj_skew_δ":  round(-skew * 0.60, 3),
    }

def safe_count(df: pd.DataFrame, col: str, vals: list) -> "int | None":
    if col not in df.columns:
        return None
    return int(df[col].astype(str).str.strip().str.lower().isin(vals).sum())


def add_kde_trace(fig: go.Figure, data: pd.Series, nbins: int = 30):
    """Overlay a KDE line on a histogram figure."""
    clean = data.dropna().values
    if len(clean) < 8:
        return
    kde = stats.gaussian_kde(clean)
    xr  = np.linspace(clean.min(), clean.max(), 300)
    sc  = len(clean) * (clean.max() - clean.min()) / nbins
    fig.add_trace(go.Scatter(
        x=xr, y=kde(xr) * sc,
        mode="lines", name="KDE",
        line=dict(color=NAVY, width=2.5, dash="dot"),
        hoverinfo="skip",
    ))

def grade_bar_chart(
    grade_series: "pd.Series",
    title: str,
    height: int = 380,
) -> "go.Figure":
    """
    Render a grade distribution bar chart with Miva-consistent
    colours and a fixed A→F x-axis order.

    Parameters
    ----------
    grade_series : pd.Series of letter grades ("A"…"F")
    title        : chart title string
    height       : figure height in pixels
    """
    counts = grade_series.value_counts()
    grades = [g for g in GRADE_ORDER if g in counts.index]
    values = [int(counts.get(g, 0)) for g in grades]
    colors = [GRADE_COLORS.get(g, MUTED) for g in grades]

    fig = go.Figure(go.Bar(
        x=grades,
        y=values,
        marker_color=colors,
        text=values,
        textposition="outside",
        width=0.55,
        hovertemplate="Grade %{x}<br>Students: %{y}<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Grade",
        yaxis_title="Number of Students",
        showlegend=False,
        yaxis=dict(range=[0, max(values) * 1.2 if values else 10]),
    )
    return apply_chart_theme(fig, height)

def _render_grade_comparison(
    grade_before: "pd.Series",
    grade_after:  "pd.Series",
    exam_fld: str,
    total_cols: list,
    mod_data: dict,
    mod_state_key: str,
):
    """Render grade KPI delta row + grouped before/after bar chart."""
    cnt_b = grade_before.value_counts()
    cnt_a = grade_after.value_counts()
    total_n = len(grade_after)

    # KPI row with delta indicators
    kpi_cols = st.columns(6)
    for col, letter in zip(kpi_cols, GRADE_ORDER):
        before_n = int(cnt_b.get(letter, 0))
        after_n  = int(cnt_a.get(letter, 0))
        pct      = f"{after_n / total_n * 100:.1f}%" if total_n else "—"
        delta    = after_n - before_n
        delta_str = f"{'↑' if delta > 0 else '↓' if delta < 0 else '='}{abs(delta)}"
        with col:
            kpi(f"Grade {letter}", f"{after_n:,}", f"{pct} · {delta_str} from before",
                GRADE_VARIANTS[letter])

    st.markdown("<br/>", unsafe_allow_html=True)

    grades_present = [
        g for g in GRADE_ORDER
        if g in cnt_b.index or g in cnt_a.index
    ]
    before_vals = [int(cnt_b.get(g, 0)) for g in grades_present]
    after_vals  = [int(cnt_a.get(g, 0)) for g in grades_present]

    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        x=grades_present, y=before_vals,
        name="Before Adjustment",
        marker_color=MUTED, opacity=0.78,
        text=before_vals, textposition="outside",
        hovertemplate="Grade %{x} – Before<br>%{y} students<extra></extra>",
    ))
    fig_cmp.add_trace(go.Bar(
        x=grades_present, y=after_vals,
        name="After Adjustment",
        marker_color=SUCCESS, opacity=0.88,
        text=after_vals, textposition="outside",
        hovertemplate="Grade %{x} – After<br>%{y} students<extra></extra>",
    ))
    fig_cmp.update_layout(
        title="Grade Distribution: Before vs After Adjustment",
        xaxis_title="Grade",
        yaxis_title="Number of Students",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(
            range=[0, max(max(before_vals), max(after_vals)) * 1.25]
            if (before_vals or after_vals) else [0, 10]
        ),
    )
    st.plotly_chart(
        apply_chart_theme(fig_cmp, 420),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════════
tab1, tab2 = st.tabs([
    "📊  Result Analysis & Adjustment",
    "⚖️  Result Moderation",
])


# ┌──────────────────────────────────────────────────────────────────────────┐
# │  TAB 1 - Result Analysis & Integrity-Based Score Adjustment             │
# └──────────────────────────────────────────────────────────────────────────┘
with tab1:

    # ── 1a. Upload ─────────────────────────────────────────────────────────
    sec("Upload Exam Portal Export")
    t1_file = st.file_uploader(
        "Drop or browse your exam portal file (CSV or Excel)",
        type=["csv", "xlsx", "xls"],
        key="t1_upload",
    )

    if t1_file is None:
        st.markdown(
            '<div class="callout">📁 Upload an exam portal file above to begin analysis. '
            "The file should contain columns such as <code>student_id</code>, <code>score</code>, "
            "<code>grade_status</code>, <code>integrity_score</code>, <code>is_risk</code>, "
            "and <code>risk_level</code>.</div>",
            unsafe_allow_html=True,
        )
    else:
        # Cache the original upload keyed by name+size to survive reruns
        t1_cache_key = f"_t1_{t1_file.name}_{t1_file.size}"
        if t1_cache_key not in st.session_state:
            raw = read_upload(t1_file)
            if raw is not None:
                raw.columns = [c.strip().lower().replace(" ", "_") for c in raw.columns]
                st.session_state[t1_cache_key] = raw.copy()

        df_orig = st.session_state.get(t1_cache_key)

        if df_orig is not None:
            df = df_orig.copy()
            SCORE = detect_score_col(df)

            # ─── 1b. KPI Dashboard ────────────────────────────────────────
            sec("Dashboard Overview")
            total = len(df)

            # Create mask for graded students (those with grade_status = "GRADED")
            graded_mask = pd.Series(True, index=df.index)
            if "grade_status" in df.columns:
                graded_mask = df["grade_status"].astype(str).str.strip().str.upper() == "GRADED"
            
            # Use only graded students for all metrics except "Total Students"
            df_graded = df[graded_mask]
            graded_count = graded_mask.sum()

            # Calculate passed/failed based on score >= 30 threshold (only graded students)
            if SCORE:
                score_numeric = pd.to_numeric(df_graded[SCORE], errors="coerce")
                passed = (score_numeric >= 30).sum()
                failed = (score_numeric < 30).sum()
            else:
                passed = None
                failed = None
            
            hr_count = graded_count # safe_count(df_graded, "grade_status",   ["GRADED"])
            flagged  = safe_count(df_graded, "is_risk",       ["true", "1", "yes"])
            ca_ok    = safe_count(df_graded, "ca_eligibility",["true", "1", "yes"])
            synced   = safe_count(df_graded, "lms_sync_status", ["synced", "true", "1"])

            avg_score = (
                round(float(pd.to_numeric(df_graded[SCORE], errors="coerce").mean()), 2)
                if SCORE else None
            )
            median_score = (
                round(float(pd.to_numeric(df_graded[SCORE], errors="coerce").median()), 2)
                if SCORE else None
            )

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                kpi("Total Students", f"{total:,}", "registered candidates", "n")
            with c2:
                kpi(
                    "Scored above 50%",
                    f"{passed:,}" if passed is not None else "-",
                    f"{passed / total * 100:.1f}% scored above 30" if passed else "",
                    "s",
                )
            with c3:
                kpi(
                    "Scored below 50%",
                    f"{failed:,}" if failed is not None else "-",
                    f"{failed / total * 100:.1f}% scored below 30" if failed else "",
                    "d",
                )
            with c4:
                kpi(
                    "Average Score",
                    f"{avg_score}%" if avg_score is not None else "-",
                    f"Median: {median_score}%" if median_score is not None else "",
                    "g",
                )

            st.markdown("<br/>", unsafe_allow_html=True)
            c5, c6, c7, c8 = st.columns(4)
            with c5:
                kpi(
                    "Total Graded Students",
                    f"{hr_count:,}" if hr_count is not None else "-",
                    "students with grades",
                    "d",
                )
            with c6:
                kpi(
                    "Flagged (is_risk)",
                    f"{flagged:,}" if flagged is not None else "-",
                    "integrity concerns",
                    "w",
                )
            with c7:
                kpi(
                    "CA Eligible",
                    f"{ca_ok:,}" if ca_ok is not None else "-",
                    "met CA threshold",
                    "s",
                )
            with c8:
                kpi(
                    "LMS Synced",
                    f"{synced:,}" if synced is not None else "-",
                    "records synced to LMS",
                    "i",
                )

            # ─── 1c. Distribution Charts ──────────────────────────────────
            sec("Score & Distribution Analysis")

            # Row 1
            r1c1, r1c2 = st.columns(2)

            with r1c1:
                st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                if SCORE:
                    scores = pd.to_numeric(df_graded[SCORE], errors="coerce").dropna()
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(
                        x=scores, nbinsx=30,
                        name="Score", marker_color=RED, opacity=0.82,
                    ))
                    add_kde_trace(fig, scores)
                    fig.update_layout(
                        title="Exam Score Distribution",
                        xaxis_title="Score (%)", yaxis_title="Count",
                        bargap=0.04,
                    )
                    show_chart(fig)
                else:
                    st.info("No `score` or `score_percentage` column found.")
                st.markdown("</div>", unsafe_allow_html=True)

            with r1c2:
                st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                if "grade_status" in df.columns:
                    gs = (
                        df["grade_status"].value_counts()
                        .reset_index()
                        .rename(columns={"grade_status": "Status", "count": "Count"})
                    )
                    if "Status" not in gs.columns:
                        gs.columns = ["Status", "Count"]
                    fig = px.bar(
                        gs, x="Status", y="Count",
                        color="Status",
                        color_discrete_sequence=PALETTE,
                        title="Grade Status Distribution",
                        text="Count",
                    )
                    fig.update_traces(textposition="outside")
                    fig.update_layout(showlegend=False)
                    show_chart(fig)
                else:
                    st.info("No `grade_status` column found.")
                st.markdown("</div>", unsafe_allow_html=True)

            # Row 2
            r2c1, r2c2 = st.columns(2)

            with r2c1:
                st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                if "risk_level" in df.columns:
                    rl = (
                        df["risk_level"].value_counts()
                        .reset_index()
                        .rename(columns={"risk_level": "Risk Level", "count": "Count"})
                    )
                    if "Risk Level" not in rl.columns:
                        rl.columns = ["Risk Level", "Count"]
                    clr_map = {
                        "high": DANGER, "medium": WARNING,
                        "low": SUCCESS, "none": MUTED,
                    }
                    colors = [
                        clr_map.get(str(r).lower(), NAVY_L)
                        for r in rl["Risk Level"]
                    ]
                    fig = go.Figure(go.Bar(
                        x=rl["Risk Level"], y=rl["Count"],
                        marker_color=colors,
                        text=rl["Count"], textposition="auto",
                    ))
                    fig.update_layout(
                        title="Risk Level Distribution",
                        xaxis_title="Risk Level", yaxis_title="Count",
                    )
                    show_chart(fig)
                else:
                    st.info("No `risk_level` column found.")
                st.markdown("</div>", unsafe_allow_html=True)

            with r2c2:
                st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                if "integrity_score" in df_graded.columns:
                    iv = pd.to_numeric(df_graded["integrity_score"], errors="coerce").dropna()
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(
                        x=iv, nbinsx=25,
                        name="Integrity Score", marker_color=GOLD, opacity=0.85,
                    ))
                    add_kde_trace(fig, iv, 25)
                    fig.update_layout(
                        title="Integrity Score Distribution",
                        xaxis_title="Integrity Score", yaxis_title="Count",
                    )
                    show_chart(fig)
                else:
                    st.info("No `integrity_score` column found.")
                st.markdown("</div>", unsafe_allow_html=True)

            # Row 3
            r3c1, r3c2 = st.columns(2)

            with r3c1:
                st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                if "programme_intake" in df.columns:
                    pi = (
                        df["programme_intake"].value_counts()
                        .nlargest(12)
                        .reset_index()
                        .rename(columns={"programme_intake": "Intake", "count": "Count"})
                    )
                    if "Intake" not in pi.columns:
                        pi.columns = ["Intake", "Count"]
                    fig = px.bar(
                        pi, x="Intake", y="Count",
                        color="Intake",
                        color_discrete_sequence=PALETTE,
                        title="Students by Programme Intake",
                        text="Count",
                    )
                    fig.update_layout(showlegend=False, xaxis_tickangle=-35)
                    show_chart(fig)
                elif "level" in df.columns:
                    lv = (
                        df["level"].value_counts()
                        .reset_index()
                        .rename(columns={"level": "Level", "count": "Count"})
                    )
                    if "Level" not in lv.columns:
                        lv.columns = ["Level", "Count"]
                    fig = px.pie(
                        lv, names="Level", values="Count",
                        color_discrete_sequence=PALETTE,
                        title="Students by Level", hole=0.42,
                    )
                    show_chart(fig)
                else:
                    st.info("No `programme_intake` or `level` column found.")
                st.markdown("</div>", unsafe_allow_html=True)

            with r3c2:
                st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                if SCORE and "grade_status" in df.columns:
                    fig = px.box(
                        df, x="grade_status", y=SCORE,
                        color="grade_status",
                        color_discrete_sequence=PALETTE,
                        title="Score Distribution by Grade Status",
                        labels={SCORE: "Score (%)", "grade_status": "Grade Status"},
                        points="outliers",
                    )
                    fig.update_layout(showlegend=False)
                    show_chart(fig)
                else:
                    st.info("Insufficient columns for grade box-plot.")
                st.markdown("</div>", unsafe_allow_html=True)

            # ─── 1d. Score Adjustment ─────────────────────────────────────
            sec("Score Adjustment - Integrity & Risk Criteria")
            st.markdown(
                '<div class="callout">Configure the criteria below to identify suspicious '
                "candidates. You can then apply a <strong>bulk deduction</strong> to all "
                "flagged candidates at once, or fine-tune individual deductions in the "
                "editable table. Download the adjusted sheet when ready.</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<br/>", unsafe_allow_html=True)

            adj_col1, adj_col2, adj_col3 = st.columns([2, 1, 1])
            with adj_col1:
                integrity_thresh = st.slider(
                    "🔍 Integrity Score threshold",
                    min_value=0, max_value=100, value=70, step=1,
                    help="Flag students with integrity_score <= this value.",
                )
                chk1, chk2, chk3 = st.columns(3)
                with chk1:
                    use_is_risk  = st.checkbox("Flag `is_risk = True`", value=True)
                with chk2:
                    use_high_risk = st.checkbox("Flag `risk_level = High`", value=True)
                with chk3:
                    use_med_risk  = st.checkbox("Flag `risk_level = Medium`", value=False)

            with adj_col2:
                exam_thresh = st.slider(
                    "📊 Exam Score threshold",
                    min_value=0, max_value=100, value=40, step=1,
                    help="Only flag students with exam_score >= this value.",
                )

            with adj_col3:
                st.markdown("<br/>", unsafe_allow_html=True)
                bulk_deduction = st.number_input(
                    "Bulk deduction (marks)", min_value=0.0, max_value=100.0,
                    value=5.0, step=0.5,
                    help="Applied to all flagged students unless overridden individually.",
                )

            susp_mask = get_suspicious_mask(
                df, integrity_thresh, exam_thresh, use_is_risk, use_high_risk, use_med_risk
            )
            n_flagged = int(susp_mask.sum())

            if not SCORE:
                st.markdown(
                    '<div class="callout-warn">⚠️ No <code>score</code> or '
                    "<code>score_percentage</code> column found - adjustments unavailable.</div>",
                    unsafe_allow_html=True,
                )
            else:
                flag_col, _, dl_col = st.columns([2, 1, 1])
                with flag_col:
                    st.metric(
                        "Flagged Candidates",
                        f"{n_flagged:,}",
                        f"{n_flagged / total * 100:.1f}% of cohort" if total else None,
                    )

                if n_flagged == 0:
                    st.markdown(
                        '<div class="callout">✅ No candidates are flagged under the '
                        "current criteria. Adjust the threshold or enable additional checks.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    # Build editable flagged table
                    display_cols = [
                        c for c in [
                            "student_id", "matric_number", "first_name", "last_name",
                            "course", "level", "integrity_score", "is_risk",
                            "risk_level", SCORE,
                        ]
                        if c in df.columns
                    ]
                    susp_df = df.loc[susp_mask, display_cols].copy().reset_index(drop=True)
                    susp_df.insert(len(susp_df.columns), "deduction_marks", 0.0)

                    sec("Flagged Candidates - Individual Deduction Override")
                    st.caption(
                        "Edit the `deduction_marks` column for per-student control. "
                        "Leave **0** to apply the bulk deduction value."
                    )

                    edited_df = st.data_editor(
                        susp_df,
                        column_config={
                            "deduction_marks": st.column_config.NumberColumn(
                                "Deduction (marks)",
                                min_value=0.0, max_value=100.0, step=0.5,
                                help="0 = use bulk; any positive value overrides bulk for this row.",
                            ),
                        },
                        hide_index=True,
                        use_container_width=True,
                        key="t1_adj_editor",
                    )

                    apply_btn = st.button("⚡ Apply Adjustments", type="primary", key="t1_apply_btn")

                    t1_adj_key = f"_adj_{t1_cache_key}"

                    if apply_btn:
                        df_adj = df_orig.copy()

                        # Identify join column
                        id_col = next(
                            (c for c in ["student_id", "matric_number"] if c in df_adj.columns),
                            None,
                        )

                        if id_col:
                            for _, row in edited_df.iterrows():
                                ded = (
                                    float(row["deduction_marks"])
                                    if float(row["deduction_marks"]) > 0
                                    else bulk_deduction
                                )
                                m = df_adj[id_col] == row[id_col]
                                df_adj.loc[m, SCORE] = (
                                    pd.to_numeric(df_adj.loc[m, SCORE], errors="coerce") - ded
                                ).clip(lower=0)
                        else:
                            # No ID column - apply bulk to all flagged rows
                            susp_idx = df_orig.index[susp_mask]
                            df_adj.loc[susp_idx, SCORE] = (
                                pd.to_numeric(df_adj.loc[susp_idx, SCORE], errors="coerce")
                                - bulk_deduction
                            ).clip(lower=0)

                        st.session_state[t1_adj_key] = df_adj
                        st.markdown(
                            f'<div class="callout-success">✅ Adjustments applied to '
                            f"<strong>{n_flagged}</strong> candidate(s). "
                            "Download the adjusted file below.</div>",
                            unsafe_allow_html=True,
                        )

                    # ── Show results if adjustment has been applied ────────
                    if t1_adj_key in st.session_state:
                        df_adj = st.session_state[t1_adj_key]

                        sec("Before vs After: Score Distribution")
                        before_scores = pd.to_numeric(df_orig[SCORE], errors="coerce")
                        after_scores  = pd.to_numeric(df_adj[SCORE],  errors="coerce")

                        fig_ba = go.Figure()
                        fig_ba.add_trace(go.Histogram(
                            x=before_scores.dropna(), nbinsx=30,
                            name="Before Adjustment",
                            marker_color=MUTED, opacity=0.65,
                        ))
                        fig_ba.add_trace(go.Histogram(
                            x=after_scores.dropna(), nbinsx=30,
                            name="After Adjustment",
                            marker_color=RED, opacity=0.78,
                        ))
                        fig_ba.update_layout(
                            barmode="overlay",
                            title="Score Distribution: Before vs After Adjustment",
                            xaxis_title="Score (%)", yaxis_title="Count",
                        )
                        show_chart(fig_ba, 340)

                        # Summary stats comparison
                        sc1, sc2, sc3, sc4 = st.columns(4)
                        with sc1:
                            kpi("Mean (Before)", f"{before_scores.mean():.2f}%", "", "n")
                        with sc2:
                            kpi("Mean (After)",  f"{after_scores.mean():.2f}%", "", "r")
                        with sc3:
                            kpi("Std Dev (Before)", f"{before_scores.std():.2f}", "", "n")
                        with sc4:
                            kpi("Std Dev (After)",  f"{after_scores.std():.2f}",  "", "r")

                        st.markdown("<br/>", unsafe_allow_html=True)
                        st.download_button(
                            label="⬇️  Download Adjusted Score Sheet",
                            data=to_csv_bytes(df_adj),
                            file_name="adjusted_exam_scores.csv",
                            mime="text/csv",
                            key="t1_download_btn",
                        )

            # Raw data expander
            st.markdown("<br/>", unsafe_allow_html=True)
            with st.expander("📋 Raw Data Preview (first 100 rows)"):
                st.dataframe(df.head(100), use_container_width=True, hide_index=True)
                st.caption(f"Total rows: {len(df):,} · Columns: {len(df.columns)}")


# ┌──────────────────────────────────────────────────────────────────────────┐
# │  TAB 2 - Result Moderation (LMS Gradebook ↔ Portal Sheet)              │
# └──────────────────────────────────────────────────────────────────────────┘
with tab2:

    # ── 2a. Upload both files ───────────────────────────────────────────────
    sec("Upload Files")
    u1, u2 = st.columns(2)
    with u1:
        lms_file = st.file_uploader(
            "📘 LMS Gradebook (source of truth for component scores)",
            type=["csv", "xlsx", "xls"], key="t2_lms",
        )
    with u2:
        portal_mod_file = st.file_uploader(
            "📗 Exam Portal Sheet (adjusted or raw exam scores)",
            type=["csv", "xlsx", "xls"], key="t2_portal",
        )

    if lms_file is None or portal_mod_file is None:
        st.markdown(
            '<div class="callout">📁 Upload <strong>both</strong> files above to begin moderation. '
            "The <strong>LMS Gradebook</strong> contains all score components (CA, assignments, "
            "etc.). The <strong>Exam Portal Sheet</strong> provides the definitive exam scores "
            "(raw or adjusted) that will replace the exam column in the gradebook.</div>",
            unsafe_allow_html=True,
        )
    else:
        # Cache each file
        lms_ck   = f"_lms_{lms_file.name}_{lms_file.size}"
        port_ck  = f"_pt_{portal_mod_file.name}_{portal_mod_file.size}"

        if lms_ck not in st.session_state:
            raw_lms = read_upload(lms_file)
            if raw_lms is not None:
                raw_lms.columns = [c.strip() for c in raw_lms.columns]
                st.session_state[lms_ck] = raw_lms

        if port_ck not in st.session_state:
            raw_port = read_upload(portal_mod_file)
            if raw_port is not None:
                raw_port.columns = [c.strip() for c in raw_port.columns]
                st.session_state[port_ck] = raw_port

        df_lms  = st.session_state.get(lms_ck)
        df_port = st.session_state.get(port_ck)

        if df_lms is None or df_port is None:
            st.stop()

        # Previews
        pv1, pv2 = st.columns(2)
        with pv1:
            with st.expander("👁 LMS Gradebook preview"):
                st.dataframe(df_lms.head(20), use_container_width=True, hide_index=True)
                st.caption(f"{len(df_lms):,} rows · {len(df_lms.columns)} columns")
        with pv2:
            with st.expander("👁 Exam Portal Sheet preview"):
                st.dataframe(df_port.head(20), use_container_width=True, hide_index=True)
                st.caption(f"{len(df_port):,} rows · {len(df_port.columns)} columns")

        # ── 2b. Field configuration ─────────────────────────────────────────
        sec("Field Configuration")
        st.markdown(
            '<div class="callout">'
            "<strong>Step 1</strong> - Select the component columns (CA, quiz, assignment …) "
            "whose values will be <strong>summed</strong> alongside the exam score. "
            "<strong>Step 2</strong> - Select which gradebook column holds the exam score to be "
            "<em>replaced</em> by the portal values. "
            "<strong>Step 3</strong> - Select the corresponding score column from the portal "
            "sheet. <strong>Step 4</strong> - Set the student ID keys so records can be matched "
            "between files.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<br/>", unsafe_allow_html=True)

        # Only offer numeric columns for aggregation / exam field
        num_lms = [
            c for c in df_lms.columns
            if pd.api.types.is_numeric_dtype(df_lms[c])
        ]

        if not num_lms:
            st.error("⚠️ No numeric columns found in the LMS Gradebook.")
        else:
            fc1, fc2, fc3 = st.columns(3)

            with fc1:
                agg_fields = st.multiselect(
                    "① Columns to SUM (CA, assignments, quizzes …)",
                    options=num_lms,
                    help="All selected columns plus the (replaced) exam column are summed.",
                )
            with fc2:
                exam_field = st.selectbox(
                    "② Exam score column to REPLACE",
                    options=["- select -"] + num_lms,
                    help="Values in this column will be replaced with portal scores before summing.",
                )
            with fc3:
                portal_score_field = st.selectbox(
                    "③ Portal score column (source)",
                    options=["- select -"] + list(df_port.columns),
                    help="This column from the portal sheet supplies the replacement exam scores.",
                )

            sec("Student Record Matching Keys")
            mk1, mk2 = st.columns(2)
            with mk1:
                lms_id_col = st.selectbox(
                    "LMS student identifier column",
                    options=["- select -"] + list(df_lms.columns),
                )
            with mk2:
                port_id_col = st.selectbox(
                    "Portal student identifier column",
                    options=["- select -"] + list(df_port.columns),
                )

            cfg_complete = (
                len(agg_fields) > 0
                and exam_field not in ("", "- select -")
                and portal_score_field not in ("", "- select -")
                and lms_id_col not in ("", "- select -")
                and port_id_col not in ("", "- select -")
            )

            if not cfg_complete:
                st.markdown(
                    '<div class="callout">⚙️ Complete all four field selections above, '
                    "then click <strong>Run Moderation</strong>.</div>",
                    unsafe_allow_html=True,
                )
            else:
                run_btn = st.button("🚀 Run Moderation", type="primary", key="t2_run_btn")
                mod_state_key = f"_mod_{lms_ck}_{port_ck}"

                # ── 2c. Moderation logic ──────────────────────────────────────
                if run_btn:
                    # Filter portal data to only include GRADED records
                    df_port_graded = df_port.copy()
                    if "grade_status" in df_port_graded.columns:
                        df_port_graded = df_port_graded[
                            df_port_graded["grade_status"].astype(str).str.strip().str.upper() == "GRADED"
                        ]
                    
                    df_mod = df_lms.copy()

                    # Build portal score lookup (by portal ID → score)
                    # Drop duplicates in portal ID to avoid reindexing error
                    score_lookup = (
                        df_port_graded.drop_duplicates(subset=[port_id_col], keep='first')
                        .set_index(port_id_col)[portal_score_field]
                        .apply(pd.to_numeric, errors="coerce")
                    )

                    # Replace exam column with portal scores
                    replaced_exam = df_mod[lms_id_col].map(score_lookup)
                    
                    # Only keep records that were successfully matched (grade_status = GRADED in portal)
                    matched_mask = replaced_exam.notna()
                    df_mod = df_mod[matched_mask].copy()
                    replaced_exam = replaced_exam[matched_mask]
                    
                    # Update the exam field with portal scores
                    df_mod[exam_field] = replaced_exam

                    matched   = matched_mask.sum()
                    unmatched = (~matched_mask).sum()

                    # Compute total: sum of agg_fields ∪ exam_field (deduped)
                    total_cols = list(dict.fromkeys(agg_fields + [exam_field]))
                    df_mod["_total_score"] = df_mod[total_cols].apply(
                        lambda r: pd.to_numeric(r, errors="coerce").sum(), axis=1
                    )

                    st.session_state[mod_state_key] = {
                        "df":         df_mod,
                        "original_df": df_mod.copy(),
                        "agg_fields": agg_fields,
                        "exam_field": exam_field,
                        "total_cols": total_cols,
                        "matched":    int(matched),
                        "unmatched":  int(unmatched),
                    }

                if mod_state_key in st.session_state:
                    mod_data   = st.session_state[mod_state_key]
                    df_mod     = mod_data["df"]
                    total_cols = mod_data["total_cols"]
                    exam_fld   = mod_data["exam_field"]

                    # Match summary
                    st.markdown(
                        f'<div class="callout-success">✅ Moderation complete - '
                        f"<strong>{mod_data['matched']:,}</strong> matched records from GRADED portal entries updated. "
                        f"({mod_data['unmatched']:,} non-matching records excluded from analysis)</div>",
                        unsafe_allow_html=True,
                    )

                    # ── 2d. Grade Distribution (Pre-Adjustment) ───────────────
                    sec("Grade Distribution (Pre-Adjustment)")

                    grade_series_pre = (
                        pd.to_numeric(df_mod["_total_score"], errors="coerce")
                        .apply(score_to_grade)
                    )
                    grade_counts_pre = grade_series_pre.value_counts()
                    total_graded     = len(grade_series_pre)

                    # KPI row – one card per grade
                    grade_kpi_cols = st.columns(6)
                    for col, letter in zip(grade_kpi_cols, GRADE_ORDER):
                        cnt = int(grade_counts_pre.get(letter, 0))
                        pct = f"{cnt / total_graded * 100:.1f}%" if total_graded else "-"
                        with col:
                            kpi(f"Grade {letter}", f"{cnt:,}", pct,
                                GRADE_VARIANTS[letter])

                    st.markdown("<br/>", unsafe_allow_html=True)
                    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                    fig_grade_pre = grade_bar_chart(
                        grade_series_pre,
                        "Exam Score Grade Distribution (Before Global Adjustment)",
                    )
                    st.plotly_chart(
                        fig_grade_pre,
                        use_container_width=True,
                        config={"displayModeBar": False},
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                    # ── 2d. Distribution & Normality ──────────────────────────
                    sec("Total Score Distribution & Normality Analysis")
                    dist_l, dist_r = st.columns([3, 1])

                    total_series = pd.to_numeric(df_mod["_total_score"], errors="coerce")

                    with dist_l:
                        # Histogram + KDE
                        fig_dist = go.Figure()
                        fig_dist.add_trace(go.Histogram(
                            x=total_series.dropna(), nbinsx=30,
                            marker_color=RED, opacity=0.82, name="Total Score",
                        ))
                        add_kde_trace(fig_dist, total_series)
                        fig_dist.update_layout(
                            title="Total Score Distribution (Post-Moderation)",
                            xaxis_title="Total Score", yaxis_title="Count",
                        )
                        show_chart(fig_dist)

                        # Q-Q plot
                        if total_series.dropna().count() > 8:
                            qq = stats.probplot(total_series.dropna().values, dist="norm")
                            fig_qq = go.Figure()
                            fig_qq.add_trace(go.Scatter(
                                x=qq[0][0], y=qq[0][1], mode="markers",
                                name="Observations",
                                marker=dict(color=RED, size=5, opacity=0.7),
                            ))
                            fig_qq.add_trace(go.Scatter(
                                x=qq[0][0],
                                y=qq[1][0] * np.array(qq[0][0]) + qq[1][1],
                                mode="lines", name="Normal Reference Line",
                                line=dict(color=NAVY, width=2),
                            ))
                            fig_qq.update_layout(
                                title="Q-Q Plot (Normality Check)",
                                xaxis_title="Theoretical Quantiles",
                                yaxis_title="Sample Quantiles",
                            )
                            show_chart(fig_qq, 320)

                    with dist_r:
                        rpt = normality_report(total_series)
                        if rpt:
                            is_norm  = rpt["p"] > 0.05
                            skew_dir = "Right-skewed (+)" if rpt["skew"] > 0 else "Left-skewed (−)"
                            kurt_lbl = "Leptokurtic" if rpt["kurt"] > 0 else "Platykurtic"

                            if rpt["skew"] > 0.5:
                                tip = "⚠️ Right skew: scores cluster low. Consider <strong>adding marks</strong>."
                            elif rpt["skew"] < -0.5:
                                tip = "⚠️ Left skew: scores cluster high. Consider <strong>deducting marks</strong>."
                            else:
                                tip = "✅ Distribution is reasonably symmetric."

                            st.markdown(f"""
<div class="kpi {'s' if is_norm else 'd'}">
  <div class="kl">Normality ({rpt['test']})</div>
  <div class="kv">{'Normal ✓' if is_norm else 'Non-Normal ✗'}</div>
  <div class="ks">p = {rpt['p']:.4f} &nbsp;|&nbsp; n = {rpt['n']:,}</div>
</div><br/>
<div class="kpi g">
  <div class="kl">Skewness</div>
  <div class="kv">{rpt['skew']:.3f}</div>
  <div class="ks">{skew_dir}</div>
</div><br/>
<div class="kpi w">
  <div class="kl">Excess Kurtosis</div>
  <div class="kv">{rpt['kurt']:.3f}</div>
  <div class="ks">{kurt_lbl}</div>
</div><br/>
<div class="kpi n">
  <div class="kl">Mean &nbsp;|&nbsp; Std Dev</div>
  <div class="kv">{rpt['mean']:.2f}</div>
  <div class="ks">σ = {rpt['std']:.2f}</div>
</div><br/>
<div class="kpi i">
  <div class="kl">Range</div>
  <div class="kv">{rpt['min']:.1f} - {rpt['max']:.1f}</div>
  <div class="ks">min - max total score</div>
</div>
""", unsafe_allow_html=True)
                            st.markdown("<br/>", unsafe_allow_html=True)
                            st.markdown(
                                f'<div class="callout">{tip}</div>',
                                unsafe_allow_html=True,
                            )

                    # ── 2e. Global Score Adjustment ────────────────────────────
                    sec(f"Global Score Adjustment (modifying `{exam_fld}`)")
                    st.markdown(
                        '<div class="callout">Two adjustment modes are available. '
                        "<strong>Uniform shift</strong> adds or subtracts a fixed number of marks "
                        "from every student's exam score. "
                        "<strong>Band-based adjustment</strong> lets you apply different deltas to "
                        "different score ranges — useful for targeted normalisation. "
                        "Only the exam score column is modified; the total is recalculated "
                        "automatically after every application.</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("<br/>", unsafe_allow_html=True)

                    # ── Statistical recommendation panel ───────────────────────
                    rpt_pre = normality_report(df_mod["_total_score"])
                    if rpt_pre:
                        sug = suggest_adjustment(rpt_pre)
                        is_norm_pre = rpt_pre["p"] > 0.05

                        if abs(rpt_pre["skew"]) < 0.3:
                            rec_html = (
                                '<div class="callout-success">'
                                "📐 <strong>Distribution looks symmetric</strong> — skewness = "
                                f"<strong>{rpt_pre['skew']:.3f}</strong>. "
                                "No adjustment is strictly necessary, but fine-tuning is still available below."
                                "</div>"
                            )
                        else:
                            arrow = "➕" if sug["direction"] == "add" else "➖"
                            rec_html = (
                                f'<div class="{"callout-warn" if not is_norm_pre else "callout"}">'
                                f"📐 <strong>Statistical recommendation:</strong> "
                                f"The distribution is <strong>{'right' if rpt_pre['skew'] > 0 else 'left'}-skewed</strong> "
                                f"(skewness = {rpt_pre['skew']:.3f}, σ = {rpt_pre['std']:.2f}). "
                                f"Suggest <strong>{arrow} {sug['suggested']} marks</strong> uniformly "
                                f"to all exam scores (projected mean: <strong>{sug['proj_mean']}</strong>, "
                                f"estimated skew reduction: ~{abs(sug['proj_skew_δ']):.2f}). "
                                f"Use the controls below to apply or override this suggestion."
                                "</div>"
                            )
                        st.markdown(rec_html, unsafe_allow_html=True)

                        # Recommendation KPIs
                        st.markdown("<br/>", unsafe_allow_html=True)
                        rk1, rk2, rk3, rk4, rk5 = st.columns(5)
                        with rk1:
                            kpi("Current Mean",    f"{rpt_pre['mean']:.2f}",  "total score", "n")
                        with rk2:
                            kpi("Std Deviation",   f"{rpt_pre['std']:.2f}",   "", "i")
                        with rk3:
                            kpi("Skewness",        f"{rpt_pre['skew']:.3f}",
                                "right(+) / left(−)", "w" if abs(rpt_pre["skew"]) > 0.5 else "s")
                        with rk4:
                            kpi("Suggested Shift",
                                f"{'+ ' if sug['direction'] == 'add' else '− '}{sug['suggested']}",
                                sug["direction"] + " marks", "g")
                        with rk5:
                            kpi("Projected Mean",  f"{sug['proj_mean']:.2f}",
                                "after suggestion applied", "n")
                    else:
                        sug = {"direction": "add", "sign": 1, "suggested": 2.0}

                    st.markdown("<br/>", unsafe_allow_html=True)

                    # ── Mode selector ──────────────────────────────────────────
                    adj_mode = st.radio(
                        "Adjustment mode",
                        ["📏 Uniform shift (all students)", "🎯 Band-based (by score range)"],
                        horizontal=True,
                        key="t2_adj_mode",
                    )

                    # ══════════════════════════════════════════════════════════
                    #  MODE A – Uniform shift
                    # ══════════════════════════════════════════════════════════
                    if "Uniform" in adj_mode:
                        ua1, ua2, ua3 = st.columns([1, 1, 1])
                        with ua1:
                            u_dir = st.radio(
                                "Direction",
                                ["➕ Add marks", "➖ Deduct marks"],
                                index=0 if sug["direction"] == "add" else 1,
                                horizontal=True,
                                key="t2_u_dir",
                            )
                        with ua2:
                            u_amt = st.number_input(
                                "Amount (marks)",
                                min_value=0.0, max_value=50.0,
                                value=float(sug["suggested"]),
                                step=0.5,
                                key="t2_u_amt",
                            )
                        with ua3:
                            st.markdown("<br/>", unsafe_allow_html=True)
                            do_uniform = st.button(
                                "⚡ Apply Uniform Shift",
                                key="t2_apply_uniform",
                            )

                        if do_uniform and u_amt > 0:
                            sign_u = 1 if "Add" in u_dir else -1
                            df_upd = df_mod.copy()
                            df_upd[exam_fld] = (
                                pd.to_numeric(df_upd[exam_fld], errors="coerce")
                                + sign_u * u_amt
                            ).clip(lower=0)
                            df_upd["_total_score"] = df_upd[total_cols].apply(
                                lambda r: pd.to_numeric(r, errors="coerce").sum(), axis=1
                            )
                            mod_data["df"] = df_upd
                            st.session_state[mod_state_key] = mod_data
                            df_mod = df_upd

                            # ── Distribution comparison ────────────────────────
                            original_df = mod_data.get("original_df", df_upd)
                            bef_ts = pd.to_numeric(original_df["_total_score"], errors="coerce").dropna()
                            aft_ts = pd.to_numeric(df_upd["_total_score"],     errors="coerce").dropna()

                            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                            cmp_fig = go.Figure()
                            cmp_fig.add_trace(go.Histogram(
                                x=bef_ts, nbinsx=30, name="Before",
                                marker_color=MUTED, opacity=0.65,
                            ))
                            cmp_fig.add_trace(go.Histogram(
                                x=aft_ts, nbinsx=30, name="After",
                                marker_color=RED, opacity=0.78,
                            ))
                            cmp_fig.update_layout(
                                barmode="overlay",
                                title="Total Score Distribution: Before vs After Uniform Shift",
                                xaxis_title="Total Score", yaxis_title="Count",
                            )
                            st.plotly_chart(
                                apply_chart_theme(cmp_fig, 340),
                                use_container_width=True,
                                config={"displayModeBar": False},
                            )
                            st.markdown("</div>", unsafe_allow_html=True)

                            rpt_after = normality_report(df_upd["_total_score"])
                            if rpt_after:
                                is_n_after = rpt_after["p"] > 0.05
                                st.markdown(
                                    f'<div class="{"callout-success" if is_n_after else "callout-warn"}">'
                                    f"After shift: mean = <strong>{rpt_after['mean']:.2f}</strong> · "
                                    f"skewness = <strong>{rpt_after['skew']:.3f}</strong> · "
                                    f"p = <strong>{rpt_after['p']:.4f}</strong> "
                                    f"({'Normal ✓' if is_n_after else 'Non-Normal ✗'})"
                                    f"</div>",
                                    unsafe_allow_html=True,
                                )

                            # ── Grade comparison ───────────────────────────────
                            st.markdown("<br/>", unsafe_allow_html=True)
                            sec("Grade Distribution: Before vs After Uniform Shift")
                            grade_before = pd.to_numeric(original_df["_total_score"], errors="coerce").apply(score_to_grade)
                            grade_after  = pd.to_numeric(df_upd["_total_score"],      errors="coerce").apply(score_to_grade)
                            _render_grade_comparison(grade_before, grade_after, exam_fld, total_cols, mod_data, mod_state_key)

                    # ══════════════════════════════════════════════════════════
                    #  MODE B – Band-based adjustment
                    # ══════════════════════════════════════════════════════════
                    else:
                        total_min = float(pd.to_numeric(df_mod["_total_score"], errors="coerce").min())
                        total_max = float(pd.to_numeric(df_mod["_total_score"], errors="coerce").max())

                        st.markdown(
                            '<div class="callout">'
                            f"Total scores range from <strong>{total_min:.1f}</strong> to "
                            f"<strong>{total_max:.1f}</strong>. "
                            "Define up to <strong>5 score bands</strong> and assign a separate "
                            "mark delta to each. Bands are applied to the exam column and the "
                            "total is recalculated. Overlapping bands are applied in order — "
                            "ensure bands are mutually exclusive for predictable results."
                            "</div>",
                            unsafe_allow_html=True,
                        )
                        st.markdown("<br/>", unsafe_allow_html=True)

                        n_bands = st.slider(
                            "Number of score bands", min_value=1, max_value=5,
                            value=3, step=1, key="t2_n_bands",
                        )

                        band_defs = []
                        hdr = st.columns([2, 2, 2, 2, 2])
                        hdr[0].markdown("**Band**")
                        hdr[1].markdown("**Lower bound (≥)**")
                        hdr[2].markdown("**Upper bound (<)**")
                        hdr[3].markdown("**Direction**")
                        hdr[4].markdown("**Marks**")

                        default_step = (total_max - total_min) / max(n_bands, 1)
                        for i in range(n_bands):
                            lo_def = round(total_min + i * default_step, 1)
                            hi_def = round(total_min + (i + 1) * default_step, 1)
                            bc = st.columns([2, 2, 2, 2, 2])
                            bc[0].markdown(
                                f"<div style='padding-top:.6rem;font-weight:700;"
                                f"color:{NAVY}'>Band {i+1}</div>",
                                unsafe_allow_html=True,
                            )
                            lo = bc[1].number_input(
                                f"Lo{i}", min_value=0.0, max_value=200.0,
                                value=lo_def, step=1.0,
                                label_visibility="collapsed", key=f"t2_band_lo_{i}",
                            )
                            hi = bc[2].number_input(
                                f"Hi{i}", min_value=0.0, max_value=200.0,
                                value=hi_def, step=1.0,
                                label_visibility="collapsed", key=f"t2_band_hi_{i}",
                            )
                            direction_b = bc[3].selectbox(
                                f"Dir{i}",
                                ["➕ Add", "➖ Deduct"],
                                label_visibility="collapsed",
                                key=f"t2_band_dir_{i}",
                            )
                            delta_b = bc[4].number_input(
                                f"Marks{i}", min_value=0.0, max_value=50.0,
                                value=0.0, step=0.5,
                                label_visibility="collapsed", key=f"t2_band_delta_{i}",
                            )
                            sign_b = 1 if "Add" in direction_b else -1
                            band_defs.append((lo, hi, sign_b * delta_b))

                        st.markdown("<br/>", unsafe_allow_html=True)

                        # Live preview: how many students fall in each band
                        ts_series = pd.to_numeric(df_mod["_total_score"], errors="coerce")
                        prev_cols = st.columns(n_bands)
                        for i, (lo, hi, delta) in enumerate(band_defs):
                            cnt_band = int(((ts_series >= lo) & (ts_series < hi)).sum())
                            with prev_cols[i]:
                                kpi(
                                    f"Band {i+1} ({lo:.0f}–{hi:.0f})",
                                    f"{cnt_band:,}",
                                    f"{'+ ' if delta >= 0 else '− '}{abs(delta):.1f} marks",
                                    "g" if delta > 0 else ("d" if delta < 0 else "n"),
                                )

                        st.markdown("<br/>", unsafe_allow_html=True)
                        do_band = st.button(
                            "⚡ Apply Band-Based Adjustment",
                            key="t2_apply_band",
                        )

                        if do_band:
                            df_upd = df_mod.copy()
                            ts_ref = pd.to_numeric(df_upd["_total_score"], errors="coerce")

                            for lo, hi, delta in band_defs:
                                if delta == 0:
                                    continue
                                mask_b = (ts_ref >= lo) & (ts_ref < hi)
                                df_upd.loc[mask_b, exam_fld] = (
                                    pd.to_numeric(df_upd.loc[mask_b, exam_fld], errors="coerce")
                                    + delta
                                ).clip(lower=0)

                            df_upd["_total_score"] = df_upd[total_cols].apply(
                                lambda r: pd.to_numeric(r, errors="coerce").sum(), axis=1
                            )
                            mod_data["df"] = df_upd
                            st.session_state[mod_state_key] = mod_data
                            df_mod = df_upd

                            # ── Distribution comparison ────────────────────────
                            original_df = mod_data.get("original_df", df_upd)
                            bef_ts = pd.to_numeric(original_df["_total_score"], errors="coerce").dropna()
                            aft_ts = pd.to_numeric(df_upd["_total_score"],      errors="coerce").dropna()

                            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                            cmp_fig_b = go.Figure()
                            cmp_fig_b.add_trace(go.Histogram(
                                x=bef_ts, nbinsx=30, name="Before",
                                marker_color=MUTED, opacity=0.65,
                            ))
                            cmp_fig_b.add_trace(go.Histogram(
                                x=aft_ts, nbinsx=30, name="After",
                                marker_color=RED, opacity=0.78,
                            ))
                            cmp_fig_b.update_layout(
                                barmode="overlay",
                                title="Total Score Distribution: Before vs After Band Adjustment",
                                xaxis_title="Total Score", yaxis_title="Count",
                            )
                            st.plotly_chart(
                                apply_chart_theme(cmp_fig_b, 340),
                                use_container_width=True,
                                config={"displayModeBar": False},
                            )
                            st.markdown("</div>", unsafe_allow_html=True)

                            rpt_after_b = normality_report(df_upd["_total_score"])
                            if rpt_after_b:
                                is_n_b = rpt_after_b["p"] > 0.05
                                st.markdown(
                                    f'<div class="{"callout-success" if is_n_b else "callout-warn"}">'
                                    f"After band adjustment: mean = <strong>{rpt_after_b['mean']:.2f}</strong> · "
                                    f"skewness = <strong>{rpt_after_b['skew']:.3f}</strong> · "
                                    f"p = <strong>{rpt_after_b['p']:.4f}</strong> "
                                    f"({'Normal ✓' if is_n_b else 'Non-Normal ✗'})"
                                    f"</div>",
                                    unsafe_allow_html=True,
                                )

                            # ── Grade comparison ───────────────────────────────
                            st.markdown("<br/>", unsafe_allow_html=True)
                            sec("Grade Distribution: Before vs After Band Adjustment")
                            grade_before_b = pd.to_numeric(original_df["_total_score"], errors="coerce").apply(score_to_grade)
                            grade_after_b  = pd.to_numeric(df_upd["_total_score"],      errors="coerce").apply(score_to_grade)
                            _render_grade_comparison(grade_before_b, grade_after_b, exam_fld, total_cols, mod_data, mod_state_key)

                    # ── 2f. Preview & Download ─────────────────────────────────
                    sec("Moderated Gradebook - Preview")
                    st.dataframe(df_mod, use_container_width=True, hide_index=True)
                    st.caption(f"{len(df_mod):,} rows · Total score column: `_total_score`")
                    st.markdown("<br/>", unsafe_allow_html=True)
                    st.download_button(
                        label="⬇️  Download Moderated Gradebook",
                        data=to_csv_bytes(df_mod),
                        file_name="moderated_gradebook.csv",
                        mime="text/csv",
                        key="t2_download_btn",
                    )
