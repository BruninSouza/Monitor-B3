import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard B3 Pro", layout="wide", page_icon="📈")
st.title("📈 Dashboard B3: Análise & Monitoramento")

# --- BANCO DE DADOS MESTRE (NOME + SETOR) ---
DADOS_EMPRESAS = {
    "PETR4.SA": {"nome": "Petrobras PN", "setor": "Petróleo & Gás"},
    "PETR3.SA": {"nome": "Petrobras ON", "setor": "Petróleo & Gás"},
    "PRIO3.SA": {"nome": "Prio (PetroRio)", "setor": "Petróleo & Gás"},
    "VIBRA3.SA": {"nome": "Vibra Energia", "setor": "Petróleo & Gás"},
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

# --- FUNÇÕES ---

def pegar_dados_tempo_real(tickers):
    if not tickers:
        return pd.DataFrame()
    
    # Baixa dados intradiários
    dados = yf.download(tickers, period="1d", interval="15m", group_by='ticker', progress=False)
    lista_final = []
    
    for t in tickers:
        try:
            if len(tickers) == 1:
                df_ticker = dados
            else:
                df_ticker = dados[t]

            if df_ticker.empty: continue

            # Garante que pegamos o valor escalar (número puro) e não uma Série
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
    # Baixa os dados
    df = yf.download(ticker, period=periodo_selecionado, progress=False)
    
    # --- LIMPEZA CRÍTICA DE DADOS ---
    # Se o yfinance devolver colunas MultiIndex (ex: ('Close', 'PETR4.SA')), achatamos para ('Close')
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = df.columns.droplevel(1)
        except:
            pass
            
    # Se ainda assim tivermos problemas, garantimos que pegamos apenas as colunas padrão
    return df

# --- SIDEBAR ---
st.sidebar.header("⚙️ Filtros")

opcoes_tickers = list(DADOS_EMPRESAS.keys())
lista_ativos = st.sidebar.multiselect(
    "Carteira Monitorada:",
    options=opcoes_tickers,
    default=["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA", "MGLU3.SA"],
    format_func=lambda x: f"{DADOS_EMPRESAS[x]['nome']} ({x})"
)

# --- INTERFACE PRINCIPAL ---

# Carrega dados gerais
df_atual = pegar_dados_tempo_real(lista_ativos)

if df_atual.empty:
    st.warning("Selecione ativos ou aguarde a abertura do mercado.")
else:
    # Abas
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "📈 Setores", "🔍 Raio-X do Ativo"])

    # --- ABA 1: Visão Geral ---
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
        st.plotly_chart(fig_bar, use_container_width=True, key="grafico_barras_geral")
        
        st.dataframe(df_atual.sort_values("Var (%)", ascending=False), use_container_width=True)

    # --- ABA 2: Análise Setorial ---
    with tab2:
        col_pizza1, col_pizza2 = st.columns(2)
        with col_pizza1:
            st.markdown("### 📐 Distribuição da Carteira")
            fig_pizza = px.pie(
                df_atual, 
                names='Setor', 
                title='Exposição por Setor (Qtd Ativos)',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig_pizza, use_container_width=True, key="grafico_pizza_setor")

        with col_pizza2:
            st.markdown("### ⚖️ Performance Média por Setor")
            df_setor = df_atual.groupby("Setor")["Var (%)"].mean().reset_index()
            fig_setor_bar = px.bar(
                df_setor, 
                x="Setor", 
                y="Var (%)",
                color="Var (%)",
                color_continuous_scale=["red", "yellow", "green"],
                title="Qual setor está ganhando hoje?"
            )
            st.plotly_chart(fig_setor_bar, use_container_width=True, key="grafico_barras_setor")

    # --- ABA 3: Raio-X Individual (BLINDADA) ---
    with tab3:
        col_sel1, col_sel2 = st.columns([1, 3])
        
        with col_sel1:
            ativo_x = st.selectbox(
                "Escolha o Ativo para Analisar:", 
                lista_ativos, 
                format_func=lambda x: f"{x} - {DADOS_EMPRESAS[x]['nome']}"
            )
            periodo_x = st.selectbox("Período:", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd"], index=3)
            
        with col_sel2:
            if ativo_x:
                try:
                    df_hist = pegar_historico(ativo_x, periodo_x)
                    
                    # Verifica se o DataFrame tem dados e as colunas certas
                    if not df_hist.empty and 'Close' in df_hist.columns:
                        
                        fig_hist = go.Figure()
                        
                        # Plota o Fechamento
                        fig_hist.add_trace(go.Scatter(
                            x=df_hist.index, 
                            y=df_hist['Close'],
                            fill='tozeroy',
                            mode='lines',
                            line=dict(color='#2196F3', width=2),
                            name='Fechamento'
                        ))
                        
                        # Tenta calcular e plotar a média móvel
                        try:
                            sma = df_hist['Close'].rolling(window=20).mean()
                            fig_hist.add_trace(go.Scatter(
                                x=df_hist.index, y=sma, 
                                line=dict(color='#FF9800', width=1, dash='dash'), 
                                name='Média 20 dias'
                            ))
                        except:
                            pass

                        fig_hist.update_layout(
                            title=f"Histórico: {DADOS_EMPRESAS[ativo_x]['nome']}",
                            xaxis_title="Data",
                            yaxis_title="Preço (R$)",
                            template="plotly_white",
                            height=450,
                            hovermode="x unified"
                        )
                        st.plotly_chart(fig_hist, use_container_width=True, key="grafico_historico_linha")
                        
                        # Estatísticas (Convertendo para float puro para evitar erros de formatação)
                        try:
                            # .item() garante que pegamos o valor Python puro, sem metadados do Pandas
                            minimo = float(df_hist['Close'].min())
                            maximo = float(df_hist['Close'].max())
                            atual_hist = float(df_hist['Close'].iloc[-1])
                            
                            c_min, c_max, c_atual = st.columns(3)
                            c_min.metric("Mínimo no Período", f"R$ {minimo:.2f}")
                            c_max.metric("Máximo no Período", f"R$ {maximo:.2f}")
                            c_atual.metric("Preço Atual", f"R$ {atual_hist:.2f}")
                        except Exception as e:
                            st.info("Gráfico carregado, mas não foi possível calcular métricas adicionais.")
                            
                    else:
                        st.warning("Sem dados históricos disponíveis para este ativo/período.")
                except Exception as e:
                    st.error(f"Erro ao processar dados: {e}")

# Botão de refresh
if st.button("🔄 Atualizar Dados Agora"):
    st.rerun()