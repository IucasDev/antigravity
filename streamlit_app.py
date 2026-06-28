import streamlit as st
import math

st.set_page_config(page_title="Cálculo de Esforços Mecânicos", layout="centered")

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
CABOS_CONVENCIONAL = ["A02", "A04", "A20", "A40", "A336", "A477",
                      "C02", "C04", "C06", "C20", "C25", "C35", "C40", "C70", "C120",
                      "S02", "S04", "S20", "S40", "S336", "S477"]

# Trações por vão - Pré-Reunido
PR = {
    "PB35":  {5: 4, 10: 14, 15: 32, 20: 56, 25: 88, 30: 127, 35: 172, 40: 225},
    "PB50":  {5: 6, 10: 24, 15: 51, 20: 91, 25: 142, 30: 204, 35: 278, 40: 363},
    "PB70":  {5: 7, 10: 30, 15: 67, 20: 119, 25: 186, 30: 267, 35: 364, 40: 475},
    "PB120": {5: 8, 10: 33, 15: 74, 20: 132, 25: 206, 30: 296, 35: 403, 40: 527},
}

# Trações por vão - Compacta (tabela completa)
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

# CAZ/CAW
CAZ = {
    "CAZ 3,09":   {50: 229, 100: 256, 150: 263, 200: 282, 300: 318, 400: 349, 500: 376, 600: 400},
    "CAZ 3x2,25": {50: 357, 100: 395, 150: 406, 200: 436, 300: 491, 400: 540, 500: 580, 600: 615},
    "CAW 3,26":   {50: 244, 100: 273, 150: 276, 200: 296, 300: 334, 400: 368, 500: 398, 600: 426},
    "CAW 3x2,59": {50: 438, 100: 492, 150: 495, 200: 524, 300: 588, 400: 645, 500: 696, 600: 741},
    "CAA 04":     {50: 217, 100: 269, 150: 313, 200: 324, 300: 324, 400: 324, 500: 324, 600: 324},
}

# Protegido unitário
PROT = {"PA50": 311, "PA70": 375, "PA95": 469, "PA120": 527, "PA185": 683, "PA240": 795}

# Cabos -> tração (tabela geral)
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


# ============================================================
# INICIALIZAÇÃO DO ESTADO
# ============================================================

if "step" not in st.session_state:
    st.session_state.step = 1

for key in ["altura_poste", "angulo", "qtd_cabos", "localizacao",
            "tipo_rede", "cabo_escolhido", "vao", "deriva_graus", "fim_linha",
            "segundo_nivel", "altura_2n", "tipo_rede_2n", "cabo_2n",
            "qtd_cabo_2n", "angulo_2n", "fim_linha_2n",
            "rede_sec", "tipo_rede_sec", "altura_sec",
            "qtd_fases_sec", "cabo_controle_sec", "cabo_neutro_sec",
            "angulo_sec", "fim_linha_sec"]:
    if key not in st.session_state:
        if key in ["altura_poste", "qtd_cabos", "deriva_graus", "qtd_cabo_2n",
                    "angulo_2n", "altura_sec", "qtd_fases_sec", "angulo_sec",
                    "angulo", "vao"]:
            st.session_state[key] = 0
        elif key in ["fim_linha", "segundo_nivel", "rede_sec",
                      "fim_linha_2n", "fim_linha_sec"]:
            st.session_state[key] = False
        else:
            st.session_state[key] = ""


# ============================================================
# INTERFACE
# ============================================================

st.title("Cálculo de Esforços Mecânicos em Postes")
st.caption("Sistema para verificação de resistência de postes de concreto")
st.divider()

# ---------- STEP 1: ALTURA DO POSTE ----------
if st.session_state.step == 1:
    st.subheader("1. Altura do Poste")
    alt = st.selectbox("Selecione a altura do poste (metros):", ALTURAS_POSTE,
                       index=ALTURAS_POSTE.index(st.session_state.altura_poste) if st.session_state.altura_poste in ALTURAS_POSTE else 3)
    h_util = altura_util(alt)
    st.info(f"Altura útil calculada: **{h_util:.2f} m** (altura - 10% enterrado - 0,7m)")
    if st.button("Continuar", type="primary"):
        st.session_state.altura_poste = alt
        st.session_state.step = 2
        st.rerun()

# ---------- STEP 2: ÂNGULO ----------
elif st.session_state.step == 2:
    st.subheader("2. Ângulo da Rede")
    ang = st.number_input("Digite o ângulo em graus (0° a 360°):",
                          min_value=0, max_value=360, value=st.session_state.angulo, step=1)
    st.caption("O ângulo é medido a partir do norte (0°) no sentido horário")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Voltar"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Continuar", type="primary"):
            st.session_state.angulo = ang
            st.session_state.step = 3
            st.rerun()

# ---------- STEP 3: CABOS ----------
elif st.session_state.step == 3:
    st.subheader("3. Quantidade de Cabos")
    qtd = st.selectbox("Quantos cabos?", [1, 2, 3],
                       index=[1, 2, 3].index(st.session_state.qtd_cabos) if st.session_state.qtd_cabos in [1, 2, 3] else 0)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Voltar"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Continuar", type="primary"):
            st.session_state.qtd_cabos = qtd
            st.session_state.step = 4
            st.rerun()

# ---------- STEP 4: LOCALIZAÇÃO ----------
elif st.session_state.step == 4:
    st.subheader("4. Localização")
    loc = st.radio("Selecione o tipo de localização:", LOCATIONS,
                   index=LOCATIONS.index(st.session_state.localizacao) if st.session_state.localizacao in LOCATIONS else 0)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Voltar"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Continuar", type="primary"):
            st.session_state.localizacao = loc
            st.session_state.step = 5
            st.rerun()

# ---------- STEP 5: TIPO DE REDE ----------
elif st.session_state.step == 5:
    st.subheader("5. Tipo de Rede")
    rede = st.selectbox("Selecione o tipo de rede:", TIPOS_REDE,
                        index=TIPOS_REDE.index(st.session_state.tipo_rede) if st.session_state.tipo_rede in TIPOS_REDE else 0)

    cabos_opcoes = CABOS_PRE_REUNIDO
    cabos_default = CABOS_PRE_REUNIDO[1]
    if rede == "Rede Compacta":
        cabos_opcoes = CABOS_COMPACTA
        cabos_default = CABOS_COMPACTA[1]
    elif rede == "CAZ/CAW":
        cabos_opcoes = CABOS_CAZ
        cabos_default = CABOS_CAZ[0]
    elif rede == "Rede Protegida":
        cabos_opcoes = CABOS_PROTEGIDO
        cabos_default = CABOS_PROTEGIDO[1]
    elif rede == "Rede Convencional":
        cabos_opcoes = CABOS_CONVENCIONAL
        cabos_default = CABOS_CONVENCIONAL[0]

    cabo_escolhido = st.selectbox("Tipo de cabo:", cabos_opcoes,
                                  index=cabos_opcoes.index(st.session_state.cabo_escolhido) if st.session_state.cabo_escolhido in cabos_opcoes else 0)

    if rede in ["Pré-Reunido", "Rede Compacta", "CAZ/CAW"]:
        vao = st.number_input("Vão (metros):", min_value=5, max_value=600,
                              value=st.session_state.vao if st.session_state.vao else 50, step=5)
    else:
        vao = st.session_state.vao

    tracao_exib = obter_tracao(rede, cabo_escolhido, vao if rede in ["Pré-Reunido", "Rede Compacta", "CAZ/CAW"] else None)
    st.info(f"Tração de projeto: **{tracao_exib:.0f} daN**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Voltar"):
            st.session_state.step = 4
            st.rerun()
    with col2:
        if st.button("Continuar", type="primary"):
            st.session_state.tipo_rede = rede
            st.session_state.cabo_escolhido = cabo_escolhido
            st.session_state.vao = vao
            st.session_state.step = 6
            st.rerun()

# ---------- STEP 6: DERIVAÇÃO / FIM DE LINHA ----------
elif st.session_state.step == 6:
    st.subheader("6. Derivação")
    fl = st.checkbox("Fim de linha (sem derivação)", value=st.session_state.fim_linha)
    if not fl:
        ang_der = st.slider("Ângulo de derivação (graus):", 0, 360,
                            value=st.session_state.deriva_graus)
    else:
        ang_der = 0
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Voltar"):
            st.session_state.step = 5
            st.rerun()
    with col2:
        if st.button("Continuar", type="primary"):
            st.session_state.fim_linha = fl
            st.session_state.deriva_graus = ang_der
            st.session_state.step = 7
            st.rerun()

# ---------- STEP 7: SEGUNDO NÍVEL DE PRIMÁRIA ----------
elif st.session_state.step == 7:
    st.subheader("7. Segundo Nível de Primária")
    sn = st.radio("Possui segundo nível de primária?", ["Não", "Sim"],
                  index=0 if not st.session_state.segundo_nivel else 1)
    if sn == "Sim":
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            h2 = st.number_input("Altura útil (m):", min_value=0.0, max_value=20.0,
                                 value=float(st.session_state.altura_2n) if st.session_state.altura_2n else 0.0, step=0.5)
        with col2:
            q2 = st.selectbox("Quantidade de cabos:", [1, 2, 3],
                              index=[1, 2, 3].index(st.session_state.qtd_cabo_2n) if st.session_state.qtd_cabo_2n in [1, 2, 3] else 0)
        r2 = st.selectbox("Tipo de rede:", TIPOS_REDE,
                          index=TIPOS_REDE.index(st.session_state.tipo_rede_2n) if st.session_state.tipo_rede_2n in TIPOS_REDE else 0)

        cabos_opcoes = CABOS_PRE_REUNIDO
        if r2 == "Rede Compacta":
            cabos_opcoes = CABOS_COMPACTA
        elif r2 == "CAZ/CAW":
            cabos_opcoes = CABOS_CAZ
        elif r2 == "Rede Protegida":
            cabos_opcoes = CABOS_PROTEGIDO
        elif r2 == "Rede Convencional":
            cabos_opcoes = CABOS_CONVENCIONAL

        cb2 = st.selectbox("Tipo de cabo:", cabos_opcoes,
                           index=cabos_opcoes.index(st.session_state.cabo_2n) if st.session_state.cabo_2n in cabos_opcoes else 0)

        fl2 = st.checkbox("Fim de linha (sem derivação)", value=st.session_state.fim_linha_2n)
        if not fl2:
            ang2 = st.slider("Ângulo de derivação (graus):", 0, 360,
                             value=st.session_state.angulo_2n)
        else:
            ang2 = 0
    else:
        h2 = q2 = r2 = cb2 = fl2 = ang2 = None

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Voltar"):
            st.session_state.step = 6
            st.rerun()
    with col2:
        if st.button("Continuar", type="primary"):
            st.session_state.segundo_nivel = (sn == "Sim")
            if sn == "Sim":
                st.session_state.altura_2n = h2
                st.session_state.qtd_cabo_2n = q2
                st.session_state.tipo_rede_2n = r2
                st.session_state.cabo_2n = cb2
                st.session_state.fim_linha_2n = fl2
                st.session_state.angulo_2n = ang2
            else:
                for k in ["altura_2n", "tipo_rede_2n", "cabo_2n",
                          "qtd_cabo_2n", "angulo_2n", "fim_linha_2n"]:
                    st.session_state[k] = "" if k in ["tipo_rede_2n", "cabo_2n"] else 0
            st.session_state.step = 8
            st.rerun()

# ---------- STEP 8: REDE SECUNDÁRIA ----------
elif st.session_state.step == 8:
    st.subheader("8. Rede Secundária")
    rs = st.radio("Possui rede secundária?", ["Não", "Sim"],
                  index=0 if not st.session_state.rede_sec else 1)
    if rs == "Sim":
        st.divider()
        rts = st.selectbox("Tipo de rede:", TIPOS_REDE,
                           index=TIPOS_REDE.index(st.session_state.tipo_rede_sec) if st.session_state.tipo_rede_sec in TIPOS_REDE else 0)

        col_a, col_b = st.columns(2)
        with col_a:
            h_sec = st.number_input("Altura (m):", min_value=0.0, max_value=20.0,
                                    value=float(st.session_state.altura_sec) if st.session_state.altura_sec else 0.0, step=0.5)
        with col_b:
            qf = st.selectbox("Quantidade de fases:", [1, 2, 3],
                              index=[1, 2, 3].index(st.session_state.qtd_fases_sec) if st.session_state.qtd_fases_sec in [1, 2, 3] else 0)

        cc = st.selectbox("Cabo de controle:", CABOS_CONVENCIONAL,
                          index=CABOS_CONVENCIONAL.index(st.session_state.cabo_controle_sec) if st.session_state.cabo_controle_sec in CABOS_CONVENCIONAL else 0)
        cn = st.selectbox("Cabo do neutro:", CABOS_CONVENCIONAL,
                          index=CABOS_CONVENCIONAL.index(st.session_state.cabo_neutro_sec) if st.session_state.cabo_neutro_sec in CABOS_CONVENCIONAL else 0)

        fl_s = st.checkbox("Fim de linha (sem derivação)", value=st.session_state.fim_linha_sec)
        if not fl_s:
            ang_s = st.slider("Ângulo de derivação (graus):", 0, 360,
                              value=st.session_state.angulo_sec)
        else:
            ang_s = 0
    else:
        rts = h_sec = qf = cc = cn = fl_s = ang_s = None

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Voltar"):
            st.session_state.step = 7
            st.rerun()
    with col2:
        if st.button("Calcular", type="primary"):
            st.session_state.rede_sec = (rs == "Sim")
            if rs == "Sim":
                st.session_state.tipo_rede_sec = rts
                st.session_state.altura_sec = h_sec
                st.session_state.qtd_fases_sec = qf
                st.session_state.cabo_controle_sec = cc
                st.session_state.cabo_neutro_sec = cn
                st.session_state.fim_linha_sec = fl_s
                st.session_state.angulo_sec = ang_s
            st.session_state.step = 9
            st.rerun()

# ---------- STEP 9: RESULTADO ----------
elif st.session_state.step == 9:
    st.subheader("9. Resultado do Cálculo")

    h_poste = st.session_state.altura_poste
    h_util = altura_util(h_poste)
    ang_principal = st.session_state.angulo
    qtd_cabos = st.session_state.qtd_cabos
    local = st.session_state.localizacao
    tipo_rede = st.session_state.tipo_rede
    deriva = st.session_state.deriva_graus
    fim_linha = st.session_state.fim_linha

    # --- Cálculo principal ---
    cabo_principal = st.session_state.cabo_escolhido or "PB50"
    vao_principal = st.session_state.vao or 50
    tracao_base = obter_tracao(tipo_rede, cabo_principal, vao_principal)
    H_CABO_PRINCIPAL = h_util * 0.85
    f_principal = tracao_transf(tracao_base, h_util, H_CABO_PRINCIPAL, qtd_cabos)

    ang_rad = math.radians(ang_principal)
    fx_principal = f_principal * math.cos(ang_rad)
    fy_principal = f_principal * math.sin(ang_rad)

    if fim_linha or deriva == 0:
        fx_total, fy_total = fx_principal, fy_principal
    else:
        ang_der_rad = math.radians(deriva)
        f_deriv = f_principal * 0.5
        fx_deriv = f_deriv * math.cos(ang_rad + ang_der_rad)
        fy_deriv = f_deriv * math.sin(ang_rad + ang_der_rad)
        fx_total, fy_total = fx_principal + fx_deriv, fy_principal + fy_deriv

    # --- Segundo nível ---
    if st.session_state.segundo_nivel:
        h2 = st.session_state.altura_2n
        q2 = st.session_state.qtd_cabo_2n
        r2 = st.session_state.tipo_rede_2n
        cb2 = st.session_state.cabo_2n
        fl2 = st.session_state.fim_linha_2n
        ang2 = st.session_state.angulo_2n

        tracao2 = obter_tracao(r2, cb2, vaio=50)
        f2 = tracao_transf(tracao2, h_util, h2, q2)
        ang2_rad = math.radians(ang2)
        fx2 = f2 * math.cos(ang2_rad)
        fy2 = f2 * math.sin(ang2_rad)

        if not fl2 and ang2 != 0:
            f2d = f2 * 0.5
            ang2d_rad = math.radians(ang2)
            fx2d = f2d * math.cos(ang2d_rad)
            fy2d = f2d * math.sin(ang2d_rad)
            fx_total += fx2 + fx2d
            fy_total += fy2 + fy2d
        else:
            fx_total += fx2
            fy_total += fy2

    # --- Rede secundária ---
    if st.session_state.rede_sec:
        rts = st.session_state.tipo_rede_sec
        h_sec = st.session_state.altura_sec
        qf = st.session_state.qtd_fases_sec
        cc = st.session_state.cabo_controle_sec
        cn = st.session_state.cabo_neutro_sec
        fl_s = st.session_state.fim_linha_sec
        ang_s = st.session_state.angulo_sec

        tracao_fase = obter_tracao(rts, cc, vaio=50)
        tracao_neutro = obter_tracao(rts, cn, vaio=50)

        f_fase = tracao_transf(tracao_fase, h_util, h_sec, qf)
        f_neutro = tracao_transf(tracao_neutro, h_util, h_sec, 1)

        ang_sec_rad = math.radians(ang_s)
        fx_fase = f_fase * math.cos(ang_sec_rad)
        fy_fase = f_fase * math.sin(ang_sec_rad)
        fx_neutro = f_neutro * math.cos(ang_sec_rad)
        fy_neutro = f_neutro * math.sin(ang_sec_rad)

        fx_total += fx_fase + fx_neutro
        fy_total += fy_fase + fy_neutro

        if not fl_s and ang_s != 0:
            f_sec_d = (f_fase + f_neutro) * 0.5
            ang_sd_rad = math.radians(ang_s)
            fx_sd = f_sec_d * math.cos(ang_sd_rad)
            fy_sd = f_sec_d * math.sin(ang_sd_rad)
            fx_total += fx_sd
            fy_total += fy_sd

    # --- Resultante final ---
    magnitude, ang_resultante = calc_resultante([fx_total], [fy_total])

    st.divider()
    colr1, colr2 = st.columns(2)
    with colr1:
        st.metric("Força Resultante", f"{magnitude:.1f} daN")
        st.metric("Ângulo Resultante", f"{ang_resultante:.1f}°")
    with colr2:
        st.metric("Componente X", f"{fx_total:.1f} daN")
        st.metric("Componente Y", f"{fy_total:.1f} daN")

    st.divider()
    st.subheader("Resumo dos Parâmetros")
    st.write(f"**Poste:** {h_poste}m | **Altura útil:** {h_util:.2f}m")
    st.write(f"**Rede:** {tipo_rede} | **Local:** {local}")
    st.write(f"**Cabos:** {qtd_cabos} | **Ângulo principal:** {ang_principal}°")
    st.write(f"**Derivação:** {'Fim de linha' if fim_linha else f'{deriva}°'}")
    if st.session_state.segundo_nivel:
        st.write(f"**2º nível:** {st.session_state.tipo_rede_2n} / {st.session_state.cabo_2n}")
    if st.session_state.rede_sec:
        st.write(f"**Rede secundária:** {st.session_state.tipo_rede_sec} / Controle: {st.session_state.cabo_controle_sec} / Neutro: {st.session_state.cabo_neutro_sec}")

    if magnitude > 0:
        st.divider()
        st.subheader("Recomendação de Poste")
        if magnitude <= 300:
            st.success("Poste de **9m** ou **10m** é suficiente (carga <= 300 daN)")
        elif magnitude <= 500:
            st.success("Poste de **11m** ou **12m** recomendado (carga <= 500 daN)")
        elif magnitude <= 800:
            st.warning("Poste de **14m** é recomendado (carga <= 800 daN)")
        elif magnitude <= 1200:
            st.warning("Poste de **16m** é necessário (carga <= 1200 daN)")
        else:
            st.error(f"Carga de {magnitude:.0f} daN excede a capacidade de postes padrão. Consulte engenharia.")

    if st.button("Novo Cálculo", type="primary"):
        for key in list(st.session_state.keys()):
            if key != "step":
                del st.session_state[key]
        st.session_state.step = 1
        st.rerun()
