# encoding: UTF-8
# authors: Jonas V. de Souza, Joao Antonio. Cardoso

# TODO: enxugar modulos
from math import sqrt
from math import ceil
import json


def det_ae_aw(_Pout, _Kp, _Kw, _j, _DB, _fs):
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


def det_aw(_ext, _iint, _h):
    """ Returns a calculated aw for a given geometry. """
    return (_ext - _iint) * (_h / 2)


def det_entreferro(_Pout, _n, _fs, _u0, _DB, _Ae):
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


def det_enrol_pri(_Pout, _n, _Vin_min, _D_max, _DB, _lg, _u0):
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


def det_enrol_sec(_np, _vout, _vd, _vin_min, _d_max):
    """ Returns a number of turns for secundary side
    _np     primary turns
    _vout   nominal secundary (output) voltage
    _Vin_min minimum input-side (primary) voltage
    _d_max  maximum duty-cycle
    """
    ns = _np * ((_vout + _vd) / _vin_min) * ((1 - _d_max) / _d_max)
    return ceil(ns)


def det_acu_min(_ip_rms, _j):
    """ Returns the minimum copper area for a given RMS current."""
    return _ip_rms / (_j * 1E4)


def det_prof_penetr(_fs):
    """ Retuns a minimum copper radius for skin effect for a given frequency"""
    return 2 * 7.5 / sqrt(_fs)


def det_sec_cond(_fs, _ip_max, _d_max, _j, _is):
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


def det_Lmag(_np, _db, _ae, _ip, _ns):
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


def det_ae(_target, _json_file, _model_opt):
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



