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


tempcelist = np.zeros(100) #liste voller 0 100Stellen
luftdrucklist = np.zeros(100) #liste voller 0 100Stellen
co2list = np.zeros(100) #liste voller 0 100Stellen
lautlist = np.zeros(100) #liste voller 0 100Stellen
helllist = np.zeros(100) #liste voller 0 100Stellen


tempcegraposi = 0
luftfeuchtgraposi = 0
co2graposi = 0
lautgraposi = 0
hellgraposi = 0




daten = '2021-08-16/16:58:04', 25, 51.0, 669.0, 50.0, 69.0


temporotgrenzlist = np.full(100, 35) #liste 100 stellen alle 70
luftdruckogrenzlist = np.full(100, 35) #liste 100 stellen alle 70
co2orotgrenzlist = np.full(100, 35) #liste 100 stellen alle 70
lautorotgrenzlist = np.full(100, 35) #liste 100 stellen alle 70
hellugelbgrenzlist = np.full(100, 35) #liste 100 stellen alle 70

tempurotgrenzlist = np.full(100, 20) #liste 100 stellen alle 70
luftdruckugrenzlist = np.full(100, 20) #liste 100 stellen alle 70
co2ogelbgrenzlist = np.full(100, 20) #liste 100 stellen alle 70
lautogelbgrenzlist = np.full(100, 20) #liste 100 stellen alle 70
hellurotgrenzlist = np.full(100, 20) #liste 100 stellen alle 70


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
        uic.loadUi('overwatchdata.ui', self)
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

        # timer
        '''
        Timer um alle graphen und die Uhr immer wieder zu Updaten
        
        '''
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)  # update every second
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
        self.data_line = self.tempw.plot(pen=pen)
        self.tempogrenz_line = self.tempw.plot(pen=ogrenzpen)
        self.tempugrenz_line = self.tempw.plot(pen=ugrenzpen)

        self.luftfeuchtogrenz_line = self.luftfeuchtw.plot(pen=ogrenzpen)
        self.luftfeuchtugrenz_line = self.luftfeuchtw.plot(pen=ugrenzpen)

        self.co2ogrenz_line = self.co2w.plot(pen=ogrenzpen)
        self.co2ugrenz_line = self.co2w.plot(pen=ugrenzpen)

        self.lautogrenz_line = self.lautw.plot(pen=ogrenzpen)
        self.lautugrenz_line = self.lautw.plot(pen=ugrenzpen)

        self.hellogrenz_line = self.hellw.plot(pen=ogrenzpen)
        self.hellugrenz_line = self.hellw.plot(pen=ugrenzpen)
        #lcd nummer



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
    def updatetempce(self):
        global tempcelist, tempcegraposi, daten, temporotgrenzlist, tempurotgrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.tempanzei.display(daten[1])

        tempcelist[tempcegraposi] = daten[1]  # nimmt den daten wert

        tempcegraposi += 1  # erhöh die stelle
        if tempcegraposi >= tempcelist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = tempcelist  # Datenliste wird in tmp gespeichert
            tempcelist = np.empty(tempcelist.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            tempcelist[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            tempogrenzlist = np.full(int(len(tempcelist)), 35)
            tempugrenzlist = np.full(int(len(tempcelist)), 20)

        self.data_line.setData(tempcelist[:tempcegraposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.tempogrenz_line.setData(tempogrenzlist[:tempcegraposi]) #obergenzline wird aktualisiert
        self.tempugrenz_line.setData(tempugrenzlist[:tempcegraposi])
        # ampel umstellung für den entsprechenden wert
        if daten[1] >= 35:
            self.tempampel.setStyleSheet('background-color: rgb(255, 255, 0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.data_line = self.tempw.plot(pen=pen)
        elif daten[1] <= 20:
            self.tempampel.setStyleSheet('background-color: rgb(0, 255, 255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.data_line = self.tempw.plot(pen=pen)
        else:
            self.tempampel.setStyleSheet('background-color: rgb(0, 255, 0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.data_line = self.tempw.plot(pen=pen)
        # muss angepasst werden an die Werte

    def updateluftfeucht(self):
        global luftdrucklist, luftfeuchtgraposi, daten, luftdruckogrenzlist, luftdruckugrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.luftfeuchtanzei.display(daten[2])

        luftfeuchtlist[luftfeuchtgraposi] = daten[2]  # nimmt den daten wert

        luftfeuchtgraposi += 1  # erhöh die stelle
        if luftfeuchtgraposi >= luftfeuchtlist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = luftfeuchtlist  # Datenliste wird in tmp gespeichert
            luftfeuchtlist = np.empty(luftfeuchtlist.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            luftfeuchtlist[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            luftfeuchtogrenzlist = np.full(int(len(luftfeuchtlist)), 35)
            luftfeuchtugrenzlist = np.full(int(len(luftfeuchtlist)), 20)

        self.data_line.setData(luftfeuchtlist[:luftfeuchtgraposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.luftfeuchtogrenz_line.setData(luftfeuchtogrenzlist[:luftfeuchtgraposi]) #obergenzline wird aktualisiert
        self.luftfeuchtugrenz_line.setData(luftfeuchtugrenzlist[:luftfeuchtgraposi])
        # ampel umstellung für den entsprechenden wert
        if daten[2] >= 70:
            self.luftfeuchtampel.setStyleSheet('background-color: rgb(255, 255, 0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.data_line = self.luftfeuchtw.plot(pen=pen)
        elif daten[2] <= 35:
            self.luftfeuchtampel.setStyleSheet('background-color: rgb(0, 255, 255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.data_line = self.luftfeuchtw.plot(pen=pen)
        else:
            self.luftfeuchtampel.setStyleSheet('background-color: rgb(0, 255, 0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.data_line = self.luftfeuchtw.plot(pen=pen)
        # muss angepasst werden an die Werte

    def updateco2(self):
        global co2list, co2graposi, daten, co2orotgrenzlist, co2ogelbgrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.co2anzei.display(daten[3])

        co2list[co2graposi] = daten[3]  # nimmt den daten wert

        co2graposi += 1  # erhöh die stelle
        if co2graposi >= co2list.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = co2list  # Datenliste wird in tmp gespeichert
            co2list = np.empty(co2list.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            co2list[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            co2ogrenzlist = np.full(int(len(co2list)), 35)
            co2ugrenzlist = np.full(int(len(co2list)), 20)

        self.data_line.setData(co2list[:co2graposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.co2ogrenz_line.setData(co2ogrenzlist[:co2graposi]) #obergenzline wird aktualisiert
        self.co2ugrenz_line.setData(co2ugrenzlist[:co2graposi])
        # ampel umstellung für den entsprechenden wert
        if daten[3] >= 1000:
            self.co2ampel.setStyleSheet('background-color: rgb(255, 255, 0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.data_line = self.co2w.plot(pen=pen)
        elif daten[3] <= 400:
            self.co2ampel.setStyleSheet('background-color: rgb(0, 255, 255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.data_line = self.co2w.plot(pen=pen)
        else:
            self.co2ampel.setStyleSheet('background-color: rgb(0, 255, 0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.data_line = self.co2w.plot(pen=pen)
        # muss angepasst werden an die Werte

    def updatelaut(self):
        global lautlist, lautgraposi, daten, lautorotgrenzlist, lautogelbgrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.lautanzei.display(daten[4])

        lautlist[lautgraposi] = daten[4]  # nimmt den daten wert

        lautgraposi += 1  # erhöh die stelle
        if lautgraposi >= lautlist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = lautlist  # Datenliste wird in tmp gespeichert
            lautlist = np.empty(lautlist.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            lautlist[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            lautogrenzlist = np.full(int(len(lautlist)), 35)
            lautugrenzlist = np.full(int(len(lautlist)), 20)

        self.data_line.setData(lautlist[:lautgraposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.lautogrenz_line.setData(lautogrenzlist[:lautgraposi]) #obergenzline wird aktualisiert
        self.lautugrenz_line.setData(lautugrenzlist[:lautgraposi])
        # ampel umstellung für den entsprechenden wert
        if daten[4] >= 70:
            self.lautampel.setStyleSheet('background-color: rgb(255, 255, 0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.data_line = self.lautw.plot(pen=pen)
        elif daten[4] <= 35:
            self.lautampel.setStyleSheet('background-color: rgb(0, 255, 255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.data_line = self.lautw.plot(pen=pen)
        else:
            self.lautampel.setStyleSheet('background-color: rgb(0, 255, 0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.data_line = self.lautw.plot(pen=pen)
        # muss angepasst werden an die Werte

    def updatehell(self):
        global helllist, hellgraposi, daten, hellugelbgrenzlist, hellurotgrenzlist

        # gibt den derzeitgigen Wert in das LCDWidget
        self.hellanzei.display(daten[5])

        helllist[hellgraposi] = daten[5]  # nimmt den daten wert

        hellgraposi += 1  # erhöh die stelle
        if hellgraposi >= helllist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = helllist  # Datenliste wird in tmp gespeichert
            helllist = np.empty(helllist.shape[0] * 2)  # die Datenlistenlänge wird verdoppelt
            helllist[:tmp.shape[0]] = tmp  # Daten werden in die längere liste gepackt
            hellogrenzlist = np.full(int(len(helllist)), 35)
            hellugrenzlist = np.full(int(len(helllist)), 20)

        self.data_line.setData(helllist[:hellgraposi])  # graph wird mit der aktualisiereten Datenliste erzeugt
        self.hellogrenz_line.setData(hellogrenzlist[:hellgraposi]) #obergenzline wird aktualisiert
        self.hellugrenz_line.setData(hellugrenzlist[:hellgraposi])
        # ampel umstellung für den entsprechenden wert
        if daten[5] >= 100:
            self.hellampel.setStyleSheet('background-color: rgb(255, 255, 0)')
            pen = pg.mkPen(color=(255, 255, 0))
            self.data_line = self.hellw.plot(pen=pen)
        elif daten[5] <= 40:
            self.hellampel.setStyleSheet('background-color: rgb(0, 255, 255)')
            pen = pg.mkPen(color=(0, 255, 255))
            self.data_line = self.hellw.plot(pen=pen)
        else:
            self.hellampel.setStyleSheet('background-color: rgb(0, 255, 0)')
            pen = pg.mkPen(color=(0, 255, 0))
            self.data_line = self.hellw.plot(pen=pen)
        # muss angepasst werden an die Werte

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









if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
