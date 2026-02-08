import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Dashboard B3 Pro", layout="wide", page_icon="📈")
st.title("📈 Dashboard B3: Análise & Monitoramento")

# --- BANCO DE DADOS MESTRE (NOME + SETOR) ---
DADOS_EMPRESAS = {
    "PETR4.SA": {"nome": "Petrobras PN", "setor": "Petróleo & Gás"},
    "PETR3.SA": {"nome": "Petrobras ON", "setor": "Petróleo & Gás"},
    "PRIO3.SA": {"nome": "Prio (PetroRio)", "setor": "Petróleo & Gás"},
    "VALE3.SA": {"nome": "Vale S.A.", "setor": "Mineração"},
    "GGBR4.SA": {"nome": "Gerdau", "setor": "Siderurgia"},
    "CSNA3.SA": {"nome": "CSN", "setor": "Siderurgia"},
    "USIM5.SA": {"nome": "Usiminas", "setor": "Siderurgia"},
    "ITUB4.SA": {"nome": "Itaú Unibanco", "setor": "Financeiro"},
    "BBDC4.SA": {"nome": "Bradesco PN", "setor": "Financeiro"},
    "BBAS3.SA": {"nome": "Banco do Brasil", "setor": "Financeiro"},
    "BPAC11.SA": {"nome": "BTG Pactual", "setor": "Financeiro"},
    "SANB11.SA": {"nome": "Santander", "setor": "Financeiro"},
    "B3SA3.SA": {"nome": "B3 (Bolsa)", "setor": "Financeiro"},
    "MGLU3.SA": {"nome": "Magalu", "setor": "Varejo"},
    "LREN3.SA": {"nome": "Lojas Renner", "setor": "Varejo"},
    "VIIA3.SA": {"nome": "Via (Casas Bahia)", "setor": "Varejo"},
    "ASAI3.SA": {"nome": "Assaí", "setor": "Varejo"},
    "CRFB3.SA": {"nome": "Carrefour", "setor": "Varejo"},
    "ELET3.SA": {"nome": "Eletrobras", "setor": "Elétrica"},
    "WEGE3.SA": {"nome": "WEG", "setor": "Bens Industriais"},
    "EQTL3.SA": {"nome": "Equatorial", "setor": "Elétrica"},
    "CMIG4.SA": {"nome": "Cemig", "setor": "Elétrica"},
    "CPLE6.SA": {"nome": "Copel", "setor": "Elétrica"},
    "TAEE11.SA": {"nome": "Taesa", "setor": "Elétrica"},
    "JBSS3.SA": {"nome": "JBS", "setor": "Alimentos"},
    "BRFS3.SA": {"nome": "BRF", "setor": "Alimentos"},
    "SUZB3.SA": {"nome": "Suzano", "setor": "Papel & Celulose"},
    "RENT3.SA": {"nome": "Localiza", "setor": "Aluguel de Carros"},
    "HAPV3.SA": {"nome": "Hapvida", "setor": "Saúde"},
    "RADL3.SA": {"nome": "Raia Drogasil", "setor": "Saúde"},
    "EMBR3.SA": {"nome": "Embraer", "setor": "Indústria"},
}

# --- FUNÇÕES AUXILIARES ---

def calcular_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def pegar_dados_tempo_real(tickers):
    if not tickers:
        return pd.DataFrame()
    
    dados = yf.download(tickers, period="1d", interval="15m", group_by='ticker', progress=False)
    lista_final = []
    
    for t in tickers:
        try:
            if len(tickers) == 1:
                df_ticker = dados
            else:
                df_ticker = dados[t]

            if df_ticker.empty: continue

            ultimo = float(df_ticker['Close'].iloc[-1].item())
            abertura = float(df_ticker['Open'].iloc[0].item())
            variacao = ((ultimo - abertura) / abertura) * 100
            
            info = DADOS_EMPRESAS.get(t, {"nome": t, "setor": "Outros"})
            
            lista_final.append({
                "Ticker": t,
                "Empresa": info["nome"],
                "Setor": info["setor"],
                "Preço (R$)": ultimo,
                "Var (%)": variacao
            })
        except:
            pass
            
    return pd.DataFrame(lista_final)

@st.cache_data(ttl=600)
def pegar_historico(ticker, periodo_selecionado):
    df = yf.download(ticker, period=periodo_selecionado, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = df.columns.droplevel(1)
        except:
            pass
    return df

@st.cache_data(ttl=3600) 
def pegar_benchmark(tickers_usuario):
    lista_download = tickers_usuario + ["^BVSP"]
    df = yf.download(lista_download, period="1y", progress=False)['Close']
    return df

# --- SIDEBAR ---
with st.expander("⚙️ Seleção de Ativos e Filtros", expanded=True):
    col_filtros1, col_filtros2 = st.columns([3, 1])
    with col_filtros1:
        opcoes_tickers = list(DADOS_EMPRESAS.keys())
        lista_ativos = st.multiselect(
            "Carteira Monitorada:",
            options=opcoes_tickers,
            default=["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA", "MGLU3.SA"],
            format_func=lambda x: f"{DADOS_EMPRESAS[x]['nome']} ({x})"
        )
    with col_filtros2:
        st.write("")
        if st.button("🔄 Atualizar"):
            st.rerun()

# --- INTERFACE PRINCIPAL ---

df_atual = pegar_dados_tempo_real(lista_ativos)

if df_atual.empty:
    st.warning("⚠️ Selecione ativos no menu acima ou aguarde a abertura do mercado.")
else:
    # 5 ABAS (ESTRUTURA COMPLETA)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "📈 Setores", 
        "🔍 Raio-X Técnico", 
        "🧩 Correlação & Bench", 
        "⚡ Risco & Timing"
    ])

    # --- ABA 1: VISÃO GERAL ---
    with tab1:
        c1, c2, c3 = st.columns(3)
        media = df_atual["Var (%)"].mean()
        if pd.isna(media): media = 0.0
        c1.metric("Média Carteira", f"{media:.2f}%", delta=f"{media:.2f}%")
        
        melhor = df_atual.loc[df_atual["Var (%)"].idxmax()]
        c2.metric("🏆 Melhor", melhor["Empresa"], f"{melhor['Var (%)']:.2f}%")
        
        pior = df_atual.loc[df_atual["Var (%)"].idxmin()]
        c3.metric("🔻 Pior", pior["Empresa"], f"{pior['Var (%)']:.2f}%")
        
        fig_bar = go.Figure(data=[
            go.Bar(
                x=df_atual['Empresa'],
                y=df_atual['Var (%)'],
                marker_color=df_atual['Var (%)'].apply(lambda x: '#4CAF50' if x > 0 else '#F44336'),
                text=df_atual['Var (%)'].apply(lambda x: f"{x:.2f}%"),
                textposition='auto'
            )
        ])
        fig_bar.update_layout(title="Performance Intradiária", height=350)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.dataframe(df_atual.sort_values("Var (%)", ascending=False), use_container_width=True)

    # --- ABA 2: SETORES ---
    with tab2:
        col_pizza1, col_pizza2 = st.columns(2)
        with col_pizza1:
            st.markdown("### 📐 Exposição por Setor")
            fig_pizza = px.pie(df_atual, names='Setor', hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig_pizza, use_container_width=True)

        with col_pizza2:
            st.markdown("### ⚖️ Performance Média por Setor")
            df_setor = df_atual.groupby("Setor")["Var (%)"].mean().reset_index()
            fig_setor_bar = px.bar(
                df_setor, x="Setor", y="Var (%)",
                color="Var (%)", color_continuous_scale=["red", "yellow", "green"],
                title="Variação Média"
            )
            st.plotly_chart(fig_setor_bar, use_container_width=True)

    # --- ABA 3: RAIO-X (LINHA + MÉDIAS) ---
    with tab3:
        col_sel1, col_sel2 = st.columns([1, 3])
        with col_sel1:
            ativo_x = st.selectbox("Escolha o Ativo:", lista_ativos, key="sel_raiox", format_func=lambda x: f"{x} - {DADOS_EMPRESAS[x]['nome']}")
            periodo_x = st.selectbox("Período:", ["3mo", "6mo", "1y", "2y", "5y"], index=2, key="per_raiox")
            
        with col_sel2:
            if ativo_x:
                try:
                    df_hist = pegar_historico(ativo_x, periodo_x)
                    if not df_hist.empty and 'Close' in df_hist.columns:
                        df_hist['SMA_20'] = df_hist['Close'].rolling(window=20).mean()
                        
                        fig_hist = go.Figure()
                        fig_hist.add_trace(go.Scatter(x=df_hist.index, y=df_hist['Close'], fill='tozeroy', mode='lines', name='Preço'))
                        fig_hist.add_trace(go.Scatter(x=df_hist.index, y=df_hist['SMA_20'], line=dict(color='orange', dash='dash'), name='Média 20'))
                        
                        fig_hist.update_layout(title=f"Tendência: {DADOS_EMPRESAS[ativo_x]['nome']}", height=450, template="plotly_white")
                        st.plotly_chart(fig_hist, use_container_width=True)
                except Exception as e:
                    st.error(f"Erro: {e}")

    # --- ABA 4: CORRELAÇÃO & BENCHMARK ---
    with tab4:
        st.markdown("### 🧠 Inteligência de Mercado")
        col_adv1, col_adv2 = st.columns(2)
        
        # 1. Correlação
        with col_adv1:
            st.markdown("#### 🔥 Matriz de Correlação")
            if len(lista_ativos) > 1:
                try:
                    dados_corr = pegar_benchmark(lista_ativos)
                    
                    cols_to_keep = [c for c in dados_corr.columns if c in lista_ativos]
                    if cols_to_keep:
                        corr_matrix = dados_corr[cols_to_keep].corr()
                        
                        fig_corr = px.imshow(
                            corr_matrix, text_auto=".2f", aspect="auto",
                            color_continuous_scale="RdBu_r", zmin=-1, zmax=1
                        )
                        st.plotly_chart(fig_corr, use_container_width=True)
                except Exception as e:
                    st.warning(f"Não foi possível calcular correlação: {e}")
            else:
                st.info("Selecione mais de 1 ativo para ver a correlação.")

        # 2. Benchmark
        with col_adv2:
            st.markdown("#### 🆚 Comparativo com IBOVESPA")
            ativo_compare = st.selectbox("Comparar qual ativo?", lista_ativos, key="sel_bench", format_func=lambda x: f"{x} - {DADOS_EMPRESAS[x]['nome']}")
            
            if ativo_compare:
                try:
                    df_bench = pegar_benchmark([ativo_compare]) # Traz IBOV junto automatico na funcao
                    
                    # Normaliza base 100
                    df_norm = (df_bench / df_bench.iloc[0]) * 100
                    
                    fig_comp = go.Figure()
                    # Linha do Ativo
                    if ativo_compare in df_norm.columns:
                        fig_comp.add_trace(go.Scatter(x=df_norm.index, y=df_norm[ativo_compare], mode='lines', name=ativo_compare))
                    
                    # Linha do IBOV
                    if '^BVSP' in df_norm.columns:
                        fig_comp.add_trace(go.Scatter(x=df_norm.index, y=df_norm['^BVSP'], mode='lines', name='IBOVESPA', line=dict(dash='dot', color='gray')))
                    
                    fig_comp.update_layout(title="Rentabilidade Relativa (Base 100)", height=400)
                    st.plotly_chart(fig_comp, use_container_width=True)
                except:
                    st.warning("Dados de Benchmark indisponíveis no momento.")

    # --- ABA 5: RISCO & TIMING ---
    with tab5:
        st.markdown("### ⚡ Risco (Drawdown) & Timing (RSI)")
        
        c_risk1, c_risk2 = st.columns([1, 3])
        with c_risk1:
            ativo_risk = st.selectbox("Analisar Risco de:", lista_ativos, key="sel_risk", format_func=lambda x: f"{x} - {DADOS_EMPRESAS[x]['nome']}")
        
        with c_risk2:
            if ativo_risk:
                df_risk = pegar_historico(ativo_risk, "1y")
                
                if not df_risk.empty:
                    # Drawdown
                    rolling_max = df_risk['Close'].cummax()
                    drawdown = (df_risk['Close'] - rolling_max) / rolling_max
                    
                    fig_dd = go.Figure()
                    fig_dd.add_trace(go.Scatter(x=drawdown.index, y=drawdown, fill='tozeroy', line=dict(color='red'), name='Queda'))
                    fig_dd.update_layout(title=f"📉 Drawdown Máximo: {ativo_risk}", yaxis_tickformat=".1%", height=300)
                    st.plotly_chart(fig_dd, use_container_width=True)
                    
                    # RSI
                    rsi = calcular_rsi(df_risk['Close'])
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(x=rsi.index, y=rsi, line=dict(color='purple'), name='RSI'))
                    fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
                    fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
                    fig_rsi.update_layout(title=f"⏱️ IFR (RSI 14 periods)", yaxis_range=[0, 100], height=300)
                    st.plotly_chart(fig_rsi, use_container_width=True)

st.markdown("---")
st.caption("Dashboard Desenvolvido com Python & Streamlit | Dados: Yahoo Finance (Atraso de 15min)")