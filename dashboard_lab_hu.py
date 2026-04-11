with st.expander("🔎 Buscar linha do tempo de um paciente", expanded=False):
    atendimento_input = st.text_input("Código do atendimento", placeholder="Ex: 12335722")

    if atendimento_input:
        atendimento_input = atendimento_input.strip()

        if not atendimento_input.isdigit():
            st.error("Digite apenas números no código do atendimento.")
        else:
            atendimento_id = int(atendimento_input)

            p = df[df["Atendimento"] == atendimento_id].sort_values("DataHoraPedido").copy()

            if p.empty:
                st.warning("Atendimento não encontrado dentro do filtro selecionado.")
            else:
                info = pac[pac["Atendimento"] == atendimento_id].iloc[0]
                dias_int = float(info["Dias_Internacao"]) if pd.notna(info["Dias_Internacao"]) else 0.0

                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Exames", format_int(info["Total"]))
                m2.metric("% normal", format_pct(info["Pct_Normal"]))
                m3.metric("Repetições", format_int(info["Reps"]))
                m4.metric("Custo repetição", f'R$ {info["Custo_Rep"]:.2f}'.replace(".", ","))
                m5.metric("Dias de internação", f"{dias_int:.1f}".replace(".", ","))

                ordem = (
                    p.groupby("Descrição Exame")["DataHoraPedido"]
                    .min()
                    .sort_values()
                    .index
                    .tolist()
                )

                if not ordem:
                    st.warning("Não há exames suficientes para montar a linha do tempo.")
                else:
                    mapa_y = {ex: i for i, ex in enumerate(ordem)}
                    p["y_pos"] = p["Descrição Exame"].map(mapa_y)

                    resumo_exame = (
                        p.groupby("Descrição Exame")
                        .agg(
                            Total_Exames=("Descrição Exame", "count"),
                            Pct_Normal=("Flag_Normal", "mean"),
                        )
                        .reindex(ordem)
                        .reset_index()
                    )

                    resumo_exame["Total_Exames"] = resumo_exame["Total_Exames"].fillna(0)
                    resumo_exame["Pct_Normal"] = (resumo_exame["Pct_Normal"].fillna(0) * 100).round(0)

                    resumo_exame["Resumo"] = resumo_exame.apply(
                        lambda r: f"{int(r['Total_Exames'])} | {int(r['Pct_Normal'])}%",
                        axis=1
                    )

                    tickvals_y = list(range(len(ordem)))
                    ticktext_y_left = [e.title() for e in ordem]
                    ticktext_y_right = resumo_exame["Resumo"].tolist()

                    x_min = pd.to_datetime(p["DataHoraPedido"].min())
                    x_max = pd.to_datetime(p["DataHoraPedido"].max())
                    tickvals_x, ticktext_x = build_pt_ticks(x_min, x_max)

                    st.markdown(
                        f"""<div class="chart-title-center">Linha do tempo · atendimento {atendimento_id}</div>""",
                        unsafe_allow_html=True,
                    )

                    fig = go.Figure()

                    # Linhas por exame
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
                                    size=9,
                                    color=COLORS["primary"],
                                    line=dict(color="white", width=1.3),
                                ),
                                customdata=np.stack(
                                    [
                                        normais_sub["Descrição Exame"].str.title(),
                                        normais_sub["Horas_Desde_Anterior"].fillna(0),
                                    ],
                                    axis=1
                                ),
                                hovertemplate=(
                                    "%{customdata[0]}<br>"
                                    "%{x|%d/%m/%Y %H:%M}<br>"
                                    "Horas desde anterior: %{customdata[1]:.1f}<extra></extra>"
                                ),
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
                                    size=9,
                                    color=COLORS["danger"],
                                    line=dict(color="white", width=1.3),
                                ),
                                customdata=np.stack(
                                    [
                                        alterados_sub["Descrição Exame"].str.title(),
                                        alterados_sub["Horas_Desde_Anterior"].fillna(0),
                                    ],
                                    axis=1
                                ),
                                hovertemplate=(
                                    "%{customdata[0]}<br>"
                                    "%{x|%d/%m/%Y %H:%M}<br>"
                                    "Horas desde anterior: %{customdata[1]:.1f}<extra></extra>"
                                ),
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
                                    line=dict(color=COLORS["alert"], width=2.5),
                                ),
                                customdata=np.stack(
                                    [
                                        repetidos_sub["Descrição Exame"].str.title(),
                                        repetidos_sub["Horas_Desde_Anterior"].fillna(0),
                                    ],
                                    axis=1
                                ),
                                hovertemplate=(
                                    "Repetição<br>"
                                    "%{customdata[0]}<br>"
                                    "%{x|%d/%m/%Y %H:%M}<br>"
                                    "Horas desde anterior: %{customdata[1]:.1f}<extra></extra>"
                                ),
                            )
                        )

                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(255,255,255,0.76)",
                        font=dict(family="Inter, sans-serif", size=12, color=COLORS["text"]),
                        margin=dict(l=8, r=8, t=75, b=8),
                        height=max(340, len(ordem) * 28 + 130),
                        hoverlabel=dict(
                            bgcolor=COLORS["deep"],
                            font_color=COLORS["white"],
                            font_size=12,
                            font_family="Inter, sans-serif",
                        ),
                        legend=dict(
                            orientation="h",
                            x=0.5,
                            xanchor="center",
                            y=1.03,
                            yanchor="bottom",
                            bgcolor="rgba(0,0,0,0)",
                        ),
                        xaxis=dict(
                            title=None,
                            showgrid=True,
                            gridcolor=COLORS["grid"],
                            tickmode="array",
                            tickvals=tickvals_x,
                            ticktext=ticktext_x,
                        ),
                        yaxis=dict(
                            title=None,
                            tickvals=tickvals_y,
                            ticktext=ticktext_y_left,
                            showgrid=False,
                        ),
                        yaxis2=dict(
                            title="Qtde | % Normal",
                            tickvals=tickvals_y,
                            ticktext=ticktext_y_right,
                            overlaying="y",
                            side="right",
                            showgrid=False,
                            tickfont=dict(color=COLORS["muted"], size=10),
                            titlefont=dict(color=COLORS["muted"], size=11),
                        ),
                    )

                    st.plotly_chart(fig, use_container_width=True)