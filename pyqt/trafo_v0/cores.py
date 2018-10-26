#!/usr/bin/python3
# encoding: UTF-8
import json


class TransformerCore:
    def __init__(self, _ae, _aw, _le, _lt, _v, _aeaw, _model, _brand):
        self.ae = _ae
        self.aw = _aw
        self.le = _le
        self.lt = _lt
        self.v = _v
        self.aeaw = _aeaw
        self.model = _model
        self.brand = _brand


def load(_filename, _brand='unknown'):
    """Returns a list of cores"""

    with open(_filename, 'r') as f:
        cores_dict = json.load(f)

    cores = []
    for c in cores_dict:
        cores.append(TransformerCore(
            float(c['Ae']),
            float(c['Aw']),
            float(c['le']),
            float(c['lt']),
            float(c['V']),
            float(c['AeAw']),
            c['Modelo'],
            _brand)
        )

    return cores


# TEST  #


#cores = load("thornton_cores.json", 'Thornton')

#for c in cores:
#    print(c.brand + ', ' + c.model)
