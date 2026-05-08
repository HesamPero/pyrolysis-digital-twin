"""
Biomass Pyrolysis Digital Twin — Public Demo
============================================
Portfolio demonstration of interactive dashboard design and data visualisation.
Physics model uses generalised correlations for illustration purposes only.
Proprietary experimental regressions are not included.

Author : Hesam Pero
Stack  : Python · Streamlit · Plotly
"""

import math
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ──────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pyrolysis Digital Twin",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
#  CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* dark background */
    .stApp { background-color: #0f1117; color: #e8e8e8; }
    [data-testid="stSidebar"] { background-color: #0d1a12; border-right: 1px solid #2d6a4f; }

    /* title banner */
    .banner {
        background: linear-gradient(135deg, #0f2b1e, #1a3a2a);
        padding: 18px 26px; border-radius: 12px;
        border-left: 5px solid #4a7c59; margin-bottom: 20px;
    }
    .banner h1 { color: #a8d8a8; font-family: monospace; letter-spacing: 2px;
                 font-size: 1.6rem; margin: 0; }
    .banner p  { color: #6bab80; font-size: 0.82rem; margin: 5px 0 0;
                 font-family: monospace; }

    /* metric cards */
    .metric-row { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
    .metric-card {
        flex: 1; min-width: 130px;
        background: #1a2a1a; border: 1px solid #2d6a4f;
        border-radius: 10px; padding: 12px 16px; text-align: center;
    }
    .metric-card .val { font-size: 1.5rem; font-weight: bold; font-family: monospace; }
    .metric-card .lbl { font-size: 0.72rem; color: #6bab80; margin-top: 3px; }

    /* error box */
    .err-box {
        background: #5c1a1a; border: 1px solid #ff4d4d;
        border-radius: 8px; padding: 12px 16px;
        color: #ffaaaa; font-weight: bold; margin-bottom: 12px;
    }

    /* demo badge */
    .demo-badge {
        display: inline-block; background: #2a1a00;
        border: 1px solid #c9722b; border-radius: 6px;
        padding: 4px 12px; color: #e8a87c;
        font-size: 0.75rem; font-family: monospace; margin-bottom: 14px;
    }

    /* section headers */
    .sec-hdr {
        font-family: monospace; font-size: 0.85rem;
        color: #a8d8a8; letter-spacing: 1px;
        border-bottom: 1px solid #2d6a4f; padding-bottom: 4px;
        margin: 18px 0 10px;
    }

    /* hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
#  CONSTANTS  (gas molar masses, LHV — public domain thermodynamic data)
# ──────────────────────────────────────────────────────────────────────────────
GAS_SPECIES  = ["H₂", "CH₄", "CO₂", "CO", "C₂H₄", "C₂H₆"]
MOLAR_MASS   = [2.016, 16.043, 44.009, 28.01, 28.054, 30.07]   # g/mol
LHV_KWH      = [33.3,  13.9,   0.0,   2.81,  13.096, 13.191]   # kWh/kg
GAS_COLORS   = ["#e8f4f8", "#ffd166", "#ef476f",
                 "#06d6a0", "#118ab2", "#073b4c"]

BIOMASS_COLORS = {
    "Cellulose":      "#4CAF50",
    "Hemicellulose":  "#FFC107",
    "Lignin":         "#9C27B0",
    "Ash":            "#9E9E9E",
    "Others":         "#FF5722",
}

# Default starting values
DEFAULT = dict(cel=40.0, hemi=20.0, lig=25.0, ash=5.0, HTT=550)

CLR = dict(
    biomass="#4a7c59", heart="#2d6a4f", biochar="#3a3a5e",
    tar="#c9722b",     aqueous="#2176ae", gas="#e8c547",
    loss="#9e2a2b",    elec="#6a0572",
    bg="#0f1117",      text="#e8e8e8",
)

LAYOUT_BASE = dict(
    paper_bgcolor=CLR["bg"], plot_bgcolor=CLR["bg"],
    font=dict(color=CLR["text"], family="monospace", size=12),
    margin=dict(l=10, r=10, t=50, b=10),
)

# ──────────────────────────────────────────────────────────────────────────────
#  GENERALISED PHYSICS MODEL
#  (illustrative correlations — not the proprietary experimental regressions)
# ──────────────────────────────────────────────────────────────────────────────
def run_model(cel, hemi, lig, ash, HTT):
    """
    Generalised pyrolysis correlations for demonstration purposes.
    Proprietary regression coefficients are not included.
    """
    oth = 100 - cel - hemi - lig - ash
    T_n = (HTT - 650) / 200          # normalised temperature

    # ── Mass yields [%] ─────────────────────────────────────────────────────
    # Biochar: decreases with temperature, increases with lignin
    biochar = (
        28.0
        - 8.5  * T_n
        + 0.18 * lig
        - 0.10 * cel
        - 1.2  * T_n * T_n
        + 0.05 * ash
    )
    biochar = max(5.0, min(55.0, biochar))

    # Tar: peaks at mid-temperature, driven by cellulose
    tar = (
        18.0
        + 0.12 * cel
        - 0.08 * lig
        - 2.0  * T_n
        - 1.5  * T_n * T_n
    )
    tar = max(2.0, min(40.0, tar))

    # Aqueous: driven by cellulose & hemicellulose
    aqueous = (
        20.0
        + 0.14 * cel
        + 0.10 * hemi
        - 1.0  * T_n
        - 0.08 * lig
    )
    aqueous = max(5.0, min(45.0, aqueous))

    # Gas: by difference
    gas = max(5.0, 100.0 - biochar - tar - aqueous)

    # ── Biochar sub-parameters ───────────────────────────────────────────────
    bc_C    = 65.0 + 8.0 * T_n + 0.10 * lig - 0.05 * cel
    bc_H    = max(0.5, 3.5 - 0.8 * T_n)
    bc_yC   = biochar * bc_C / 100
    bc_yN   = 0.8 + 0.02 * hemi
    bc_ash  = (ash / max(biochar, 1.0)) * 70.0
    bc_HC   = max(0.05, (bc_H / 1.008) / (bc_C / 12.011))

    # ── Tar sub-parameters ──────────────────────────────────────────────────
    tar_C   = 52.0 + 4.0 * T_n + 0.08 * lig
    tar_yC  = tar * tar_C / 100

    # ── Aqueous sub-parameters ──────────────────────────────────────────────
    aq_yN   = 15.0 + 0.3 * hemi - 1.0 * T_n
    aq_yC   = aqueous * 5.0 / 100

    # ── Gas carbon yield (carbon balance closure) ────────────────────────────
    gas_yC  = max(0.0, 100.0 - aq_yC - tar_yC - bc_yC)

    # ── Gas species  (vol%, illustrative) ───────────────────────────────────
    # Trends: H2 & CO rise with T; CH4 peaks mid-T; CO2 dominant at low T
    raw_vol = [
        max(0.1, 12.0 + 10.0 * T_n),               # H2
        max(0.1, 22.0 +  4.0 * T_n),               # CH4
        max(0.1, 30.0 -  6.0 * T_n),               # CO2
        max(0.1, 28.0 +  8.0 * T_n),               # CO
        max(0.1,  5.0 -  2.0 * T_n),               # C2H4
        max(0.1,  3.0 -  1.5 * T_n),               # C2H6
    ]
    vol_sum = sum(raw_vol)
    vol_pct = [v / vol_sum * 100 for v in raw_vol]

    # wt% from vol% × molar mass
    wt_raw  = [v * m for v, m in zip(vol_pct, MOLAR_MASS)]
    wt_sum  = sum(wt_raw)
    wt_pct  = [w / wt_sum * 100 for w in wt_raw]

    # ── Energy balance [MJ/kg biomass] ───────────────────────────────────────
    # Biomass LHV (Channiwala & Parikh, 2002 — public correlation)
    bm_LHV = (
        349.1 * (cel * 0.44 / 100)
        + 117.9 * (cel * 0.062 / 100)
        - 103.4 * (cel * 0.31 / 100)
        + 100.5 * (ash / 100)
        + 15000 * (lig / 100)
    )
    bm_LHV = max(12000, min(22000, bm_LHV + 14500))   # realistic range J/g

    # Biochar LHV
    bc_LHV  = max(5000, bm_LHV * (0.7 + 0.15 * T_n))
    bc_e    = bc_LHV  * biochar  / 100 * 1000 * 1e-6

    # Tar HHV
    tar_HHV = 35000 + 2000 * T_n
    tar_e   = tar_HHV * tar / 100 * 1000 * 1e-6

    # Gas energy
    gas_LHV = sum(wt_pct[i] * LHV_KWH[i] for i in range(6)) / 100 * 3600
    gas_ch  = gas_LHV * gas / 100 * 1000 * 1e-6
    gas_sn  = gas / 100 * 1000 * 1.05 * (HTT - 25) * 1e-6

    # Aqueous
    aq_cond = aqueous * 0.01 * 2257 * 1000 * 1e-6
    aq_sens = aqueous * 0.01 * 1000 * 1.8 * (HTT - 25) * 1e-6

    # Electrical heating input
    elec_in = 1.5 + 0.008 * (HTT - 450) + 0.01 * lig

    # Total input & losses
    bm_e    = bm_LHV * 1000 * 1e-6
    losses  = max(0.01, (bm_e + elec_in) - bc_e - tar_e - gas_ch - gas_sn
                        - aq_cond - aq_sens)

    return dict(
        # inputs
        cel=cel, hemi=hemi, lig=lig, ash=ash, oth=oth, HTT=HTT,
        # mass yields
        biochar=biochar, tar=tar, aqueous=aqueous, gas=gas,
        # biochar
        bc_C=bc_C, bc_H=bc_H, bc_yC=bc_yC, bc_yN=bc_yN,
        bc_ash=bc_ash, bc_HC=bc_HC, bc_LHV=bc_LHV,
        # tar
        tar_C=tar_C, tar_yC=tar_yC, tar_HHV=tar_HHV,
        # aqueous
        aq_yN=aq_yN, aq_yC=aq_yC,
        # gas
        gas_yC=gas_yC,
        gas_vol=dict(zip(GAS_SPECIES, vol_pct)),
        gas_wt= dict(zip(GAS_SPECIES, wt_pct)),
        # energy
        bm_LHV=bm_LHV, bm_e=bm_e,
        bc_e=bc_e, tar_e=tar_e,
        gas_ch=gas_ch, gas_sn=gas_sn,
        aq_cond=aq_cond, aq_sens=aq_sens,
        elec_in=elec_in, losses=losses,
    )


# ──────────────────────────────────────────────────────────────────────────────
#  CHART BUILDERS
# ──────────────────────────────────────────────────────────────────────────────
def chart_biomass_pie(r):
    labels = list(BIOMASS_COLORS.keys())
    values = [r["cel"], r["hemi"], r["lig"], r["ash"], r["oth"]]
    colors = list(BIOMASS_COLORS.values())
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors, line=dict(color="#0f1117", width=2)),
        hole=0.42,
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>Share: %{value:.1f}%<extra></extra>",
        pull=[0.03] * 5,
        rotation=90,
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="🌾  Biomass Composition",
                   font=dict(size=14, color="#a8d8a8"), x=0.5, xanchor="center"),
        height=340,
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11),
                    orientation="v", x=1.0, y=0.5),
    )
    return fig


def chart_mass_sankey(r):
    labels = [
        "Biomass\n1.00 kg",
        "Pyrolysis\nReactor",
        f"Biochar\n{r['biochar']:.1f}%",
        f"Tar\n{r['tar']:.1f}%",
        f"Aqueous\n{r['aqueous']:.1f}%",
        f"Gas\n{r['gas']:.1f}%",
    ]
    hover = [
        (f"Cellulose: {r['cel']:.1f}%<br>Hemicellulose: {r['hemi']:.1f}%<br>"
         f"Lignin: {r['lig']:.1f}%<br>Ash: {r['ash']:.1f}%<br>Others: {r['oth']:.1f}%"),
        f"HTT: {r['HTT']} °C",
        (f"C content: {r['bc_C']:.1f}%<br>H content: {r['bc_H']:.2f}%<br>"
         f"C yield: {r['bc_yC']:.2f}%<br>N yield: {r['bc_yN']:.2f}%<br>"
         f"Ash: {r['bc_ash']:.1f}%<br>H/C molar: {r['bc_HC']:.3f}"),
        f"C content: {r['tar_C']:.1f}%<br>C yield: {r['tar_yC']:.2f}%",
        f"N yield: {r['aq_yN']:.2f}%<br>C yield: {r['aq_yC']:.2f}%",
        (f"C yield: {r['gas_yC']:.2f}%<br>"
         + "<br>".join(f"{s}: {r['gas_wt'][s]:.1f} wt% | {r['gas_vol'][s]:.1f} vol%"
                       for s in GAS_SPECIES)),
    ]
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=8, thickness=28,
            label=labels,
            color=[CLR["biomass"], CLR["heart"],
                   CLR["biochar"], CLR["tar"], CLR["aqueous"], CLR["gas"]],
            customdata=hover,
            hovertemplate="%{customdata}<extra>%{label}</extra>",
        ),
        link=dict(
            source=[0, 1, 1, 1, 1],
            target=[1, 2, 3, 4, 5],
            value=[100, r["biochar"], r["tar"], r["aqueous"], r["gas"]],
            color=["rgba(45,106,79,0.45)", "rgba(58,58,94,0.7)",
                   "rgba(201,114,43,0.7)", "rgba(33,118,174,0.7)",
                   "rgba(232,197,71,0.7)"],
            hovertemplate="Flow: %{value:.1f}%<extra></extra>",
        ),
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="⚖️  Mass Balance — per 1 kg Biomass",
                   font=dict(size=14, color="#a8d8a8"), x=0.5, xanchor="center"),
        height=340,
    )
    return fig


def chart_yield_bar(r):
    names  = ["Biochar", "Tar", "Aqueous", "Gas"]
    values = [r["biochar"], r["tar"], r["aqueous"], r["gas"]]
    colors = [CLR["biochar"], CLR["tar"], CLR["aqueous"], CLR["gas"]]
    fig = go.Figure(go.Bar(
        x=values, y=names, orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        textfont=dict(color=CLR["text"]),
        hovertemplate="%{y}: %{x:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        xaxis=dict(title="Yield [%]", gridcolor="#2a2a3e", range=[0, 108]),
        yaxis=dict(gridcolor="#2a2a3e"),
        title=dict(text="📊  Product Yield Overview",
                   font=dict(size=14, color=CLR["text"]), x=0.5, xanchor="center"),
        height=240,
        showlegend=False,
    )
    return fig


def chart_gas_pies(r):
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "pie"}]],
        subplot_titles=["Gas Composition  [wt%]", "Gas Composition  [vol%]"],
    )
    common = dict(
        marker=dict(colors=GAS_COLORS, line=dict(color="#0f1117", width=1)),
        hole=0.4,
        textinfo="label+percent",
        textposition="outside",
    )
    fig.add_trace(go.Pie(
        labels=GAS_SPECIES,
        values=[r["gas_wt"][s] for s in GAS_SPECIES],
        hovertemplate="<b>%{label}</b><br>%{value:.1f} wt%<extra></extra>",
        **common,
    ), row=1, col=1)
    fig.add_trace(go.Pie(
        labels=GAS_SPECIES,
        values=[r["gas_vol"][s] for s in GAS_SPECIES],
        hovertemplate="<b>%{label}</b><br>%{value:.1f} vol%<extra></extra>",
        **common,
    ), row=1, col=2)
    fig.update_layout(
        paper_bgcolor=CLR["bg"],
        plot_bgcolor=CLR["bg"],
        font=dict(color=CLR["text"], family="monospace", size=11),
        margin=dict(l=60, r=60, t=60, b=100),
        title=dict(text="🔬  Gas Phase Composition",
                   font=dict(size=14, color="#ffd166"), x=0.5, xanchor="center"),
        height=500,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_annotations(font_color=CLR["text"])
    return fig


def chart_energy_sankey(r):
    bm_e  = r["bm_e"]
    elec  = r["elec_in"]
    bc_e  = r["bc_e"]
    tar_e = r["tar_e"]
    g_tot = r["gas_ch"] + r["gas_sn"]
    a_tot = r["aq_cond"] + r["aq_sens"]
    loss  = max(0.001, r["losses"])

    labels = [
        f"Biomass LHV\n{bm_e:.3f} MJ",
        f"Electrical\nInput\n{elec:.3f} MJ",
        "Total\nEnergy\nInput",
        f"Biochar\n{bc_e:.3f} MJ",
        f"Tar\n{tar_e:.3f} MJ",
        f"Gas\n{g_tot:.3f} MJ",
        f"Aqueous\n{a_tot:.3f} MJ",
        f"Losses\n{loss:.3f} MJ",
    ]
    hover = [
        f"Biomass LHV: {r['bm_LHV']:.0f} J/g<br>Chemical energy: {bm_e:.4f} MJ/kg",
        f"Electrical heating correction<br>{elec:.4f} MJ/kg",
        f"Total input: {bm_e+elec:.4f} MJ/kg",
        f"Biochar LHV: {r['bc_LHV']:.0f} J/g<br>Energy stored: {bc_e:.4f} MJ/kg",
        f"Tar HHV: {r['tar_HHV']:.0f} J/g<br>Energy in tar: {tar_e:.4f} MJ/kg",
        f"Chemical: {r['gas_ch']:.4f} MJ/kg<br>Sensible: {r['gas_sn']:.4f} MJ/kg",
        f"Condensation: {r['aq_cond']:.4f} MJ/kg<br>Sensible: {r['aq_sens']:.4f} MJ/kg",
        f"Non-recovered losses: {loss:.4f} MJ/kg",
    ]
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=8, thickness=26,
            label=labels,
            color=[CLR["biomass"], CLR["elec"], CLR["heart"],
                   CLR["biochar"], CLR["tar"], CLR["gas"],
                   CLR["aqueous"], CLR["loss"]],
            customdata=hover,
            hovertemplate="%{customdata}<extra>%{label}</extra>",
        ),
        link=dict(
            source=[0, 1, 2, 2, 2, 2, 2],
            target=[2, 2, 3, 4, 5, 6, 7],
            value=[bm_e, elec, bc_e, tar_e, g_tot, a_tot, loss],
            color=["rgba(74,124,89,0.5)", "rgba(106,5,114,0.5)",
                   "rgba(58,58,94,0.7)", "rgba(201,114,43,0.7)",
                   "rgba(232,197,71,0.6)", "rgba(33,118,174,0.6)",
                   "rgba(158,42,43,0.7)"],
            hovertemplate="Flow: %{value:.4f} MJ/kg<extra></extra>",
        ),
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text="⚡  Energy Balance — MJ per kg Biomass",
                   font=dict(size=14, color="#e8c547"), x=0.5, xanchor="center"),
        height=400,
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
#  SIDEBAR — INPUTS
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Input Parameters")
    st.markdown("---")
    st.markdown("**Biochemical Composition [%]**")

    cel  = st.slider("🌿 Cellulose",     20.0, 60.0, DEFAULT["cel"],  0.1)
    hemi = st.slider("🍂 Hemicellulose",  5.0, 35.0, DEFAULT["hemi"], 0.1)
    lig  = st.slider("🪵 Lignin",         5.0, 60.0, DEFAULT["lig"],  0.1)
    ash  = st.slider("⚪ Ash",            0.0, 10.0, DEFAULT["ash"],  0.1)

    total = cel + hemi + lig + ash
    oth   = 100.0 - total

    if oth >= 0:
        st.success(f"✅ Others: **{oth:.1f}%**  |  Total: **{total:.1f}%**")
    else:
        st.error(f"❌ Exceeds 100% by **{-oth:.1f}%** — reduce inputs!")

    st.markdown("---")
    st.markdown("**Process Temperature**")
    HTT = st.slider("🌡️ HTT [°C]", 450, 850, DEFAULT["HTT"], 10)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.72rem;color:#4a7c59;font-family:monospace;'>"
        "⚠️ Demo model uses generalised literature<br>"
        "correlations. Proprietary regressions<br>"
        "are not included.</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
#  MAIN PANEL
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="banner">
  <h1>🌿 BIOMASS PYROLYSIS DIGITAL TWIN</h1>
  <p>Mass &amp; Energy Balance Model · 1 kg Basis · Slow Pyrolysis · HTT 450–850 °C</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="demo-badge">⚠️ PUBLIC DEMO — Generalised model for portfolio purposes. '
    'Proprietary experimental regressions not included.</div>',
    unsafe_allow_html=True,
)

# Guard: error if inputs invalid
if oth < 0:
    st.markdown(
        f'<div class="err-box">❌ Component sum exceeds 100% by {-oth:.1f}%. '
        f'Please reduce Cellulose, Hemicellulose, Lignin, or Ash.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# Run model
r = run_model(cel, hemi, lig, ash, HTT)

# ── Quick summary metric cards ────────────────────────────────────────────────
st.markdown('<div class="sec-hdr">📋 PRODUCT YIELD SUMMARY</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
card_data = [
    (c1, f"{r['biochar']:.1f}%", "Biochar", "#3a3a5e",  "#a8a8e8"),
    (c2, f"{r['tar']:.1f}%",     "Tar",     "#3a1a0a",  "#e8a87c"),
    (c3, f"{r['aqueous']:.1f}%", "Aqueous", "#0a1a3a",  "#7cb8e8"),
    (c4, f"{r['gas']:.1f}%",     "Gas",     "#3a3a0a",  "#e8d87c"),
]
for col, val, lbl, bg, fg in card_data:
    col.markdown(
        f'<div class="metric-card" style="background:{bg};border-color:{fg}22;">'
        f'<div class="val" style="color:{fg};">{val}</div>'
        f'<div class="lbl">{lbl} Yield</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Biomass pie + Mass Sankey ─────────────────────────────────────────
col_pie, col_sankey = st.columns([1, 1.6])
with col_pie:
    st.plotly_chart(chart_biomass_pie(r), use_container_width=True, key="bm_pie")
with col_sankey:
    st.plotly_chart(chart_mass_sankey(r), use_container_width=True, key="sankey")

# ── Yield bar ─────────────────────────────────────────────────────────────────
st.plotly_chart(chart_yield_bar(r), use_container_width=True, key="bar")

# ── Gas composition pies ──────────────────────────────────────────────────────
st.plotly_chart(chart_gas_pies(r), use_container_width=True, key="gas")

# ── Energy Sankey ─────────────────────────────────────────────────────────────
st.plotly_chart(chart_energy_sankey(r), use_container_width=True, key="energy")

# ── Energy summary table ──────────────────────────────────────────────────────
st.markdown('<div class="sec-hdr">⚡ ENERGY BALANCE SUMMARY</div>', unsafe_allow_html=True)
e_col1, e_col2 = st.columns(2)
with e_col1:
    st.markdown(f"""
    | Input | Value |
    |-------|-------|
    | Biomass LHV | `{r['bm_LHV']:.0f} J/g` |
    | Biomass Chemical Energy | `{r['bm_e']:.4f} MJ/kg` |
    | Electrical Heating Input | `{r['elec_in']:.4f} MJ/kg` |
    | **Total Input** | **`{r['bm_e']+r['elec_in']:.4f} MJ/kg`** |
    """)
with e_col2:
    st.markdown(f"""
    | Output | Value |
    |--------|-------|
    | Biochar Chemical Energy | `{r['bc_e']:.4f} MJ/kg` |
    | Tar Chemical Energy | `{r['tar_e']:.4f} MJ/kg` |
    | Gas (Chem + Sensible) | `{r['gas_ch']+r['gas_sn']:.4f} MJ/kg` |
    | Aqueous (Cond + Sensible) | `{r['aq_cond']+r['aq_sens']:.4f} MJ/kg` |
    | Non-recovered Losses | `{r['losses']:.4f} MJ/kg` |
    """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-family:monospace;font-size:0.75rem;"
    "color:#4a7c59;padding:10px;'>"
    "🌿 Biomass Pyrolysis Digital Twin · Built by Hesam Pero · Python & Streamlit<br>"
    "Physics model uses generalised correlations for illustrative purposes. "
    "Proprietary experimental data not included."
    "</div>",
    unsafe_allow_html=True,
)
