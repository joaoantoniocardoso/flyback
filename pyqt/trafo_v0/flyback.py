#!/usr/bin/python3
# encoding: UTF-8
# ref: https://www.fairchildsemi.com/application-notes/AN/AN-4137.pdf
from math import sqrt, pow, pi, ceil

import trafo
from cores import TransformerCore
from wires import Wire
from transformers import Coil, CoilCombination


def intersection(lst1, lst2):
    return [value for value in lst1 if value in lst2]


def maximumTotalLoss(coilCombination, nscoil):
    return (coilCombination.np.Ww_max + nscoil.Ww_max,
            coilCombination.np.awg,
            nscoil.awg)


def minimumTotalLoss(coilCombination, nscoil):
    return (coilCombination.np.Ww_min + nscoil.Ww_min,
            coilCombination.np.awg,
            nscoil.awg)


def find_next_core_aeaw(_aeaw_min, _cores_list, _index=0):
    """ ? """
    for i, c in enumerate(_cores_list):
        if(i > _index):
            if (c.aeaw > _aeaw_min):
                break
    return i


def find_next_wire_acu(_acu_min, _wires_list, _aw_max, _core,
                       _awg_min=1, _awg_max=100, _nw_min=1, _nw_max=10,
                       _index=0):
    """ ? """
    if(_acu_min > _aw_max):
        return _index, _nw_min
    if(_awg_min > _awg_max):
        _awg_max, _awg_min = _awg_min, _awg_max
    if(_nw_min > _nw_max):
        _nw_max, _nw_min = _nw_min, _nw_max

    __index = _index
    __nw = _nw_min
    for i, w in enumerate(_wires_list):
        if(i > _index):
            if((w.awg >= _awg_min) and (w.awg <= _awg_max)):
                # number of paralell wires:
                _nw = ceil(_acu_min / w.acu)
                if((_nw >= _nw_min) and (_nw <= _nw_max)):
                    # occuped window area:
                    _aw = pi * pow(w.dw / 2, 2)         # wire area
                    _aw_occup = _aw * _nw               # total wires area

                    print('\t\t\t' + str(w.awg) + ' awg: ' + str(_nw) + 'x' +
                          str(round(w.acu * 1E4, 3)) + 'cm^2 = ' +
                          str(round(_aw_occup * 1E4, 3)) + 'cm^2')

                    if (_aw_occup < _aw_max):
                        __index = i
                        __nw = _nw
                    else:
                        break

    return __index, __nw


# Loads thornton cores:
cores_list = TransformerCore
cores_list = TransformerCore.load(
    "../../cores/thornton_cores.json", 'Thornton')
print('(' + str(len(cores_list)) + ' Cores loaded)')
cores_list = TransformerCore.sort(cores_list)
# for c in cores_list:
#    print('\t' + c.brand + ', ' + c.model)

# Loads awg wires:
wires_list = Wire
wires_list = Wire.load("../../wires/wires.json")
print('(' + str(len(wires_list)) + ' Wires loaded)')
wires_list = Wire.sort(wires_list)


# STEP 1. Determine the system specifications
# Line voltage Range (Vline_min and Vline_max)
# Following brazillian PRODIST module 8 from 01/01/2018 for
# adequated 380/220 voltage range: 202 to 231 volts.
# The european range: 195 to 265 volts.
# The universal range: 85 to 265 volts.
Vline_rms_min = 85
Vline_rms_max = 265
# Line frequency (fl)
# Following brazillian PRODIST module 8 form 01/01/2018 the range
# is from 59.9 to 60.1 Hz.
fl = 60
# Maximum output power (Pout) in watts
Pout = 60
# Estimated efficiency (Eff)
Eff = 0.70

Pin = Pout / Eff
# Load occupying factor for each output
# Kl = Pout[n]/Po
Kl1 = Kl = 1


# STEP 2. Determine DC link capacitor (CDC) and DC link voltage range
Cdc = 2E-6 * Pin        # 1uF per watt
print('Cdc: ' + str(round(Cdc * 1E6, 2)) + ' uF')
Cdc = 220 * 1E-6        # ESCOLHA ARBITRARIA
print('Cdc adjusted: ' + str(round(Cdc * 1E6, 2)) + ' uF')
Dch = 0.2               # typical capacitor charge dutycycle
Vdc_min = sqrt(2 * pow(Vline_rms_min, 2) - (Pin * (1 - Dch)) / (Cdc * fl))
Vdc_max = sqrt(2) * Vline_rms_max
print('Vdc_min: ' + str(round(Vdc_min, 3)) + ' [V]')
print('Vdc_max: ' + str(round(Vdc_max, 3)) + ' [V]')

# STEP 3. Determine the maximum dutyratio (Dmax)
# Typical Dmax for an universal input range for 650V mosfets:
Vds_nom = 650
Dmax = 0.4

# Output voltage reflected to the primary:
VRO = Vdc_min * (Dmax / (1 - Dmax))
Vds_max = Vds_nom - VRO
print('Vds_max: ' + str(round(Vds_max, 3)) + ' [V]')

# STEP 4. Determine the transformer primary side inductance (Lm)
fs = 50E3      # switching frequency

IEDC = Pin / (Vdc_min * Dmax)

# Worst case ripple factor (KRF = dI / (2 * IEDC));
KRF = 0.4       # typical value
# dI = Vdc_min * Dmax / (Lm * fs)
# but from KFR equation:
dI = KRF * 2 / IEDC

Lm = pow(Vdc_min * Dmax, 2) / (2 * Pin * fs * KRF)
print('Lm: ' + str(round(Lm * 1E3, 3)) + ' [mH]')

# Mosfet drain-source peak current:
Ids_peak = IEDC + (dI / 2)
print('Ids_peak: ' + str(round(Ids_peak, 3)) + ' [A]')
Ids_rms = sqrt((3 * pow(IEDC, 2) + pow(dI / 2, 2)) * (Dmax / 3))
print('Ids_rms: ' + str(round(Ids_rms, 3)) + ' [A]')

# The maximum input voltage guaranteeing CCM in full load condition:
# if it is negative, it is always at CCM regardless of input voltage variation
Vdc_ccm = pow(pow(2 * Lm * fs * Pin, -0.5) - pow(VRO, -1), -1)
print('Vdc_ccm: ' + str(round(Vdc_ccm, 3)) + ' [V]')

# STEP 5. Choose proper FPS considering input power and Idspeak
Iover = 1.1 * Ids_peak
print('Iover: ' + str(round(Iover, 3)) + ' [A]')

# STEP 6. Determine the proper core and the minimum primary turns (Np_min)
Bsat = 0.35

# Section 3.2.1.1: Core Selection
j = 400
u0 = pi * 4E-7
DB = 0.25
kp = 0.5
kw = 0.4

# Calculates minimal AeAw:
aeaw_min = trafo.det_ae_aw(Pout, kp, kw, j, DB, fs)
print('\nCalculed AeAw_min: ' + str(aeaw_min))

core_index = 0
for c in cores_list:
    print('\nCore selection:')
    # Finds the smallest core from loaded ones that has a grater
    # aeaw than aeaw_min
    if(core_index >= len(cores_list) - 1):
        break
    else:
        core_index = find_next_core_aeaw(aeaw_min, cores_list, core_index)
        core_selected = cores_list[core_index]
        print('\tSelected core: ' + core_selected.model)

    # Section 3.2.1.2: Calculates the necessary air gap for the
    # selected EE core:
    lg = trafo.det_entreferro(Pout, Eff, fs, u0, DB, core_selected.ae)
    print('\tAir Gap: ' + str(round(lg * 1E3, 3)) + ' [mm]')

    # STEP 7. Determine the number of turns for each output
    Np_min = ceil(Lm * Iover * 1E6 / (Bsat * core_selected.ae * 1E2))
    print('\tNp_min: ' + str(Np_min) + ' [turns]')

    Vdf1 = 1.5       # Diode forward voltage drop for output 1
    Vo1 = 12        # Voltage for Output 1
    # Ns_min = trafo.det_enrol_sec(Np_min, Vo1, Vdf1, Vdc_min, Dmax)
    n = (Dmax / (1 - Dmax)) * (Vdc_min / (Vo1 + Vdf1))
    Ns_min = Np_min / n
    Np = int(ceil(Np_min))
    Ns = int(ceil(Ns_min))

    # Optimizes Np and Ns for the smaller integers that fits in n ratio:
    print('\n\tCoil Turns optimization:')
    print('\t\tInitial condition:\n\t\t\tVVn = Np/Ns = ' +
          str(Np) + '/' + str(Ns) + ' = ' + str(round(n, 3)))
    print('\t\t\tVVo1_min @ Dmax: ' +
          str(round((Vdc_min * (Dmax / (1 - Dmax)) / (Np / Ns)) - Vdf1, 3)))
    print('\t\t\tVo1_max @ Dmax: ' +
          str(round((Vdc_max * (Dmax / (1 - Dmax)) / (Np / Ns)) - Vdf1, 3)))

    vo_err = 0.001      # accepted error for Vo
    for _Np in range(Np, 1000):
        for _Ns in range(Ns, 1000):
            _n = _Np / _Ns
            _Vo = (Vdc_min * (Dmax / (1 - Dmax)) / (_n) - Vdf1)
            if((_Vo < Vo1 * (1 + vo_err)) and
               (_Vo > Vo1 * (1 - vo_err))):
                Ns = _Ns
                Np = _Np
                n = Np / Ns
                break
        else:
            continue
        break

    print('\t\tOptimized condition:\n\t\t\tn = Np/Ns = ' +
          str(Np) + '/' + str(Ns) + ' = ' + str(round(n, 3)))
    Dmin = (Vo1 + Vdf1) / ((Vo1 + Vdf1) + (Vdc_max / (Np / Ns)))
    print('\t\t\tDmin: ' + str(round(Dmin, 3)))
    Dmax = (Vo1 + Vdf1) / ((Vo1 + Vdf1) + (Vdc_min / (Np / Ns)))
    print('\t\t\tDmax: ' + str(round(Dmax, 3)))
    print('\t\t\tVo1_min @ Dmin: ' +
          str(round((Vdc_min * (Dmin / (1 - Dmin)) / (Np / Ns)) - Vdf1, 3)))
    print('\t\t\tVo1_min @ Dmax: ' +
          str(round((Vdc_min * (Dmax / (1 - Dmax)) / (Np / Ns)) - Vdf1, 3)))
    print('\t\t\tVo1_max @ Dmin: ' +
          str(round((Vdc_max * (Dmin / (1 - Dmin)) / (Np / Ns)) - Vdf1, 3)))
    print('\t\t\tVo1_max @ Dmax: ' +
          str(round((Vdc_max * (Dmax / (1 - Dmax)) / (Np / Ns)) - Vdf1, 3)))

    # STEP 8. Determine the wire diameter for each winding
    print('\t\t\nCoil wire selection:')

    # Section 3.2.1.5: Wires
    # Compute primary and secundary currents
    Ip1_rms = Ids_rms
    Is1_rms = Ids_rms * sqrt(((1 - Dmax) / Dmax) * (
        (VRO * Kl1) / (Vo1 + Vdf1)))

    # Compute reserved area for each coil
    aw_iso = core_selected.aw * 0.01        # lost window area by insulation
    aw_util = core_selected.aw - aw_iso     # remaining window area
    aw1 = aw_util * 0.5 * ((Ip1_rms / (Ip1_rms + Is1_rms)) + (Np / (Np + Ns)))
    aw2 = aw_util * 0.5 * ((Is1_rms / (Ip1_rms + Is1_rms)) + (Ns / (Np + Ns)))
    print('\t\tArea reserved for primary winding: ' + str(round(aw1, 3)) +
          ' cm^2' + ' (' + str(round(100 * aw1 / core_selected.aw, 3)) + '%)')
    print('\t\tArea reserved for secundary winding: ' + str(round(aw2, 3)) +
          ' cm^2' + ' (' + str(round(100 * aw2 / core_selected.aw, 3)) + '%)')
    print('\t\tArea reserved for insulation: ' + str(round(aw_iso, 3)) +
          ' cm^2' + ' (' +
          str(round(100 * aw_iso / core_selected.aw, 3)) + '%)')
    print('\t\tTotal usable area: ' + str(round(aw_util, 3)) +
          ' cm^2' + ' (' +
          str(round(100 * aw_util / core_selected.aw, 3)) + '%)')

    # Compute the necessary area for each coil
    wire_pri_acu_min = trafo.det_acu_min(Ip1_rms, j)
    print('\t\tFor a primary RMS current of ' + str(round(Ip1_rms, 3)) +
          ' [A], a minimum copper area of ' +
          str(round(wire_pri_acu_min * 1E4, 3)) + ' [cm^2] is needed')
    wire_sec_acu_min = trafo.det_acu_min(Is1_rms, j)
    print('\t\tFor a secundary RMS current of ' + str(round(Is1_rms, 3)) +
          ' [A], a minimum copper area of ' +
          str(round(wire_sec_acu_min * 1E4, 3)) + ' [cm^2] is needed')

    coilCombinationList = []
    kw = 0.7        # wire winding factor
    # Primary Calculations
    for wp in wires_list:
        secundaryCoilList = []
        # Number of paralell wires for the primary:
        Nwp_min = (wire_pri_acu_min / wp.acu)
        if(Nwp_min < 1):
            Nwp_min = 1
        Awtp_min = ceil(Nwp_min) * Np * (wp.aw / kw)
        if((Awtp_min <= aw1)):        # it is possible to use it
            pcoil = Coil(wire_pri_acu_min,
                         core_selected,
                         aw1,
                         wp,
                         Np,
                         Ip1_rms,
                         kw)
            # Debug by printing
            '''
            print('==========[Primary]==========')
            pcoil.print()
            print('---------[Secundary]---------')
            '''
            # Secundary Calculations
            for ws in wires_list:
                # Number of paralell wires for the secundary:
                Nws_min = ceil(wire_sec_acu_min / ws.acu)
                if(Nws_min < 1):
                    Nws_min = 1
                Awts_min = Nws_min * Ns * (ws.aw / kw)
                if((Awts_min <= aw2)):        # it is possible to use it
                    scoil = Coil(wire_sec_acu_min,
                                 core_selected,
                                 aw2,
                                 ws,
                                 Ns,
                                 Is1_rms,
                                 kw)
                    # Debug by printing
                    '''scoil.print()'''
                    # Appends every secundary coil in a list
                    secundaryCoilList.append(scoil)

            if(0):
                print('\nerr..')
                print('Cannot fit a wire for the secundary coil...')
                print('Changing transformer core to a bigger one...')

            # appends each combination in a database
            coilCombination = CoilCombination(pcoil, secundaryCoilList)
            coilCombinationList.append(coilCombination)

    if(0):
        print('\nerr..')
        print('Cannot fit a wire for the primary coil...')
        print('Changing transformer core to a bigger one...')
    else:
        break

# Less losses
coilCombinationList_Ww_max = sorted(coilCombinationList,
                                    key=lambda x: x.np.Ww_max,
                                    reverse=False)
for cc in coilCombinationList_Ww_max:
    cc.ns = sorted(cc.ns, key=lambda x: x.Ww_max, reverse=False)

# Less Occuped Area
coilCombinationList_Awt_max = sorted(coilCombinationList,
                                     key=lambda x: x.np.Awt_max,
                                     reverse=False)
for cc in coilCombinationList_Awt_max:
    cc.ns = sorted(cc.ns, key=lambda x: x.Awt_max, reverse=False)

# Intersection of two lists looking for awg
coilCombinationList_intersection = intersection(coilCombinationList_Ww_max,
                                                coilCombinationList_Awt_max)


# Debug Prints
d = 10
for cc in coilCombinationList_intersection[:d]:
    print('==========[Primary]==========')
    cc.np.print()
    print('---------[Secundary]---------')
    for ns in cc.ns[:d]:
        ns.print()


primaryWire_selected = coilCombinationList_intersection[1].np
secundaryWire_selected = coilCombinationList_intersection[1].ns[1]

print('\t\tThe selected primary wire is ' +
      str(primaryWire_selected.awg) + ' awg')
print('\t\tThe selected secundary wire is ' +
      str(secundaryWire_selected.awg) + ' awg')
print('\t\tUsing ' + str(primaryWire_selected.Nw_min) +
      ' in paralell for primary side and ' +
      str(secundaryWire_selected.Nw_min) +
      ' for secundary:')
print('\t\t\toccuped area is ' +
      str(round(primaryWire_selected.Awt_min +
                secundaryWire_selected.Awt_min, 2)) + ' cm^2' +
      ' (' + str(round(100 * (primaryWire_selected.Awt_min +
                              secundaryWire_selected.Awt_min) /
                       aw_util, 2)) + '%)')
print('\t\t\tlosses is ' +
      str(round(primaryWire_selected.Ww_max +
                secundaryWire_selected.Ww_max, 2)) + ' W')
print('\t\tUsing ' + str(primaryWire_selected.Nw_max) +
      ' in paralell for primary side and ' +
      str(secundaryWire_selected.Nw_max) +
      ' for secundary:')
print('\t\t\toccuped area is ' +
      str(round(primaryWire_selected.Awt_max +
                secundaryWire_selected.Awt_max, 2)) + ' cm^2' +
      ' (' + str(round(100 * (primaryWire_selected.Awt_max +
                              secundaryWire_selected.Awt_max) /
                       aw_util, 2)) + '%)')
print('\t\t\tlosses is ' +
      str(round(primaryWire_selected.Ww_min +
                secundaryWire_selected.Ww_min, 2)) + ' W')

'''
k = 0.9    # transformer coupling factor
Lp = Lm / k


Lsp = (Np / Ns) * M
Lps = (Ns / Np) * M
'''

# STEP-9 : Choose the rectifier diode in the secondary
# side based on the voltage and current ratings
print('Output Diode selection:')
Vd1 = Vo1 + (Vdc_max * (Vo1 + Vdf1) / VRO)
Id1_rms = Ids_rms * sqrt((1 - Dmax) / Dmax) * (VRO * Kl1 / (Vo1 + Vdf1))
print('\tVd: ' + str(ceil(1.3 * Vd1)) + ' V')
print('\tId: ' + str(ceil(1.5 * Id1_rms)) + ' A')

# (10) STEP-10 : Determine the output capacitor
# considering the voltage and current ripple.
print('Output Capacitor Selection:')
Io1 = Pout / Vo1
Co1 = 1000 * 1E-6            # Capacitance
Co1_esr = 20 * 1E-3         # ESR
Ico1_rms = sqrt(pow(Id1_rms, 2) - pow(Io1, 2))
dVo1 = (Io1 * Dmax / (Co1 * fs)) + (
    Ids_peak * VRO * Co1_esr * Kl1 / (Vo1 + Vdf1))
Co1_loss = Co1_esr * pow(Ico1_rms, 2)
print('\tCo1: ' + str(ceil(Co1 * 1E6)) + ' uF')
print('\tIco1: ' + str(round(Ico1_rms, 2)) + ' A')
print('\tCo1_esr: ' + str(round(Co1_loss, 2) * 1E3) + ' mW')
print('\tRipple: ' + str(ceil(100 * dVo1 / Vo1)) + ' %')

# (11) STEP-11 : Design the RCD snubber.
# snubber capacitor voltage at the minimum input voltage
# and full load condition
print('Snubber selection:')
for k in range(25, 10, -1):
    Vsn = (k / 10) * VRO
    Llk = 1 * 1E-6
    dVsn = (5 / 100) * Vsn     # 5~10% ripple is reasonable
    Psn = fs * Llk * pow(Ids_peak, 2) * (Vsn / (Vsn - VRO))
    Rsn = pow(Vsn, 2) / Psn
    Csn = Vsn / (Rsn * fs * dVsn)
    Ids2 = (Pin * (Vdc_max + VRO) / (Vdc_max * VRO)) + (
        (Vdc_max * VRO) / (2 * Lm * fs * (Vdc_max + VRO)))
    Vsn2 = VRO + sqrt(pow(VRO, 2) + 2 * Rsn * Llk * fs * pow(Ids2, 2))
    Vds_max2 = Vdc_max + Vsn2
    # print(k / 10, Vds_max2, Csn, Rsn, Psn) # debug
    if(Vds_max2 < 0.9 * Vds_max):
        break
print('\tVds(max): ' + str(ceil(Vds_max2)) + ' V')
print('\tCsn: ' + str(ceil(Csn * 1E9)) + ' nF')
print('\tRsm: ' + str(ceil(Rsn) * 1E-3) + ' kOhms')
print('\tPsn: ' + str(round(Psn, 2)) + ' W')


# end
