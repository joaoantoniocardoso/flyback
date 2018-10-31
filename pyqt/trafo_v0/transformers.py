#!/usr/bin/python3
# encoding: UTF-8
from math import ceil
from dataclasses import dataclass, field
from typing import List


class Coil:
    awg: float          # awg wire size
    Nw_min: int         # minimum paralell wires
    Nw_max: int         # maximum paralell wires
    Rw_min: float       # minimum wire resistance
    Rw_max: float       # maximum wire resistance
    Ww_min: float       # minimum power losses
    Ww_max: float       # maximum power losses
    Awt_min: float      # minimum total window area
    Awt_max: float      # maximum total window area

    def __init__(self, wire_pri_acu_min, core, aw, wire, N, I_rms):
        self.awg = wire.awg
        self.Nw_min = (wire_pri_acu_min / wire.acu)
        if(self.Nw_min < 1):
            self.Nw_min = 1
        self.Nw_max = ceil((aw) / (wire.acu * N))
        if(self.Nw_max < 1):
                self.Nw_max = 1
        self.Rw_min = wire.rho100c * core.lt * N / ceil(self.Nw_max)
        self.Rw_max = wire.rho100c * core.lt * N / ceil(self.Nw_min)
        self.Ww_min = self.Rw_min * pow(I_rms, 2)
        self.Ww_max = self.Rw_max * pow(I_rms, 2)
        self.Awt_min = ceil(self.Nw_min) * N * wire.aw
        self.Awt_max = ceil(self.Nw_max) * N * wire.aw

    def print(self):
            print(str(self.awg) + ' awg MIN\t\tMAX')
            print('\tN: ' + str(round(self.Nw_min, 1)) +
                  '\t\t' + str(round(self.Nw_max, 1)))
            print('\tA: ' + str(round(self.Awt_min, 2)) +
                  '\t\t' + str(round(self.Awt_max, 2)))
            print('\tP: ' + str(round(self.Ww_max, 2)) +
                  '\t\t' + str(round(self.Ww_min, 2)))


@dataclass
class CoilCombination:
    np: Coil
    ns: List[Coil] = field(default_factory=list)
