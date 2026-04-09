"""
╔══════════════════════════════════════════════════════════════════════╗
║  DASHBOARD — MONITORAMENTO LABORATORIAL HU                           ║
║  App Streamlit completo com filtro por setor                         ║
║                                                                      ║
║  EXECUÇÃO LOCAL:                                                     ║
║    pip install streamlit pandas numpy plotly openpyxl matplotlib     ║
║    streamlit run dashboard_lab_hu.py                                 ║
║                                                                       ║
║  COMPARTILHAR VIA STREAMLIT COMMUNITY CLOUD:                         ║
║    1. Suba este arquivo + dados_lab_hu.xlsx no GitHub                ║
║    2. Acesse share.streamlit.io → conecte o repositório              ║
║    3. Gere o link e compartilhe com a equipe                         ║
║                                                                      ║
║  PARA LER DO GOOGLE DRIVE (opcional):                                ║
║    Substitua a função carregar_dados() pela versão                   ║
║    com gspread + service_account ao final deste arquivo.             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")
 
# ─────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "Lab Monitor · HU",
    page_icon   = "🔬",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)
 
# ─────────────────────────────────────────────────────────────────────
# CSS GLOBAL — visual limpo, tipografia refinada, baixo impacto cognitivo
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
 
/* Reset e base */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main { background: #F7F8FA; }
.block-container { padding: 1.5rem 2rem 2rem; max-width: 1600px; }
 
/* Sidebar */
[data-testid="stSidebar"] {
    background: #0D1B2A;
    border-right: 1px solid #1E3A5F;
}
[data-testid="stSidebar"] * { color: #C8D8E8 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #E8F0F8 !important; }
 
/* KPI Cards */
.kpi-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    border-left: 4px solid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s;
    min-height: 96px;
}
.kpi-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.10); }
.kpi-value {
    font-size: 2rem; font-weight: 600; line-height: 1;
    font-family: 'DM Mono', monospace; margin-bottom: 4px;
}
.kpi-label { font-size: 0.78rem; font-weight: 500; text-transform: uppercase;
             letter-spacing: 0.06em; color: #6B7280; margin-bottom: 2px; }
.kpi-sub   { font-size: 0.75rem; color: #9CA3AF; }
 
/* Separador de seção */
.section-title {
    font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.1em; color: #6B7280; margin: 1.8rem 0 0.6rem;
    padding-bottom: 6px; border-bottom: 1px solid #E5E7EB;
}
 
/* Esconder menu e rodapé do Streamlit */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
 
# ─────────────────────────────────────────────────────────────────────
# PALETA E TEMA PLOTLY
# ─────────────────────────────────────────────────────────────────────
C = {
    "normal"   : "#10B981",  # esmeralda
    "alterado" : "#EF4444",  # vermelho
    "rep"      : "#F59E0B",  # âmbar
    "critico"  : "#991B1B",  # borgonha
    "azul"     : "#3B82F6",  # azul
    "cinza"    : "#6B7280",
    "bg"       : "#F7F8FA",
    "card"     : "#FFFFFF",
    "border"   : "#E5E7EB",
}
 
PLOTLY_BASE = dict(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "#FFFFFF",
    font          = dict(family="DM Sans, sans-serif", color="#374151", size=12),
    margin        = dict(l=0, r=0, t=36, b=0),
    hoverlabel    = dict(bgcolor="#1F2937", font_color="#F9FAFB",
                         font_family="DM Mono, monospace", font_size=12),
)
 
CMAP_SEMAFORO = ["#10B981", "#F59E0B", "#EF4444"]   # verde→âmbar→vermelho (para taxas de repetição: maior = pior)
CMAP_NORMALIDADE = ["#EF4444", "#F59E0B", "#10B981"] # vermelho→âmbar→verde (para normalidade: maior = melhor)
 
# ─────────────────────────────────────────────────────────────────────
# CARREGAMENTO E CACHE DE DADOS
# ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Carregando dados…")
def carregar_dados(path: str = "dados_lab_hu.xlsx"):
    """
    Lê as abas 'data' e 'dim_exames' do arquivo Excel.
    Para ler do Google Drive, substitua esta função pela versão
    com gspread documentada no final do arquivo.
    """
    df = pd.read_excel(path, sheet_name="data")
    dim = pd.read_excel(path, sheet_name="dim_exames")
 
    # Padronização
    for col in ["Interpretação", "Descrição Exame", "Setor Solicitante"]:
        df[col] = df[col].astype(str).str.strip().str.upper()
    dim["Descrição Exame"] = dim["Descrição Exame"].astype(str).str.strip().str.upper()
 
    df["DataHoraPedido"] = pd.to_datetime(df["DataHoraPedido"])
    df["Data"]           = df["DataHoraPedido"].dt.date
    df["Hora"]           = df["DataHoraPedido"].dt.hour
    df["DiaSemana"]      = df["DataHoraPedido"].dt.dayofweek
    df["Turno"]          = pd.cut(df["Hora"], bins=[-1,6,12,18,23],
                                   labels=["Madrugada","Manhã","Tarde","Noite"])
 
    # Mapear custo e intervalo a partir da aba dim_exames
    custo_map     = dict(zip(dim["Descrição Exame"], dim["CUSTO_EXAME"]))
    intervalo_map = dict(zip(dim["Descrição Exame"], dim["INTERVALOS_CLINICOS"]))
 
    df["Custo_Unit"]          = df["Descrição Exame"].map(custo_map).fillna(3.50)
    df["Intervalo_Clinico_h"] = df["Descrição Exame"].map(intervalo_map).fillna(24)
    df["Flag_Normal"]         = (df["Interpretação"] == "NORMAL").astype(int)
 
    # Repetições: comparar com resultado anterior do mesmo paciente + exame
    df = df.sort_values(["Atendimento", "Descrição Exame", "DataHoraPedido"])
    g  = df.groupby(["Atendimento", "Descrição Exame"])
    df["Interp_Anterior"]      = g["Interpretação"].shift(1)
    df["DataHora_Anterior"]    = g["DataHoraPedido"].shift(1)
    df["Horas_Desde_Anterior"] = (
        (df["DataHoraPedido"] - df["DataHora_Anterior"]).dt.total_seconds() / 3600
    ).round(1)
 
    df["Flag_Rep"]      = ((df["Interpretação"] == "NORMAL") &
                           (df["Interp_Anterior"] == "NORMAL")).astype(int)
    df["Flag_Rep_Crit"] = ((df["Flag_Rep"] == 1) &
                           (df["Horas_Desde_Anterior"] < df["Intervalo_Clinico_h"])).astype(int)
    df["Custo_Rep"]     = df["Custo_Unit"] * df["Flag_Rep"]
 
    return df
 
# ─────────────────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────────────
def kpi_card(valor, label, sub, cor, prefixo="", sufixo=""):
    return f"""
    <div class="kpi-card" style="border-left-color:{cor}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value" style="color:{cor}">{prefixo}{valor}{sufixo}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""
 
def layout_plotly(**extra):
    cfg = {**PLOTLY_BASE, **extra}
    return cfg
 
def color_scale_semaforo(values, vmin=0, vmax=100, cmap_colors=None):
    """Retorna lista de cores RGB interpoladas. Padrão: verde→âmbar→vermelho (para taxas de repetição).
    Para normalidade, passar cmap_colors=CMAP_NORMALIDADE (vermelho→âmbar→verde)."""
    import matplotlib.colors as mc
    import matplotlib as mpl
    colors = cmap_colors if cmap_colors is not None else CMAP_SEMAFORO
    cmap = mpl.colors.LinearSegmentedColormap.from_list("sem", colors)
    norm = mc.Normalize(vmin=vmin, vmax=vmax)
    return [f"rgb{tuple(int(c*255) for c in cmap(norm(v))[:3])}" for v in values]
 
# ─────────────────────────────────────────────────────────────────────
# SIDEBAR — filtros
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 Lab Monitor")
    st.markdown("---")
 
    df_raw = carregar_dados()
 
    # ── Limites do período disponível nos dados ───────────────────────
    data_min_disp = df_raw["DataHoraPedido"].dt.date.min()
    data_max_disp = df_raw["DataHoraPedido"].dt.date.max()
 
    st.markdown(
        "<div style='font-size:0.75rem;font-weight:600;color:#C8D8E8;"
        "text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px'>"
        "Período</div>",
        unsafe_allow_html=True,
    )
 
    data_inicio = st.date_input(
        "Data inicial",
        value=data_min_disp,
        min_value=data_min_disp,
        max_value=data_max_disp,
        format="DD/MM/YYYY",
        key="data_inicio",
    )
    data_fim = st.date_input(
        "Data final",
        value=data_max_disp,
        min_value=data_min_disp,
        max_value=data_max_disp,
        format="DD/MM/YYYY",
        key="data_fim",
    )
 
    # Validação: data início não pode ser posterior à data fim
    if data_inicio > data_fim:
        st.error("⚠️ A data inicial deve ser anterior ou igual à data final.")
        data_inicio = data_fim
 
    st.markdown("---")
 
    # ── Filtro de setor ───────────────────────────────────────────────
    setores = sorted(df_raw["Setor Solicitante"].unique())
    setor_sel = st.selectbox(
        "Setor Solicitante",
        options=["— Todos os setores —"] + setores,
        index=0,
    )
 
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:0.72rem;color:#4B6A8A;line-height:1.8'>"
        f"Dados disponíveis:<br>"
        f"<b>{data_min_disp.strftime('%d/%m/%Y')}</b> → "
        f"<b>{data_max_disp.strftime('%d/%m/%Y')}</b><br><br>"
        f"Fonte: SIGH / HU<br>"
        f"Custo: SIGTAP/SUS ref."
        f"</div>",
        unsafe_allow_html=True,
    )
 
# ─────────────────────────────────────────────────────────────────────
# FILTRO DE DADOS — período + setor
# ─────────────────────────────────────────────────────────────────────
import datetime
 
df = df_raw[
    (df_raw["DataHoraPedido"].dt.date >= data_inicio) &
    (df_raw["DataHoraPedido"].dt.date <= data_fim)
].copy()
 
if setor_sel != "— Todos os setores —":
    df = df[df["Setor Solicitante"] == setor_sel].copy()
    titulo_setor = setor_sel.title()
else:
    titulo_setor = "Todos os setores"
 
# Rótulo do período selecionado para o cabeçalho
if data_inicio == data_fim:
    titulo_periodo = data_inicio.strftime("%d/%m/%Y")
else:
    titulo_periodo = (
        f"{data_inicio.strftime('%d/%m/%Y')} → {data_fim.strftime('%d/%m/%Y')}"
    )
 
# ─────────────────────────────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────────────────────────────
st.markdown(
    f"<h1 style='font-size:1.5rem;font-weight:600;color:#111827;"
    f"margin:0 0 4px'>Monitoramento Laboratorial</h1>"
    f"<p style='font-size:0.85rem;color:#6B7280;margin:0 0 1.2rem'>"
    f"Hospital Universitário · {titulo_periodo} · <b>{titulo_setor}</b></p>",
    unsafe_allow_html=True,
)
 
# ─────────────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────────────
total    = len(df)
normais  = df["Flag_Normal"].sum()
reps     = int(df["Flag_Rep"].sum())
criticas = int(df["Flag_Rep_Crit"].sum())
custo_m  = df["Custo_Rep"].sum()
custo_a  = custo_m * 12
taxa_n   = normais / total * 100 if total else 0
taxa_r   = reps / total * 100    if total else 0
 
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card(f"{total:,}", "Total de Exames",
                f"{df['Atendimento'].nunique():,} pacientes · {df['Pedido'].nunique():,} pedidos",
                C["azul"]), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card(f"{taxa_n:.1f}", "Taxa de Normalidade",
                f"{normais:,} resultados normais",
                C["normal"], sufixo="%"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card(f"{reps:,}", "Repetições Desnecessárias",
                f"{taxa_r:.1f}% do total · {criticas:,} abaixo do intervalo clínico",
                C["rep"]), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card(f"{custo_m:,.0f}", "Custo/Mês das Repetições",
                f"Projeção anual: R$ {custo_a:,.0f}",
                C["critico"], prefixo="R$ "), unsafe_allow_html=True)
 
# ─────────────────────────────────────────────────────────────────────
# SEÇÃO 1 — NORMALIDADE
# ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Módulo 1 · Normalidade</div>', unsafe_allow_html=True)
 
col_a, col_b = st.columns([1, 1])
 
# ── Gráfico: barras horizontais por exame (M01·C4) ────────────────────
with col_a:
    exame_norm = (df.groupby("Descrição Exame")
        .agg(Total=("Flag_Normal","count"), Normais=("Flag_Normal","sum"))
        .reset_index())
    exame_norm["Pct"] = (exame_norm["Normais"] / exame_norm["Total"] * 100).round(1)
    exame_norm = exame_norm[exame_norm["Total"] >= 5].sort_values("Pct")
 
    cores_e = color_scale_semaforo(exame_norm["Pct"], cmap_colors=CMAP_NORMALIDADE)
    fig_e = go.Figure(go.Bar(
        y=[e.title() for e in exame_norm["Descrição Exame"]],
        x=exame_norm["Pct"],
        orientation="h",
        marker_color=cores_e,
        text=[f"{v:.0f}%" for v in exame_norm["Pct"]],
        textposition="outside",
        hovertemplate="%{y}<br>Normal: %{x:.1f}%<br>n=%{customdata:,}<extra></extra>",
        customdata=exame_norm["Total"],
    ))
    fig_e.add_vline(x=75, line_dash="dot", line_color="#9CA3AF", line_width=1)
    fig_e.update_layout(**layout_plotly(
        title=dict(text="Normalidade por Exame", font_size=13, x=0),
        xaxis=dict(range=[0, 115], showgrid=True, gridcolor="#F3F4F6",
                   ticksuffix="%", title=None),
        yaxis=dict(showgrid=False, title=None, tickfont_size=11),
        height=420,
    ))
    st.plotly_chart(fig_e, use_container_width=True)
 
# ── Heatmap normalidade Setor × Exame (M01·C7) ────────────────────────
with col_b:
    N_S, N_E = 8, 10
    top_set = df["Setor Solicitante"].value_counts().head(N_S).index
    top_exa = df["Descrição Exame"].value_counts().head(N_E).index
    sub_h = df[df["Setor Solicitante"].isin(top_set) & df["Descrição Exame"].isin(top_exa)]
    piv_n = (sub_h.groupby(["Setor Solicitante","Descrição Exame"])["Flag_Normal"]
             .mean().mul(100).round(1).unstack().fillna(np.nan))
 
    lab_set = [s[:28]+"…" if len(s)>28 else s for s in piv_n.index]
    lab_exa = [e.title() for e in piv_n.columns]
 
    fig_h = go.Figure(go.Heatmap(
        z=piv_n.values, x=lab_exa, y=lab_set,
        colorscale=[[0,"#EF4444"],[0.5,"#F59E0B"],[1,"#10B981"]],
        zmin=0, zmax=100,
        text=[[f"{v:.0f}%" if not np.isnan(v) else "—"
               for v in row] for row in piv_n.values],
        texttemplate="%{text}", textfont=dict(size=10),
        colorbar=dict(title="% Normal", ticksuffix="%", len=0.8, thickness=12),
        hovertemplate="<b>%{y}</b><br>%{x}<br>Normal: %{z:.1f}%<extra></extra>",
    ))
    fig_h.update_layout(**layout_plotly(
        title=dict(text="Normalidade — Setor × Exame", font_size=13, x=0),
        xaxis=dict(tickangle=-35, tickfont_size=10, title=None),
        yaxis=dict(tickfont_size=10, title=None),
        height=420,
    ))
    st.plotly_chart(fig_h, use_container_width=True)
 
# Barras empilhadas setor (M01·C6) — largura total
setor_stack = (df.groupby("Setor Solicitante")
    .agg(Total=("Flag_Normal","count"), Normais=("Flag_Normal","sum"))
    .reset_index())
setor_stack["Alterados"] = setor_stack["Total"] - setor_stack["Normais"]
setor_stack["Pct_N"] = (setor_stack["Normais"] / setor_stack["Total"] * 100).round(1)
setor_stack["Pct_A"] = (100 - setor_stack["Pct_N"]).round(1)
setor_stack = setor_stack[setor_stack["Total"] >= 30].sort_values("Pct_N", ascending=False)
lab_st = [s[:32]+"…" if len(s)>32 else s for s in setor_stack["Setor Solicitante"]]
 
fig_st = go.Figure()
fig_st.add_trace(go.Bar(
    y=lab_st, x=setor_stack["Pct_N"], orientation="h",
    name="Normal", marker_color=C["normal"],
    hovertemplate="%{y}<br>Normal: %{x:.1f}%<extra></extra>",
    text=[f"{v:.0f}%" for v in setor_stack["Pct_N"]],
    textposition="inside", textfont=dict(color="white", size=10),
))
fig_st.add_trace(go.Bar(
    y=lab_st, x=setor_stack["Pct_A"], orientation="h",
    name="Alterado", marker_color=C["alterado"],
    hovertemplate="%{y}<br>Alterado: %{x:.1f}%<extra></extra>",
    text=[f"{v:.0f}%" for v in setor_stack["Pct_A"]],
    textposition="inside", textfont=dict(color="white", size=10),
))
fig_st.update_layout(**layout_plotly(
    title=dict(text="Normal vs Alterado por Setor", font_size=13, x=0),
    barmode="stack", xaxis=dict(range=[0,100], ticksuffix="%", showgrid=True,
                                gridcolor="#F3F4F6", title=None),
    yaxis=dict(showgrid=False, title=None, tickfont_size=10),
    legend=dict(orientation="h", x=0, y=1.08, bgcolor="rgba(0,0,0,0)"),
    height=340,
))
st.plotly_chart(fig_st, use_container_width=True)
 
# ─────────────────────────────────────────────────────────────────────
# SEÇÃO 2 — REPETIÇÕES DESNECESSÁRIAS
# ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Módulo 2 · Repetições Desnecessárias</div>',
            unsafe_allow_html=True)
 
rep_df = df[df["Flag_Rep"] == 1].copy()
 
col_c, col_d = st.columns([1, 1])
 
# ── Ranking exames — barras empilhadas por criticidade (M02·C5·C6) ────
with col_c:
    rep_ex = (df.groupby("Descrição Exame").agg(
        Total=("Flag_Normal","count"),
        Reps=("Flag_Rep","sum"),
        Criticas=("Flag_Rep_Crit","sum"),
        Custo_Rep=("Custo_Rep","sum"),
    ).reset_index())
    rep_ex["Outras"] = rep_ex["Reps"] - rep_ex["Criticas"]
    rep_ex["Taxa_R"] = (rep_ex["Reps"] / rep_ex["Total"] * 100).round(1)
    rep_ex = rep_ex[rep_ex["Reps"] > 0].sort_values("Reps")
 
    fig_re = go.Figure()
    fig_re.add_trace(go.Bar(
        y=[e.title() for e in rep_ex["Descrição Exame"]],
        x=rep_ex["Outras"], orientation="h",
        name="Alerta/Atenção", marker_color=C["rep"],
        hovertemplate="%{y}<br>Repetições: %{x:,}<extra></extra>",
    ))
    fig_re.add_trace(go.Bar(
        y=[e.title() for e in rep_ex["Descrição Exame"]],
        x=rep_ex["Criticas"], orientation="h",
        name="Críticas", marker_color=C["critico"],
        hovertemplate="%{y}<br>Críticas: %{x:,}<extra></extra>",
    ))
    fig_re.update_layout(**layout_plotly(
        title=dict(text="Repetições por Exame — Criticidade", font_size=13, x=0),
        barmode="stack",
        xaxis=dict(title=None, showgrid=True, gridcolor="#F3F4F6"),
        yaxis=dict(title=None, tickfont_size=10, showgrid=False),
        legend=dict(
            orientation="h", x=0.5, y=-0.18, xanchor="center",
            bgcolor="rgba(0,0,0,0)", font_size=11,
        ),
        annotations=[dict(
            text=(
                "<b>Críticas:</b> repetição Normal→Normal dentro do intervalo clínico mínimo do exame<br>"
                "<b>Alerta/Atenção:</b> repetição Normal→Normal com intervalo acima do mínimo, mas ainda suspeita"
            ),
            xref="paper", yref="paper", x=0, y=-0.30,
            xanchor="left", yanchor="top",
            showarrow=False,
            font=dict(size=10, color="#6B7280"),
            align="left",
        )],
        margin=dict(l=0, r=0, t=36, b=90),
        height=460,
    ))
    st.plotly_chart(fig_re, use_container_width=True)
 
# ── Distribuição de intervalos (M02·C9) ───────────────────────────────
with col_d:
    bins   = [0, 6, 12, 24, 48, 72, 168, 9999]
    labels = ["<6h", "6–12h", "12–24h", "24–48h", "48–72h", "3–7d", ">7d"]
    cores_int = [C["critico"], C["alterado"], C["rep"], C["rep"],
                 "#A3A3A3", "#6B7280", "#4B5563"]
 
    if len(rep_df):
        rep_df["Faixa"] = pd.cut(rep_df["Horas_Desde_Anterior"],
                                   bins=bins, labels=labels, right=False)
        dist = rep_df["Faixa"].value_counts().reindex(labels).fillna(0).astype(int)
    else:
        dist = pd.Series(0, index=labels)
 
    fig_di = go.Figure(go.Bar(
        x=labels, y=dist.values,
        marker_color=cores_int,
        text=dist.values,
        textposition="outside",
        hovertemplate="Intervalo: %{x}<br>Repetições: %{y:,}<extra></extra>",
    ))
    fig_di.update_layout(**layout_plotly(
        title=dict(text="Intervalo entre Repetições Normal→Normal", font_size=13, x=0),
        xaxis=dict(title=None, showgrid=False),
        yaxis=dict(title="Nº de Repetições", showgrid=True, gridcolor="#F3F4F6"),
        height=420,
    ))
    st.plotly_chart(fig_di, use_container_width=True)
 
# ── Bolhas: setor — volume × taxa × custo (M02·C8) ───────────────────
setor_rep = (df.groupby("Setor Solicitante").agg(
    Total=("Flag_Normal","count"),
    Reps=("Flag_Rep","sum"),
    Custo_Rep=("Custo_Rep","sum"),
).reset_index())
setor_rep = setor_rep[setor_rep["Total"] >= 30].copy()
setor_rep["Taxa_R"] = (setor_rep["Reps"] / setor_rep["Total"] * 100).round(1)
lab_sr = [s[:28]+"…" if len(s)>28 else s for s in setor_rep["Setor Solicitante"]]
cores_sr = color_scale_semaforo(setor_rep["Taxa_R"], vmin=0,
                                 vmax=setor_rep["Taxa_R"].max() or 1)
 
fig_bo = go.Figure(go.Scatter(
    x=setor_rep["Reps"], y=setor_rep["Taxa_R"],
    mode="markers+text",
    marker=dict(
        size=np.sqrt(setor_rep["Custo_Rep"] + 1) * 2.5,
        color=cores_sr, opacity=0.80,
        line=dict(color="white", width=1),
    ),
    text=lab_sr, textposition="top center", textfont=dict(size=9),
    customdata=np.stack([setor_rep["Custo_Rep"], setor_rep["Total"]], axis=1),
    hovertemplate=(
        "<b>%{text}</b><br>"
        "Repetições: %{x:,}<br>"
        "Taxa: %{y:.1f}%<br>"
        "Custo: R$ %{customdata[0]:,.0f}<extra></extra>"
    ),
))
fig_bo.update_layout(**layout_plotly(
    title=dict(text="Setores — Volume × Taxa de Repetição  (tamanho = custo)", font_size=13, x=0),
    xaxis=dict(title="Nº de Repetições Desnecessárias", showgrid=True, gridcolor="#F3F4F6"),
    yaxis=dict(title="Taxa de Repetição (%)", ticksuffix="%", showgrid=True, gridcolor="#F3F4F6"),
    annotations=[dict(
        text=(
            "Repetição Desnecessária: mesmo exame repetido para o mesmo paciente com resultado Normal "
            "anterior, sem ocorrência de resultado Alterado entre as coletas."
        ),
        xref="paper", yref="paper", x=0.5, y=-0.16,
        xanchor="center", yanchor="top",
        showarrow=False,
        font=dict(size=10, color="#6B7280"),
        align="center",
    )],
    margin=dict(l=0, r=0, t=36, b=70),
    height=420,
))
st.plotly_chart(fig_bo, use_container_width=True)
 
# ─────────────────────────────────────────────────────────────────────
# SEÇÃO 3 — JORNADA DO PACIENTE
# ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Módulo 3 · Jornada do Paciente</div>',
            unsafe_allow_html=True)
 
# Perfil por paciente
pac = (df.groupby("Atendimento").agg(
    Total=("Flag_Normal","count"),
    Pct_N=("Flag_Normal","mean"),
    Reps=("Flag_Rep","sum"),
    Criticas=("Flag_Rep_Crit","sum"),
    Ex_Dist=("Descrição Exame","nunique"),
    Custo_Rep=("Custo_Rep","sum"),
    Primeiro=("DataHoraPedido","min"),
    Ultimo=("DataHoraPedido","max"),
    Setor=("Setor Solicitante", lambda x: x.value_counts().idxmax()),
).reset_index())
pac["Pct_N"]   = (pac["Pct_N"] * 100).round(1)
pac["Dias"]    = ((pac["Ultimo"] - pac["Primeiro"]).dt.total_seconds() / 86400).clip(lower=0).round(1)
pac["Rep_Dia"] = (pac["Reps"] / pac["Dias"].replace(0, 0.5)).round(2)
 
def perfil(r):
    if r["Total"] == 1:                                  return "Pontual"
    if r["Dias"] < 1:                                    return "Passagem rápida"
    if r["Pct_N"] < 40 and r["Reps"] == 0:              return "Crítico"
    if r["Pct_N"] >= 70 and r["Rep_Dia"] >= 1:          return "Alto desperdício"
    if r["Pct_N"] >= 70 and r["Reps"] > 0:              return "Desperdício moderado"
    if r["Pct_N"] >= 70 and r["Reps"] == 0:             return "Monitoramento adequado"
    return                                                        "Misto"
 
pac["Perfil"] = pac.apply(perfil, axis=1)
 
CORES_PERFIL = {
    "Alto desperdício"    : C["critico"],
    "Desperdício moderado": C["alterado"],
    "Misto"               : C["rep"],
    "Crítico"             : "#7C3AED",
    "Monitoramento adequado": C["normal"],
    "Passagem rápida"     : "#9CA3AF",
    "Pontual"             : "#D1D5DB",
}
 
col_e, col_f = st.columns([1.2, 0.8])
 
# ── Mapa de dispersão população (M03·C5) ──────────────────────────────
with col_e:
    fig_sc = go.Figure()
    for perf, grupo in pac[pac["Dias"] >= 1].groupby("Perfil"):
        fig_sc.add_trace(go.Scatter(
            x=grupo["Dias"], y=grupo["Pct_N"],
            mode="markers",
            name=perf,
            marker=dict(
                size=np.clip(grupo["Reps"] * 3 + 8, 8, 60),
                color=CORES_PERFIL.get(perf, "#9CA3AF"),
                opacity=0.60, line=dict(color="white", width=0.5),
            ),
            customdata=np.stack([grupo["Atendimento"], grupo["Reps"],
                                  grupo["Custo_Rep"]], axis=1),
            hovertemplate=(
                "Atendimento: %{customdata[0]}<br>"
                "Dias: %{x:.1f}<br>Normal: %{y:.1f}%<br>"
                "Repetições: %{customdata[1]:,}<br>"
                "Custo: R$ %{customdata[2]:.2f}<extra></extra>"
            ),
        ))
    fig_sc.add_hline(y=70, line_dash="dot", line_color="#10B981", line_width=1,
                     annotation_text="70% normal", annotation_font_color="#10B981")
    fig_sc.add_hline(y=40, line_dash="dot", line_color="#EF4444", line_width=1,
                     annotation_text="40% normal", annotation_font_color="#EF4444")
 
    # Descrição dos perfis como anotação na base do gráfico
    desc_perfis = (
        "<b>Alto desperdício:</b> ≥70% Normal e ≥1 rep./dia — solicitação rotineira sem revisão de resultado &nbsp;|&nbsp; "
        "<b>Desperdício moderado:</b> ≥70% Normal com repetições, mas ritmo controlado &nbsp;|&nbsp; "
        "<b>Misto:</b> perfil intermediário — normal e repetições coexistem &nbsp;|&nbsp; "
        "<b>Crítico:</b> <40% Normal sem repetições — monitoramento clinicamente justificado &nbsp;|&nbsp; "
        "<b>Monitoramento adequado:</b> ≥70% Normal sem repetições &nbsp;|&nbsp; "
        "<b>Passagem rápida:</b> múltiplos exames no mesmo dia &nbsp;|&nbsp; "
        "<b>Pontual:</b> único exame no atendimento"
    )
 
    fig_sc.update_layout(**layout_plotly(
        title=dict(text="Perfil da População — Normal × Dias de Internação", font_size=13, x=0),
        xaxis=dict(title="Dias de internação", showgrid=True, gridcolor="#F3F4F6"),
        yaxis=dict(title="Taxa de normalidade (%)", ticksuffix="%",
                   showgrid=True, gridcolor="#F3F4F6"),
        legend=dict(orientation="h", x=0, y=1.06, bgcolor="rgba(0,0,0,0)", font_size=10),
        annotations=[dict(
            text=desc_perfis,
            xref="paper", yref="paper", x=0, y=-0.22,
            xanchor="left", yanchor="top",
            showarrow=False,
            font=dict(size=9, color="#6B7280"),
            align="left",
        )],
        margin=dict(l=0, r=0, t=36, b=110),
        height=480,
    ))
    st.plotly_chart(fig_sc, use_container_width=True)
 
# ── Comparativo exames/dia top internações (M03·C11) ──────────────────
with col_f:
    long_pac = (pac[(pac["Dias"] >= 7) & (pac["Total"] >= 20)]
                .sort_values("Reps", ascending=False).head(12))
    if len(long_pac):
        long_pac = long_pac.copy()
        long_pac["Ex_Dia"]   = (long_pac["Total"] / long_pac["Dias"]).round(1)
        long_pac["Rep_Dia2"] = (long_pac["Reps"]  / long_pac["Dias"]).round(2)
 
        # Forçar string com prefixo para evitar interpretação numérica pelo Plotly
        atend_labels = ["Atend. " + str(a) for a in long_pac["Atendimento"].tolist()]
 
        fig_ld = go.Figure()
        fig_ld.add_trace(go.Bar(
            x=atend_labels,
            y=long_pac["Ex_Dia"],
            name="Exames / dia",
            marker=dict(color=C["azul"], opacity=0.90, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Exames/dia: %{y:.1f}<extra></extra>",
        ))
        fig_ld.add_trace(go.Bar(
            x=atend_labels,
            y=long_pac["Rep_Dia2"],
            name="Repetições / dia",
            marker=dict(color=C["rep"], opacity=0.95, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Repetições/dia: %{y:.2f}<extra></extra>",
        ))
        fig_ld.update_layout(**layout_plotly(
            title=dict(
                text="Internações ≥7d — Intensidade Assistencial vs Desperdício",
                font_size=13, x=0,
            ),
            barmode="group",
            bargap=0.25,
            bargroupgap=0.08,
            xaxis=dict(
                type="category",          # garante eixo discreto — barras largas
                title="Código de Atendimento",
                tickangle=-40,
                tickfont=dict(size=9),
                showgrid=False,
                categoryorder="array",
                categoryarray=atend_labels,
            ),
            yaxis=dict(
                title="Média por dia de internação",
                showgrid=True,
                gridcolor="#F3F4F6",
                rangemode="tozero",
            ),
            legend=dict(
                orientation="h", x=0.5, xanchor="center",
                y=1.06, bgcolor="rgba(0,0,0,0)", font_size=11,
            ),
            margin=dict(l=0, r=0, t=48, b=60),
            height=420,
        ))
        st.plotly_chart(fig_ld, use_container_width=True)
    else:
        st.info("Sem internações ≥ 7 dias no filtro selecionado.")
 
# ── Busca interativa de paciente (M03·C10) ────────────────────────────
with st.expander("🔍  Buscar linha do tempo de um paciente", expanded=False):
    atend_input = st.text_input("Código de atendimento", placeholder="Ex: 12335722")
    if atend_input:
        try:
            atend_id = int(atend_input.strip())
            p = df[df["Atendimento"] == atend_id].sort_values("DataHoraPedido")
            if p.empty:
                st.warning("Atendimento não encontrado no filtro atual.")
            else:
                info = pac[pac["Atendimento"] == atend_id].iloc[0]
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Exames totais", f"{int(info['Total'])}")
                m2.metric("% Normal",      f"{info['Pct_N']:.1f}%")
                m3.metric("Repetições",    f"{int(info['Reps'])}")
                m4.metric("Custo rep.",    f"R$ {info['Custo_Rep']:.2f}")
 
                # Linha do tempo
                ordem = p.groupby("Descrição Exame")["DataHoraPedido"].min().sort_values().index.tolist()
                p["y_pos"] = p["Descrição Exame"].map({e: i for i, e in enumerate(ordem)})
 
                fig_lt = go.Figure()
                # Linha de conexão por exame
                for ex in ordem:
                    sub = p[p["Descrição Exame"] == ex].sort_values("DataHoraPedido")
                    if len(sub) > 1:
                        fig_lt.add_trace(go.Scatter(
                            x=sub["DataHoraPedido"], y=[ordem.index(ex)]*len(sub),
                            mode="lines", line=dict(color="#E5E7EB", width=1.5),
                            showlegend=False, hoverinfo="skip",
                        ))
                # Pontos
                for interp, cor, nome in [("NORMAL", C["normal"], "Normal"),
                                          ("ALTERADO", C["alterado"], "Alterado")]:
                    sub = p[p["Interpretação"] == interp]
                    if len(sub):
                        fig_lt.add_trace(go.Scatter(
                            x=sub["DataHoraPedido"], y=sub["y_pos"],
                            mode="markers", name=nome,
                            marker=dict(size=10, color=cor,
                                        line=dict(color="white", width=1.5)),
                            hovertemplate="%{customdata}<br>%{x|%d/%m %H:%M}<extra></extra>",
                            customdata=[e.title() for e in sub["Descrição Exame"]],
                        ))
                # Repetições
                rep_p = p[p["Flag_Rep"] == 1]
                if len(rep_p):
                    fig_lt.add_trace(go.Scatter(
                        x=rep_p["DataHoraPedido"], y=rep_p["y_pos"],
                        mode="markers", name="Repetição",
                        marker=dict(size=18, color="rgba(0,0,0,0)",
                                    line=dict(color=C["rep"], width=2.5)),
                        hovertemplate="⚠ Repetição<br>%{customdata}<extra></extra>",
                        customdata=[e.title() for e in rep_p["Descrição Exame"]],
                    ))
                fig_lt.update_layout(**layout_plotly(
                    title=dict(text=f"Linha do Tempo · Atendimento {atend_id}", font_size=13, x=0),
                    yaxis=dict(tickvals=list(range(len(ordem))),
                               ticktext=[e.title() for e in ordem],
                               tickfont_size=10, showgrid=False),
                    xaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
                    legend=dict(orientation="h", x=0, y=1.05, bgcolor="rgba(0,0,0,0)"),
                    height=max(280, len(ordem)*26 + 80),
                    plot_bgcolor="#FAFAFA",
                ))
                st.plotly_chart(fig_lt, use_container_width=True)
        except ValueError:
            st.error("Digite apenas o número do atendimento.")
 
# ─────────────────────────────────────────────────────────────────────
# SEÇÃO 4 — ANÁLISE INTEGRADA
# ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Módulo 4 · Análise Integrada</div>',
            unsafe_allow_html=True)
 
col_g, col_h = st.columns([1, 1])
 
# ── Heatmap combinações Setor × Exame — taxa de repetição (M04·C8) ────
with col_g:
    top_sv = df["Setor Solicitante"].value_counts().head(8).index
    top_ev = df["Descrição Exame"].value_counts().head(10).index
    sub_c  = df[df["Setor Solicitante"].isin(top_sv) & df["Descrição Exame"].isin(top_ev)]
    piv_r  = (sub_c.groupby(["Setor Solicitante","Descrição Exame"])["Flag_Rep"]
              .mean().mul(100).round(1).unstack().fillna(np.nan))
    piv_cu = (sub_c.groupby(["Setor Solicitante","Descrição Exame"])["Custo_Rep"]
              .sum().round(0).unstack().fillna(0))
 
    lab_sv = [s[:26]+"…" if len(s)>26 else s for s in piv_r.index]
    annot  = [[f"{piv_r.values[i,j]:.0f}%\nR${piv_cu.values[i,j]:,.0f}"
               if not np.isnan(piv_r.values[i,j]) else "—"
               for j in range(piv_r.shape[1])]
              for i in range(piv_r.shape[0])]
 
    fig_hc = go.Figure(go.Heatmap(
        z=piv_r.values, x=[e.title() for e in piv_r.columns], y=lab_sv,
        colorscale=[[0,"#F0FDF4"],[0.4,"#FEF9C3"],[0.7,"#FEE2E2"],[1,"#7F1D1D"]],
        zmin=0, zmax=85,
        text=annot, texttemplate="%{text}", textfont=dict(size=9),
        colorbar=dict(title="Taxa Rep. %", ticksuffix="%", len=0.9, thickness=12),
        hovertemplate="<b>%{y}</b><br>%{x}<br>Taxa: %{z:.1f}%<extra></extra>",
    ))
    fig_hc.update_layout(**layout_plotly(
        title=dict(text="Taxa de Repetição (%) + Custo (R$) — Setor × Exame", font_size=13, x=0),
        xaxis=dict(tickangle=-35, tickfont_size=10, title=None),
        yaxis=dict(tickfont_size=10, title=None),
        height=380,
    ))
    st.plotly_chart(fig_hc, use_container_width=True)
 
# ── Heatmap temporal Hora × Dia (M04·C9) ─────────────────────────────
with col_h:
    DIAS_PT = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]
    piv_t   = (df[df["Flag_Rep"]==1]
               .groupby(["DiaSemana","Hora"])["Flag_Rep"].count()
               .unstack(fill_value=0)
               .reindex(columns=range(24), fill_value=0))
    piv_t.index = [DIAS_PT[i] for i in piv_t.index]
 
    fig_ht = go.Figure(go.Heatmap(
        z=piv_t.values, x=[f"{h:02d}h" for h in range(24)], y=DIAS_PT,
        colorscale=[[0,"#EFF6FF"],[0.3,"#3B82F6"],[0.7,"#EF4444"],[1,"#7F1D1D"]],
        text=[[str(int(v)) if v>0 else "" for v in row] for row in piv_t.values],
        texttemplate="%{text}", textfont=dict(size=9),
        colorbar=dict(title="Nº Rep.", len=0.9, thickness=12),
        hovertemplate="%{y} %{x}<br>%{z} repetições<extra></extra>",
    ))
    # Linhas de pico
    for h_pk in [8, 9, 19, 20]:
        fig_ht.add_vline(x=h_pk-0.5, line_dash="dash",
                          line_color=C["rep"], line_width=1, opacity=0.6)
    fig_ht.update_layout(**layout_plotly(
        title=dict(text="Concentração Temporal das Repetições — Hora × Dia", font_size=13, x=0),
        xaxis=dict(tickfont_size=9, title=None),
        yaxis=dict(tickfont_size=10, title=None),
        height=380,
    ))
    st.plotly_chart(fig_ht, use_container_width=True)
 
# ── Matriz de prioridade — bolhas Setor × Exame (M04·C11) ────────────
combo = (df.groupby(["Setor Solicitante","Descrição Exame"]).agg(
    Total=("Flag_Normal","count"),
    Reps=("Flag_Rep","sum"),
    Custo_Rep=("Custo_Rep","sum"),
    Pct_N=("Flag_Normal","mean"),
).reset_index())
combo = combo[combo["Total"] >= 10].copy()
combo["Taxa_R"] = (combo["Reps"] / combo["Total"] * 100).round(1)
combo["Pct_N"]  = (combo["Pct_N"] * 100).round(1)
combo_plot = combo[combo["Reps"] >= 3]
 
cores_cb = color_scale_semaforo(combo_plot["Taxa_R"], vmin=0, vmax=85)
fig_mb = go.Figure(go.Scatter(
    x=[e.title() for e in combo_plot["Descrição Exame"]],
    y=[s[:24]+"…" if len(s)>24 else s for s in combo_plot["Setor Solicitante"]],
    mode="markers",
    marker=dict(
        size=np.clip(combo_plot["Reps"] * 3 + 10, 10, 70),
        color=cores_cb, opacity=0.80,
        line=dict(color="white", width=0.8),
    ),
    customdata=np.stack([combo_plot["Taxa_R"], combo_plot["Reps"],
                          combo_plot["Custo_Rep"]], axis=1),
    hovertemplate=(
        "<b>%{y}</b><br>%{x}<br>"
        "Taxa: %{customdata[0]:.1f}%<br>"
        "Repetições: %{customdata[1]:,}<br>"
        "Custo: R$ %{customdata[2]:,.0f}<extra></extra>"
    ),
))
fig_mb.update_layout(**layout_plotly(
    title=dict(text="Matriz de Prioridade — Setor × Exame  (tamanho = nº repetições · cor = taxa)",
               font_size=13, x=0),
    xaxis=dict(tickangle=-40, tickfont_size=10, showgrid=True, gridcolor="#F3F4F6", title=None),
    yaxis=dict(tickfont_size=10, showgrid=True, gridcolor="#F3F4F6", title=None),
    height=480,
    plot_bgcolor="#FAFAFA",
))
st.plotly_chart(fig_mb, use_container_width=True)
 
# ─────────────────────────────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<hr style='border:none;border-top:1px solid #E5E7EB;margin:2rem 0 0.8rem'>"
    "<p style='font-size:0.72rem;color:#9CA3AF;text-align:center'>"
    "Lab Monitor · Hospital Universitário · Dados: SIGH/HU · Referência de custos: SIGTAP/SUS"
    "</p>",
    unsafe_allow_html=True,
)