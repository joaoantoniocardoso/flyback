
# ...
# -- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
import sys # exercutar app
from PyQt5.QtCore import * # ...
from PyQt5.QtWidgets import *   # base da janela
from PyQt5.QtGui import *       # controle das figuras

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

        button = QPushButton('teste combo_box_check', self)
        button.setToolTip('...')
        button.move(100, 70) 
        button.clicked.connect(self.on_click)

        button2 = QPushButton('teste combo_box_check2', self)
        button2.setToolTip('...')
        button2.move(100, 30) 
        button2.clicked.connect(self.on_click2)

        self.ComboBox = combo_box_checkable(self)
        for i in range(12):
            self.ComboBox.add_item("Combobox Item " + str(i))

        self.show()

    def on_click(self):
        print(self.ComboBox.check_item(2))

    def on_click2(self):
        print(self.ComboBox.checke_all_itens(12))

# ...
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
