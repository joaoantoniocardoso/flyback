# codificado em UTF-8
# autor: Jonas V. de Souza
# data: 10/19/2018
# ação: ...
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

# módulos : falta enxugar!
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
from math import sqrt
import json

# escolha do núcleo
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def det_ae_aw(_Pout, _Kp, _Kw, _j, _DB, _fs):
    # Ae*Aw = (1.1 * Pout) / (Kp*Kw*j*DB*fs)
    en = (1.1 * _Pout) / (_Kp * _Kw * _j * _DB * _fs)
    cm4 = en * 10000
    return round(cm4, 3)

# ...
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def det_aw(_ext, _iint, _h):
    return (_ext - _iint) * (_h / 2)

# determinação do entreferro
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def det_entreferro(_Pout, _n, _fs, _uo, _DB, _Ae):
    # DW = Pout / (n*fs)
    # o = 2*uo*DW / (DB^2*Ae)
    # de = o / 2
    DW = _Pout / (_n * _fs) # [J]
    o = (2 * _uo * DW) / (_DB * _DB * _Ae)
    mm = o / 2
    return mm

# Cálculo do Número de Espiras do Enrolamento Primário
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def det_enrol_pri(_Pout, _n, _Vin_min, _D_max, _DB, _o, _uo):
    # Ip
    Ip = (2 * _Pout) / (_n * _Vin_min * _D_max)
    # np
    np = (_DB * _o) / (_uo * Ip)

    return np, Ip

# Cálculo do Número de Espiras do Enrolamento Secundário
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def det_enrol_sec(_np, _vout, _vd, _vin_min, _d_max):
    ns = _np * ((_vout + _vd) / _vin_min) * ((1 - _d_max) / _d_max)
    return ns

# Determinação da Seção dos Condutores
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def det_sec_cond(_fs, _ip, _d_max, _j, _is):
    D = (2 * 7.5) / sqrt(_fs)

    Ipef_p = _ip * sqrt(_d_max / 3)

    Sp = Ipef_p / (_j * pow(10, 4))

    To = (1 - _d_max) / _fs
    Ipef_s = _is * sqrt((To * _fs) / 3)

    Ss = Ipef_s / (_j * pow(10, 4))

    # consultar tabela
    # faltar implementar !
    SD = 6.527 * pow(10, -7)
    # O número de condutores em paralelo será
    ns = Ss / SD

    # A condutores em paralelo de bitola B para confecção do enrolamento secundário.
    return round(ns)

# Determinação das Indutâncias Magnetizantes dos Enrolamentos
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def det_Lmag(_np, _db, _ae, _ip, _ns):
    Lmp = (_np * _db * _ae) / _ip
    Is = _ip * (_np / _ns)    
    Lms = (_ns * _db * _ae) / Is
    return Lmp, Lms

def det_ae(_target, _json_file, _model_opt):
    # flag de depuração
    depurar = 0

    # carregar .json
    with open(_json_file, 'r') as f:
        cores = json.load(f)

    # criar um dicionário dos modelos thornton do arquivo .json
    myDict = {'dict': []}
    for c in cores:
        myDict['dict'].append(
            (
                {
                    'target': _target,
                    'AeAw': float(c["AeAw"]),
                    'dif_per%': abs(round(((float(c["AeAw"]) - _target) / _target) * 100)),
                    'Ae': c["Ae"],
                    'Aw': c["Aw"],
                    'Modelo': c["Modelo"]}))

    if depurar:
        print('ordenado: nao.............................')
        for c in myDict['dict']:
            print(c)

    # ordenar dicionário
    sorted_obj = dict(myDict) 
    sorted_obj['dict'] = sorted(myDict['dict'], key=lambda x: x['dif_per%'], reverse=False)

    if depurar:
        print('ordenado: sim.............................')
        for c in sorted_obj['dict']:
            print(c)

    # criar um dicionário dos modelos disponíveis
    var_dic = {'dic_opt': []}
    for c in sorted_obj['dict']:
        if c['Modelo'] in _model_opt:
            var_dic['dic_opt'].append(c)

    if depurar:
        print('modelos disponiveis.............................')
        for c in var_dic['dic_opt']:
            print(c)

    return float(var_dic['dic_opt'][0]['Ae']) * 10**-4, var_dic['dic_opt'][0]['Modelo']
