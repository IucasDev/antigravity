import streamlit as st
import math

st.set_page_config(page_title="Cálculo de Esforços Mecânicos", layout="wide")

st.markdown("""
<style>
input[type=range] {
    cursor: pointer;
    height: 6px;
    -webkit-appearance: none;
    appearance: none;
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    border-radius: 4px;
    outline: none;
}
input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(102,126,234,0.5);
    border: 2px solid white;
}
input[type=range]::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(102,126,234,0.5);
    border: 2px solid white;
}
.stTabs [data-baseweb="tab"] {
    font-size: 14px;
    font-weight: 600;
    padding: 8px 16px;
}
.block-container { padding: 1rem 1.5rem; max-width: 1300px; }
div[data-testid="stMetric"] {
    background: #f0f2f6;
    border-radius: 8px;
    padding: 12px;
    border: 1px solid #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

ALTURAS_POSTE = [9, 10, 11, 12, 14, 16]

ALTURAS_NIVEIS = {
    9:  {"primaria": [7.5, 7.0, 6.5], "secundaria": [6.5, 6.0, 5.5]},
    10: {"primaria": [8.4, 7.9, 7.4], "secundaria": [7.4, 6.9, 6.4]},
    11: {"primaria": [9.3, 8.8, 8.3], "secundaria": [8.3, 7.8, 7.3]},
    12: {"primaria": [10.2, 9.7, 9.2], "secundaria": [9.2, 8.7, 8.2]},
    14: {"primaria": [12.0, 11.5, 11.0], "secundaria": [11.0, 10.5, 10.0]},
    16: {"primaria": [13.8, 13.3, 12.8], "secundaria": [12.8, 12.3, 11.8]},
}

TIPOS_REDE = ["Pré-Reunido", "Rede Compacta", "CAZ/CAW", "Rede Protegida", "Rede Convencional"]
LOCATIONS = ["URBANO", "RURAL", "RURAL > 80m"]

CABOS_PRE_REUNIDO = ["PB35", "PB50", "PB70", "PB120"]
CABOS_COMPACTA = ["A35P", "A50P", "A70P", "A120P", "A185P", "A240P"]
CABOS_CAZ = ["CAZ 3,09", "CAZ 3x2,25", "CAW 3,26", "CAW 3x2,59", "CAA 04"]
CABOS_PROTEGIDO = ["PA50", "PA70", "PA95", "PA120", "PA185", "PA240"]
CABOS_CONVENCIONAL = [
    "A02", "A04", "A20", "A40", "A336", "A477",
    "C02", "C04", "C06", "C20", "C25", "C35", "C40", "C70", "C120",
    "S02", "S04", "S20", "S40", "S336", "S477",
]

PR = {
    "PB35":  {5: 4, 10: 14, 15: 32, 20: 56, 25: 88, 30: 127, 35: 172, 40: 225},
    "PB50":  {5: 6, 10: 24, 15: 51, 20: 91, 25: 142, 30: 204, 35: 278, 40: 363},
    "PB70":  {5: 7, 10: 30, 15: 67, 20: 119, 25: 186, 30: 267, 35: 364, 40: 475},
    "PB120": {5: 8, 10: 33, 15: 74, 20: 132, 25: 206, 30: 296, 35: 403, 40: 527},
}
CP = {
    "A50P":  {10: 461, 15: 469, 20: 477, 25: 486, 30: 495, 35: 503, 40: 516,
              45: 537, 50: 555, 55: 571, 60: 586, 65: 600, 70: 612, 75: 623, 80: 632},
    "A70P":  {10: 468, 15: 483, 20: 498, 25: 514, 30: 530, 35: 544, 40: 558,
              45: 582, 50: 604, 55: 624, 60: 641, 65: 657, 70: 672, 75: 685, 80: 697},
    "A120P": {10: 489, 15: 521, 20: 553, 25: 584, 30: 614, 35: 641, 40: 665,
              45: 692, 50: 722, 55: 749, 60: 774, 65: 797, 70: 818, 75: 837, 80: 854},
    "A180P": {10: 514, 15: 562, 20: 610, 25: 655, 30: 697, 35: 735, 40: 770,
              45: 802, 50: 837, 55: 872, 60: 903, 65: 933, 70: 960, 75: 985, 80: 1008},
    "A185P": {10: 514, 15: 562, 20: 610, 25: 655, 30: 697, 35: 735, 40: 770,
              45: 802, 50: 837, 55: 872, 60: 903, 65: 933, 70: 960, 75: 985, 80: 1008},
    "A240P": {10: 550, 15: 600, 20: 650, 25: 700, 30: 750, 35: 800, 40: 850,
              45: 880, 50: 920, 55: 950, 60: 980, 65: 1010, 70: 1040, 75: 1060, 80: 1080},
}
CAZ = {
    "CAZ 3,09":   {50: 229, 100: 256, 150: 263, 200: 282, 300: 318, 400: 349, 500: 376, 600: 400},
    "CAZ 3x2,25": {50: 357, 100: 395, 150: 406, 200: 436, 300: 491, 400: 540, 500: 580, 600: 615},
    "CAW 3,26":   {50: 244, 100: 273, 150: 276, 200: 296, 300: 334, 400: 368, 500: 398, 600: 426},
    "CAW 3x2,59": {50: 438, 100: 492, 150: 495, 200: 524, 300: 588, 400: 645, 500: 696, 600: 741},
    "CAA 04":     {50: 217, 100: 269, 150: 313, 200: 324, 300: 324, 400: 324, 500: 324, 600: 324},
}
PROT = {"PA50": 311, "PA70": 375, "PA95": 469, "PA120": 527, "PA185": 683, "PA240": 795}
CAB_TR = {
    "A02": 86, "A04": 60, "A20": 173, "A336": 436, "A40": 274, "A477": 619,
    "C02": 171, "C04": 107, "C06": 60, "C120": 568, "C20": 342, "C25": 106,
    "C35": 155, "C40": 544, "C70": 296, "S02": 347, "S04": 219, "S20": 696,
    "S40": 1108, "S336": 1388, "S477": 2497,
}

def altura_util(h):
    if not h:
        return 0
    return h - h * 0.1 - 0.6

def tracao_transf(tracao, h_util, h_cabo, qtd=1, mult=1.0):
    if not tracao or not h_util or h_util == 0:
        return 0
    return tracao / h_util * h_cabo * qtd * mult

def obter_tracao(tipo_rede, cabo, vaio=None):
    if tipo_rede == "Pré-Reunido":
        if vaio and cabo in PR:
            dados = PR[cabo]
            return dados.get(min(dados.keys(), key=lambda k: abs(k - vaio)), list(dados.values())[0])
        return list(PR.get(cabo, {}).values())[0] if PR.get(cabo) else 0
    elif tipo_rede == "Rede Compacta":
        if vaio and cabo in CP:
            dados = CP[cabo]
            return dados.get(min(dados.keys(), key=lambda k: abs(k - vaio)), list(dados.values())[0])
        return 245
    elif tipo_rede == "CAZ/CAW":
        if vaio and cabo in CAZ:
            dados = CAZ[cabo]
            return dados.get(min(dados.keys(), key=lambda k: abs(k - vaio)), list(dados.values())[0])
        return list(CAZ.get(cabo, {}).values())[0] if CAZ.get(cabo) else 0
    elif tipo_rede == "Rede Protegida":
        return PROT.get(cabo, 0)
    elif tipo_rede == "Rede Convencional":
        return CAB_TR.get(cabo, 0)
    return 0

def calc_resultante(forcas_x, forcas_y):
    sx = sum(forcas_x)
    sy = sum(forcas_y)
    mag = math.sqrt(sx ** 2 + sy ** 2)
    if mag == 0:
        return 0, 0
    ang_rad = math.acos(max(-1, min(1, sx / mag)))
    if sy < 0:
        ang_rad = -ang_rad
    ang_deg = math.degrees(ang_rad)
    ang_exib = ang_deg if ang_deg >= 0 else 360 + ang_deg
    return mag, ang_exib

def cabos_para_rede(tipo_rede):
    if tipo_rede == "Pré-Reunido":
        return CABOS_PRE_REUNIDO
    elif tipo_rede == "Rede Compacta":
        return CABOS_COMPACTA
    elif tipo_rede == "CAZ/CAW":
        return CABOS_CAZ
    elif tipo_rede == "Rede Protegida":
        return CABOS_PROTEGIDO
    elif tipo_rede == "Rede Convencional":
        return CABOS_CONVENCIONAL
    return []

def precisa_vao(tipo_rede):
    return tipo_rede in ["Pré-Reunido", "Rede Compacta", "CAZ/CAW"]

def campo_rede_cabo_vao(prefixo, padrao_rede=0):
    rede = st.selectbox("Tipo de rede:", TIPOS_REDE, index=padrao_rede, key=f"{prefixo}_rede")
    cabos = cabos_para_rede(rede)
    if cabos:
        st.selectbox("Tipo de cabo:", cabos, key=f"{prefixo}_cabo")
    if precisa_vao(rede):
        st.number_input("Vão (m):", min_value=5, max_value=600, value=50, step=5, key=f"{prefixo}_vao")
    else:
        st.caption("Vão: N/A")

def campo_saida(prefixo):
    col_x, col_y, col_z = st.columns(3)
    with col_x:
        rede_s = st.selectbox("Tipo de rede (saída):", TIPOS_REDE, index=0, key=f"{prefixo}_rede_saida")
    with col_y:
        cabos_s = cabos_para_rede(rede_s)
        if cabos_s:
            st.selectbox("Tipo de cabo (saída):", cabos_s, key=f"{prefixo}_cabo_saida")
    with col_z:
        if precisa_vao(rede_s):
            st.number_input("Vão (saída):", min_value=5, max_value=600, value=50, step=5, key=f"{prefixo}_vao_saida")
        else:
            st.caption("Vão: N/A")

st.title("Cálculo de Esforços Mecânicos em Postes")
st.caption("Sistema para verificação de resistência de postes de concreto")
st.markdown("---")

config = st.radio(
    "**Configuração da rede:**",
    ["Apenas Primária (1 nível)", "Dois níveis de Primária",
     "Apenas Secundária", "Primária + Secundária",
     "Dois níveis de Primária + Secundária"],
    index=0, horizontal=True,
)
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    altura_poste = st.selectbox("Altura do poste (m):", ALTURAS_POSTE, index=3)
    h_util = altura_util(altura_poste)
    st.caption(f"Altura útil engastamento: **{altura_poste * 0.1 + 0.6:.2f}m**")
with col2:
    localizacao = st.selectbox("Localização:", LOCATIONS, index=0)
with col3:
    qtd_cabos_princ = st.radio("Quantidade de cabos:", [1, 2, 3], index=1, horizontal=True)

st.markdown("---")

fx_total = 0.0
fy_total = 0.0
resumo_linhas = []

def processar_nivel(prefixo, h_nivel):
    global fx_total, fy_total
    chave_ang = f"{prefixo}_ang_chegada"
    if chave_ang not in st.session_state:
        return
    ang_chegada = st.session_state[chave_ang]
    rede = st.session_state.get(f"{prefixo}_rede", "")
    cabo = st.session_state.get(f"{prefixo}_cabo", "")
    vao = st.session_state.get(f"{prefixo}_vao", None)
    fim_linha = st.session_state.get(f"{prefixo}_fim_linha", False)
    if not rede or not cabo:
        return
    tracao = obter_tracao(rede, cabo, vao if precisa_vao(rede) else None)
    f_mag = tracao_transf(tracao, altura_util(altura_poste), h_nivel, qtd_cabos_princ)
    ang_rad_c = math.radians(ang_chegada)
    fx_total += f_mag * math.cos(ang_rad_c)
    fy_total += f_mag * math.sin(ang_rad_c)
    resumo_linhas.append(f"**{prefixo.upper()}** Chegada (Fonte): {rede} / {cabo} -> {f_mag:.0f} daN @ {ang_chegada}°")
    if not fim_linha:
        ang_saida = st.session_state.get(f"{prefixo}_ang_saida", 0)
        cabos_iguais = st.session_state.get(f"{prefixo}_cabos_iguais", "Mesmos")
        if cabos_iguais == "Diferentes":
            rede_s = st.session_state.get(f"{prefixo}_rede_saida", rede)
            cabo_s = st.session_state.get(f"{prefixo}_cabo_saida", cabo)
            vao_s = st.session_state.get(f"{prefixo}_vao_saida", vao)
            tracao_s = obter_tracao(rede_s, cabo_s, vao_s if precisa_vao(rede_s) else None)
            f_saida = tracao_transf(tracao_s, altura_util(altura_poste), h_nivel, qtd_cabos_princ)
        else:
            f_saida = f_mag
        ang_rad_s = math.radians(ang_saida)
        fx_total += f_saida * math.cos(ang_rad_s)
        fy_total += f_saida * math.sin(ang_rad_s)
        resumo_linhas.append(f"  Saida (Carga): {ang_saida}° -> {f_saida:.0f} daN")

tem_1n = config in ["Apenas Primária (1 nível)", "Dois níveis de Primária",
                     "Primária + Secundária", "Dois níveis de Primária + Secundária"]
tem_2n = config in ["Dois níveis de Primária", "Dois níveis de Primária + Secundária"]
tem_sec = config in ["Apenas Secundária", "Primária + Secundária",
                      "Dois níveis de Primária + Secundária"]

tab_list = []
if tem_1n:
    tab_list.append("1° Nivel (Primaria)")
if tem_2n:
    tab_list.append("2° Nivel (Primaria)")
if tem_sec:
    tab_list.append("Rede Secundaria")
tabs = st.tabs(tab_list) if tab_list else []
ti = 0

if tem_1n:
    with tabs[ti]:
        ti += 1
        alturas_1 = ALTURAS_NIVEIS[altura_poste]["primaria"]
        h_1n = st.radio("Altura de montagem (m):", alturas_1, index=0, horizontal=True, key="1n_alt")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            campo_rede_cabo_vao("1n")
        with col_b:
            st.markdown("##### Ângulo de Chegada (Fonte)")
            st.slider("0° a 360°:", 0, 360, value=0, key="1n_ang_chegada")
        with col_c:
            fim_1n = st.checkbox("Fim de linha?", key="1n_fim_linha")
        if not fim_1n:
            st.markdown("---")
            col_d, col_e = st.columns(2)
            with col_d:
                st.markdown("##### Ângulo de Saida (Carga)")
                st.slider("0° a 360°:", 0, 360, value=0, key="1n_ang_saida")
            with col_e:
                cabos_iguais = st.radio("Cabos da saida:", ["Mesmos", "Diferentes"],
                                        horizontal=True, key="1n_cabos_iguais")
            if cabos_iguais == "Diferentes":
                campo_saida("1n")
        processar_nivel("1n", h_1n)

if tem_2n:
    with tabs[ti]:
        ti += 1
        mesm_ang = st.checkbox("Mesmo angulo de chegada do 1° nivel?", key="2n_mesmo_ang")
        if mesm_ang:
            ang_ref = st.session_state.get("1n_ang_chegada", 0)
            st.markdown(f"Angulo de Chegada (Fonte): **{ang_ref}°** (herdado do 1° nivel)")
            st.session_state["2n_ang_chegada"] = ang_ref
        else:
            st.slider("Angulo de chegada:", 0, 360, value=0, key="2n_ang_chegada")
        alturas_2 = ALTURAS_NIVEIS[altura_poste]["primaria"]
        h_2n = st.radio("Altura de montagem (m):", alturas_2, index=1, horizontal=True, key="2n_alt")
        col_d, col_e, col_f = st.columns(3)
        with col_d:
            campo_rede_cabo_vao("2n")
        with col_e:
            st.markdown("##### Ângulo de Chegada (Fonte)")
            if not mesm_ang:
                st.caption("(ajuste acima)")
            else:
                st.caption(f"(herdado: {ang_ref}°)")
        with col_f:
            fim_2n = st.checkbox("Fim de linha?", key="2n_fim_linha")
        if not fim_2n:
            st.markdown("---")
            col_g, col_h = st.columns(2)
            with col_g:
                st.markdown("##### Ângulo de Saida (Carga)")
                st.slider("0° a 360°:", 0, 360, value=0, key="2n_ang_saida")
            with col_h:
                cabos_iguais_2n = st.radio("Cabos da saida:", ["Mesmos", "Diferentes"],
                                           horizontal=True, key="2n_cabos_iguais")
            if cabos_iguais_2n == "Diferentes":
                campo_saida("2n")
        processar_nivel("2n", h_2n)

if tem_sec:
    with tabs[ti]:
        ti += 1
        mesm_ang_sec = st.checkbox("Mesmo angulo de chegada do 1° nivel?", key="sec_mesmo_ang")
        if mesm_ang_sec:
            ang_ref_sec = st.session_state.get("1n_ang_chegada", 0)
            st.markdown(f"Angulo de Chegada (Fonte): **{ang_ref_sec}°** (herdado do 1° nivel)")
            st.session_state["sec_ang_chegada"] = ang_ref_sec
        else:
            st.slider("Angulo de chegada:", 0, 360, value=0, key="sec_ang_chegada")
        alturas_3 = ALTURAS_NIVEIS[altura_poste]["secundaria"]
        h_sec = st.radio("Altura de montagem (m):", alturas_3, index=0, horizontal=True, key="sec_alt")
        col_i, col_j, col_k = st.columns(3)
        with col_i:
            campo_rede_cabo_vao("sec", padrao_rede=4)
        with col_j:
            st.radio("Quantas fases?", [1, 2, 3], index=1, horizontal=True, key="sec_qtd_fases")
            st.selectbox("Bitola do neutro:", CABOS_CONVENCIONAL, index=1, key="sec_cabo_neutro")
        with col_k:
            tem_controle_sec = st.checkbox("Possui Controle?", key="sec_tem_controle")
            if tem_controle_sec:
                st.selectbox("Bitola do controle:", CABOS_CONVENCIONAL, index=0, key="sec_cabo_controle")
            fim_sec = st.checkbox("Fim de linha?", key="sec_fim_linha")
        if not fim_sec:
            st.markdown("---")
            col_l, col_m = st.columns(2)
            with col_l:
                st.markdown("##### Ângulo de Saida (Carga)")
                st.slider("0° a 360°:", 0, 360, value=0, key="sec_ang_saida")
            with col_m:
                cabos_iguais_sec = st.radio("Cabos da saida:", ["Mesmos", "Diferentes"],
                                            horizontal=True, key="sec_cabos_iguais")
            if cabos_iguais_sec == "Diferentes":
                campo_saida("sec")

        ang_chegada_sec = st.session_state.get("sec_ang_chegada", 0)
        rede_sec = st.session_state.get("sec_rede", "")
        cabo_sec = st.session_state.get("sec_cabo", "")
        vao_sec = st.session_state.get("sec_vao", None)
        qtd_fases = st.session_state.get("sec_qtd_fases", 2)
        cabo_neutro = st.session_state.get("sec_cabo_neutro", "A04")
        tem_controle = st.session_state.get("sec_tem_controle", False)
        fim_linha_sec = st.session_state.get("sec_fim_linha", False)

        if rede_sec and cabo_sec and qtd_fases:
            t_fase = obter_tracao(rede_sec, cabo_sec, vao_sec if precisa_vao(rede_sec) else None)
            f_fases = tracao_transf(t_fase, altura_util(altura_poste), h_sec, int(qtd_fases))
            t_neutro = obter_tracao(rede_sec, cabo_neutro, vao_sec if precisa_vao(rede_sec) else None)
            f_neutro = tracao_transf(t_neutro, altura_util(altura_poste), h_sec, 1)
            f_controle = 0
            if tem_controle:
                cabo_controle = st.session_state.get("sec_cabo_controle", "A02")
                t_controle = obter_tracao(rede_sec, cabo_controle, vao_sec if precisa_vao(rede_sec) else None)
                f_controle = tracao_transf(t_controle, altura_util(altura_poste), h_sec, 1)
            f_total_sec = f_fases + f_neutro + f_controle
            ang_rad_c = math.radians(ang_chegada_sec)
            fx_total += f_total_sec * math.cos(ang_rad_c)
            fy_total += f_total_sec * math.sin(ang_rad_c)
            detalhe_sec = f"{rede_sec} / {cabo_sec} ({qtd_fases}f) / Neutro: {cabo_neutro}"
            if tem_controle:
                detalhe_sec += f" / Controle: {cabo_controle}"
            resumo_linhas.append(f"**SEC** Chegada (Fonte): {detalhe_sec} -> {f_total_sec:.0f} daN @ {ang_chegada_sec}°")

            if not fim_linha_sec:
                ang_saida_sec = st.session_state.get("sec_ang_saida", 0)
                cabos_iguais_sec = st.session_state.get("sec_cabos_iguais", "Mesmos")
                if cabos_iguais_sec == "Diferentes":
                    rede_s_sec = st.session_state.get("sec_rede_saida", rede_sec)
                    cabo_s_sec = st.session_state.get("sec_cabo_saida", cabo_sec)
                    vao_s_sec = st.session_state.get("sec_vao_saida", vao_sec)
                    t_saida_sec = obter_tracao(rede_s_sec, cabo_s_sec, vao_s_sec if precisa_vao(rede_s_sec) else None)
                    f_saida_sec = tracao_transf(t_saida_sec, altura_util(altura_poste), h_sec, int(qtd_fases))
                else:
                    f_saida_sec = f_total_sec
                ang_rad_s = math.radians(ang_saida_sec)
                fx_total += f_saida_sec * math.cos(ang_rad_s)
                fy_total += f_saida_sec * math.sin(ang_rad_s)
                resumo_linhas.append(f"  Saida (Carga): {ang_saida_sec}° -> {f_saida_sec:.0f} daN")

st.markdown("---")
st.subheader("Resultado do Calculo", divider="red")

magnitude, ang_resultante = calc_resultante([fx_total], [fy_total])

col_r1, col_r2, col_r3, col_r4 = st.columns(4)
with col_r1:
    st.metric("Forca Resultante", f"{magnitude:.1f} daN")
with col_r2:
    st.metric("Angulo Resultante", f"{ang_resultante:.1f}°")
with col_r3:
    st.metric("Componente X", f"{fx_total:.1f} daN")
with col_r4:
    st.metric("Componente Y", f"{fy_total:.1f} daN")

st.markdown("---")

col_rec1, col_rec2 = st.columns([2, 1])
with col_rec1:
    st.markdown("### Resumo dos Esforcos")
    for linha in resumo_linhas:
        st.markdown(f"- {linha}")
    st.markdown(f"**Poste:** {altura_poste}m | **Altura util:** {h_util:.2f}m | **Local:** {localizacao}")
with col_rec2:
    st.markdown("### Recomendacao (daN)")
    thresholds = [200, 400, 600, 1000, 1500, 2000]
    if magnitude == 0:
        st.info("Preencha os parametros para calcular.")
    else:
        recomendado = next((t for t in thresholds if magnitude <= t), None)
        if recomendado:
            st.success(f"Esforco: **{magnitude:.0f} daN** -> Recomendado: **{recomendado} daN**")
        else:
            st.error(f"Esforco de {magnitude:.0f} daN excede 2000 daN. Consulte engenharia.")
    st.markdown("---")
    if st.button("🔄 Zerar e Recomeçar", use_container_width=True):
        st.session_state.clear()
        st.rerun()
