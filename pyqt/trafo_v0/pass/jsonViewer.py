# encoding: utf-8
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

# módulos
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
import json

# variáveis globais
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

def det_ae(_target, _json_file, _model_opt):
    # flag de depuração
    depurar = 1

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

    return var_dic['dic_opt'][0]['Ae']