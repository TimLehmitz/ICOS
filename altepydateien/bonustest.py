#https://stackoverflow.com/questions/66946885/multiple-windows-in-pyqt5
import sys
from random import randint

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent,
    it will appear as a free-floating window.
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window % d" % randint(0, 100))
        layout.addWidget(self.label)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.windows = []

        l = QVBoxLayout()
        button1 = QPushButton("Push for new window")
        button1.clicked.connect(self.open_newWindow)
        l.addWidget(button1)

        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)

    def open_newWindow(self):
        window = AnotherWindow()
        self.windows.append(window)
        window.show()


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()