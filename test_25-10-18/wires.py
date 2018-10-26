#!/usr/bin/python3
# encoding: UTF-8
import json


class Wire:
    def __init__(self, _awg, _dcu, _acu, _dw, _aw, _rho20c, _rho100c, _idc450):
        self.awg = _awg
        self.dcu = _dcu
        self.acu = _acu
        self.dw = _dw
        self.aw = _aw
        self.rho20c = _rho20c
        self.rho100c = _rho100c
        self.idc450 = _idc450


def load(_filename):
    """Returns a list of wires"""

    with open(_filename, 'r') as f:
        wires_dict = json.load(f)

    wires = []
    for c in wires_dict:
        wires.append(Wire(
            int(c['AWG']),
            float(c['Dcu']),
            float(c['Acu']),
            float(c['Dw']),
            float(c['Aw']),
            float(c['Rho20C']),
            float(c['Rho100C']),
            c['IDC450'])
        )

    return wires


# TEST  #


# wires = load("wires.json")

# for c in wires:
#    print(c.awg)
