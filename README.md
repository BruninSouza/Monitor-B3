# 📈 Dashboard de Análise de Mercado B3

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)
![Status](https://img.shields.io/badge/Status-Online-success.svg)

> Um dashboard interativo para monitoramento em tempo real e análise técnica de ações da Bolsa Brasileira (B3).

## 🔗 [Acesse o Dashboard Online Aqui](https://monitor-b3.streamlit.app/)

## 🎯 Objetivo do Projeto
Este projeto foi desenvolvido para democratizar o acesso a indicadores técnicos (RSI, Drawdown, Médias Móveis) de forma visual e intuitiva. O objetivo é demonstrar habilidades em **Engenharia de Dados** (extração e tratamento) e **Visualização de Dados** para tomada de decisão.

## 🛠️ Tecnologias Utilizadas
* **Python:** Linguagem principal.
* **Streamlit:** Framework para web apps de dados.
* **Pandas:** Manipulação e limpeza de dados (ETL).
* **YFinance:** Integração via API para dados de mercado.
* **Plotly:** Criação de gráficos interativos e dinâmicos.

## 📊 Funcionalidades
1.  **Monitoramento Intradiário:** Cotações e variações em tempo real.
2.  **Análise Setorial:** Breakdown da carteira por setores (Financeiro, Varejo, etc.).
3.  **Indicadores Técnicos:**
    * *RSI (Índice de Força Relativa):* Identificação de sobrecompra/sobrevenda.
    * *Drawdown:* Análise de risco e queda máxima histórica.
    * *Médias Móveis:* Identificação de tendências de curto e longo prazo.
4.  **Correlação:** Heatmap para análise de diversificação de portfólio.

## 🚀 Como rodar localmente
1. Clone o repositório:
   ```bash
   git clone https://github.com/BruninSouza/Monitor-B3.git
   ````

2. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3. Execute o app:
    ```bash
    streamlit run app.py
    ```

### Desenvolvido por Bruno Souza | [LinkedIn](https://www.linkedin.com/in/bruno-souza-a74396214/)