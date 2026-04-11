# dashboard_lab_hu.py
# ============================================================
# DASHBOARD — MONITORAMENTO LABORATORIAL HU
# Repetições desnecessárias de exames em pacientes internados
# Versão redesenhada com identidade visual Unimed
# ============================================================

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Lab Vision | HU",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PALETA INSTITUCIONAL UNIMED
# ============================================================
COLORS = {
    "primary": "#00995D",
    "primary_light": "#B6D44C",
    "deep": "#004B52",
    "alert": "#F47920",

    "support_rose": "#C59A8B",
    "support_blush": "#E5C6C0",
    "support_sand": "#D5CEC2",
    "support_warm": "#F4E2B1",
    "support_mint": "#C1D0B9",
    "support_ice": "#C7DEE2",

    "danger": "#C94F4F",
    "danger_dark": "#8F2D2D",
    "warning": "#F0B24A",
    "success": "#00995D",
    "info": "#2E7D8A",

    "bg": "#F4F8F6",
    "surface": "#FFFFFF",
    "surface_soft": "#EEF5F1",
    "surface_deep": "#073B3A",
    "border": "#D8E4DD",
    "text": "#18302B",
    "muted": "#6B7D76",
    "grid": "#E8EFEB",
    "white": "#FFFFFF",
}

DIAS_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


# ============================================================
# CSS GLOBAL
# ============================================================
def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: {COLORS["text"]};
        }}

        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(182,212,76,0.12), transparent 25%),
                radial-gradient(circle at top left, rgba(0,153,93,0.10), transparent 30%),
                linear-gradient(180deg, #F6FBF8 0%, #F2F7F4 100%);
        }}

        .block-container {{
            max-width: 1550px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            padding-left: 1.6rem;
            padding-right: 1.6rem;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0A3E3D 0%, #063434 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }}

        [data-testid="stSidebar"] * {{
            color: #EAF7F1 !important;
        }}

        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {{
            background-color: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 14px;
        }}

        #MainMenu, footer, header {{
            visibility: hidden;
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(135deg, rgba(0,75,82,0.98) 0%, rgba(0,153,93,0.94) 55%, rgba(182,212,76,0.88) 100%);
            border-radius: 24px;
            padding: 1.4rem 1.6rem 1.5rem 1.6rem;
            box-shadow: 0 14px 40px rgba(0, 75, 82, 0.18);
            border: 1px solid rgba(255,255,255,0.16);
            margin-bottom: 1rem;
        }}

        .hero:before {{
            content: "";
            position: absolute;
            right: -40px;
            top: -40px;
            width: 200px;
            height: 200px;
            background: rgba(255,255,255,0.08);
            filter: blur(4px);
            border-radius: 50%;
        }}

        .hero-title {{
            color: white;
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -0.03em;
            margin-bottom: 0.25rem;
        }}

        .hero-sub {{
            color: rgba(255,255,255,0.88);
            font-size: 0.96rem;
            line-height: 1.45;
            margin-bottom: 0.9rem;
            max-width: 980px;
        }}

        .hero-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.42rem 0.75rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            color: white;
            font-size: 0.78rem;
            font-weight: 600;
            border: 1px solid rgba(255,255,255,0.12);
            backdrop-filter: blur(6px);
        }}

        .section-title {{
            margin-top: 1.15rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }}

        .section-title .dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_light"]});
            box-shadow: 0 0 0 4px rgba(0,153,93,0.10);
        }}

        .section-title .text {{
            font-size: 0.83rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: {COLORS["deep"]};
        }}

        .kpi-card {{
            position: relative;
            overflow: hidden;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(247,251,248,0.98) 100%);
            border: 1px solid {COLORS["border"]};
            border-radius: 22px;
            padding: 1rem 1.05rem 1rem 1.05rem;
            min-height: 136px;
            box-shadow: 0 12px 28px rgba(0,75,82,0.07);
        }}

        .kpi-card:before {{
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 6px;
            background: var(--accent);
        }}

        .kpi-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.55rem;
        }}

        .kpi-icon {{
            width: 38px;
            height: 38px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            background: var(--accent-soft);
        }}

        .kpi-label {{
            font-size: 0.74rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {COLORS["muted"]};
        }}

        .kpi-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.72rem;
            font-weight: 800;
            color: var(--accent);
            line-height: 1.0;
            margin-bottom: 0.35rem;
        }}

        .kpi-sub {{
            font-size: 0.82rem;
            color: {COLORS["muted"]};
            line-height: 1.35;
            min-height: 38px;
        }}

        .kpi-bar {{
            margin-top: 0.65rem;
            height: 8px;
            border-radius: 999px;
            background: #EAF2EE;
            overflow: hidden;
        }}

        .kpi-fill {{
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--accent), var(--accent-2));
        }}

        .footer-note {{
            color: {COLORS["muted"]};
            font-size: 0.75rem;
            text-align: center;
            padding-top: 1rem;
            margin-top: 1rem;
            border-top: 1px solid {COLORS["border"]};
        }}

        .caption-box {{
            background: linear-gradient(180deg, rgba(193,208,185,0.22), rgba(255,255,255,0.75));
            border: 1px solid {COLORS["border"]};
            padding: 0.75rem 0.9rem;
            border-radius: 16px;
            color: {COLORS["muted"]};
            font-size: 0.8rem;
            margin-bottom: 0.75rem;
        }}

        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,0.8);
            border: 1px solid {COLORS["border"]};
            border-radius: 16px;
            padding: 0.75rem 0.9rem;
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid {COLORS["border"]};
            border-radius: 18px;
            background: rgba(255,255,255,0.75);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def format_int(v):
    return f"{int(v):,}".replace(",", ".")


def format_money(v):
    return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_pct(v, nd=1):
    return f"{v:.{nd}f}%".replace(".", ",")


def truncate_text(text, n=30):
    text = str(text)
    return text if len(text) <= n else text[: n - 1] + "…"


def section_header(title):
    st.markdown(
        f"""
        <div class="section-title">
            <span class="dot"></span>
            <span class="text">{title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label, value, sub, accent, icon="•", fill=0.7, accent_2=None):
    accent_2 = accent_2 or COLORS["primary_light"]
    accent_soft = f"{accent}22"
    fill_pct = max(0, min(fill, 1)) * 100
    return f"""
    <div class="kpi-card" style="--accent:{accent}; --accent-2:{accent_2}; --accent-soft:{accent_soft}">
        <div class="kpi-top">
            <div class="kpi-label">{label}</div>
            <div class="kpi-icon">{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
        <div class="kpi-bar">
            <div class="kpi-fill" style="width:{fill_pct:.0f}%"></div>
        </div>
    </div>
    """


def plot_layout(title, height=380, legend=None, **kwargs):
    base = dict(
        title=dict(text=title, x=0, font=dict(size=15, color=COLORS["deep"])),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.75)",
        font=dict(family="Inter, sans-serif", size=12, color=COLORS["text"]),
        margin=dict(l=8, r=8, t=50, b=8),
        height=height,
        hoverlabel=dict(
            bgcolor=COLORS["deep"],
            font_color=COLORS["white"],
            font_size=12,
            font_family="Inter, sans-serif",
        ),
    )

    if legend is None:
        base["legend"] = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
        )
    else:
        base["legend"] = legend

    base.update(kwargs)
    return base


def color_scale(value, vmin=0, vmax=100):
    import matplotlib.colors as mcolors
    import matplotlib as mpl

    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "unimed_scale",
        [COLORS["primary"], COLORS["primary_light"], COLORS["alert"], COLORS["danger_dark"]],
    )
    norm = mcolors.Normalize(vmin=vmin, vmax=max(vmax, vmin + 1e-9))
    rgba = cmap(norm(value))
    return mcolors.to_hex(rgba)


def color_scale_list(values, vmin=0, vmax=100):
    values = list(values)
    if len(values) == 0:
        return []
    vmax = vmax if vmax is not None else max(values)
    return [color_scale(v, vmin=vmin, vmax=vmax) for v in values]


# ============================================================
# LEITURA E PREPARAÇÃO DOS DADOS
# ============================================================
@st.cache_data(ttl=3600, show_spinner="Carregando dados laboratoriais...")
def carregar_dados(path="dados_lab_hu.xlsx"):
    df = pd.read_excel(path, sheet_name="data")
    dim = pd.read_excel(path, sheet_name="dim_exames")

    for col in ["Interpretação", "Descrição Exame", "Setor Solicitante"]:
        df[col] = df[col].astype(str).str.strip().str.upper()

    dim["Descrição Exame"] = dim["Descrição Exame"].astype(str).str.strip().str.upper()

    df["DataHoraPedido"] = pd.to_datetime(df["DataHoraPedido"], errors="coerce")
    df = df.dropna(subset=["DataHoraPedido"]).copy()

    df["Data"] = df["DataHoraPedido"].dt.date
    df["Hora"] = df["DataHoraPedido"].dt.hour
    df["DiaSemana"] = df["DataHoraPedido"].dt.dayofweek
    df["MesAno"] = df["DataHoraPedido"].dt.strftime("%m/%Y")
    df["Turno"] = pd.cut(
        df["Hora"],
        bins=[-1, 6, 12, 18, 23],
        labels=["Madrugada", "Manhã", "Tarde", "Noite"],
    )

    custo_map = dict(zip(dim["Descrição Exame"], dim["CUSTO_EXAME"]))
    intervalo_map = dict(zip(dim["Descrição Exame"], dim["INTERVALOS_CLINICOS"]))

    df["Custo_Unit"] = df["Descrição Exame"].map(custo_map).fillna(3.50)
    df["Intervalo_Clinico_h"] = df["Descrição Exame"].map(intervalo_map).fillna(24)

    df["Flag_Normal"] = (df["Interpretação"] == "NORMAL").astype(int)
    df["Flag_Alterado"] = (df["Interpretação"] != "NORMAL").astype(int)

    df = df.sort_values(["Atendimento", "Descrição Exame", "DataHoraPedido"]).copy()
    grp = df.groupby(["Atendimento", "Descrição Exame"], dropna=False)

    df["Interp_Anterior"] = grp["Interpretação"].shift(1)
    df["DataHora_Anterior"] = grp["DataHoraPedido"].shift(1)
    df["Horas_Desde_Anterior"] = (
        (df["DataHoraPedido"] - df["DataHora_Anterior"]).dt.total_seconds() / 3600
    ).round(1)

    df["Flag_Rep"] = (
        (df["Interpretação"] == "NORMAL") &
        (df["Interp_Anterior"] == "NORMAL")
    ).astype(int)

    df["Flag_Rep_Crit"] = (
        (df["Flag_Rep"] == 1) &
        (df["Horas_Desde_Anterior"] < df["Intervalo_Clinico_h"])
    ).astype(int)

    df["Flag_Rep_Alerta"] = ((df["Flag_Rep"] == 1) & (df["Flag_Rep_Crit"] == 0)).astype(int)
    df["Custo_Rep"] = df["Custo_Unit"] * df["Flag_Rep"]
    df["Custo_Rep_Crit"] = df["Custo_Unit"] * df["Flag_Rep_Crit"]

    return df


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding-top:0.2rem;">
            <div style="font-size:1.1rem;font-weight:800;">Lab Vision</div>
            <div style="font-size:0.83rem;opacity:0.85;">Monitoramento de repetições laboratoriais</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    df_raw = carregar_dados()
    setores = sorted(df_raw["Setor Solicitante"].dropna().unique().tolist())

    setor_sel = st.selectbox(
        "Setor solicitante",
        ["— Todos os setores —"] + setores,
        index=0,
    )

    datas = pd.to_datetime(df_raw["DataHoraPedido"])
    periodo_label = f"{datas.min():%d/%m/%Y} até {datas.max():%d/%m/%Y}"

    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size:0.78rem;line-height:1.65;opacity:0.92;">
            <b>Base analisada</b><br>
            {periodo_label}<br><br>
            <b>Fonte</b><br>
            Sistema laboratorial / internação hospitalar<br><br>
            <b>Objetivo</b><br>
            Identificar repetições desnecessárias, concentração temporal, setores críticos e impacto financeiro.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FILTRO
# ============================================================
if setor_sel == "— Todos os setores —":
    df = df_raw.copy()
    titulo_setor = "Todos os setores"
else:
    df = df_raw[df_raw["Setor Solicitante"] == setor_sel].copy()
    titulo_setor = setor_sel.title()

if df.empty:
    st.warning("Não há dados disponíveis para o filtro selecionado.")
    st.stop()


# ============================================================
# CÁLCULOS GERAIS
# ============================================================
total_exames = len(df)
total_pacientes = df["Atendimento"].nunique()
total_pedidos = df["Pedido"].nunique() if "Pedido" in df.columns else np.nan

normais = int(df["Flag_Normal"].sum())
alterados = total_exames - normais
reps = int(df["Flag_Rep"].sum())
reps_crit = int(df["Flag_Rep_Crit"].sum())
reps_alerta = int(df["Flag_Rep_Alerta"].sum())

taxa_normal = (normais / total_exames * 100) if total_exames else 0
taxa_rep = (reps / total_exames * 100) if total_exames else 0
taxa_rep_crit = (reps_crit / max(reps, 1) * 100) if reps else 0

custo_rep_mes = float(df["Custo_Rep"].sum())
custo_rep_ano = custo_rep_mes * 12

periodo_inicio = pd.to_datetime(df["DataHoraPedido"]).min()
periodo_fim = pd.to_datetime(df["DataHoraPedido"]).max()


# ============================================================
# HERO HEADER
# ============================================================
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">Lab Vision · Repetições Desnecessárias</div>
        <div class="hero-sub">
            Painel analítico para monitoramento do comportamento de exames laboratoriais em pacientes internados,
            com foco em desperdício assistencial, criticidade clínica e impacto econômico.
        </div>
        <div class="hero-badges">
            <span class="badge">🏥 Hospital Unimed</span>
            <span class="badge">🧭 Escopo: {titulo_setor}</span>
            <span class="badge">📅 Período: {periodo_inicio:%d/%m/%Y} a {periodo_fim:%d/%m/%Y}</span>
            <span class="badge">🧪 {format_int(total_exames)} exames analisados</span>
            <span class="badge">💸 {format_money(custo_rep_mes)} em repetições</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="caption-box">
        <b>Leitura executiva:</b> o dashboard destaca onde há maior concentração de resultados normais seguidos de novos pedidos,
        em especial quando a repetição ocorre abaixo do intervalo clínico esperado para o exame.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPI CARDS
# ============================================================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        kpi_card(
            "Volume processado",
            format_int(total_exames),
            f"{format_int(total_pacientes)} pacientes · {format_int(total_pedidos) if pd.notna(total_pedidos) else '—'} pedidos",
            COLORS["deep"],
            icon="🧪",
            fill=min(total_exames / max(total_exames, 1), 1),
            accent_2=COLORS["primary"],
        ),
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        kpi_card(
            "Normalidade",
            format_pct(taxa_normal),
            f"{format_int(normais)} normais · {format_int(alterados)} alterados",
            COLORS["primary"],
            icon="✅",
            fill=taxa_normal / 100,
            accent_2=COLORS["primary_light"],
        ),
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        kpi_card(
            "Repetições",
            format_int(reps),
            f"{format_pct(taxa_rep)} do total · {format_int(reps_crit)} críticas",
            COLORS["alert"],
            icon="⚠️",
            fill=min(taxa_rep / max(taxa_rep + 5, 1), 1),
            accent_2=COLORS["danger"],
        ),
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        kpi_card(
            "Impacto financeiro",
            format_money(custo_rep_mes),
            f"Projeção anual estimada: {format_money(custo_rep_ano)}",
            COLORS["danger_dark"],
            icon="💰",
            fill=min(custo_rep_mes / max(custo_rep_mes + 500, 1), 1),
            accent_2=COLORS["alert"],
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# MÓDULO 1 — VISÃO DE NORMALIDADE
# ============================================================
section_header("Módulo 1 · Perfil de normalidade")

c1, c2 = st.columns([1, 1])

with c1:
    exame_norm = (
        df.groupby("Descrição Exame")
        .agg(Total=("Flag_Normal", "count"), Normais=("Flag_Normal", "sum"))
        .reset_index()
    )
    exame_norm = exame_norm[exame_norm["Total"] >= 5].copy()
    exame_norm["Pct_Normal"] = (exame_norm["Normais"] / exame_norm["Total"] * 100).round(1)
    exame_norm = exame_norm.sort_values("Pct_Normal", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=[truncate_text(x.title(), 34) for x in exame_norm["Descrição Exame"]],
            x=exame_norm["Pct_Normal"],
            orientation="h",
            marker=dict(
                color=color_scale_list(exame_norm["Pct_Normal"], vmin=0, vmax=100),
                line=dict(color="rgba(255,255,255,0.65)", width=1),
            ),
            text=[f"{v:.0f}%" for v in exame_norm["Pct_Normal"]],
            textposition="outside",
            customdata=exame_norm["Total"],
            hovertemplate="<b>%{y}</b><br>Normalidade: %{x:.1f}%<br>Volume: %{customdata:,}<extra></extra>",
        )
    )
    fig.add_vline(
        x=75,
        line_dash="dot",
        line_color=COLORS["deep"],
        opacity=0.5,
        annotation_text="meta visual 75%",
        annotation_position="top",
    )
    fig.update_layout(
        **plot_layout("Normalidade por exame", height=430),
        xaxis=dict(
            title=None,
            range=[0, 110],
            ticksuffix="%",
            showgrid=True,
            gridcolor=COLORS["grid"],
            zeroline=False,
        ),
        yaxis=dict(title=None, showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    top_setores = df["Setor Solicitante"].value_counts().head(8).index
    top_exames = df["Descrição Exame"].value_counts().head(10).index

    df_sub = df[
        (df["Setor Solicitante"].isin(top_setores)) &
        (df["Descrição Exame"].isin(top_exames))
    ].copy()

    piv = (
        df_sub.groupby(["Setor Solicitante", "Descrição Exame"])["Flag_Normal"]
        .mean()
        .mul(100)
        .round(1)
        .unstack()
    )

    fig = go.Figure(
        go.Heatmap(
            z=piv.values,
            x=[truncate_text(x.title(), 24) for x in piv.columns],
            y=[truncate_text(y, 26) for y in piv.index],
            colorscale=[
                [0.00, "#F6D9D5"],
                [0.35, COLORS["support_warm"]],
                [0.60, COLORS["primary_light"]],
                [1.00, COLORS["primary"]],
            ],
            zmin=0,
            zmax=100,
            text=[
                [f"{v:.0f}%" if pd.notna(v) else "—" for v in row]
                for row in piv.values
            ],
            texttemplate="%{text}",
            textfont=dict(size=10),
            colorbar=dict(title="% Normal", ticksuffix="%"),
            hovertemplate="<b>%{y}</b><br>%{x}<br>Normalidade: %{z:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        **plot_layout("Normalidade por setor × exame", height=430),
        xaxis=dict(title=None, tickangle=-35),
        yaxis=dict(title=None),
    )
    st.plotly_chart(fig, use_container_width=True)

setor_stack = (
    df.groupby("Setor Solicitante")
    .agg(Total=("Flag_Normal", "count"), Normais=("Flag_Normal", "sum"))
    .reset_index()
)
setor_stack = setor_stack[setor_stack["Total"] >= 30].copy()
setor_stack["Alterados"] = setor_stack["Total"] - setor_stack["Normais"]
setor_stack["Pct_Normal"] = (setor_stack["Normais"] / setor_stack["Total"] * 100).round(1)
setor_stack["Pct_Alterado"] = 100 - setor_stack["Pct_Normal"]
setor_stack = setor_stack.sort_values("Pct_Normal", ascending=False)

fig = go.Figure()
fig.add_trace(
    go.Bar(
        y=[truncate_text(x, 34) for x in setor_stack["Setor Solicitante"]],
        x=setor_stack["Pct_Normal"],
        orientation="h",
        name="Normal",
        marker_color=COLORS["primary"],
        text=[f"{x:.0f}%" for x in setor_stack["Pct_Normal"]],
        textposition="inside",
        textfont=dict(color="white"),
        hovertemplate="<b>%{y}</b><br>Normal: %{x:.1f}%<extra></extra>",
    )
)
fig.add_trace(
    go.Bar(
        y=[truncate_text(x, 34) for x in setor_stack["Setor Solicitante"]],
        x=setor_stack["Pct_Alterado"],
        orientation="h",
        name="Alterado",
        marker_color=COLORS["support_blush"],
        text=[f"{x:.0f}%" for x in setor_stack["Pct_Alterado"]],
        textposition="inside",
        hovertemplate="<b>%{y}</b><br>Alterado: %{x:.1f}%<extra></extra>",
    )
)
fig.update_layout(
    **plot_layout("Composição normal × alterado por setor", height=360, barmode="stack"),
    xaxis=dict(title=None, ticksuffix="%", range=[0, 100], showgrid=True, gridcolor=COLORS["grid"]),
    yaxis=dict(title=None, showgrid=False),
)
st.plotly_chart(fig, use_container_width=True)


# ============================================================
# MÓDULO 2 — REPETIÇÕES DESNECESSÁRIAS
# ============================================================
section_header("Módulo 2 · Foco em repetições desnecessárias")

rep_df = df[df["Flag_Rep"] == 1].copy()
c3, c4 = st.columns([1, 1])

with c3:
    rep_ex = (
        df.groupby("Descrição Exame")
        .agg(
            Total=("Flag_Normal", "count"),
            Reps=("Flag_Rep", "sum"),
            Criticas=("Flag_Rep_Crit", "sum"),
            Custo_Rep=("Custo_Rep", "sum"),
        )
        .reset_index()
    )
    rep_ex = rep_ex[rep_ex["Reps"] > 0].copy()
    rep_ex["Alerta"] = rep_ex["Reps"] - rep_ex["Criticas"]
    rep_ex["Taxa_Rep"] = (rep_ex["Reps"] / rep_ex["Total"] * 100).round(1)
    rep_ex = rep_ex.sort_values("Reps", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=[truncate_text(x.title(), 34) for x in rep_ex["Descrição Exame"]],
            x=rep_ex["Alerta"],
            orientation="h",
            name="Alerta",
            marker_color=COLORS["alert"],
            customdata=rep_ex["Taxa_Rep"],
            hovertemplate="<b>%{y}</b><br>Repetições alerta: %{x:,}<br>Taxa: %{customdata:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=[truncate_text(x.title(), 34) for x in rep_ex["Descrição Exame"]],
            x=rep_ex["Criticas"],
            orientation="h",
            name="Crítica",
            marker_color=COLORS["danger_dark"],
            customdata=rep_ex["Custo_Rep"],
            hovertemplate="<b>%{y}</b><br>Repetições críticas: %{x:,}<br>Custo: R$ %{customdata:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        **plot_layout("Ranking de repetições por exame", height=430, barmode="stack"),
        xaxis=dict(title=None, showgrid=True, gridcolor=COLORS["grid"]),
        yaxis=dict(title=None, showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)

with c4:
    bins = [0, 6, 12, 24, 48, 72, 168, 9999]
    labels = ["<6h", "6–12h", "12–24h", "24–48h", "48–72h", "3–7d", ">7d"]

    if not rep_df.empty:
        rep_df["Faixa"] = pd.cut(rep_df["Horas_Desde_Anterior"], bins=bins, labels=labels, right=False)
        dist = rep_df["Faixa"].value_counts().reindex(labels).fillna(0).astype(int)
    else:
        dist = pd.Series(0, index=labels)

    colors_interval = [
        COLORS["danger_dark"],
        COLORS["danger"],
        COLORS["alert"],
        COLORS["warning"],
        COLORS["support_sand"],
        COLORS["support_ice"],
        COLORS["support_mint"],
    ]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=dist.values,
            marker_color=colors_interval,
            text=dist.values,
            textposition="outside",
            hovertemplate="Faixa: %{x}<br>Repetições: %{y:,}<extra></extra>",
        )
    )
    fig.update_layout(
        **plot_layout("Intervalo entre repetições normal → normal", height=430),
        xaxis=dict(title=None, showgrid=False),
        yaxis=dict(title="Nº de repetições", showgrid=True, gridcolor=COLORS["grid"]),
    )
    st.plotly_chart(fig, use_container_width=True)

setor_rep = (
    df.groupby("Setor Solicitante")
    .agg(
        Total=("Flag_Normal", "count"),
        Reps=("Flag_Rep", "sum"),
        Custo_Rep=("Custo_Rep", "sum"),
    )
    .reset_index()
)
setor_rep = setor_rep[setor_rep["Total"] >= 30].copy()
setor_rep["Taxa_Rep"] = (setor_rep["Reps"] / setor_rep["Total"] * 100).round(1)
setor_rep["Classe"] = np.where(setor_rep["Taxa_Rep"] >= setor_rep["Taxa_Rep"].median(), "Alta taxa", "Baixa taxa")

x_med = setor_rep["Reps"].median() if not setor_rep.empty else 0
y_med = setor_rep["Taxa_Rep"].median() if not setor_rep.empty else 0

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=setor_rep["Reps"],
        y=setor_rep["Taxa_Rep"],
        mode="markers+text",
        text=[truncate_text(x, 22) for x in setor_rep["Setor Solicitante"]],
        textposition="top center",
        marker=dict(
            size=np.sqrt(setor_rep["Custo_Rep"].clip(lower=1)) * 2.6,
            color=color_scale_list(setor_rep["Taxa_Rep"], vmin=0, vmax=max(setor_rep["Taxa_Rep"].max(), 1)),
            line=dict(color="white", width=1.2),
            opacity=0.82,
        ),
        customdata=np.stack([setor_rep["Custo_Rep"], setor_rep["Total"]], axis=1),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Repetições: %{x:,}<br>"
            "Taxa: %{y:.1f}%<br>"
            "Custo: R$ %{customdata[0]:,.0f}<br>"
            "Volume total: %{customdata[1]:,}<extra></extra>"
        ),
    )
)

fig.add_vline(x=x_med, line_dash="dot", line_color=COLORS["deep"], opacity=0.45)
fig.add_hline(y=y_med, line_dash="dot", line_color=COLORS["deep"], opacity=0.45)

fig.add_annotation(
    x=x_med * 0.45 if x_med > 0 else 0.5,
    y=y_med * 0.45 if y_med > 0 else 0.5,
    text="Menor prioridade",
    showarrow=False,
    font=dict(size=11, color=COLORS["muted"]),
)

fig.add_annotation(
    x=max(setor_rep["Reps"].max() * 0.82, x_med + 1) if not setor_rep.empty else 1,
    y=max(setor_rep["Taxa_Rep"].max() * 0.92, y_med + 0.2) if not setor_rep.empty else 1,
    text="Alta prioridade",
    showarrow=False,
    font=dict(size=11, color=COLORS["danger_dark"]),
)

fig.update_layout(
    **plot_layout("Setores prioritários · volume × taxa × custo", height=390),
    xaxis=dict(title="Nº de repetições", showgrid=True, gridcolor=COLORS["grid"]),
    yaxis=dict(title="Taxa de repetição (%)", ticksuffix="%", showgrid=True, gridcolor=COLORS["grid"]),
)
st.plotly_chart(fig, use_container_width=True)


# ============================================================
# MÓDULO 3 — JORNADA DO PACIENTE
# ============================================================
section_header("Módulo 3 · Jornada do paciente")

pac = (
    df.groupby("Atendimento")
    .agg(
        Total=("Flag_Normal", "count"),
        Pct_Normal=("Flag_Normal", "mean"),
        Reps=("Flag_Rep", "sum"),
        Criticas=("Flag_Rep_Crit", "sum"),
        Exames_Distintos=("Descrição Exame", "nunique"),
        Custo_Rep=("Custo_Rep", "sum"),
        Primeiro=("DataHoraPedido", "min"),
        Ultimo=("DataHoraPedido", "max"),
        Setor=("Setor Solicitante", lambda x: x.value_counts().idxmax()),
    )
    .reset_index()
)

pac["Pct_Normal"] = (pac["Pct_Normal"] * 100).round(1)
pac["Dias_Internacao"] = (
    (pac["Ultimo"] - pac["Primeiro"]).dt.total_seconds() / 86400
).clip(lower=0).round(1)
pac["Reps_Dia"] = (pac["Reps"] / pac["Dias_Internacao"].replace(0, 0.5)).round(2)


def classificar_perfil(row):
    if row["Total"] == 1:
        return "Pontual"
    if row["Dias_Internacao"] < 1:
        return "Passagem rápida"
    if row["Pct_Normal"] < 40 and row["Reps"] == 0:
        return "Crítico"
    if row["Pct_Normal"] >= 70 and row["Reps_Dia"] >= 1:
        return "Alto desperdício"
    if row["Pct_Normal"] >= 70 and row["Reps"] > 0:
        return "Desperdício moderado"
    if row["Pct_Normal"] >= 70 and row["Reps"] == 0:
        return "Monitoramento adequado"
    return "Misto"


pac["Perfil"] = pac.apply(classificar_perfil, axis=1)

perfil_colors = {
    "Alto desperdício": COLORS["danger_dark"],
    "Desperdício moderado": COLORS["alert"],
    "Misto": COLORS["support_warm"],
    "Crítico": COLORS["deep"],
    "Monitoramento adequado": COLORS["primary"],
    "Passagem rápida": COLORS["support_ice"],
    "Pontual": COLORS["support_sand"],
}

c5, c6 = st.columns([1.15, 0.85])

with c5:
    fig = go.Figure()
    df_scatter = pac[pac["Dias_Internacao"] >= 1].copy()

    for perfil, grupo in df_scatter.groupby("Perfil"):
        fig.add_trace(
            go.Scatter(
                x=grupo["Dias_Internacao"],
                y=grupo["Pct_Normal"],
                mode="markers",
                name=perfil,
                marker=dict(
                    size=np.clip(grupo["Reps"] * 3 + 8, 8, 58),
                    color=perfil_colors.get(perfil, COLORS["support_sand"]),
                    opacity=0.75,
                    line=dict(color="white", width=0.9),
                ),
                customdata=np.stack([grupo["Atendimento"], grupo["Reps"], grupo["Custo_Rep"]], axis=1),
                hovertemplate=(
                    "Atendimento: %{customdata[0]}<br>"
                    "Dias: %{x:.1f}<br>"
                    "Normalidade: %{y:.1f}%<br>"
                    "Repetições: %{customdata[1]:,}<br>"
                    "Custo: R$ %{customdata[2]:,.2f}<extra></extra>"
                ),
            )
        )

    fig.add_hline(y=70, line_dash="dot", line_color=COLORS["primary"], opacity=0.65)
    fig.add_hline(y=40, line_dash="dot", line_color=COLORS["danger"], opacity=0.65)

    fig.update_layout(
        **plot_layout(
            "Perfil da população internada",
            height=410,
            legend=dict(
                orientation="v",
                x=1.01,
                y=0.5,
                bgcolor="rgba(0,0,0,0)",
            ),
        ),
        xaxis=dict(title="Dias de internação", showgrid=True, gridcolor=COLORS["grid"]),
        yaxis=dict(title="Taxa de normalidade (%)", ticksuffix="%", showgrid=True, gridcolor=COLORS["grid"]),
    )
    st.plotly_chart(fig, use_container_width=True)

with c6:
    longos = pac[(pac["Dias_Internacao"] >= 7) & (pac["Total"] >= 20)].copy()
    longos = longos.sort_values("Reps", ascending=False).head(12)

    if not longos.empty:
        longos["Exames_Dia"] = (longos["Total"] / longos["Dias_Internacao"]).round(1)
        longos["Reps_Dia"] = (longos["Reps"] / longos["Dias_Internacao"]).round(2)
        longos = longos.sort_values("Exames_Dia", ascending=True)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=longos["Atendimento"].astype(str),
                x=longos["Exames_Dia"],
                orientation="h",
                name="Exames/dia",
                marker_color=COLORS["support_ice"],
                hovertemplate="Atendimento %{y}<br>Exames/dia: %{x:.1f}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                y=longos["Atendimento"].astype(str),
                x=longos["Reps_Dia"],
                mode="markers+lines",
                name="Repetições/dia",
                marker=dict(size=9, color=COLORS["danger_dark"]),
                line=dict(color=COLORS["danger_dark"], width=2.2),
                hovertemplate="Atendimento %{y}<br>Repetições/dia: %{x:.2f}<extra></extra>",
            )
        )
        fig.update_layout(
            **plot_layout("Internações longas · intensidade assistencial × desperdício", height=410),
            xaxis=dict(title="Frequência diária", showgrid=True, gridcolor=COLORS["grid"]),
            yaxis=dict(title=None, showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem internações com pelo menos 7 dias e 20 exames no filtro atual.")


# ============================================================
# BUSCA DE PACIENTE
# ============================================================
with st.expander("🔎 Buscar linha do tempo de um paciente", expanded=False):
    atendimento_input = st.text_input("Código do atendimento", placeholder="Ex: 12335722")

    if atendimento_input:
        try:
            atendimento_id = int(atendimento_input.strip())
            p = df[df["Atendimento"] == atendimento_id].sort_values("DataHoraPedido").copy()

            if p.empty:
                st.warning("Atendimento não encontrado dentro do filtro selecionado.")
            else:
                info = pac[pac["Atendimento"] == atendimento_id].iloc[0]
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Exames", format_int(info["Total"]))
                m2.metric("% normal", format_pct(info["Pct_Normal"]))
                m3.metric("Repetições", format_int(info["Reps"]))
                m4.metric("Custo repetição", f'R$ {info["Custo_Rep"]:.2f}'.replace(".", ","))

                ordem = (
                    p.groupby("Descrição Exame")["DataHoraPedido"]
                    .min()
                    .sort_values()
                    .index
                    .tolist()
                )
                mapa_y = {ex: i for i, ex in enumerate(ordem)}
                p["y_pos"] = p["Descrição Exame"].map(mapa_y)

                fig = go.Figure()

                for ex in ordem:
                    sub = p[p["Descrição Exame"] == ex].sort_values("DataHoraPedido")
                    if len(sub) > 1:
                        fig.add_trace(
                            go.Scatter(
                                x=sub["DataHoraPedido"],
                                y=[mapa_y[ex]] * len(sub),
                                mode="lines",
                                line=dict(color="#DDE8E2", width=1.5),
                                hoverinfo="skip",
                                showlegend=False,
                            )
                        )

                normais_sub = p[p["Interpretação"] == "NORMAL"]
                alterados_sub = p[p["Interpretação"] != "NORMAL"]
                repetidos_sub = p[p["Flag_Rep"] == 1]

                if not normais_sub.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=normais_sub["DataHoraPedido"],
                            y=normais_sub["y_pos"],
                            mode="markers",
                            name="Normal",
                            marker=dict(
                                size=10,
                                color=COLORS["primary"],
                                line=dict(color="white", width=1.4),
                            ),
                            customdata=[x.title() for x in normais_sub["Descrição Exame"]],
                            hovertemplate="%{customdata}<br>%{x|%d/%m/%Y %H:%M}<extra></extra>",
                        )
                    )

                if not alterados_sub.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=alterados_sub["DataHoraPedido"],
                            y=alterados_sub["y_pos"],
                            mode="markers",
                            name="Alterado",
                            marker=dict(
                                size=10,
                                color=COLORS["deep"],
                                line=dict(color="white", width=1.4),
                            ),
                            customdata=[x.title() for x in alterados_sub["Descrição Exame"]],
                            hovertemplate="%{customdata}<br>%{x|%d/%m/%Y %H:%M}<extra></extra>",
                        )
                    )

                if not repetidos_sub.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=repetidos_sub["DataHoraPedido"],
                            y=repetidos_sub["y_pos"],
                            mode="markers",
                            name="Repetição",
                            marker=dict(
                                size=18,
                                color="rgba(0,0,0,0)",
                                line=dict(color=COLORS["alert"], width=2.7),
                            ),
                            customdata=[x.title() for x in repetidos_sub["Descrição Exame"]],
                            hovertemplate="Repetição<br>%{customdata}<br>%{x|%d/%m/%Y %H:%M}<extra></extra>",
                        )
                    )

                fig.update_layout(
                    **plot_layout(f"Linha do tempo · atendimento {atendimento_id}", height=max(300, len(ordem) * 28 + 110)),
                    xaxis=dict(showgrid=True, gridcolor=COLORS["grid"], title=None),
                    yaxis=dict(
                        title=None,
                        tickvals=list(range(len(ordem))),
                        ticktext=[x.title() for x in ordem],
                        showgrid=False,
                    ),
                )
                st.plotly_chart(fig, use_container_width=True)

        except ValueError:
            st.error("Digite apenas números no código do atendimento.")


# ============================================================
# MÓDULO 4 — ANÁLISE INTEGRADA
# ============================================================
section_header("Módulo 4 · Mapa integrado de priorização")

c7, c8 = st.columns([1, 1])

with c7:
    top_sv = df["Setor Solicitante"].value_counts().head(8).index
    top_ev = df["Descrição Exame"].value_counts().head(10).index

    sub = df[
        (df["Setor Solicitante"].isin(top_sv)) &
        (df["Descrição Exame"].isin(top_ev))
    ].copy()

    piv_taxa = (
        sub.groupby(["Setor Solicitante", "Descrição Exame"])["Flag_Rep"]
        .mean()
        .mul(100)
        .round(1)
        .unstack()
    )

    piv_custo = (
        sub.groupby(["Setor Solicitante", "Descrição Exame"])["Custo_Rep"]
        .sum()
        .round(0)
        .unstack()
        .fillna(0)
    )

    annotations = []
    for i in range(piv_taxa.shape[0]):
        row = []
        for j in range(piv_taxa.shape[1]):
            taxa = piv_taxa.values[i, j]
            custo = piv_custo.values[i, j]
            if pd.isna(taxa):
                row.append("—")
            else:
                row.append(f"{taxa:.0f}%\nR${custo:,.0f}")
        annotations.append(row)

    zmax_heat = 1
    if not np.isnan(piv_taxa.values).all():
        zmax_heat = max(np.nanmax(piv_taxa.values), 1)

    fig = go.Figure(
        go.Heatmap(
            z=piv_taxa.values,
            x=[truncate_text(x.title(), 22) for x in piv_taxa.columns],
            y=[truncate_text(x, 24) for x in piv_taxa.index],
            colorscale=[
                [0.00, "#EFF7F3"],
                [0.30, COLORS["support_mint"]],
                [0.55, COLORS["primary_light"]],
                [0.75, COLORS["alert"]],
                [1.00, COLORS["danger_dark"]],
            ],
            zmin=0,
            zmax=zmax_heat,
            text=annotations,
            texttemplate="%{text}",
            textfont=dict(size=9),
            colorbar=dict(title="Taxa rep. %", ticksuffix="%"),
            hovertemplate="<b>%{y}</b><br>%{x}<br>Taxa: %{z:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        **plot_layout("Taxa de repetição e custo por setor × exame", height=400),
        xaxis=dict(title=None, tickangle=-35),
        yaxis=dict(title=None),
    )
    st.plotly_chart(fig, use_container_width=True)

with c8:
    piv_hora = (
        df[df["Flag_Rep"] == 1]
        .groupby(["DiaSemana", "Hora"])["Flag_Rep"]
        .count()
        .unstack(fill_value=0)
        .reindex(columns=range(24), fill_value=0)
    )

    if not piv_hora.empty:
        idx_presentes = list(piv_hora.index)
        labels_dias = [DIAS_PT[i] for i in idx_presentes]
        z_vals = piv_hora.values
    else:
        labels_dias = DIAS_PT
        z_vals = np.zeros((7, 24))

    fig = go.Figure(
        go.Heatmap(
            z=z_vals,
            x=[f"{h:02d}h" for h in range(24)],
            y=labels_dias,
            colorscale=[
                [0.00, "#F5FBF8"],
                [0.25, COLORS["support_ice"]],
                [0.55, COLORS["primary_light"]],
                [0.78, COLORS["alert"]],
                [1.00, COLORS["danger_dark"]],
            ],
            text=[[str(int(v)) if v > 0 else "" for v in row] for row in z_vals],
            texttemplate="%{text}",
            textfont=dict(size=9),
            colorbar=dict(title="Nº rep."),
            hovertemplate="%{y} · %{x}<br>%{z} repetições<extra></extra>",
        )
    )

    for h in [8, 9, 19, 20]:
        fig.add_vline(x=h - 0.5, line_dash="dash", line_color=COLORS["deep"], opacity=0.35)

    fig.update_layout(
        **plot_layout("Concentração temporal das repetições", height=400),
        xaxis=dict(title=None),
        yaxis=dict(title=None),
    )
    st.plotly_chart(fig, use_container_width=True)

combo = (
    df.groupby(["Setor Solicitante", "Descrição Exame"])
    .agg(
        Total=("Flag_Normal", "count"),
        Reps=("Flag_Rep", "sum"),
        Custo_Rep=("Custo_Rep", "sum"),
        Pct_Normal=("Flag_Normal", "mean"),
    )
    .reset_index()
)
combo = combo[combo["Total"] >= 10].copy()
combo["Taxa_Rep"] = (combo["Reps"] / combo["Total"] * 100).round(1)
combo["Pct_Normal"] = (combo["Pct_Normal"] * 100).round(1)
combo_plot = combo[combo["Reps"] >= 3].copy()

fig = go.Figure(
    go.Scatter(
        x=[truncate_text(x.title(), 20) for x in combo_plot["Descrição Exame"]],
        y=[truncate_text(x, 22) for x in combo_plot["Setor Solicitante"]],
        mode="markers",
        marker=dict(
            size=np.clip(combo_plot["Reps"] * 3 + 10, 10, 72),
            color=color_scale_list(combo_plot["Taxa_Rep"], vmin=0, vmax=max(combo_plot["Taxa_Rep"].max(), 1) if not combo_plot.empty else 1),
            opacity=0.82,
            line=dict(color="white", width=0.9),
        ),
        customdata=np.stack([combo_plot["Taxa_Rep"], combo_plot["Reps"], combo_plot["Custo_Rep"]], axis=1) if not combo_plot.empty else None,
        hovertemplate=(
            "<b>%{y}</b><br>%{x}<br>"
            "Taxa: %{customdata[0]:.1f}%<br>"
            "Repetições: %{customdata[1]:,}<br>"
            "Custo: R$ %{customdata[2]:,.0f}<extra></extra>"
        ),
    )
)
fig.update_layout(
    **plot_layout("Matriz de prioridade operacional", height=500),
    xaxis=dict(title=None, tickangle=-38, showgrid=True, gridcolor=COLORS["grid"]),
    yaxis=dict(title=None, showgrid=True, gridcolor=COLORS["grid"]),
)
st.plotly_chart(fig, use_container_width=True)


# ============================================================
# RODAPÉ
# ============================================================
st.markdown(
    """
    <div class="footer-note">
        Lab Vision · Hospital Unimed · Monitoramento de repetições laboratoriais ·
        Painel redesenhado com foco em leitura executiva, priorização assistencial e impacto financeiro.
    </div>
    """,
    unsafe_allow_html=True,
)