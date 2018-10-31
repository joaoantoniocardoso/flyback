#!/usr/bin/python3
# encoding: UTF-8
import json


class Wire:
    def __init__(self, awg, dcu, acu, dw, aw, rho20c, rho100c, idc450):
        self.awg = awg                 # AWG size
        self.dcu = dcu                 # Copper diameter
        self.acu = acu                 # Copper area
        self.dw = dw                   # Wire diameter
        self.aw = aw                   # Wire area
        self.rho20c = rho20c           # Resistivity at 20°C
        self.rho100c = rho100c         # Resistivity at 100°C
        self.idc450 = idc450           # Current for a density of 450 A/cm^2

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

    def sort(_wires_list):
        """Returns a decreasing awg sorted list of wires"""
        return sorted(_wires_list, key=lambda x: x.awg, reverse=False)
