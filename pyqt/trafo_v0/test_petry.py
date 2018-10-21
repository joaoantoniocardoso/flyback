#!/usr/bin/python3
# encoding: UTF-8
from math import pi
from math import sqrt

import trafo
import cores
import wires


def find_next_core_aeaw(_aeaw_min, _cores_list, _index=0):
    """ ? """
    for c in _cores_list:
        _index = _index + 1
        if (c.aeaw > _aeaw_min):
            break

    return _index


def find_next_wire_acu(_acu_min, _wires_list, _index=0):
    """ ? """
    for w in _wires_list:
        _index = _index + 1
        if (w.acu > _acu_min):
            break

    return _index


# Petry flyback parameters:
Vin_min = 253
Vin_max = 340
Vd = 1.5
Vout = 13
dVc = 100E-3
eff = 0.7
Pout = 100
Dmax = 0.4
fs = 28E3
DB = 0.25
Ta = 50
Is_max = 32.2
u0 = pi * 4E-7
j = 400
kp = 0.5
kw = 0.4

# Section 3.2.1.1: Core Selection

# Calculates minimal AeAw:
aeaw_min = trafo.det_ae_aw(Pout, kp, kw, j, DB, fs)
print('Calculed AeAw_min: ' + str(aeaw_min))

# Loads thornton cores:
cores_list = cores.load("../../cores/thornton_cores.json", 'Thornton')
print('(' + str(len(cores_list)) + ' Cores loaded)')
# for c in cores_list:
#    print('\t' + c.brand + ', ' + c.model)

# Finds the smallest core from loaded ones that has a grater aeaw than aeaw_min
core_index = find_next_core_aeaw(aeaw_min, cores_list)
core_selected = cores_list[core_index]
print('Selected core: ' + core_selected.model)

# Section 3.2.1.2: Calculates the necessary air gap for the selected EE core:
lg = trafo.det_entreferro(Pout, eff, fs, u0, DB, core_selected.ae)
print('Air Gap: ' + str(round(lg * 1E3, 3)) + ' [mm]')

# Section 3.2.1.3: Calculates transformer's primary turns
np, Ip_max = trafo.det_enrol_pri(Pout, eff, Vin_min, Dmax, DB, lg, u0)
print('Primary Turns: ' + str(np))
print('Primary Maximum Current: ' + str(round(Ip_max, 3)) + ' [A]')

# Section 3.2.1.4: Calculates transformer' secundary turns
ns = trafo.det_enrol_sec(np, Vout, Vd, Vin_min, Dmax)
print('Secundary Turns: ' + str(ns))

# Section 3.2.1.5: Wires
# Loads awg wires:
wires_list = wires.load("../../wires/wires.json")
print('(' + str(len(wires_list)) + ' Wires loaded)')
# for c in wires_list:
#    print('\t' + c.awg)

# Primary:
Ip_rms = Ip_max * sqrt(Dmax / 3)
wire_pri_acu_min = trafo.det_acu_min(Ip_rms, j)
print('For a primary RMS current of ' + str(round(Ip_rms, 3)) +
      ' [A], a minimum copper area of ' +
      str(round(wire_pri_acu_min * 1E6, 3)) + ' [mm^2] is needed')
wire_pri_index = find_next_wire_acu(wire_pri_acu_min, wires_list)
wire_pri_selected = wires_list[wire_pri_index]
print('Selected primary wire: ' + str(wire_pri_selected.awg) + ' AWG')

# Secundary:
Is_rms = Is_max * sqrt((1 - Dmax) / (3))
wire_sec_acu_min = trafo.det_acu_min(Is_rms, j)
print('For a secundary RMS current of ' + str(round(Is_rms, 3)) +
      ' [A], a minimum copper area of ' +
      str(round(wire_sec_acu_min * 1E6, 3)) + ' [mm^2] is needed')
wire_sec_index = find_next_wire_acu(wire_sec_acu_min, wires_list)
wire_sec_selected = wires_list[wire_sec_index]
print('Selected secundary wire: ' + str(wire_sec_selected.awg) + ' AWG')
