from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, uic, QtCore
from random import randint
import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, QTime, Qt
import serial
import datetime
import threading
import sys
import ctypes
import serial.tools.list_ports
import time
from darktheme.widget_template import DarkPalette


#standart wert für die daten da damit das programm nicht crasht wenn kein device conn
daten = '2021-08-16/16:58:04', 25, 51.0, 669.0, 50.0, 69.0



#erstellung von leeren listen für die graphen
tempcelist = np.zeros(100)  # liste voller 0 100Stellen
luftdrucklist = np.zeros(100)  # liste voller 0 100Stellen
co2list = np.zeros(100)  # liste voller 0 100Stellen
lautlist = np.zeros(100)  # liste voller 0 100Stellen
helllist = np.zeros(100)  # liste voller 0 100Stellen

tempcegraposi = 0
luftfeuchtgraposi = 0
co2graposi = 0
lautgraposi = 0
hellgraposi = 0

temporotgrenzlist = np.full(100, 35)  # liste 100 stellen alle 70
luftdruckogrenzlist = np.full(100, 70)  # liste 100 stellen alle 70
co2orotgrenzlist = np.full(100, 1000)  # liste 100 stellen alle 70
lautorotgrenzlist = np.full(100, 70)  # liste 100 stellen alle 70
hellugelbgrenzlist = np.full(100, 100)  # liste 100 stellen alle 70

tempurotgrenzlist = np.full(100, 20)  # liste 100 stellen alle 70
luftdruckugrenzlist = np.full(100, 35)  # liste 100 stellen alle 70
co2ogelbgrenzlist = np.full(100, 400)  # liste 100 stellen alle 70
lautogelbgrenzlist = np.full(100, 35)  # liste 100 stellen alle 70
hellurotgrenzlist = np.full(100, 40)  # liste 100 stellen alle 70

# dinge die am anfang asugeführrt werden müssen
myappid = 'glichoverwatch'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid.encode('utf-8'))

try:
    COM = [comport.device for comport in serial.tools.list_ports.comports()]
    COM.remove('COM1')
    print(COM)
    ser = serial.Serial(str(COM[0]), baudrate=115200, timeout=1)
    deviceconnected = True
except:
    deviceconnected = False
print(deviceconnected)


class Warnungen(QWidget):
    def __init__(self):
        super(Warnungen, self).__init__()
        uic.loadUi('allgemeinWarnung.ui', self)
        self.move(1520, 900)
        self.setWindowIcon(QIcon('warningIcon.png'))
        self.setPalette(DarkPalette())
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: grey; border: 1px grey; }")
        self.show()
    def closeEvent(self, event):
        event.ignore()

        self.hide()

    def warnungTemphoch(self):
        self.textLabel.setText( "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Es ist zu heiß</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im Raum!</span></p></body></html>")
        self.show()

    def warnungenTempniedrig(self):
        self.textLabel.setText( "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Es ist zu kalt</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im Raum!</span></p></body></html>")
        self.show()

    def warnungLautstaerke(self):
        self.textLabel.setText( "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Es ist zu laut</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im Raum!</span></p></body></html>")
        self.show()

    def warnungCo2(self):
        self.textLabel.setText( "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Der CO2 Gehalt ist zu hoch</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im Raum!</span></p></body></html>")
        self.show()

    def warnungLicht(self):
        self.textLabel.setText("<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Es ist zu dunkel</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im Raum!</span></p></body></html>")
        self.show()

testapp = QtWidgets.QApplication(sys.argv)
warnungPopup = Warnungen()



class MainWindow(QMainWindow):
    """
         system tray icons.
         Will initialize in the constructor.
    """

    tray_icon = None

    # Override the class constructor
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        uic.loadUi('overstagt.ui', self)
        # window icon
        self.setWindowIcon(QIcon('icon.png'))
        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        icon = QIcon('icon.png')
        self.tray_icon.setIcon(icon)

        # einstellung für widget
        self.tempw.setDownsampling(mode='peak')
        self.tempw.setClipToView(True)
        self.luftfeuchtw.setDownsampling(mode='peak')
        self.luftfeuchtw.setClipToView(True)
        self.co2w.setDownsampling(mode='peak')
        self.co2w.setClipToView(True)
        self.lautw.setDownsampling(mode='peak')
        self.lautw.setClipToView(True)
        self.hellw.setDownsampling(mode='peak')
        self.hellw.setClipToView(True)
        # self.tempw.setLabel('bottom', 'Time', 's')

        self.darkmodebutton.setCheckable(True)
        self.darkmodebutton.clicked.connect(self.changeColor)

        # Einstellungen fuer die Ampeln
        self.tempampel.setStyleSheet('border: 2px solid black; border-radius:60px; background-color: rgb(0,255,0)')
        self.luftfeuchtampel.setStyleSheet('border: 2px solid black; border-radius:60px; background-color: rgb(0,255,0)')
        self.co2ampel.setStyleSheet('border: 2px solid black; border-radius:60px; background-color: rgb(0,255,0)')
        self.lautampel.setStyleSheet('border: 2px solid black; border-radius:60px; background-color: rgb(0,255,0)')
        self.hellampel.setStyleSheet('border: 2px solid black; border-radius:60px; background-color: rgb(0,255,0)')
        self.einfacheAmpelTemperatur.setStyleSheet('border: 2px solid black; border-radius:40px;background-color: rgb(0,255,0)')
        self.einfacheAmpelFeuchtigkeit.setStyleSheet('border: 2px solid black; border-radius:40px;background-color: rgb(0,255,0)')
        self.einfachAmpelCO2.setStyleSheet('border: 2px solid black; border-radius:40px;background-color: rgb(0,255,0)')
        self.einfacheAmpelLaut.setStyleSheet('border: 2px solid black; border-radius:40px;background-color: rgb(0,255,0)')
        self.einfacheAmpelHelligkeit.setStyleSheet('border: 2px solid black; border-radius:40px;background-color: rgb(0,255,0)')

        # timer
        '''
        Timer um alle graphen und die Uhr immer wieder zu Updaten

        '''
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)  # update every second
        self.timer.timeout.connect(self.checkifdevcon)
        self.timer.timeout.connect(self.updatetempce)
        self.timer.timeout.connect(self.updateluftfeucht)
        self.timer.timeout.connect(self.updateco2)
        self.timer.timeout.connect(self.updatelaut)
        self.timer.timeout.connect(self.updatehell)
        self.timer.timeout.connect(self.zeitausgabe)
        self.timer.start()

        # graph zeug

        pen = pg.mkPen(color=(0, 255, 0))
        ogrenzpen = pg.mkPen(color=(255, 0, 0))
        ugrenzpen = pg.mkPen(color=(0, 0, 255))
        self.temp_line = self.tempw.plot(pen=pen)
        self.tempogrenz_line = self.tempw.plot(pen=ogrenzpen)
        self.tempugrenz_line = self.tempw.plot(pen=ugrenzpen)

        self.luftfeucht_line = self.luftfeuchtw.plot(pen=pen)
        self.luftfeuchtogrenz_line = self.luftfeuchtw.plot(pen=ogrenzpen)
        self.luftfeuchtugrenz_line = self.luftfeuchtw.plot(pen=ugrenzpen)

        self.co2_line = self.co2w.plot(pen=pen)
        self.co2ogrenz_line = self.co2w.plot(pen=ogrenzpen)
        self.co2ugrenz_line = self.co2w.plot(pen=ugrenzpen)

        self.laut_line = self.lautw.plot(pen=pen)
        self.lautogrenz_line = self.lautw.plot(pen=ogrenzpen)
        self.lautugrenz_line = self.lautw.plot(pen=ugrenzpen)

        self.hell_line = self.hellw.plot(pen=pen)
        self.hellogrenz_line = self.hellw.plot(pen=ogrenzpen)
        self.hellugrenz_line = self.hellw.plot(pen=ugrenzpen)

        # aufsetzten der Uhr

        fnt = QFont('Open Sans', 20, QFont.Bold)
        self.uhr.setAlignment(Qt.AlignCenter)
        self.uhr.setFont(fnt)
        self.zeitausgabe()

        # alles für das tray icon
        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        self.tray_icon.activated.connect(self.clickedonicon)

        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)

        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        # sollte allgemein noch erweitert werden mit doppelclick auf icon etc.
    def clickedonicon(self):
            self.show()

    def checkifdevcon(self):

        if deviceconnected == True:

            self.istdevcon.setStyleSheet('background-color : green')
            self.istdevcon.setText('Device connected')

        else:
            self.istdevcon.setStyleSheet('background-color : red')
            self.istdevcon.setText('Device not connected')

    def changeColor(self):

        # if button is checked
        if self.darkmodebutton.isChecked():

            # setting background color to light-blue
            self.darkmodebutton.setStyleSheet("background-color : green")
            self.setStyleSheet('color: white;background-color : black')

        # if it is unchecked
        else:

            # set background color back to light-grey
            self.darkmodebutton.setStyleSheet("color: black;background-color : darkgrey")
            self.setStyleSheet('background-color : white')


    def updatetempce(self):
        global tempcelist, tempcegraposi, daten, temporotgrenzlist, tempurotgrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.tempanzei.display(daten[1])
        # ampel umstellung für den entsprechenden wert
        if daten[1] >= 35:
            self.tempampel.setStyleSheet('border: 1px solid black; border-radius:40px; background-color: rgb(255,255,0)')
            self.einfacheAmpelTemperatur.setStyleSheet('border: 0px solid black; border-radius:40px; background-color: rgb(255,255,0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.temp_line = self.tempw.plot(pen=pen)
            warnungPopup.warnungTemphoch()
        elif daten[1] <= 20:
            self.tempampel.setStyleSheet('border: 1px solid black; border-radius:60px;'
                                         'background-color: rgb(0, 255, 255)')
            self.einfacheAmpelTemperatur.setStyleSheet('border: 0px solid black; border-radius:40px; background-color: rgb(0, 255, 255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.temp_line = self.tempw.plot(pen=pen)
            warnungPopup.warnungenTempniedrig()
        else:
            self.tempampel.setStyleSheet('border: 1px solid black; border-radius: 60px; '
                                         'background-color: rgb(0, 255, 0)')
            self.einfacheAmpelTemperatur.setStyleSheet('border: 0px solid black; border-radius: 40px; '
                                                       'background-color: rgb(0,255,0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.temp_line = self.tempw.plot(pen=pen)
        # muss angepasst werden an die Werte

        tempcelist[tempcegraposi] = daten[1]  # nimmt den daten wert

        tempcegraposi += 1  # erhöh die stelle
        if tempcegraposi >= tempcelist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = tempcelist  # Datenliste wird in tmp gespeichert
            tempcelist = np.empty(tempcelist.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            tempcelist[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            tempogrenzlist = np.full(int(len(tempcelist)), 35)
            tempugrenzlist = np.full(int(len(tempcelist)), 20)

        self.temp_line.setData(tempcelist[:tempcegraposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.tempogrenz_line.setData(tempogrenzlist[:tempcegraposi])  # obergenzline wird aktualisiert
        self.tempugrenz_line.setData(tempugrenzlist[:tempcegraposi])

    def updateluftfeucht(self):
        global luftdrucklist, luftfeuchtgraposi, daten, luftdruckogrenzlist, luftdruckugrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.luftfeuchtanzei.display(daten[2])
        # ampel umstellung für den entsprechenden wert
        if daten[2] >= 70:
            self.luftfeuchtampel.setStyleSheet('border: 1px solid black; border-radius:60px;'
                                               'background-color: rgb(255, 255, 0)')
            self.einfacheAmpelFeuchtigkeit.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(255,255,0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.luftfeucht_line = self.luftfeuchtw.plot(pen=pen)
        elif daten[2] <= 35:
            self.luftfeuchtampel.setStyleSheet('border: 1px solid black; border-radius:60px;'
                                               'background-color: rgb(0, 255, 255)')
            self.einfacheAmpelFeuchtigkeit.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(0,255,255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.luftfeucht_line = self.luftfeuchtw.plot(pen=pen)
        else:
            self.luftfeuchtampel.setStyleSheet('border: 1px solid black; border-radius:60px; '
                                               'background-color: rgb(0,255,0)')
            self.einfacheAmpelFeuchtigkeit.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(0,255,0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.luftfeucht_line = self.luftfeuchtw.plot(pen=pen)
        # muss angepasst werden an die Werte

        luftfeuchtlist[luftfeuchtgraposi] = daten[2]  # nimmt den daten wert

        luftfeuchtgraposi += 1  # erhöh die stelle
        if luftfeuchtgraposi >= luftfeuchtlist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = luftfeuchtlist  # Datenliste wird in tmp gespeichert
            luftfeuchtlist = np.empty(luftfeuchtlist.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            luftfeuchtlist[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            luftfeuchtogrenzlist = np.full(int(len(luftfeuchtlist)), 70)
            luftfeuchtugrenzlist = np.full(int(len(luftfeuchtlist)), 35)

        self.luftfeucht_line.setData(
            luftfeuchtlist[:luftfeuchtgraposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.luftfeuchtogrenz_line.setData(
            luftfeuchtogrenzlist[:luftfeuchtgraposi])  # obergenzline wird aktualisiert
        self.luftfeuchtugrenz_line.setData(luftfeuchtugrenzlist[:luftfeuchtgraposi])

    def updateco2(self):
        global co2list, co2graposi, daten, co2orotgrenzlist, co2ogelbgrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.co2anzei.display(daten[3])
        # ampel umstellung für den entsprechenden wert
        if daten[3] >= 1000:
            self.co2ampel.setStyleSheet('border: 1px solid black; border-radius:60px;'
                                        'background-color: rgb(255, 255, 0)')
            self.einfachAmpelCO2.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(255,255,0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.co2_line = self.co2w.plot(pen=pen)
            warnungPopup.warnungCo2()
        elif daten[3] <= 400:
            self.co2ampel.setStyleSheet('border: 1px solid black; border-radius:60px; '
                                        'background-color: rgb(0, 255, 255)')
            self.einfachAmpelCO2.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(0,255,255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.co2_line = self.co2w.plot(pen=pen)
            warnungPopup.warnungCo2()
        else:
            self.co2ampel.setStyleSheet('border: 1px solid black; border-radius:60px; '
                                        'background-color: rgb(0,255,0)')
            self.einfachAmpelCO2.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(0,255,0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.co2_line = self.co2w.plot(pen=pen)
        # muss angepasst werden an die Werte

        co2list[co2graposi] = daten[3]  # nimmt den daten wert

        co2graposi += 1  # erhöh die stelle
        if co2graposi >= co2list.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = co2list  # Datenliste wird in tmp gespeichert
            co2list = np.empty(co2list.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            co2list[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            co2ogrenzlist = np.full(int(len(co2list)), 1000)
            co2ugrenzlist = np.full(int(len(co2list)), 400)

        self.co2_line.setData(co2list[:co2graposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.co2ogrenz_line.setData(co2ogrenzlist[:co2graposi])  # obergenzline wird aktualisiert
        self.co2ugrenz_line.setData(co2ugrenzlist[:co2graposi])

    def updatelaut(self):
        global lautlist, lautgraposi, daten, lautorotgrenzlist, lautogelbgrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.lautanzei.display(daten[4])
        # ampel umstellung für den entsprechenden wert
        if daten[4] >= 70:
            self.lautampel.setStyleSheet('border: 1px solid black; border-radius:60px;'
                                         'background-color: rgb(255, 255, 0)')
            self.einfacheAmpelLaut.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(255,255,0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.laut_line = self.lautw.plot(pen=pen)
            warnungPopup.warnungLautstaerke()
        elif daten[4] <= 35:
            self.lautampel.setStyleSheet('border: 1px solid black; border-radius:60px; '
                                         'background-color: rgb(0, 255, 255)')
            self.einfacheAmpelLaut.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(0,255,255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.laut_line = self.lautw.plot(pen=pen)
            warnungPopup.warnungLautstaerke()
        else:
            self.lautampel.setStyleSheet('border: 1px solid black; border-radius:60px;'
                                         'background-color: rgb(0,255,0)')
            self.einfacheAmpelLaut.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(0,255,0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.laut_line = self.lautw.plot(pen=pen)

        # muss angepasst werden an die Werte

        lautlist[lautgraposi] = daten[4]  # nimmt den daten wert

        lautgraposi += 1  # erhöh die stelle
        if lautgraposi >= lautlist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = lautlist  # Datenliste wird in tmp gespeichert
            lautlist = np.empty(lautlist.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            lautlist[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            lautogrenzlist = np.full(int(len(lautlist)), 70)
            lautugrenzlist = np.full(int(len(lautlist)), 35)

        self.laut_line.setData(lautlist[:lautgraposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.lautogrenz_line.setData(lautogrenzlist[:lautgraposi])  # obergenzline wird aktualisiert
        self.lautugrenz_line.setData(lautugrenzlist[:lautgraposi])

    def updatehell(self):
        global helllist, hellgraposi, daten, hellugelbgrenzlist, hellurotgrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.hellanzei.display(daten[5])
        # ampel umstellung für den entsprechenden wert
        if daten[5] >= 100:
            self.hellampel.setStyleSheet('border: 1px solid black; border-radius:60px;'
                                         'background-color: rgb(255, 255, 0)')
            self.einfacheAmpelHelligkeit.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(255,255,0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.hell_line = self.hellw.plot(pen=pen)
            warnungPopup.warnungLicht()
        elif daten[5] <= 40:
            self.hellampel.setStyleSheet('border: 1px solid black; border-radius:60px;'
                                         'background-color: rgb(0, 255, 255)')
            self.einfacheAmpelHelligkeit.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(0,255,255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.hell_line = self.hellw.plot(pen=pen)
            warnungPopup.warnungLicht()
        else:
            self.hellampel.setStyleSheet('border: 1px solid black; border-radius:60px;'
                                         'background-color: rgb(0,255,0)')
            self.einfacheAmpelHelligkeit.setStyleSheet('border: 0px solid black; border-radius:40px;background-color: rgb(0,255,0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.hell_line = self.hellw.plot(pen=pen)
        # muss angepasst werden an die Werte

        helllist[hellgraposi] = daten[5]  # nimmt den daten wert

        hellgraposi += 1  # erhöh die stelle
        if hellgraposi >= helllist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = helllist  # Datenliste wird in tmp gespeichert
            helllist = np.empty(helllist.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            helllist[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            hellogrenzlist = np.full(int(len(helllist)), 100)
            hellugrenzlist = np.full(int(len(helllist)), 40)

        self.hell_line.setData(helllist[:hellgraposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.hellogrenz_line.setData(hellogrenzlist[:hellgraposi])  # obergenzline wird aktualisiert
        self.hellugrenz_line.setData(hellugrenzlist[:hellgraposi])

    def zeitausgabe(self):
        currentTime = QTime.currentTime()

        displayTxt = currentTime.toString('hh:mm:ss')

        self.uhr.setText(displayTxt)

    # Schließevent wird verändert sodass-->
    # The window will not be closed unless you close it over the stry icon thing
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Tray Program",
            "Application was minimized to Tray",
            QSystemTrayIcon.Information,
            2000
        )  # weiß nicht wen diese nachricht auftauchen soll ideen bitte hier:


def grafikdingens():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())


def datenzeugs():
    global daten
    print(daten)

    def dateianlegen():
        """ nimmt die aktualle Zeit und erstellt eine .txt Datei mit der Startzeit als Namen"""

        def punktentferner(x):
            """entfernt die doppelpunkte in der zeit da Dateien keine Doppelpunkt im Namen haben kann"""
            stelle = 0
            x = list(x)
            for i in x:
                if i == ':':
                    i = ' '  # möglichst keine Leerzeichen (was ist noich offen)
                    x[stelle] = i
                stelle = stelle + 1
            z = ''
            for i in x:
                z = z + i
            return z

        zeit = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        zeit = punktentferner(zeit)

        dateiname = str(zeit + '.txt')
        speicher = open(dateiname, "a")
        speicher.write('time,tempce,luftfeucht,co2,laut,hell')  # auf göße anpassen
        speicher.close()
        return dateiname

    def connect():
        """ stellt die Verbindung zu serial port auf"""
        global deviceconnected, ser
        if deviceconnected == False:
            COM = [comport.device for comport in serial.tools.list_ports.comports()]
            try:
                COM.remove('COM1')
                print(COM)
                ser = serial.Serial(str(COM[0]), baudrate=115200, timeout=1)
                deviceconnected = True
            except:
                ser = None
                deviceconnected = False
            return ser
        else:
            pass


    def datenverarbeitung():
        global daten, deviceconnected

        def datenabruf():
            global deviceconnected,ser
            """ empfängt die daten die vom esp32 gesendet werden, kombiniert sie mit der zeit
            und speicher die in der oben erstllen .txt datei"""

            try:

                data = ser.readline().decode('ascii')
                datalist = data.split(' ')
                time = datetime.datetime.now().strftime("%Y-%m-%d/%H:%M:%S")
                tempce = float(datalist[0])
                luftfeucht = float(datalist[1])
                co2 = float(datalist[2])
                laut = float(datalist[3])
                hell = float(datalist[4])
                datentu = time, tempce, luftfeucht, co2, laut, hell

            except:
                datentu = ('2021-08-16/16:58:04', 25, 51.0, 669.0, 50.0, 69.0)
                deviceconnected = False


            return datentu
            # gibt keinen error aus aber geht trotzdem manchmal nicht(hängt mit dem start des esp32 zusammen)

        def speichern(dateiname, daten):
            """öffnet die datei schreibt die Daten in die .txt und schließt diese wieder"""
            datenstr = str(daten[0]) + ',' + str(daten[1]) + ',' + str(daten[2]) + ',' + str(daten[3]) + ',' + str(
                daten[4]) + ',' + str(daten[5])
            speicher = open(dateiname, "a")
            speicher.write('\n')
            speicher.write(str(datenstr))
            speicher.close()  # stess testen

        while True:
            connect()

            daten = datenabruf()

            speichern(dateiname, daten)
            time.sleep(1)

    dateiname = dateianlegen()
    datenverarbeitung()


# Create new threads
datenthread = threading.Thread(target=datenzeugs, daemon=True)


# Start new Threads
datenthread.start()

# Start vom GUI
grafikdingens()

print("Exiting Main Thread")
