# importing the required libraries

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import sys
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QStyle

from PyQt5.QtGui import *
from darktheme.widget_template import DarkPalette

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()


        # set the title
        self.setWindowTitle("")

        # setting the geometry of window
        self.setGeometry(60, 60, 600, 400)

        # creating a label widget
        # by default label will display at top left corner
        self.label_1 = QLabel(self)

        # moving position
        self.label_1.move(100, 100)

        # making label square in size
        self.label_1.resize(80, 80)

        # setting up border and radius
        self.label_1.setStyleSheet("border: 3px solid black;border-radius: 40px; background-color: rgb(0,255,0)")
        #self.label_1.setStyleSheet('background-color: rgb(255, 255, 0:)')

        # show all the widgets
        self.show()






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())