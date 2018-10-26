# encoding: UTF-8
# authors: Jonas V. de Souza, Joao Antonio. Cardoso

# TODO: enxugar modulos
from math import sqrt, ceil, pi
import json

def core_aeaw_approx(_aeaw_min, _cores_list, _core_avai):
    """ ? """
    percs = []
    for i, c in enumerate(_cores_list):
        if c.model in _core_avai:
            percs.append([i, (((c.aeaw - _aeaw_min) / _aeaw_min) * 100)])

    core_sorted = sorted(percs, key=lambda y: y[1], reverse=False)
    return core_sorted[0][0]

def core_aeaw_min(_aeaw_min, _cores_list, _core_avai):
    """ ? """
    for c in _cores_list:
        if c.model in _core_avai:
            if (c.aeaw > _aeaw_min):
                break

    return _cores_list.index(c) + 1


def find_next_wire_acu(_acu_min, _wires_list):
    """ ? """
    for w in _wires_list:
        if (w.acu > _acu_min):
            break

    return _wires_list.index(w) + 1

def ae_aw(_Pout, _Kp, _Kw, _j, _DB, _fs):
    """ Returns a minimal Ae*Aw geometry for a given flyback transformer.
    Ref: BARBI, Ivo. – Projeto de Fontes Chaveadas, Florianopolis, 1997.
    _Pout   Flyback output power
    _Kp     primary winding occupation factor
    _Kw     occupation factor for core' wind
    _j      current density
    _DB     variation of density of magnetic flux
    _fs     flyback switching frequency
    Ae*Aw = (1.1 * Pout) / (Kp*Kw*j*DB*fs)
    """
    return round(10000 * (1.1 * _Pout) / (_Kp * _Kw * _j * _DB * _fs), 3)

def aw(_ext, _iint, _h):
    """ Returns a calculated aw for a given geometry. """
    return (_ext - _iint) * (_h / 2)

def air_gap(_Pout, _n, _fs, _u0, _DB, _Ae):
    """ Returns a calculated gap for a given core.
    _Pout   Flyback output power
    _n      efficiency
    _fs     flyback switching frequency
    _u0     permeability
    _DB     variation of density of magnetic flux
    _Ae     core dimension in cm
    DW = Pout / (n*fs)
    d = (2*u0*DW / (DB^2*Ae) ) / 2
    """
    DW = _Pout / (_n * _fs)  # [J]
    d = (_u0 * DW) / (_DB * _DB * (_Ae * 1E-4))
    return d

def enrol_pri(_Pout, _n, _Vin_min, _D_max, _DB, _lg, _u0):
    """ Returns a number of turns for primary side
    _Pout   Flyback output power
    _n      efficiency
    _Vin_min minimum input-side (primary) voltage
    _DB     variation of density of magnetic flux
    _u0     permeability
    _lg     air gap
    """
    Ip = (2 * _Pout) / (_n * _Vin_min * _D_max)
    np = (_DB * 2 * _lg) / (_u0 * Ip)
    return ceil(np), Ip

def enrol_sec(_np, _vout, _vd, _vin_min, _d_max):
    """ Returns a number of turns for secundary side
    _np     primary turns
    _vout   nominal secundary (output) voltage
    _Vin_min minimum input-side (primary) voltage
    _d_max  maximum duty-cycle
    """
    ns = _np * ((_vout + _vd) / _vin_min) * ((1 - _d_max) / _d_max)
    return ceil(ns)

def acu_min(_ip_rms, _j):
    """ Returns the minimum copper area for a given RMS current."""
    return _ip_rms / (_j * 1E4)

def prof_penetr(_fs):
    """ Retuns a minimum copper radius for skin effect for a given frequency"""
    return 2 * 7.5 / sqrt(_fs)

def l_mag(_np, _db, _ae, _ip, _ns):
    """ Returns a magnetizing inductance for primary and secundary coils
    _np     primary turns
    _db     ?
    _ae     ?
    _ip     primary current
    _ns     secundary turns
    """
    Lmp = (_np * _db * _ae) / _ip
    Is = _ip * (_np / _ns)
    Lms = (_ns * _db * _ae) / Is
    return Lmp, Lms

def ae(_target, _json_file, _model_opt):
    """ ??? """

    # Funcionamento:
    # 1) carrega os nucleos de um json
    # 2) calcula a diferença do AeAw almejado (_target) e o AeAw de cada modelo
    # 3) ordena pela diferença (do menor para o maior)
    # 4) retorna Ae (float) e o Modelo (string) escolhido
    #
    depurar = 1         # flag de depuração

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
                    'dif_per%': abs(round(((
                        float(c["AeAw"]) - _target) / _target) * 100)),
                    'Ae': c["Ae"],
                    'Aw': c["Aw"],
                    'Modelo': c["Modelo"]}))

    if depurar:
        print('ordenado: nao.............................')
        for c in myDict['dict']:
            print(c)

    # ordenar dicionário
    sorted_obj = dict(myDict)
    sorted_obj['dict'] = sorted(myDict['dict'], key=lambda x: x[
                                'dif_per%'], reverse=False)

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

def sec_cond(_fs, _ip_max, _d_max, _j, _is):
    """ Returns a calculated wire copper area
    _fs     flyback switching frequency
    _ip_max primary maximum current
    _d_max  maximum duty-cycle
    _j      current density
    _is     secundary current
    """
    D = (2 * 7.5) / sqrt(_fs)

    Ip_rms = _ip_max * sqrt(_d_max / 3)

    Sp = Ip_rms / (_j * pow(10, 4))

    To = (1 - _d_max) / _fs
    Ipef_s = _is * sqrt((To * _fs) / 3)

    Ss = Ipef_s / (_j * pow(10, 4))

    # consultar tabela
    # faltar implementar !
    SD = 6.527E-7
    # O número de condutores em paralelo será
    ns = Ss / SD

    # A condutores em paralelo de bitola B para confecção do enrolamento
    # secundário.
    return ceil(ps)

    # Seções por condutores em paralelo, primario
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def sec_pri(_ip, _d_max, _j, _is, _fs, _ns_max):
    Ipef_p = _ip * sqrt(_d_max / 3)

    Sp = Ipef_p / (_j * pow(10, 4))

    array_sd = []
    for ns in range(1, _ns_max + 1):
        array_sd.append([ns, (Sp / ns)])

    return array_sd


def wire_acu_min(_acu_list, _wires_list, _wire_avai):
    """ ? """
    par = 1
    array_wire = []
    for a in _acu_list:
        for w in _wires_list:
            if w.awg in _wire_avai:
                if(w.acu * 1E-4 < a[1]):
                    # print(w.awg, w.acu * 1E-4, a)
                    array_wire.append([par, w.awg, w.acu * 1E-4, w.dw])
                    par = par + 1
                    break

    return array_wire


def area_total(_n_esp, _list_wire):
    array_at = []
    for v in _list_wire:
        array_at.append([v[0], _n_esp * (v[0]) * pi * pow((v[3] / 2), 2)])

    return array_at


# Perdas por fio
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def perdas_awg(_list):
    array_ape = []
    for v in _list:
        array_ape.append([v[0], 1 / (v[2] * v[0])])

    return array_ape

# Seções por condutores em paralelo, secundario
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def sec_sec(_d_max, _fs, _is, _j, _ns_max):
    To = (1 - _d_max) / _fs
    Ipef_s = _is * sqrt((To * _fs) / 3)
    Ss = Ipef_s / (_j * pow(10, 4))

    array_ss = []
    for ns in range(1, _ns_max + 1):
        array_ss.append([ns, (Ss / ns)])

    return array_ss

    
# Determinação das Indutâncias Magnetizantes dos Enrolamentos
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def det_Lmag(_np, _db, _ae, _ip, _ns):
    Lmp = (_np * _db * _ae) / _ip
    Is = _ip * (_np / _ns)    
    Lms = (_ns * _db * _ae) / Is
    return Lmp, Lms
