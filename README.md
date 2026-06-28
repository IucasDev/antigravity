# Cálculo de Esforços Mecânicos em Postes

Aplicação Streamlit para cálculo de esforços mecânicos em postes de concreto para redes de distribuição de energia elétrica.

## Funcionalidades

- Cálculo passo a passo com perguntas sequenciais
- Seleção de altura do poste (9m a 16m)
- Ângulo da rede (entrada manual)
- Suporte a múltiplos tipos de rede:
  - Pré-Reunido (PB35, PB50, PB70, PB120)
  - Rede Compacta (A35P a A240P)
  - CAZ/CAW
  - Rede Protegida (PA50 a PA240)
  - Rede Convencional
- Cálculo de derivação (0° a 360°) ou fim de linha
- Segundo nível de primária
- Rede secundária com fases, controle e neutro
- Cálculo vetorial da força resultante em daN
- Recomendação de poste adequado

## Como usar

1. Acesse a aplicação online ou rode localmente
2. Responda cada pergunta sequencialmente
3. Veja o resultado com a força resultante e recomendação de poste

## Executar localmente

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy no Streamlit Cloud

1. Faça upload deste repositório no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório
4. Configure: `streamlit_app.py` como arquivo principal

## Tecnologias

- Python 3.10+
- Streamlit
- Matemática vetorial para composição de forças

## Licença

Uso interno - Energec
