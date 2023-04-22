#https://stackoverflow.com/questions/4357258/how-to-get-the-height-of-windows-taskbar-using-python-pyqt-win32
#https://stackoverflow.com/questions/35887237/current-screen-size-in-python3-with-pyqt5
#https://stackoverflow.com/questions/6854947/how-to-display-a-window-on-a-secondary-display-in-pyqt

import sys
from PyQt5.QtWidgets import *

app = QApplication(sys.argv)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("My App")

widget = MainWindow()# define your widget
display_monitor = 1 # the number of the monitor you want to display your widget

monitor = QDesktopWidget().screenGeometry(display_monitor)
widget.move(monitor.left(), monitor.top())
widget.showFullScreen()

widget.show()
app.exec()


######

import sys
from PyQt5 import QtWidgets

#def screen_resolutions():
#    for displayNr in range(QtWidgets.QDesktopWidget().screenCount()):
#        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(displayNr)
#        print("Display: " + str(displayNr) + " Screen size : " + str(sizeObject.width()) + "x" + str(sizeObject.height()))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    #main()
    #screen_resolutions()
    x = QtWidgets.QDesktopWidget().screenCount()
    print(x)
    dw = app.desktop()
    taskbar_height = dw.screenGeometry().height() - dw.availableGeometry().height()
    print(taskbar_height)
    sys.exit(app.exec_())