import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QStyle

from PyQt5.QtGui import *
from darktheme.widget_template import DarkPalette



class Warnungen(QWidget):
    def __init__(self):
        super(Warnungen, self).__init__()
        uic.loadUi('lichtWarnung.ui', self)

    def warnungTemphoch(self):
        self.move(1520,900)
        self.label_4 = QLabel()
        self.label_4.setText('Es ist zu heiß im Raum!')
        #self.label_4.setStyle(QStyle())
        #self.label_4.setFixedSize('24')
        self.label_4.setText( "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Es ist zu Dunkel</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im Raum!</span></p></body></html>")
        self.setWindowIcon(QIcon('warningIcon.png'))
        self.setPalette(DarkPalette())
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: grey; border: 1px grey; }")
        self.show()

    def warnungenTempniedrig(self):
        uic.loadUi('warnungTempniedrig.ui', self)
        self.move(1520,900)
        self.setWindowIcon(QIcon('warningIcon.png'))
        self.setPalette(DarkPalette())
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: grey; border: 1px grey; }")
        self.show()

    def warnungLautstaerke(self):
        uic.loadUi('Lautstaerkewarnung.ui', self)
        self.move(1520,900)
        self.setWindowIcon(QIcon('LautstaerkeIcon.png'))
        self.setPalette(DarkPalette())
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: grey; border: 1px grey; }")
        self.show()

    def warnungCo2(self):

        uic.loadUi('CO2Warnung.ui', self)
        self.move(1520,900)
        self.setWindowIcon(QIcon('warningIcon.png'))
        self.setPalette(DarkPalette())
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: grey; border: 1px grey; }")
        self.show()

    def warnungLicht(self):
        uic.loadUi('lichtWarnung.ui', self)
        self.move(1520,900)
        self.setWindowIcon(QIcon('LautstaerkeIcon.png'))
        self.setPalette(DarkPalette())
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: grey; border: 1px grey; }")
        self.show()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Warnungentrest = Warnungen()
    #Warnungentrest.warnungCo2()
    Warnungentrest.warnungTemphoch()
    sys.exit(app.exec_())
