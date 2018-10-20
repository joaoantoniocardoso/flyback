# encoding:  iso-8859-1
# autor: Jonas V. de Souza
# data: 10/19/2018
# ação: ...
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

# módulos
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
import trafo
import sys # exercutar app
from PyQt5 import uic # importa designer.ui
from PyQt5.QtCore import * # ...
from PyQt5.QtWidgets import *   # base da janela
from PyQt5.QtGui import *       # controle das figuras
import json

# ...
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
class combo_box_checkable(QComboBox):
    def add_item(self, item):
        super(combo_box_checkable, self).addItem(item)
        item = self.model().item(self.count() - 1, 0)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)

    def check_item(self, index):
        item = self.model().item(index, 0)
        return item.checkState() == Qt.Checked

    def checke_all_itens(self, _size):
        statusItens = []
        for idx in range(_size):
            status = self.check_item(idx)
            statusItens.append(status)
        return statusItens

# ...
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
class App(QWidget):
    def __init__(self):
        super().__init__()

        # abre janela do programa
        uic.loadUi('design3.ui', self)
        self.conf_tab_def(self.tabela_def)
        # self.conf_tab_model(self.tabela_model)

        self.tabela_model.setSelectionBehavior(QTableView.SelectRows)
        self.tabela_model.clicked.connect(self.sel_lin)

        self.botao_cm.clicked.connect(self.carregar_json)
        self.botao_sa.clicked.connect(self.selecionar_modelo)
        # self.proc_calc.clicked.connect(self.teste)
        # self.botao_thornton.clicked.connect(self.carregar_json_thornton)

        '''
        <x>180</x>
        <y>220</y>
        <width>151</width>
        <height>23</height>
        '''
        self.combo_box = combo_box_checkable(self)
        self.combo_box.move(454, 263) 
        self.combo_box.setFixedWidth(148)
        # self.combo_box.toolTip("Modelos disponíveis")

        self.mudar_img(self.label_model, 'trafo2.png')
        self.show()

    def selecionar_modelo(self):
        print(1)

    def carregar_json(self):
        end_json = self.pegar_end_arq()
        self.conf_tab_model(self.tabela_model, end_json)
        self.tabela_model.setEnabled(False)

    def mudar_img(self, _obj, _img):
        _obj.setPixmap(QPixmap(_img).scaledToHeight(240))

    def carregar_json_thornton(self):
        print(2)

    def teste(self):
        self.navegar_carregar_end()

    def pegar_end_arq(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            return fileName

    def sel_lin(self):
        indices = self.tabela_model.selectionModel().selectedRows() 
        for index in sorted(indices):
            nl = index.row()

        self.tabela_model.selectRow(nl);
        self.modelo_selecionado = nl

    def conf_tab_def(self, _obj):

        pi = 3.141592653589793
        ctes_inic_des  = ["DB", "fs", "Ipk_sec", "j", "kp", "kw", "n", "Pou", "u0", "Vmin_in", "Vout", "Vd"]
        ctes_inic_val  = [0.25, 50000, 32.2, 400, 0.5, 0.4, 0.7, 120, 4 * pi * 10**-7, 280, 12, 1.5]
        ctes_inic_unid = ["T", "Hz", "A", "A/cm^2", "-", "-", "*100=%", "W", "*10^-6u0", "V", "V", "V"]

        num_linhas = 12
        _obj.setRowCount(num_linhas)
        num_colunas = 3
        _obj.setColumnCount(num_colunas)
        infos = ['Constantes', 'Valores', 'Unidade']
        _obj.setHorizontalHeaderLabels(infos)

        for nl in range(12):
            nc = 0
            _obj.setItem(nl, nc, QTableWidgetItem(ctes_inic_des[nl]))
            if nl == 8:
                _obj.setItem(
                    nl,
                    nc + 1,
                    QTableWidgetItem(
                        str(round(ctes_inic_val[nl] * 10**6, 3) ) ) )
            else:
                _obj.setItem(
                    nl,
                    nc + 1,
                    QTableWidgetItem(
                        str(ctes_inic_val[nl] ) ) )

            _obj.setItem(nl, nc + 2, QTableWidgetItem(ctes_inic_unid[nl]))

        # ajustar largura das colunas
        # modo 3, definido pela célula de maior tamanho
        # http://doc.qt.io/qt-5/qheaderview.html#ResizeMode-enum
        _obj.horizontalHeader().setSectionResizeMode(3)

    def conf_tab_model(self, _obj, _end_json):
        # carregar .json
        # thornton_file = "thornton_cores.json"
        with open(_end_json, 'r') as f:
            _dic = json.load(f)

        num_linhas = len(list(_dic))
        num_colunas = len(list(_dic[0]))

        _obj.setRowCount(num_linhas)
        _obj.setColumnCount(num_colunas / 2 + 1)
        infos = ['Ae**', 'Aw', 'le', 'lt', 'V', 'AeAw', 'Modelo']
        _obj.setHorizontalHeaderLabels(infos)

        nc = 0
        nl = 0
        for item in _dic:
            for label, v in item.items():
                if nc % 2:
                    pass
                else:
                    _obj.setItem(nl, nc / 2, QTableWidgetItem(v))
                nc += 1
                if nc == 13:
                    self.combo_box.add_item("Modelo " + str(v))
                    break

            nc = 0
            nl += 1

        _obj.horizontalHeader().setSectionResizeMode(3)

        # for i in range(num_linhas):
        # self.combo_box.add_item("Modelo " + str(i))


# ...
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
def proj_trafo():

    # definições
    # -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
    delta_b = 0.25          # 01 - variação da densidade de fluxo [T];
    fs = 50000              # 02 - frequência de chaveamento [Hz];
    ips = 32.2              # 03 - corrente de pico no secundário [A];
    j = 400                 # 04 - densidade de corrente [A/cm2];
    kp = 0.5                # 05 - fator de utilização do primário;
    kw = 0.4                # 06 - fator de utilização da área da janela;
    n = 0.7                 # 07 - rendimento do conversor Flyback [n*100=%];
    pout = 120              # 08 - potência de saída [W];
    pi = 3.141592653589793  # Pi
    uo = 4 * pi * 10**-7    # 09 - permeabilidade do ar
    vmin = 280              # 10 - tensão de entrada mínima [V];
    vout = 12               # 11 - tensão de saída [V];
    vd = 1.5                # 12 - queda de tensão do diodo [V];
    thornton_file = "thornton_cores.json"
    modelos_d = ["EE-25/6", "EE-30/7", "EE-40/12", "EE-42/20", "EE-42/15"]

    # -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
    # -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
    # -- ----  PASSO-A-PASSO (6)  ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
    # -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
    # -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

    # step: 1
    # obj: determinar o produto da área da janela do núcleo (Aa) pela área da seção transversal do núcleo (Ae)
    ae_aw        = trafo.det_ae_aw(pout, kp, kw, j, delta_b, fs)
    print("[1] - ae*aw =", ae_aw, "cm^4, critério de escolha do trafo.")

    # step: 2
    # obj: ...
    ae, modelo = trafo.det_ae(ae_aw, thornton_file, modelos_d)
    print("[2] - modelo =", modelo, ", ae =", ae)

    # step: 3
    # obj: determinar o dimetro do entreferro
    entreferro   = trafo.det_entreferro(pout, n, fs, uo, delta_b, ae)
    print("[3] - entreferro =", entreferro, "cm, visto ocupar os dois lados do núcleo do tipo E.")

    # step: 4
    # obj: determinar o número de espiras do enrolamento primário
    enrol_pri, ip = trafo.det_enrol_pri(pout, n, vmin, kw, delta_b, entreferro * 2, uo)
    print("[4] - np =", round(enrol_pri), "espiras")

    # step: 5   
    # obj: determinar o número de espiras do enrolamento secundário
    enrol_sec    = trafo.det_enrol_sec(round(enrol_pri), vout, vd, vmin, kw)
    print("[5] - ns =", round(enrol_sec), "espiras")

    # step: 6
    # obj: determinar a seção dos condutores
    sec_cond     = trafo.det_sec_cond(fs, ip, kw, j, ips)
    print("[6] - sec_cond =", sec_cond, ", visto ser em paralelo." )

    # step: 7
    # obj: determinar as indutâncias magnetizantes dos enrolamentos
    Lm_pri, Lm_sec = trafo.det_Lmag(round(enrol_pri), delta_b, ae, ip, enrol_sec)
    print("[7] - lm_pri =", Lm_pri, "H,", "Lm_sec =", Lm_sec, "H")

# ...
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
