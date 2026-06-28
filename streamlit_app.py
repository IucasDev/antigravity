import streamlit as st
import math

st.set_page_config(page_title="Cálculo de Esforços Mecânicos", layout="wide")

# ============================================================
# CONSTANTES - DADOS TÉCNICOS
# ============================================================

ALTURAS_POSTE = [9, 10, 11, 12, 14, 16]

TIPOS_REDE = [
    "Pré-Reunido",
    "Rede Compacta",
    "CAZ/CAW",
    "Rede Protegida",
    "Rede Convencional",
]

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

# ============================================================
# FUNÇÕES DE CÁLCULO
# ============================================================

def altura_util(h):
    if not h:
        return 0
    return h - h * 0.1 - 0.7

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

# ============================================================
# CABEÇALHO
# ============================================================

st.title("Cálculo de Esforços Mecânicos em Postes")
st.caption("Sistema para verificação de resistência de postes de concreto")
st.markdown("---")

# ============================================================
# FORMULÁRIO ÚNICO - TODAS AS PERGUNTAS DE UMA VEZ
# ============================================================

config = st.radio(
    "**Configuração da rede:**",
    [
        "Apenas Primária (1 nível)",
        "Dois níveis de Primária",
        "Apenas Secundária",
        "Primária + Secundária",
        "Dois níveis de Primária + Secundária",
    ],
    index=0,
    horizontal=True,
)

st.markdown("---")

# ============================================================
# SEÇÃO 1: DADOS GERAIS DO POSTE
# ============================================================

with st.expander("**1. Dados Gerais do Poste**", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        altura_poste = st.selectbox("Altura do poste (m):", ALTURAS_POSTE, index=3)
        h_util = altura_util(altura_poste)
        st.caption(f"Altura útil: **{h_util:.2f} m**")
    with col2:
        localizacao = st.selectbox("Localização:", LOCATIONS, index=0)
    with col3:
        angulo_principal = st.number_input(
            "Ângulo principal (0° a 360°):",
            min_value=0, max_value=360, value=0, step=1,
            help="Ângulo medido a partir do norte (0°) no sentido horário",
        )
    with col4:
        qtd_cabos_princ = st.selectbox("Quantidade de cabos:", [1, 2, 3], index=0)

# ============================================================
# SEÇÃO 2: PRIMEIRO NÍVEL (PRIMÁRIA)
# ============================================================

if config in [
    "Apenas Primária (1 nível)",
    "Dois níveis de Primária",
    "Primária + Secundária",
    "Dois níveis de Primária + Secundária",
]:

    with st.expander("**2. Primeiro Nível (Primária)**", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            rede_1n = st.selectbox(
                "Tipo de rede:", TIPOS_REDE, index=0, key="rede_1n"
            )
        with col_b:
            cabos_disp = cabos_para_rede(rede_1n)
            cabo_1n = st.selectbox("Tipo de cabo:", cabos_disp, key="cabo_1n")
        with col_c:
            vao_1n = (
                st.number_input(
                    "Vão (m):", min_value=5, max_value=600, value=50, step=5, key="vao_1n"
                )
                if precisa_vao(rede_1n)
                else st.caption("Vão: N/A")
            )

        st.markdown("#### Derivação do Primeiro Nível")
        col_d, col_e = st.columns(2)
        with col_d:
            fim_linha_1n = st.checkbox("Fim de linha (sem derivação)", key="fl_1n")
        with col_e:
            ang_der_1n = (
                0
                if fim_linha_1n
                else st.slider(
                    "Ângulo de derivação (graus):",
                    0, 360, value=0, key="ang_der_1n",
                )
            )

        st.markdown("#### Cabos que derivam do Primeiro Nível")
        cabo_deriv_1n = st.radio(
            "Os cabos que derivam são os mesmos do primeiro nível ou diferentes?",
            ["Mesmos cabos", "Cabos diferentes"],
            horizontal=True,
            key="deriv_1n_opcao",
        )

        if cabo_deriv_1n == "Cabos diferentes":
            col_f, col_g, col_h = st.columns(3)
            with col_f:
                rede_deriv_1n = st.selectbox(
                    "Tipo de rede (derivação):", TIPOS_REDE, index=0, key="rede_deriv_1n"
                )
            with col_g:
                cabos_deriv_disp = cabos_para_rede(rede_deriv_1n)
                cabo_deriv_1n_tipo = st.selectbox(
                    "Tipo de cabo:", cabos_deriv_disp, key="cabo_deriv_1n_tipo"
                )
            with col_h:
                if precisa_vao(rede_deriv_1n):
                    vao_deriv_1n = st.number_input(
                        "Vão (derivação):",
                        min_value=5, max_value=600, value=50, step=5, key="vao_deriv_1n",
                    )
                else:
                    st.caption("Vão: N/A")
                    vao_deriv_1n = None
        else:
            rede_deriv_1n = rede_1n
            cabo_deriv_1n_tipo = cabo_1n

# ============================================================
# SEÇÃO 3: SEGUNDO NÍVEL DE PRIMÁRIA
# ============================================================

if config in ["Dois níveis de Primária", "Dois níveis de Primária + Secundária"]:

    with st.expander("**3. Segundo Nível de Primária**", expanded=True):
        col_i, col_j, col_k = st.columns(3)
        with col_i:
            altura_2n = st.number_input(
                "Altura útil (m):", min_value=0.0, max_value=20.0, value=6.0, step=0.5, key="altura_2n"
            )
        with col_j:
            rede_2n = st.selectbox(
                "Tipo de rede:", TIPOS_REDE, index=0, key="rede_2n"
            )
        with col_k:
            qtd_cabos_2n = st.selectbox("Quantidade de cabos:", [1, 2, 3], index=0, key="qtd_2n")

        col_l, col_m = st.columns(2)
        with col_l:
            cabos_2n_disp = cabos_para_rede(rede_2n)
            cabo_2n = st.selectbox("Tipo de cabo:", cabos_2n_disp, key="cabo_2n")
        with col_m:
            if precisa_vao(rede_2n):
                vao_2n = st.number_input(
                    "Vão (m):", min_value=5, max_value=600, value=50, step=5, key="vao_2n"
                )
            else:
                st.caption("Vão: N/A")
                vao_2n = None

        st.markdown("#### Derivação do Segundo Nível")
        col_n, col_o = st.columns(2)
        with col_n:
            fim_linha_2n = st.checkbox("Fim de linha (sem derivação)", key="fl_2n")
        with col_o:
            ang_der_2n = (
                0
                if fim_linha_2n
                else st.slider(
                    "Ângulo de derivação (graus):",
                    0, 360, value=0, key="ang_der_2n",
                )
            )

        st.markdown("#### Cabos que derivam do Segundo Nível")
        cabo_deriv_2n = st.radio(
            "Os cabos que derivam são os mesmos do segundo nível ou diferentes?",
            ["Mesmos cabos", "Cabos diferentes"],
            horizontal=True,
            key="deriv_2n_opcao",
        )

        if cabo_deriv_2n == "Cabos diferentes":
            col_p, col_q, col_r = st.columns(3)
            with col_p:
                rede_deriv_2n = st.selectbox(
                    "Tipo de rede (derivação):", TIPOS_REDE, index=0, key="rede_deriv_2n"
                )
            with col_q:
                cabos_deriv_2n_disp = cabos_para_rede(rede_deriv_2n)
                cabo_deriv_2n_tipo = st.selectbox(
                    "Tipo de cabo:", cabos_deriv_2n_disp, key="cabo_deriv_2n_tipo"
                )
            with col_r:
                if precisa_vao(rede_deriv_2n):
                    vao_deriv_2n = st.number_input(
                        "Vão (derivação):",
                        min_value=5, max_value=600, value=50, step=5, key="vao_deriv_2n",
                    )
                else:
                    st.caption("Vão: N/A")
                    vao_deriv_2n = None
        else:
            rede_deriv_2n = rede_2n
            cabo_deriv_2n_tipo = cabo_2n

# ============================================================
# SEÇÃO 4: REDE SECUNDÁRIA
# ============================================================

if config in ["Apenas Secundária", "Primária + Secundária", "Dois níveis de Primária + Secundária"]:

    with st.expander("**4. Rede Secundária**", expanded=True):
        col_s, col_t, col_u = st.columns(3)
        with col_s:
            rede_sec = st.selectbox(
                "Tipo de rede:", TIPOS_REDE, index=4, key="rede_sec"
            )
        with col_t:
            altura_sec = st.number_input(
                "Altura (m):", min_value=0.0, max_value=20.0, value=5.0, step=0.5, key="altura_sec"
            )
        with col_u:
            qtd_fases_sec = st.selectbox(
                "Quantidade de fases:", [1, 2, 3], index=0, key="qtd_fases_sec"
            )

        col_v, col_w = st.columns(2)
        with col_v:
            cabo_controle_sec = st.selectbox(
                "Cabo de controle:", CABOS_CONVENCIONAL, index=0, key="cabo_controle_sec"
            )
        with col_w:
            cabo_neutro_sec = st.selectbox(
                "Cabo do neutro:", CABOS_CONVENCIONAL, index=1, key="cabo_neutro_sec"
            )

        st.markdown("#### Derivação da Rede Secundária")
        col_x, col_y = st.columns(2)
        with col_x:
            fim_linha_sec = st.checkbox("Fim de linha (sem derivação)", key="fl_sec")
        with col_y:
            ang_der_sec = (
                0
                if fim_linha_sec
                else st.slider(
                    "Ângulo de derivação (graus):",
                    0, 360, value=0, key="ang_der_sec",
                )
            )

st.markdown("---")

# ============================================================
# RESULTADO DINÂMICO
# ============================================================

st.subheader("Resultado do Cálculo", divider="red")

# --- Processar forças ---
fx_total = 0.0
fy_total = 0.0
tem_primaria = config in [
    "Apenas Primária (1 nível)",
    "Dois níveis de Primária",
    "Primária + Secundária",
    "Dois níveis de Primária + Secundária",
]
tem_2n = config in ["Dois níveis de Primária", "Dois níveis de Primária + Secundária"]
tem_sec = config in ["Apenas Secundária", "Primária + Secundária", "Dois níveis de Primária + Secundária"]

resumo_linhas = []

if tem_primaria:
    tracao_1n = obter_tracao(rede_1n, cabo_1n, vao_1n if precisa_vao(rede_1n) else None)
    H_1n = h_util * 0.85
    f_1n = tracao_transf(tracao_1n, h_util, H_1n, qtd_cabos_princ)
    ang_rad_1n = math.radians(angulo_principal)
    fx_1n = f_1n * math.cos(ang_rad_1n)
    fy_1n = f_1n * math.sin(ang_rad_1n)
    fx_total += fx_1n
    fy_total += fy_1n
    resumo_linhas.append(f"1º Nível: **{rede_1n}** / **{cabo_1n}** → {f_1n:.0f} daN @ {angulo_principal}°")

    # Derivação do primeiro nível
    ang_der_1n_atual = ang_der_1n if not fim_linha_1n else 0
    if not fim_linha_1n and ang_der_1n_atual > 0:
        if cabo_deriv_1n == "Cabos diferentes":
            vao_deriv_usar_1n = vao_deriv_1n if "vao_deriv_1n" in dir() else vao_1n
            tracao_d1 = obter_tracao(
                rede_deriv_1n,
                cabo_deriv_1n_tipo,
                vao_deriv_usar_1n if precisa_vao(rede_deriv_1n) else None,
            )
            f_d1 = tracao_transf(tracao_d1, h_util, H_1n, qtd_cabos_princ)
        else:
            f_d1 = f_1n * 0.5

        ang_der_rad_1n = math.radians(ang_der_1n_atual)
        fx_d1 = f_d1 * math.cos(ang_rad_1n + ang_der_rad_1n)
        fy_d1 = f_d1 * math.sin(ang_rad_1n + ang_der_rad_1n)
        fx_total += fx_d1
        fy_total += fy_d1
        resumo_linhas.append(
            f"  └ Derivação: {ang_der_1n_atual}° ({cabo_deriv_1n}) → {f_d1:.0f} daN"
        )

if tem_2n:
    tracao_2n = obter_tracao(rede_2n, cabo_2n, vao_2n if precisa_vao(rede_2n) else None)
    f_2n = tracao_transf(tracao_2n, h_util, altura_2n, qtd_cabos_2n)
    ang_2n_rad = math.radians(angulo_principal)
    fx_2n = f_2n * math.cos(ang_2n_rad)
    fy_2n = f_2n * math.sin(ang_2n_rad)
    fx_total += fx_2n
    fy_total += fy_2n
    resumo_linhas.append(f"2º Nível: **{rede_2n}** / **{cabo_2n}** → {f_2n:.0f} daN @ {angulo_principal}°")

    ang_der_2n_atual = ang_der_2n if not fim_linha_2n else 0
    if not fim_linha_2n and ang_der_2n_atual > 0:
        if cabo_deriv_2n == "Cabos diferentes":
            vao_deriv_usar_2n = vao_deriv_2n if "vao_deriv_2n" in dir() else vao_2n
            tracao_d2 = obter_tracao(
                rede_deriv_2n,
                cabo_deriv_2n_tipo,
                vao_deriv_usar_2n if precisa_vao(rede_deriv_2n) else None,
            )
            f_d2 = tracao_transf(tracao_d2, h_util, altura_2n, qtd_cabos_2n)
        else:
            f_d2 = f_2n * 0.5

        ang_der_rad_2n = math.radians(ang_der_2n_atual)
        fx_d2 = f_d2 * math.cos(ang_2n_rad + ang_der_rad_2n)
        fy_d2 = f_d2 * math.sin(ang_2n_rad + ang_der_rad_2n)
        fx_total += fx_d2
        fy_total += fy_d2
        resumo_linhas.append(
            f"  └ Derivação: {ang_der_2n_atual}° ({cabo_deriv_2n}) → {f_d2:.0f} daN"
        )

if tem_sec:
    tracao_fase = obter_tracao(rede_sec, cabo_controle_sec)
    tracao_neutro = obter_tracao(rede_sec, cabo_neutro_sec)
    f_fase_sec = tracao_transf(tracao_fase, h_util, altura_sec, qtd_fases_sec)
    f_neutro_sec = tracao_transf(tracao_neutro, h_util, altura_sec, 1)

    ang_sec_rad = math.radians(ang_der_sec if not fim_linha_sec else 0)
    fx_fase_sec = f_fase_sec * math.cos(ang_sec_rad)
    fy_fase_sec = f_fase_sec * math.sin(ang_sec_rad)
    fx_neutro_sec = f_neutro_sec * math.cos(ang_sec_rad)
    fy_neutro_sec = f_neutro_sec * math.sin(ang_sec_rad)

    fx_total += fx_fase_sec + fx_neutro_sec
    fy_total += fy_fase_sec + fy_neutro_sec
    resumo_linhas.append(
        f"Rede Sec.: **{rede_sec}** / Controle: **{cabo_controle_sec}** / Neutro: **{cabo_neutro_sec}** → "
        f"{f_fase_sec + f_neutro_sec:.0f} daN"
    )

    if not fim_linha_sec and ang_der_sec > 0:
        f_sec_d = (f_fase_sec + f_neutro_sec) * 0.5
        ang_sec_d_rad = math.radians(ang_der_sec)
        fx_sd = f_sec_d * math.cos(ang_sec_d_rad)
        fy_sd = f_sec_d * math.sin(ang_sec_d_rad)
        fx_total += fx_sd
        fy_total += fy_sd
        resumo_linhas.append(f"  └ Derivação: {ang_der_sec}° → {f_sec_d:.0f} daN")

# --- Resultante final ---
magnitude, ang_resultante = calc_resultante([fx_total], [fy_total])

# ============================================================
# EXIBIR RESULTADO EM DESTAQUE
# ============================================================

col_r1, col_r2, col_r3, col_r4 = st.columns(4)
with col_r1:
    st.metric("Força Resultante", f"{magnitude:.1f} daN", delta_color="off")
with col_r2:
    st.metric("Ângulo Resultante", f"{ang_resultante:.1f}°", delta_color="off")
with col_r3:
    st.metric("Componente X", f"{fx_total:.1f} daN", delta_color="off")
with col_r4:
    st.metric("Componente Y", f"{fy_total:.1f} daN", delta_color="off")

st.markdown("---")

col_rec1, col_rec2 = st.columns([2, 1])
with col_rec1:
    st.markdown("### Resumo dos Esforços")
    for linha in resumo_linhas:
        st.markdown(f"- {linha}")
    st.markdown(f"**Poste:** {altura_poste}m | **Altura útil:** {h_util:.2f}m | **Local:** {localizacao}")

with col_rec2:
    st.markdown("### Recomendação")
    if magnitude == 0:
        st.info("Preencha os parâmetros acima para calcular.")
    elif magnitude <= 300:
        st.success(f"Poste de **9m** ou **10m** é suficiente")
        st.caption("Carga <= 300 daN")
    elif magnitude <= 500:
        st.success(f"Poste de **11m** ou **12m** recomendado")
        st.caption("Carga <= 500 daN")
    elif magnitude <= 800:
        st.warning(f"Poste de **14m** é recomendado")
        st.caption("Carga <= 800 daN")
    elif magnitude <= 1200:
        st.warning(f"Poste de **16m** é necessário")
        st.caption("Carga <= 1200 daN")
    else:
        st.error(f"Carga de {magnitude:.0f} daN excede postes padrão")
        st.caption("Consulte engenharia")

# ============================================================
# TABELA COMPARATIVA
# ============================================================

if magnitude > 0:
    st.markdown("---")
    st.markdown("### Comparativo de Postes")

    cargas_limite = [300, 500, 800, 1200]
    postes_sugeridos = ["9m / 10m", "11m / 12m", "14m", "16m"]

    dados_comp = {
        "Poste": postes_sugeridos,
        "Carga Máx. (daN)": cargas_limite,
        "Atende": [
            "✅" if magnitude <= c else "❌" for c in cargas_limite
        ],
    }

    st.dataframe(dados_comp, use_container_width=True, hide_index=True)
