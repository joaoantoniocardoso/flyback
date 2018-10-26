#!/usr/bin/python3
# encoding: UTF-8
from math import sqrt, pi
import proj
import cores
import wires

# Petry flyback parameters:
Vin_max = 340
DB = 0.25
fs = 50E3
ips = 32.2
j = 400
kp = 0.5
kw = 0.4
eff = 0.7
Pout = 120
u0 = pi * 4E-7
Vin_min = 280
Vout = 12
Vd = 1.5
dVc = 100E-3
Dmax = 0.4
Ta = 50
max_paralelos = 5
mostrar_comparacoes = True

# Section 3.2.1.1: Core Selection
# Calculates minimal AeAw:
aeaw_min = proj.ae_aw(Pout, kp, kw, j, DB, fs)
print('Calculed AeAw_min: ' + str(aeaw_min))

# Loads thornton cores:
cores_list = cores.load("../cores/thornton_cores.json", 'Thornton')
core_available = ["EE-25/6", "EE-30/7", "EE-40/12", "EE-42/20", "EE-42/15"]

# Finds the smallest core from loaded ones that has a grater aeaw than aeaw_min
core_index = proj.core_aeaw_approx(aeaw_min, cores_list, core_available)
core_selected = cores_list[core_index]
print('Selected core: ' + core_selected.model)
print('Ae core(E-6): ', core_selected.ae)

# Section 3.2.1.2: Calculates the necessary air gap for the selected EE core:
lg = proj.air_gap(Pout, eff, fs, u0, DB, core_selected.ae)
print('Air Gap: ' + str(round(lg * 1E3, 3)) + ' [mm]')

# Section 3.2.1.3: Calculates transformer's primary turns
np, Ip_max = proj.enrol_pri(Pout, eff, Vin_min, Dmax, DB, lg, u0)
print('Primary Turns: ' + str(np))
print('Primary Maximum Current: ' + str(round(Ip_max, 3)) + ' [A]')

# Section 3.2.1.4: Calculates transformer' secundary turns
ns = proj.enrol_sec(np, Vout, Vd, Vin_min, Dmax)
print('Secundary Turns: ' + str(ns))

# Section 3.2.1.5: Wires
# Loads awg wires:
wires_list = wires.load("../wires/wires.json")
wires_available = [17, 18, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32]

# Primary:
Ip_rms = Ip_max * sqrt(Dmax / 3)

# step: 6
# obj: determinar a seção dos condutores

# primário
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
sec_pri    = proj.sec_pri(Ip_max, kw, j, ips, fs, max_paralelos)

# mostrar resultados
if mostrar_comparacoes:
    print("[06a] - (p): n paralelos por sec_pri =" )
    for i in sec_pri:
        print("\tpar =", i[0], "sec_pri =", i[1])

wires_select_p = proj.wire_acu_min(sec_pri, wires_list, wires_available)

# mostrar resultados
if mostrar_comparacoes:
    print("[06b] - (p): n paralelos por AWG =" )
    for i in wires_select_p:
        print("\tpar =", i[0], "awg|acu|dw =", i[1], i[2], i[3])

area_total_p = proj.area_total(np, wires_select_p)
# mostrar resultados
if mostrar_comparacoes:
    print("[06c] - (p): n paralelos por area =" )
    for i in area_total_p:
        print("\tpar =", i[0], "area =", round(i[1], 5))

wires_perdas_p = proj.perdas_awg(wires_select_p)
# mostrar resultados
if mostrar_comparacoes:
    print("[06d] - (p): n paralelos por perda =" )
    for i in wires_perdas_p:
        print("\tpar =", i[0], "perda =", round(i[1]))


escolha_p = sorted(wires_perdas_p, key=lambda y: y[1], reverse=False)
idx_best_awg_p = escolha_p[0][0]
print("[06] - num. pri. em paralelo =", escolha_p[0][0], ", awg =", wires_select_p[idx_best_awg_p - 1][1])

# secundário
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
sec_sec    = proj.sec_sec(kw, fs, ips, j, max_paralelos)
# mostrar resultados
if mostrar_comparacoes:
    print("[07a] - (s): n paralelos por sec_pri =" )
    for i in sec_sec:
        print("\tpar =", i[0], "sec_sec =", i[1])

wires_select_s = proj.wire_acu_min(sec_sec, wires_list, wires_available)
# mostrar resultados
if mostrar_comparacoes:
    print("[07b] - (s): n paralelos por AWG =" )
    for i in wires_select_s:
        print("\tpar =", i[0], "awg|acu|dw =", i[1], i[2], i[3])

area_total_s = proj.area_total(ns, wires_select_s)
# mostrar resultados
if mostrar_comparacoes:
    print("[07c] - (s): n paralelos por area =" )
    for i in area_total_s:
        print("\tpar =", i[0], "area =", round(i[1], 5))

wires_perdas_s = proj.perdas_awg(wires_select_s)
# mostrar resultados
if mostrar_comparacoes:
    print("[07d] - (s): n paralelos por perda =" )
    for i in wires_perdas_s:
        print("\tpar =", i[0], "perda =", round(i[1]))

escolha_s = sorted(wires_perdas_s, key=lambda y: y[1], reverse=False)
idx_best_awg_s = escolha_s[0][0]
print("[07] - num. sec. em paralelo = ", escolha_s[0][0], ", awg =", wires_select_s[idx_best_awg_s - 1][1])

# step: 16
# obj: determinar as indutâncias magnetizantes dos enrolamentos
Lm_pri, Lm_sec = proj.det_Lmag(round(np), DB, core_selected.ae * 1E-4, Ip_max, ns)
print("[08] - lm_pri =", Lm_pri, "H,", "Lm_sec =", Lm_sec, "H")
