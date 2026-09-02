import pandas as pd

import streamlit as st

import plotly.express as px
 
# Configuração da página

st.set_page_config(

    page_title="Histórico do Spotify entre 2009 e 2025",

    layout="wide"

)
 
st.title("Histórico do Spotify entre 2009 e 2025")

st.write("Realizado por: Karen Farias Menezes, Mariana Marchiori e Luiza Silva Romeiro.\n"
         "\nOrientado por: Felipe Garbin\n",
 "\nEste projeto analisa o histórico musical do Spotify entre 2009 e 2025, utilizando uma base com 8.582 registros de músicas. O objetivo é identificar os principais artistas, gêneros e características das músicas presentes nesse período.")
 
arquivo = "spotify_data clean.csv"
if arquivo is not None:

    df = pd.read_csv(arquivo)

    # === TRATAMENTO DOS DADOS ===

    df.columns = df.columns.str.strip()

    # === IDENTIFICAR COLUNA DE ANO ===

    ano_col = None

    for col in df.columns:

        if any(word in col.lower() for word in ['year', 'ano', 'date', 'release']):

            ano_col = col

            break

    # === FILTRAR APENAS DADOS A PARTIR DE 2009 ===

    if ano_col is not None:

        # Extrair ano da data

        df['ano_filtro'] = pd.to_datetime(df[ano_col], errors='coerce').dt.year

        # Contar registros antes do filtro

        total_antes = len(df)

        # FILTRO PRINCIPAL: APENAS ANOS >= 2009

        df = df[df['ano_filtro'] >= 2009]

        # Remover registros sem ano

        df = df.dropna(subset=['ano_filtro'])

        total_depois = len(df)

        # Mostrar quantos registros foram filtrados

        st.info(f"🎯 Filtrando dados a partir de 2009: {total_depois} registros (de {total_antes} totais)")

    else:

        st.warning("⚠️ Não foi possível identificar a coluna de ano. Os dados serão mostrados sem filtro temporal.")

        # Criar coluna fictícia para evitar erros

        df['ano_filtro'] = None

    # === DIAGNÓSTICO DOS DADOS ===

    st.subheader("Diagnóstico dos dados")

    col_diag1, col_diag2, col_diag3 = st.columns(3)

    col_diag1.metric("Valores ausentes", df.isnull().sum().sum())

    col_diag2.metric("Registros duplicados", df.duplicated().sum())

    col_diag3.metric("Anos disponíveis", f"{df['ano_filtro'].min():.0f} - {df['ano_filtro'].max():.0f}" if df['ano_filtro'].notna().any() else "N/A")

    # === FILTROS ADICIONAIS ===

    st.subheader("🔍 Filtros")

    filtro_col1, filtro_col2, filtro_col3 = st.columns(3)

    # FILTRO 1: Por ano (apenas 2009-2025)

    with filtro_col1:

        if 'ano_filtro' in df.columns and df['ano_filtro'].notna().any():

            anos_disponiveis = sorted(df['ano_filtro'].dropna().unique())

            # Garantir que só mostra de 2009 pra cima

            anos_disponiveis = [ano for ano in anos_disponiveis if ano >= 2009]

            if len(anos_disponiveis) > 0:

                anos_selecionados = st.multiselect(

                    "Selecione os anos (2009-2025)",

                    options=anos_disponiveis,

                    default=anos_disponiveis[-5:] if len(anos_disponiveis) > 5 else anos_disponiveis

                )

            else:

                anos_selecionados = None

        else:

            anos_selecionados = None

    # FILTRO 2: Por gênero

    with filtro_col2:

        if "artist_genres" in df.columns:

            df['genero_principal'] = df['artist_genres'].apply(

                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x

            )

            generos_disponiveis = sorted(df['genero_principal'].dropna().unique())

            if len(generos_disponiveis) > 0:

                generos_selecionados = st.multiselect(

                    "Selecione os gêneros",

                    options=generos_disponiveis,

                    default=generos_disponiveis[:10] if len(generos_disponiveis) > 10 else generos_disponiveis

                )

            else:

                generos_selecionados = None

        else:

            generos_selecionados = None

    # FILTRO 3: Por popularidade

    with filtro_col3:

        if "artist_popularity" in df.columns:

            min_pop = int(df["artist_popularity"].min())

            max_pop = int(df["artist_popularity"].max())

            pop_range = st.slider(

                "Intervalo de popularidade",

                min_value=min_pop,

                max_value=max_pop,

                value=(min_pop, max_pop)

            )

        else:

            pop_range = None

    # === APLICAR FILTROS ===

    df_filtrado = df.copy()

    # Aplicar filtro de ano (já está filtrado >= 2009, mas aplicamos os selecionados)

    if anos_selecionados and len(anos_selecionados) > 0:

        if 'ano_filtro' in df_filtrado.columns:

            df_filtrado = df_filtrado[df_filtrado['ano_filtro'].isin(anos_selecionados)]

    # Aplicar filtro de gênero

    if generos_selecionados and len(generos_selecionados) > 0:

        if 'genero_principal' in df_filtrado.columns:

            df_filtrado = df_filtrado[df_filtrado['genero_principal'].isin(generos_selecionados)]

    # Aplicar filtro de popularidade

    if pop_range:

        if "artist_popularity" in df_filtrado.columns:

            df_filtrado = df_filtrado[

                (df_filtrado["artist_popularity"] >= pop_range[0]) & 

                (df_filtrado["artist_popularity"] <= pop_range[1])

            ]

    st.info(f"📊 Mostrando {len(df_filtrado)} registros de {len(df)} totais")

    # === VISUALIZAÇÃO INICIAL ===

    st.subheader("Visualização dos dados")

    st.dataframe(df_filtrado.head())

    # === MÉTRICAS PRINCIPAIS ===

    col1, col2, col3 = st.columns(3)

    col1.metric(

        "Quantidade de registros",

        f"{len(df_filtrado):,}".replace(",", ".")

    )

    col2.metric(

        "Quantidade de colunas",

        df_filtrado.shape[1]

    )

    if "artist_popularity" in df_filtrado.columns and len(df_filtrado) > 0:

        media_pop = df_filtrado["artist_popularity"].mean()

        col3.metric(

            "Popularidade média",

            f"{media_pop:.1f}"

        )

    # === GRÁFICO 1: Músicas por gênero ===

    st.subheader("Distribuição de músicas por gênero")

    if "artist_genres" in df_filtrado.columns and len(df_filtrado) > 0:

        df_genres = df_filtrado.copy()

        if df_genres["artist_genres"].dtype == object:

            df_genres["genero"] = df_genres["artist_genres"].apply(

                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x

            )

        else:

            df_genres["genero"] = df_genres["artist_genres"]

        genre_counts = df_genres["genero"].value_counts().reset_index()

        genre_counts.columns = ["Gênero", "Quantidade"]

        top_genres = genre_counts.head(20)

        fig1 = px.bar(

            top_genres,

            x="Gênero",

            y="Quantidade",

            title=f"Top 20 gêneros musicais mais frequentes (2009-2025)",

            color="Quantidade",

            color_continuous_scale="Viridis"

        )

        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("""

        **O que podemos observar?**

        Este gráfico mostra os gêneros musicais mais frequentes no período de 2009 a 2025.

        Quanto maior a barra, mais músicas daquele gênero estão presentes.

        """)

    # === GRÁFICO 2: Distribuição de Popularidade ===

    st.subheader("Distribuição da Popularidade dos Artistas (2009-2025)")

    if "artist_popularity" in df_filtrado.columns and len(df_filtrado) > 0:

        fig2 = px.histogram(

            df_filtrado,

            x="artist_popularity",

            title=f"Distribuição da popularidade dos artistas (2009-2025)",

            nbins=20,

            color_discrete_sequence=["#636EFA"]

        )

        fig2.update_layout(

            xaxis_title="Popularidade (0-100)",

            yaxis_title="Quantidade de artistas",

            bargap=0.1

        )

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""

        **O que podemos observar?**

        Este histograma mostra como a popularidade dos artistas está distribuída no período de 2009 a 2025.

        - Picos mais altos indicam faixas de popularidade com mais artistas

        - Permite ver se a maioria dos artistas tem popularidade baixa, média ou alta

        """)

        # Métricas de popularidade

        st.subheader("📊 Estatísticas de Popularidade (2009-2025)")

        pop_col1, pop_col2, pop_col3, pop_col4 = st.columns(4)

        pop_col1.metric("Mínimo", f"{df_filtrado['artist_popularity'].min():.0f}")

        pop_col2.metric("Máximo", f"{df_filtrado['artist_popularity'].max():.0f}")

        pop_col3.metric("Média", f"{df_filtrado['artist_popularity'].mean():.1f}")

        pop_col4.metric("Mediana", f"{df_filtrado['artist_popularity'].median():.1f}")

    # === GRÁFICO 3: Top Artistas ===

    st.subheader("Top Artistas Mais Populares (2009-2025)")

    if "artist_popularity" in df_filtrado.columns and "artist_name" in df_filtrado.columns and len(df_filtrado) > 0:

        artistas_agrupados = df_filtrado.groupby('artist_name')['artist_popularity'].max().reset_index()

        artistas_agrupados = artistas_agrupados.sort_values('artist_popularity', ascending=False)

        top_artists = artistas_agrupados.head(30)

        fig3 = px.bar(

            top_artists,

            x="artist_name",

            y="artist_popularity",

            title=f"Top 30 artistas mais populares (2009-2025)",

            color="artist_popularity",

            color_continuous_scale="Plasma",

            text="artist_popularity"

        )

        fig3.update_layout(

            xaxis_title="Artista",

            yaxis_title="Popularidade (0-100)",

            xaxis_tickangle=-45,

            height=500

        )

        fig3.update_traces(textposition='outside')

        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("""

        **O que podemos observar?**

        Este gráfico mostra os 30 artistas com maior popularidade no período de 2009 a 2025.

        - As barras mais altas indicam artistas mais populares

        - O valor numérico aparece no topo de cada barra

        """)

    # === TABELA COMPLETA ===

    st.subheader("📋 Tabela Completa de Artistas (2009-2025)")

    if "artist_popularity" in df_filtrado.columns and "artist_name" in df_filtrado.columns and len(df_filtrado) > 0:

        tabela_artistas = df_filtrado[['artist_name', 'artist_popularity']].copy()

        colunas_adicionais = []

        for col in ['artist_genres', 'track_name', 'album_name', 'ano_filtro']:

            if col in df_filtrado.columns:

                colunas_adicionais.append(col)

                tabela_artistas[col] = df_filtrado[col]

        tabela_artistas = tabela_artistas.sort_values('artist_popularity', ascending=False)

        tabela_artistas = tabela_artistas.drop_duplicates(subset=['artist_name'], keep='first')

        tabela_artistas = tabela_artistas.reset_index(drop=True)

        tabela_artistas.insert(0, 'Posição', range(1, len(tabela_artistas) + 1))

        st.dataframe(

            tabela_artistas,

            use_container_width=True,

            height=400

        )

        csv = tabela_artistas.to_csv(index=False).encode('utf-8')

        st.download_button(

            label="📥 Baixar tabela completa (CSV)",

            data=csv,

            file_name="artistas_spotify_2009_2025.csv",

            mime="text/csv"

        )

    # === GRÁFICO 4: Tendência temporal ===

    if 'ano_filtro' in df_filtrado.columns and len(df_filtrado) > 0:

        st.subheader("Evolução temporal (2009-2025)")

        tendencia = df_filtrado.groupby('ano_filtro').size().reset_index()

        tendencia.columns = ['Ano', 'Quantidade']

        # Garantir que só mostra de 2009 pra cima

        tendencia = tendencia[tendencia['Ano'] >= 2009]

        fig4 = px.line(

            tendencia,

            x="Ano",

            y="Quantidade",

            title="Quantidade de músicas por ano (2009-2025)",

            markers=True,

            line_shape='linear'

        )

        fig4.update_layout(

            xaxis_title="Ano",

            yaxis_title="Número de músicas",

            xaxis_tickangle=-45

        )

        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("""

        **O que podemos observar?**

        Este gráfico mostra a evolução da quantidade de músicas ao longo dos anos (2009-2025).

        - Permite identificar tendências de crescimento ou declínio

        - Mostra quais anos tiveram mais lançamentos

        """)

    # === BUSCAR REGISTRO ===

    st.subheader("🔍 Buscar registro específico")

    if len(df_filtrado) > 0:

        num_linha = st.number_input(

            "Digite o número da linha (0 = primeira)",

            min_value=0,

            max_value=len(df_filtrado) - 1,

            value=0,

            step=1,

            key="linha_selector"

        )

        col_busca1, col_busca2 = st.columns(2)

        if col_busca1.button("Buscar registro", key="buscar_btn"):

            try:

                registro = df_filtrado.iloc[num_linha]

                col_busca1.success(f"Registro da linha {num_linha} encontrado!")

                col_busca1.dataframe(pd.DataFrame([registro]))

            except IndexError:

                col_busca1.error("Linha não encontrada!")

        if col_busca2.button("Mostrar como métricas", key="metricas_btn"):

            try:

                registro = df_filtrado.iloc[num_linha]

                col_busca2.info(f"Detalhes da linha {num_linha}")

                cols_metricas = col_busca2.columns(3)

                colunas_para_mostrar = [c for c in df_filtrado.columns if c not in ['ano_filtro', 'genero_principal']]

                for i, col in enumerate(colunas_para_mostrar[:3]):

                    if i < 3:

                        cols_metricas[i].metric(

                            label=col,

                            value=registro[col]

                        )

                expander = col_busca2.expander("Ver todos os dados")

                for col in colunas_para_mostrar:

                    expander.write(f"**{col}:** {registro[col]}")

            except IndexError:

                col_busca2.error("Linha não encontrada!")

    else:

        st.warning("Nenhum registro encontrado com os filtros selecionados.")

    # === ESTATÍSTICAS ===

    expander_estatisticas = st.expander("📊 Estatísticas descritivas (2009-2025)")

    if len(df_filtrado) > 0:

        expander_estatisticas.dataframe(df_filtrado.describe())

    else:

        expander_estatisticas.warning("Sem dados para mostrar estatísticas")

    # === INFORMAÇÕES ===

    expander_info = st.expander("ℹ️ Informações das colunas")

    col_info = pd.DataFrame({

        "Coluna": df_filtrado.columns,

        "Tipo": df_filtrado.dtypes.values,

        "Valores nulos": df_filtrado.isnull().sum().values,

        "Valores únicos": df_filtrado.nunique().values

    })

    expander_info.dataframe(col_info)
 
else:

    st.info("👆 Envie um arquivo CSV para começar a análise!")
 
