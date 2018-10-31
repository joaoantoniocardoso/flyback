#!/usr/bin/python3
# encoding: UTF-8
import json


class TransformerCore:
    def __init__(self, ae, aw, le, lt, v, aeaw, model, brand):
        self.ae = ae               # Central E Area
        self.aw = aw               # Window Area
        self.le = le               # Central length
        self.lt = lt               # Average turn length
        self.v = v                 # Core Volume
        self.aeaw = aeaw           # Core Central and Window Area product
        self.model = model         # Model name
        self.brand = brand         # Brand name

    def load(_filename, brand='unknown'):
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
                brand)
            )
        return cores

    def sort(_cores_list):
        """Returns a decreasing awg sorted list of wires"""
        return sorted(_cores_list, key=lambda x: x.aeaw, reverse=False)
