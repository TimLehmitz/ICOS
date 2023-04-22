import datetime
import os
import sys
import threading
import time

import numpy as np
import pyqtgraph as pg
import serial
import serial.tools.list_ports
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtCore import QTime, Qt
from PyQt5.QtGui import *
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, qApp

# Bildschirmgrößen Bestimmung

auflwidget = QtWidgets.QApplication(sys.argv)
screen = auflwidget.primaryScreen()
bild = screen.size()
bildohnetaskl = screen.availableGeometry()
bildbreite = int(bildohnetaskl.width())
bildhoehe = int(bildohnetaskl.height())

# Startwert für Daten

daten = '2021-08-16/16:58:04', 22, 1000, 0, 50.0, 400

# erstellung von leeren listen für die graphen

tempcelist = np.full(300, 22)
luftdrucklist = np.full(300, 1000)
co2list = np.full(300, 0)
lautlist = np.full(300, 0)
helllist = np.full(300, 400)

grenzdaten = open('../src/ui/einstellungen/grenzen.txt', 'r')
grenzen = grenzdaten.readlines()
temporotgrenz = int(grenzen[3])
tempogelbgrenz = int(grenzen[1])
tempurotgrenz = int(grenzen[7])
tempugelbgrenz = int(grenzen[5])

luftdruckogrenz = int(grenzen[11])
luftdruckugrenz = int(grenzen[9])

co2orotgrenz = int(grenzen[15])
co2ogelbgrenz = int(grenzen[13])

lautorotgrenz = int(grenzen[19])
lautogelbgrenz = int(grenzen[17])

hellurotgrenz = int(grenzen[23])
hellugelbgrenz = int(grenzen[21])
grenzdaten.close()

# grenzlisten

temporotgrenzlist = np.full(300, temporotgrenz)
tempogelbgrenzlist = np.full(300, tempogelbgrenz)
tempurotgrenzlist = np.full(300, tempurotgrenz)
tempugelbgrenzlist = np.full(300, tempugelbgrenz)

luftdruckogrenzlist = np.full(300, luftdruckogrenz)
luftdruckugrenzlist = np.full(300, luftdruckugrenz)

co2orotgrenzlist = np.full(300, co2orotgrenz)
co2ogelbgrenzlist = np.full(300, co2ogelbgrenz)

lautorotgrenzlist = np.full(300, lautorotgrenz)
lautogelbgrenzlist = np.full(300, lautogelbgrenz)

hellurotgrenzlist = np.full(300, hellurotgrenz)
hellugelbgrenzlist = np.full(300, hellugelbgrenz)

dateiausgabe = ''

# Variablen Definition

tempwarnungen = True
lautwarnungen = True
co2warnungen = True
hellwarnungen = True
deviceconnected = False
treiber = False

startzeit = QTime(0, 0, 0)
endzeit = QTime(0, 0, 0)
hellampelfarbe = 'gruen'
tempampelfarbe = 'gruen'
lautampelfarbe = 'gruen'
co2ampelfarbe = 'gruen'

# erster Verbindungsversuch

COM = [comport.device for comport in serial.tools.list_ports.comports()]
print(COM)
for i in COM:
    try:
        ser = serial.Serial(str(i), baudrate=115200, timeout=2)
        data = ser.readline().decode('ascii')
        datalist = data.split(' ')
        comtestwert = float(datalist[0])
        print(i)
        deviceconnected = True
        devicecom = i
        break
    except:
        ser = None
        deviceconnected = False


# Klassen für verschiedene Elemente

# Uhren


class Uhr(QLabel):
    '''Allgemeine Uhren Klasse welche an die verschieden Uhren vererbt'''

    def __init__(self):
        super().__init__()

        self.hPointer = QtGui.QPolygon([QPoint(6, 7),
                                        QPoint(-6, 7),
                                        QPoint(0, -50)])

        self.mPointer = QPolygon([QPoint(6, 7),
                                  QPoint(-6, 7),
                                  QPoint(0, -70)])

        self.sPointer = QPolygon([QPoint(1, 1),
                                  QPoint(-1, 1),
                                  QPoint(0, -90)])

        self.bColor = Qt.darkGreen

        self.sColor = Qt.red


class Infouhr(Uhr):
    '''Infouhrklasse für die Uhren im Advanced-Modus '''

    def __init__(self):
        super().__init__()


class Startinfouhr(Infouhr):
    '''Zeigt die Startzeit der Messung im Advanced-Modus an '''

    def __init__(self):
        super().__init__()

    def paintEvent(self, event):

        rec = min(self.width(), self.height())

        tik = startzeit

        painter = QPainter(self)

        def zeigermalen(color, rotation, pointer):

            painter.setBrush(QBrush(color))

            painter.save()

            painter.rotate(rotation)

            painter.drawConvexPolygon(pointer)

            painter.restore()

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(rec / 225, rec / 225)
        painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))

        painter.drawEllipse(-100, -100, 200, 200)
        painter.setPen(QtCore.Qt.NoPen)

        zeigermalen(self.bColor, (30 * (tik.hour() + tik.minute() / 60)), self.hPointer)
        zeigermalen(self.bColor, (6 * (tik.minute() + tik.second() / 60)), self.mPointer)
        zeigermalen(self.sColor, (6 * tik.second()), self.sPointer)

        painter.setPen(QPen(self.bColor))

        for i in range(0, 60):

            if (i % 5) == 0:
                painter.drawLine(87, 0, 97, 0)

            painter.rotate(6)

        painter.end()


class Endinfouhr(Infouhr):
    '''Zeigt die Endzeit der Messung im Advanced-Modus an'''

    def __init__(self):
        super().__init__()

    def paintEvent(self, event):

        rec = min(self.width(), self.height())

        tik = endzeit

        painter = QPainter(self)

        def zeigermalen(color, rotation, pointer):

            painter.setBrush(QBrush(color))

            painter.save()

            painter.rotate(rotation)

            painter.drawConvexPolygon(pointer)

            painter.restore()

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(rec / 225, rec / 225)
        painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
        painter.drawEllipse(-100, -100, 200, 200)
        painter.setPen(QtCore.Qt.NoPen)

        zeigermalen(self.bColor, (30 * (tik.hour() + tik.minute() / 60)), self.hPointer)
        zeigermalen(self.bColor, (6 * (tik.minute() + tik.second() / 60)), self.mPointer)
        zeigermalen(self.sColor, (6 * tik.second()), self.sPointer)

        painter.setPen(QPen(self.bColor))

        for i in range(0, 60):

            if (i % 5) == 0:
                painter.drawLine(87, 0, 97, 0)

            painter.rotate(6)

        painter.end()


class Liveuhr(Uhr):
    '''Liveuhr im Developer-Modus zeigt die aktuelle Zeit '''

    def __init__(self):
        super().__init__()
        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)

    def paintEvent(self, event):

        rec = min(self.width(), self.height())

        tik = QTime.currentTime()

        painter = QPainter(self)

        def drawPointer(color, rotation, pointer):

            painter.setBrush(QBrush(color))

            painter.save()

            painter.rotate(rotation)

            painter.drawConvexPolygon(pointer)

            painter.restore()

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(rec / 225, rec / 225)

        painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
        painter.drawEllipse(-100, -100, 200, 200)
        painter.setPen(QtCore.Qt.NoPen)

        drawPointer(self.bColor, (30 * (tik.hour() + tik.minute() / 60)), self.hPointer)
        drawPointer(self.bColor, (6 * (tik.minute() + tik.second() / 60)), self.mPointer)
        drawPointer(self.sColor, (6 * tik.second()), self.sPointer)

        painter.setPen(QPen(self.bColor))

        for i in range(0, 60):

            if (i % 5) == 0:
                painter.drawLine(87, 0, 97, 0)

            painter.rotate(6)

        painter.end()


# Ampeln


class Ampel(QLabel):
    '''Basis Ampelklasse vererbt an die spezifischen Ampeln '''

    def __init__(self):
        super().__init__()
        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)
        self.setStyleSheet("background-color : rgb(30, 27, 24);")

        self.rotan = QColor(255, 0, 0, 255)
        self.rotaus = QColor(255, 0, 0, 50)

        self.gelban = QColor(255, 255, 0, 255)
        self.gelbaus = QColor(255, 255, 0, 50)

        self.gruenan = QColor(0, 255, 0, 255)
        self.gruenaus = QColor(0, 255, 0, 50)

    def paintEvent(self, event):
        global farbe

        rec = min(self.width() * 3, self.height())

        painter = QPainter(self)

        def zeichnekreise(farbe='gruen'):
            if farbe == 'gruen':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenan))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'gelb':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelban))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'rot':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotan))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)

            painter.save()

            painter.restore()

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(rec / 610, rec / 610)

        zeichnekreise(farbe=farbe)

        painter.end()


class Hellampel(Ampel):
    '''Ampel für die Helligkeit '''

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        print('hell geklickt')

    def paintEvent(self, event):
        global hellampelfarbe

        rec = min(self.width() * 3, self.height())

        painter = QPainter(self)

        def zeichnekreise(farbe='gruen'):
            if farbe == 'gruen':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenan))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'gelb':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelban))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'rot':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotan))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)

            painter.save()

            painter.restore()

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(rec / 610, rec / 610)

        zeichnekreise(farbe=hellampelfarbe)

        painter.end()


class Tempampel(Ampel):
    '''Ampel für die Temperatur '''

    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        global tempampelfarbe
        rec = min(self.width() * 3, self.height())

        painter = QPainter(self)

        def zeichnekreise(farbe='gruen'):
            if farbe == 'gruen':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenan))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'gelb':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelban))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'rot':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotan))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)

            painter.save()

            painter.restore()

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(rec / 610, rec / 610)

        zeichnekreise(farbe=tempampelfarbe)

        painter.end()


class Lautampel(Ampel):
    ''' Ampel für die Lautstärke '''

    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        global lautampelfarbe
        rec = min(self.width() * 3, self.height())

        painter = QPainter(self)

        def zeichnekreise(farbe='gruen'):
            if farbe == 'gruen':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenan))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'gelb':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelban))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'rot':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotan))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)

            painter.save()

            painter.restore()

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(rec / 610, rec / 610)

        zeichnekreise(farbe=lautampelfarbe)

        painter.end()


class Co2ampel(Ampel):
    '''Ampel für den Co2-Gehalt '''

    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        global co2ampelfarbe
        rec = min(self.width() * 3, self.height())

        painter = QPainter(self)

        def zeichnekreise(farbe='gruen'):
            if farbe == 'gruen':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenan))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'gelb':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotaus))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelban))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)
            elif farbe == 'rot':
                painter.setPen(QtCore.Qt.NoPen)

                painter.setPen(QPen(Qt.white, 3, Qt.SolidLine))
                painter.drawRect(-100, -300, 200, 600)

                painter.setPen(QPen(Qt.color1, 1, Qt.SolidLine))
                painter.setBrush(QBrush(self.rotan))
                painter.drawEllipse(-95, -290, 190, 190)

                painter.setBrush(QBrush(self.gelbaus))
                painter.drawEllipse(-95, -95, 190, 190)

                painter.setBrush(QBrush(self.gruenaus))
                painter.drawEllipse(-95, 100, 190, 190)

            painter.save()

            painter.restore()

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(rec / 610, rec / 610)

        zeichnekreise(farbe=co2ampelfarbe)

        painter.end()


# Vertikales Label für die Beschriftung im Simpelmodus


class VerticalLabel(QLabel):
    '''Verticales Label für den Simpel-Modus um die Ampeln zu beschriften '''

    def __init__(self, *args):
        QLabel.__init__(self, *args)
        self.setStyleSheet("color : white; ")
        self.setFont(QtGui.QFont('Arial', 15))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.translate(0, self.height())
        painter.rotate(-90)
        # calculate the size of the font
        fm = QtGui.QFontMetrics(painter.font())
        xoffset = int(fm.boundingRect(self.text()).width() / 2)
        yoffset = int(fm.boundingRect(self.text()).height() / 2)
        x = int(self.width() / 2) + yoffset
        y = int(self.height() / 2) - xoffset
        # because we rotated the label, x affects the vertical placement, and y affects the horizontal
        painter.drawText(y, x, self.text())
        painter.end()

    def minimumSizeHint(self):
        size = QtWidgets.QLabel.minimumSizeHint(self)
        return QtCore.QSize(size.height(), size.width())

    def sizeHint(self):
        size = QtWidgets.QLabel.sizeHint(self)
        return QtCore.QSize(size.height(), size.width())


class Aboutwindow(QWidget):
    ''' Fenster welches bei About angezeigt wird '''

    def __init__(self, *args, **kwargs):
        super(Aboutwindow, self).__init__(*args, **kwargs)
        uic.loadUi('ui/aboutwindow.ui', self)
        self.setWindowIcon(QIcon('../src/ui/grafiken/icon.png'))
        self.setWindowTitle('About')


# Warnungsklassen


class Warnungen(QWidget):
    '''Algemeine Klasse für Warnungen aller Art '''

    def __init__(self, *args, **kwargs):
        super(Warnungen, self).__init__(*args, **kwargs)
        QWidget.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        uic.loadUi('ui/allgemeinWarnung.ui', self)
        self.move((bildbreite - 360), (bildhoehe - 150))
        self.setWindowIcon(QIcon('../src/ui/grafiken/warningIcon.png'))
        self.setWindowTitle('Warnung')

        #   self.show()

    def closeEvent(self, event):
        global hellwarnungen, tempwarnungen, lautwarnungen, co2warnungen

        event.ignore()
        if hellampelfarbe == 'rot':
            hellwarnungen = False
        if tempampelfarbe == 'rot':
            tempwarnungen = False
        if lautampelfarbe == 'rot':
            lautwarnungen = False
        if co2ampelfarbe == 'rot':
            co2warnungen = False
        self.hide()

    def erscheinen(self):
        self.show()
        # platzhalter funktion für erweiterungen

    def verschwinden(self):
        if hellampelfarbe != 'rot' and tempampelfarbe != 'rot' and lautampelfarbe != 'rot' and co2ampelfarbe != 'rot':
            self.hide()

    def warnungTemphoch(self):
        if tempwarnungen:
            self.textLabel.setText(
                "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Es ist zu "
                "heiß</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im "
                "Raum!</span></p></body></html>")
            self.erscheinen()

    def warnungenTempniedrig(self):
        if tempwarnungen:
            self.textLabel.setText(
                "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Es ist zu "
                "kalt</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im "
                "Raum!</span></p></body></html>")
            self.erscheinen()

    def warnungLautstaerke(self):
        if lautwarnungen:
            self.textLabel.setText(
                "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Es ist zu "
                "laut</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im "
                "Raum!</span></p></body></html>")
            self.erscheinen()

    def warnungCo2(self):
        if co2warnungen:
            self.textLabel.setText(
                "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">CO2 "
                "ist zu hoch</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im "
                "Raum!</span></p></body></html>")
            self.erscheinen()

    def warnungLicht(self):
        if hellwarnungen:
            self.textLabel.setText(
                "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">Es ist zu "
                "dunkel</span></p><p><span style=\" font-size:22pt; font-weight:600; color:#aa0000;\">im "
                "Raum!</span></p></body></html>")
            self.erscheinen()


# Hauptfenster-Klasse + Rest


class MainWindow(QMainWindow):
    """
    Klasse des gesamten Hauptfensters mit allen Funktionen und Modi
    """

    tray_icon = None

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        QMainWindow.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
        # Load die UI Page
        uic.loadUi("ui/mainw.ui", self)

        # window icon
        self.setWindowIcon(QIcon('../src/ui/grafiken/icon.png'))
        self.setWindowTitle('ICOS')
        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        icon = QIcon('../src/ui/grafiken/icon.png')
        self.tray_icon.setIcon(icon)

        # Einstellung für Graphdingens
        self.tempw.setDownsampling(mode='peak')
        self.tempw.setClipToView(True)
        self.tempw.showGrid(x=True, y=True)
        # self.tempw.setBackground('w')

        self.luftdruckw.setDownsampling(mode='peak')
        self.luftdruckw.setClipToView(True)
        self.luftdruckw.showGrid(x=True, y=True)
        # self.luftfeuchtw.setBackground('w')

        self.co2w.setDownsampling(mode='peak')
        self.co2w.setClipToView(True)
        self.co2w.showGrid(x=True, y=True)
        # self.co2w.setBackground('w')

        self.lautw.setDownsampling(mode='peak')
        self.lautw.setClipToView(True)
        self.lautw.showGrid(x=True, y=True)
        # self.lautw.setBackground('w')

        self.hellw.setDownsampling(mode='peak')
        self.hellw.setClipToView(True)
        self.hellw.showGrid(x=True, y=True)
        # self.hellw.setBackground('w')

        self.anzeigegraph.setDownsampling(mode='peak')
        self.anzeigegraph.setClipToView(True)
        self.anzeigegraph.showGrid(x=True, y=True)
        # self.anzeigegraph.setBackground('w')

        # darkmode button konfig

        self.darkmodebutton.clicked.connect(self.changecolor)

        # dev clear button
        self.cleardevbutton.clicked.connect(self.cleardevausgabe)

        #   Timer um alle Graphen zu updaten

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)  # update aller 1000ms = 1s
        self.timer.timeout.connect(self.checkifdevcon)
        self.timer.timeout.connect(self.updatetempce)
        self.timer.timeout.connect(self.updateluftdruck)
        self.timer.timeout.connect(self.updateco2)
        self.timer.timeout.connect(self.updatelaut)
        self.timer.timeout.connect(self.updatehell)
        self.timer.timeout.connect(self.zeitausgabe)
        self.timer.timeout.connect(warnungPopup.verschwinden)
        self.timer.start()

        # Graphenzeug

        pen = pg.mkPen(color=(0, 255, 0))
        rotgrenzpen = pg.mkPen(color=(255, 0, 0, 150))
        gelbgrenzpen = pg.mkPen(color=(255, 255, 0, 150))
        self.temp_line = self.tempw.plot(pen=pen)
        self.temporotgrenz_line = self.tempw.plot(pen=rotgrenzpen)
        self.tempurotgrenz_line = self.tempw.plot(pen=rotgrenzpen)
        self.tempogelbgrenz_line = self.tempw.plot(pen=gelbgrenzpen)
        self.tempugelbgrenz_line = self.tempw.plot(pen=gelbgrenzpen)

        self.luftdruck_line = self.luftdruckw.plot(pen=pen)
        self.luftdruckogrenz_line = self.luftdruckw.plot(pen=rotgrenzpen)
        self.luftdruckugrenz_line = self.luftdruckw.plot(pen=gelbgrenzpen)

        self.co2_line = self.co2w.plot(pen=pen)
        self.co2orotgrenz_line = self.co2w.plot(pen=rotgrenzpen)
        self.co2ogelbgrenz_line = self.co2w.plot(pen=gelbgrenzpen)

        self.laut_line = self.lautw.plot(pen=pen)
        self.lautorotgrenz_line = self.lautw.plot(pen=rotgrenzpen)
        self.lautogelbgrenz_line = self.lautw.plot(pen=gelbgrenzpen)

        self.hell_line = self.hellw.plot(pen=pen)
        self.hellurotgrenz_line = self.hellw.plot(pen=rotgrenzpen)
        self.hellugelbgrenz_line = self.hellw.plot(pen=gelbgrenzpen)

        #   advanvanced dings

        self.advanced_line = self.anzeigegraph.plot(pen=pen)

        self.adorotgrenz = self.anzeigegraph.plot(pen=rotgrenzpen)
        self.adurotgrenz = self.anzeigegraph.plot(pen=rotgrenzpen)

        self.adogelbgrenz = self.anzeigegraph.plot(pen=gelbgrenzpen)
        self.adugelbgrenz = self.anzeigegraph.plot(pen=gelbgrenzpen)

        # fuer den graphen Dingens

        self.temp_line.setPos(-300, 0)
        self.temporotgrenz_line.setPos(-300, 0)
        self.tempogelbgrenz_line.setPos(-300, 0)
        self.tempurotgrenz_line.setPos(-300, 0)
        self.tempugelbgrenz_line.setPos(-300, 0)

        self.luftdruck_line.setPos(-300, 0)
        self.luftdruckogrenz_line.setPos(-300, 0)
        self.luftdruckugrenz_line.setPos(-300, 0)

        self.co2_line.setPos(-300, 0)
        self.co2orotgrenz_line.setPos(-300, 0)
        self.co2ogelbgrenz_line.setPos(-300, 0)

        self.laut_line.setPos(-300, 0)
        self.lautorotgrenz_line.setPos(-300, 0)
        self.lautogelbgrenz_line.setPos(-300, 0)

        self.hell_line.setPos(-300, 0)
        self.hellurotgrenz_line.setPos(-300, 0)
        self.hellugelbgrenz_line.setPos(-300, 0)

        self.temporotgrenz_line.setData(temporotgrenzlist)
        self.tempogelbgrenz_line.setData(tempogelbgrenzlist)
        self.tempurotgrenz_line.setData(tempurotgrenzlist)
        self.tempugelbgrenz_line.setData(tempugelbgrenzlist)

        self.co2orotgrenz_line.setData(co2orotgrenzlist)
        self.co2ogelbgrenz_line.setData(co2ogelbgrenzlist)

        self.luftdruckogrenz_line.setData(luftdruckogrenzlist)
        self.luftdruckugrenz_line.setData(luftdruckugrenzlist)

        self.lautorotgrenz_line.setData(lautorotgrenzlist)
        self.lautogelbgrenz_line.setData(lautogelbgrenzlist)

        self.hellurotgrenz_line.setData(hellurotgrenzlist)
        self.hellugelbgrenz_line.setData(hellugelbgrenzlist)

        # Uhrzeug

        uhrfnt = QFont('Arial', 32, QFont.Bold)
        self.uhr.setAlignment(Qt.AlignCenter)
        self.uhr.setFont(uhrfnt)
        self.zeitausgabe()

        # alles für das tray icon

        self.tray_icon.activated.connect(self.clickedonicon)

        show_action = QAction("Show", self)
        quit_action = QAction("Schließen", self)
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

        # Menü
        self.actionSimpel.triggered.connect(self.changetosimpel)
        self.actionAdvanced.triggered.connect(self.changetoadvanced)
        self.actionDeveloper.triggered.connect(self.changetodeveloper)
        self.actionBeenden.triggered.connect(qApp.quit)

        self.actiontempwarnungen.triggered.connect(self.tempwarnanaus)
        self.actionlautwarnungen.triggered.connect(self.lautwarnanaus)
        self.actionco2warnungen.triggered.connect(self.co2warnanaus)
        self.actionhellwarnungen.triggered.connect(self.hellwarnanaus)
        self.actionalleaus.triggered.connect(self.allewarnaus)

        self.actionFilmmodus.triggered.connect(self.filmmodus)
        self.actionGruppenarbeit.triggered.connect(self.gruppenarbeit)
        self.actionAudiowarnsignal.triggered.connect(self.audiowarnsignal)

        self.actionQuickfixes.triggered.connect(self.openhilfe)
        self.actionUnbekanterFehler.triggered.connect(self.openhilfe)
        self.actionNotfall.triggered.connect(self.openhilfe)

        # einstellungen für advanced modus eingaben

        self.onlyInt = QIntValidator()
        self.adtempogelbedit.setValidator(self.onlyInt)
        self.adtemporotedit.setValidator(self.onlyInt)
        self.adtempugelbedit.setValidator(self.onlyInt)
        self.adtempurotedit.setValidator(self.onlyInt)
        self.adluftdruckugelbedit.setValidator(self.onlyInt)
        self.adluftdruckorotedit.setValidator(self.onlyInt)
        self.adCO2ogelbedit.setValidator(self.onlyInt)
        self.adCO2orotedit.setValidator(self.onlyInt)
        self.adlautogelbedit.setValidator(self.onlyInt)
        self.adlautorotedit.setValidator(self.onlyInt)
        self.adhellugelbedit.setValidator(self.onlyInt)
        self.adhellurotedit.setValidator(self.onlyInt)

        self.adtempogelbedit.insert(str(tempogelbgrenz))
        self.adtemporotedit.insert(str(temporotgrenz))
        self.adtempugelbedit.insert(str(tempugelbgrenz))
        self.adtempurotedit.insert(str(tempurotgrenz))
        self.adluftdruckugelbedit.insert(str(luftdruckugrenz))
        self.adluftdruckorotedit.insert(str(luftdruckogrenz))
        self.adCO2ogelbedit.insert(str(co2ogelbgrenz))
        self.adCO2orotedit.insert(str(co2orotgrenz))
        self.adlautogelbedit.insert(str(lautogelbgrenz))
        self.adlautorotedit.insert(str(lautorotgrenz))
        self.adhellugelbedit.insert(str(hellugelbgrenz))
        self.adhellurotedit.insert(str(hellurotgrenz))

        self.adwaehledateibutton.clicked.connect(self.opendatei)
        self.adchangegrenze.clicked.connect(self.changegrenzen)

        self.adtempbutton.clicked.connect(self.adtempbuttons)
        self.adluftdruckbutton.clicked.connect(self.adluftdruckbuttons)
        self.adCO2button.clicked.connect(self.adco2buttons)
        self.adlautbutton.clicked.connect(self.adlautbuttons)
        self.adhellbutton.clicked.connect(self.adhellbuttons)

        self.adcleardatabutton.clicked.connect(self.adcleardata)

        # setzen der verticalen labels für den simpel modus

        self.hell_label = VerticalLabel('Helligkeit')
        self.temp_label = VerticalLabel('Temperatur')
        self.laut_label = VerticalLabel('Lautstärke')
        self.co2_label = VerticalLabel('CO2')
        self.labellayout.addWidget(self.hell_label)
        self.labellayout.addWidget(self.temp_label)
        self.labellayout.addWidget(self.laut_label)
        self.labellayout.addWidget(self.co2_label)

        # setzen der Uhren (Liveuhr und Advanced-Modus Uhren)
        digiuhrfnt = QFont('Arial', 12)
        self.anauhr = Liveuhr()
        self.uhrlayout.addWidget(self.anauhr, 2)

        self.adanauhr1 = Startinfouhr()
        self.adanauhr1.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                                           QtWidgets.QSizePolicy.Preferred))
        self.adanauhr2 = Endinfouhr()
        self.adanauhr2.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                                           QtWidgets.QSizePolicy.Preferred))
        self.anfangzeit.addWidget(self.adanauhr1)
        self.endzeit.addWidget(self.adanauhr2)
        self.digiuhr1 = QLabel()
        self.digiuhr2 = QLabel()

        self.digiuhr1.setAlignment(Qt.AlignCenter)
        self.digiuhr2.setAlignment(Qt.AlignCenter)
        self.digiuhr1.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                                          QtWidgets.QSizePolicy.Fixed))
        self.digiuhr2.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                                          QtWidgets.QSizePolicy.Fixed))
        self.digiuhr1.setFont(digiuhrfnt)
        self.digiuhr2.setFont(digiuhrfnt)
        self.anfangzeit.addWidget(self.digiuhr1)
        self.endzeit.addWidget(self.digiuhr2)

        self.digiuhr1.setText('Anfang: \n' + 'JJJJ-MM-TT/HH-MM-SS')
        self.digiuhr2.setText('Ende: \n' + 'JJJJ-MM-TT/HH-MM-SS')

        self.addateiname.setText('JJJJ-MM-TT/HH-MM-SS.txt')

        # ampeln zuweisen

        self.einfacheampelhelligkeit = Hellampel()
        self.einfacheampeltemperatur = Tempampel()
        self.einfacheampellautstaerke = Lautampel()
        self.einfacheampelco2 = Co2ampel()

        self.ampellayout.addWidget(self.einfacheampelhelligkeit)
        self.ampellayout.addWidget(self.einfacheampeltemperatur)
        self.ampellayout.addWidget(self.einfacheampellautstaerke)
        self.ampellayout.addWidget(self.einfacheampelco2)

        # großampelzeug + buttonartig

        self.groampel = Hellampel()
        self.groampellayout.addWidget(self.groampel)

        self.einfacheampelhelligkeit.mousePressEvent = self.zugroampelhell
        self.einfacheampeltemperatur.mousePressEvent = self.zugroampeltemp
        self.einfacheampellautstaerke.mousePressEvent = self.zugroampellaut
        self.einfacheampelco2.mousePressEvent = self.zugroampelco2

        # about Fenster

        self.actionAbout.triggered.connect(aboutPopup.show)

        # sound
        self.player = QMediaPlayer()

        # Scaling zum Bildschirm beim Start

        if self.uimode.currentIndex() == 1:
            self.move(0, 0)
            self.resize(bildbreite // 10, int(bildhoehe) - 30)
        elif self.uimode.currentIndex() == 0:
            self.move(bildbreite // 5, bildhoehe // 8)
            self.resize((int(bildbreite * 1.3)) // 2, (int(bildhoehe * 1.5)) // 2)
        elif self.uimode.currentIndex() == 2:
            self.move(bildbreite // 5, bildhoehe // 8)
            self.resize((int(bildbreite * 1.3)) // 2, (int(bildhoehe * 1.5)) // 2)

    # modus ändern funktionen

    def changetosimpel(self, plhaltervar):
        self.uimode.setCurrentIndex(1)
        self.resize(bildbreite // 10, int(bildhoehe) - 30)
        # print(bildbreite // 10, int(bildhoehe) - 30)
        self.move(0, 0)
        if self.darkmodebutton.isChecked():
            self.uimode.setStyleSheet('color: white;'
                                      'background-color : rgb(30, 27, 24)')
        else:
            self.uimode.setStyleSheet('')

    def changetoadvanced(self):
        self.uimode.setCurrentIndex(2)
        self.resize((int(bildbreite * 1.3)) // 2, (int(bildhoehe * 1.5)) // 2)
        self.move(bildbreite // 5, bildhoehe // 8)
        if self.darkmodebutton.isChecked():
            self.uimode.setStyleSheet('color: white;'
                                      'background-color : rgb(30, 27, 24)')
        else:
            self.uimode.setStyleSheet('')

    def changetodeveloper(self):
        self.uimode.setCurrentIndex(0)
        self.resize((int(bildbreite * 1.3)) // 2, (int(bildhoehe * 1.5)) // 2)
        self.move(bildbreite // 5, bildhoehe // 8)
        if self.darkmodebutton.isChecked():
            self.uimode.setStyleSheet('color: white;'
                                      'background-color : rgb(30, 27, 24)')
        else:
            self.uimode.setStyleSheet('')

    # zugroßample funktionen

    def zugroampelhell(self, plhaltervar):
        self.groampellayout.removeWidget(self.groampel)
        self.groampel = Hellampel()
        self.groampellayout.addWidget(self.groampel)
        self.uimode.setCurrentIndex(3)
        self.ampelnamelabel.setText('Helligkeit')
        self.groampel.mousePressEvent = self.changetosimpel

    def zugroampeltemp(self, plhaltervar):
        self.groampellayout.removeWidget(self.groampel)
        self.groampel = Tempampel()
        self.groampellayout.addWidget(self.groampel)
        self.uimode.setCurrentIndex(3)
        self.ampelnamelabel.setText('Temperatur')
        self.groampel.mousePressEvent = self.changetosimpel

    def zugroampellaut(self, plhaltervar):
        self.groampellayout.removeWidget(self.groampel)
        self.groampel = Lautampel()
        self.groampellayout.addWidget(self.groampel)
        self.uimode.setCurrentIndex(3)
        self.ampelnamelabel.setText('Lautstärke')
        self.groampel.mousePressEvent = self.changetosimpel

    def zugroampelco2(self, plhaltervar):

        self.groampellayout.removeWidget(self.groampel)
        self.groampel = Co2ampel()
        self.groampellayout.addWidget(self.groampel)
        self.uimode.setCurrentIndex(3)
        self.ampelnamelabel.setText('CO2')
        self.groampel.mousePressEvent = self.changetosimpel

    # advancced modus funktionen

    def opendatei(self):
        global dateiausgabe, startzeit, endzeit
        path = QFileDialog.getOpenFileName(None, 'Open a file', 'savedluftdata/', 'All Files (*.*)')
        if path != ('', ''):
            print("File path : " + path[0])
            dateiausgabe = path[0]
            addatei = path[0].split('/')
            self.addateiname.setText(str(addatei[-1]))
            savedatei = open(dateiausgabe, 'r')
            luftdaten = savedatei.readlines()
            savedatei.close()
            luftdaten.pop(0)

            sz = luftdaten[0].split(',')
            ez = luftdaten[-1].split(',')
            self.digiuhr1.setText('Anfang: \n' + str(sz[0]))
            self.digiuhr2.setText('Ende: \n' + str(ez[0]))
            sz = sz[0].split('/')
            ez = ez[0].split('/')
            sz = sz[1].split(':')
            ez = ez[1].split(':')
            startzeit = QTime(int(sz[0]), int(sz[1]), int(sz[2]))
            endzeit = QTime(int(ez[0]), int(ez[1]), int(ez[2]))
            self.adtempbuttons()

    def adtempbuttons(self):
        self.datendateiverarb(1)
        self.adinfolabel.setText('Temperatur\n in °C')

    def adluftdruckbuttons(self):
        self.datendateiverarb(2)
        self.adinfolabel.setText('Luftdruck\n in hPa')

    def adco2buttons(self):
        self.datendateiverarb(3)
        self.adinfolabel.setText('CO2\n in ppm')

    def adlautbuttons(self):
        self.datendateiverarb(4)
        self.adinfolabel.setText('Lautstärke\n in dB')

    def adhellbuttons(self):
        self.datendateiverarb(5)
        self.adinfolabel.setText('Helligkeit\n in lx')

    def adcleardata(self):
        global dateiausgabe
        dateiausgabe = ''
        self.advanced_line.setData()
        self.digiuhr1.setText('Anfang: \n' + 'JJJJ-MM-TT/HH-MM-SS')
        self.digiuhr2.setText('Ende: \n' + 'JJJJ-MM-TT/HH-MM-SS')
        self.addateiname.setText('JJJJ-MM-TT/HH-MM-SS.txt')

    def datendateiverarb(self, stelle=1):
        global dateiausgabe

        if dateiausgabe == '':
            pass
        else:
            savedatei = open(dateiausgabe, 'r')
            luftdaten = savedatei.readlines()
            luftdaten.pop(0)
            daten_line = []
            for z in luftdaten:
                z = z.split(',')
                daten_punkt = float(z[stelle])
                daten_line.append(daten_punkt)

            print(len(daten_line))
            self.advanced_line.setData(daten_line)
            listenlen = len(daten_line)
            adtemporotgrenzlist = np.full(listenlen, temporotgrenz)
            adtempogelbgrenzlist = np.full(listenlen, tempogelbgrenz)
            adtempurotgrenzlist = np.full(listenlen, tempurotgrenz)
            adtempugelbgrenzlist = np.full(listenlen, tempugelbgrenz)

            adluftdruckogrenzlist = np.full(listenlen, luftdruckogrenz)
            adluftdruckugrenzlist = np.full(listenlen, luftdruckugrenz)

            adco2orotgrenzlist = np.full(listenlen, co2orotgrenz)
            adco2ogelbgrenzlist = np.full(listenlen, co2ogelbgrenz)

            adlautorotgrenzlist = np.full(listenlen, lautorotgrenz)
            adlautogelbgrenzlist = np.full(listenlen, lautogelbgrenz)

            adhellurotgrenzlist = np.full(listenlen, hellurotgrenz)
            adhellugelbgrenzlist = np.full(listenlen, hellugelbgrenz)

            if stelle == 1:
                self.adorotgrenz.setData(adtemporotgrenzlist)
                self.adogelbgrenz.setData(adtempogelbgrenzlist)
                self.adugelbgrenz.setData(adtempugelbgrenzlist)
                self.adurotgrenz.setData(adtempurotgrenzlist)
            elif stelle == 2:
                self.adorotgrenz.setData(adluftdruckogrenzlist)
                self.adogelbgrenz.setData('')
                self.adugelbgrenz.setData('')
                self.adurotgrenz.setData(adluftdruckugrenzlist)
            elif stelle == 3:
                self.adorotgrenz.setData(adco2orotgrenzlist)
                self.adogelbgrenz.setData(adco2ogelbgrenzlist)
                self.adugelbgrenz.setData('')
                self.adurotgrenz.setData('')
            elif stelle == 4:
                self.adorotgrenz.setData(adlautorotgrenzlist)
                self.adogelbgrenz.setData(adlautogelbgrenzlist)
                self.adugelbgrenz.setData('')
                self.adurotgrenz.setData('')
            elif stelle == 5:
                self.adorotgrenz.setData('')
                self.adogelbgrenz.setData('')
                self.adugelbgrenz.setData(adhellugelbgrenzlist)
                self.adurotgrenz.setData(adhellurotgrenzlist)
            # zum erweitern wäre noch
            #   https://stackoverflow.com/questions/49046931/how-can-i-use-dateaxisitem-of-pyqtgraph

    def changegrenzen(self):
        global temporotgrenzlist, tempogelbgrenzlist, \
            tempurotgrenzlist, tempugelbgrenzlist, luftdruckogrenzlist, \
            luftdruckugrenzlist, co2orotgrenzlist, co2ogelbgrenzlist, \
            lautorotgrenzlist, lautogelbgrenzlist, hellurotgrenzlist, hellugelbgrenzlist, \
            temporotgrenz, tempogelbgrenz, tempurotgrenz, tempugelbgrenz, luftdruckogrenz, \
            luftdruckugrenz, co2orotgrenz, co2ogelbgrenz, lautorotgrenz, lautogelbgrenz, \
            hellurotgrenz, hellugelbgrenz

        if int(self.adtemporotedit.text()) > int(self.adtempogelbedit.text()) and int(
                self.adtempogelbedit.text()) > int(self.adtempugelbedit.text()):
            temporotgrenzlist = np.full(300, int(self.adtemporotedit.text()))
            tempogelbgrenzlist = np.full(300, int(self.adtempogelbedit.text()))
            temporotgrenz = int(self.adtemporotedit.text())
            tempogelbgrenz = int(self.adtempogelbedit.text())

        if int(self.adtempurotedit.text()) < int(self.adtempugelbedit.text()) < int(
                self.adtempogelbedit.text()):
            tempurotgrenzlist = np.full(300, int(self.adtempurotedit.text()))
            tempugelbgrenzlist = np.full(300, int(self.adtempugelbedit.text()))
            tempurotgrenz = int(self.adtempurotedit.text())
            tempugelbgrenz = int(self.adtempugelbedit.text())

        if int(self.adluftdruckorotedit.text()) > int(self.adluftdruckugelbedit.text()):
            luftdruckogrenzlist = np.full(300, int(self.adluftdruckorotedit.text()))
            luftdruckugrenzlist = np.full(300, int(self.adluftdruckugelbedit.text()))
            luftdruckogrenz = int(self.adluftdruckorotedit.text())
            luftdruckugrenz = int(self.adluftdruckugelbedit.text())

        if int(self.adCO2orotedit.text()) > int(self.adCO2ogelbedit.text()):
            co2orotgrenzlist = np.full(300, int(self.adCO2orotedit.text()))
            co2ogelbgrenzlist = np.full(300, int(self.adCO2ogelbedit.text()))
            co2orotgrenz = int(self.adCO2orotedit.text())
            co2ogelbgrenz = int(self.adCO2ogelbedit.text())

        if int(self.adlautorotedit.text()) > int(self.adlautogelbedit.text()):
            lautorotgrenzlist = np.full(300, int(self.adlautorotedit.text()))
            lautogelbgrenzlist = np.full(300, int(self.adlautogelbedit.text()))
            lautorotgrenz = int(self.adlautorotedit.text())
            lautogelbgrenz = int(self.adlautogelbedit.text())

        if int(self.adhellurotedit.text()) < int(self.adhellugelbedit.text()):
            hellurotgrenzlist = np.full(300, int(self.adhellurotedit.text()))
            hellugelbgrenzlist = np.full(300, int(self.adhellugelbedit.text()))
            hellurotgrenz = int(self.adhellurotedit.text())
            hellugelbgrenz = int(self.adhellugelbedit.text())

        self.adtempogelbedit.clear()
        self.adtemporotedit.clear()
        self.adtempugelbedit.clear()
        self.adtempurotedit.clear()
        self.adluftdruckugelbedit.clear()
        self.adluftdruckorotedit.clear()
        self.adCO2ogelbedit.clear()
        self.adCO2orotedit.clear()
        self.adlautogelbedit.clear()
        self.adlautorotedit.clear()
        self.adhellugelbedit.clear()
        self.adhellurotedit.clear()

        self.adtempogelbedit.insert(str(tempogelbgrenz))
        self.adtemporotedit.insert(str(temporotgrenz))
        self.adtempugelbedit.insert(str(tempugelbgrenz))
        self.adtempurotedit.insert(str(tempurotgrenz))
        self.adluftdruckugelbedit.insert(str(luftdruckugrenz))
        self.adluftdruckorotedit.insert(str(luftdruckogrenz))
        self.adCO2ogelbedit.insert(str(co2ogelbgrenz))
        self.adCO2orotedit.insert(str(co2orotgrenz))
        self.adlautogelbedit.insert(str(lautogelbgrenz))
        self.adlautorotedit.insert(str(lautorotgrenz))
        self.adhellugelbedit.insert(str(hellugelbgrenz))
        self.adhellurotedit.insert(str(hellurotgrenz))

        self.temporotgrenz_line.setData(temporotgrenzlist)
        self.tempogelbgrenz_line.setData(tempogelbgrenzlist)
        self.tempurotgrenz_line.setData(tempurotgrenzlist)
        self.tempugelbgrenz_line.setData(tempugelbgrenzlist)

        self.co2orotgrenz_line.setData(co2orotgrenzlist)
        self.co2ogelbgrenz_line.setData(co2ogelbgrenzlist)

        self.luftdruckogrenz_line.setData(luftdruckogrenzlist)
        self.luftdruckugrenz_line.setData(luftdruckugrenzlist)

        self.lautorotgrenz_line.setData(lautorotgrenzlist)
        self.lautogelbgrenz_line.setData(lautogelbgrenzlist)

        self.hellurotgrenz_line.setData(hellurotgrenzlist)
        self.hellugelbgrenz_line.setData(hellugelbgrenzlist)

        grenzdaten = open('../src/ui/einstellungen/grenzen.txt', 'r')
        grenzen = grenzdaten.readlines()
        grenzen[3] = str(temporotgrenz) + '\n'
        grenzen[1] = str(tempogelbgrenz) + '\n'
        grenzen[7] = str(tempurotgrenz) + '\n'
        grenzen[5] = str(tempugelbgrenz) + '\n'

        grenzen[11] = str(luftdruckogrenz) + '\n'
        grenzen[9] = str(luftdruckugrenz) + '\n'

        grenzen[15] = str(co2orotgrenz) + '\n'
        grenzen[13] = str(co2ogelbgrenz) + '\n'

        grenzen[19] = str(lautorotgrenz) + '\n'
        grenzen[17] = str(lautogelbgrenz) + '\n'

        grenzen[23] = str(hellurotgrenz) + '\n'
        grenzen[21] = str(hellugelbgrenz) + '\n'

        grenzdaten = open('../src/ui/einstellungen/grenzen.txt', 'w')
        grenzdaten.writelines(grenzen)
        grenzdaten.close()

    # Unterricht und Warnungen

    def filmmodus(self):
        global lautwarnungen, hellwarnungen
        if self.actionFilmmodus.isChecked():

            self.actionlautwarnungen.setChecked(0)
            self.actionhellwarnungen.setChecked(0)
            self.actionlautwarnungen.setEnabled(0)
            self.actionhellwarnungen.setEnabled(0)
            lautwarnungen = False
            hellwarnungen = False
            self.actionGruppenarbeit.setEnabled(0)
        else:
            self.actionlautwarnungen.setChecked(1)
            self.actionhellwarnungen.setChecked(1)
            self.actionlautwarnungen.setEnabled(1)
            self.actionhellwarnungen.setEnabled(1)
            lautwarnungen = True
            hellwarnungen = True
            self.actionGruppenarbeit.setEnabled(1)

    def gruppenarbeit(self):
        global lautwarnungen
        if self.actionGruppenarbeit.isChecked():
            self.actionlautwarnungen.setChecked(0)
            self.actionlautwarnungen.setEnabled(0)
            lautwarnungen = False
            self.actionFilmmodus.setEnabled(0)
        else:
            self.actionlautwarnungen.setChecked(1)
            self.actionlautwarnungen.setEnabled(1)
            lautwarnungen = True
            self.actionFilmmodus.setEnabled(1)

    def audiowarnsignal(self):
        global warntonbeiswitch
        full_file_path = os.path.join(os.getcwd(), '../src/ui/sounds/sound.mp3')
        url = QUrl.fromLocalFile(full_file_path)
        content = QMediaContent(url)
        self.player.setMedia(content)

    def tempwarnanaus(self):
        global tempwarnungen
        warnungPopup.hide()
        if not self.actiontempwarnungen.isChecked():
            tempwarnungen = False
        else:
            tempwarnungen = True

    def lautwarnanaus(self):
        global lautwarnungen
        warnungPopup.hide()
        if not self.actionlautwarnungen.isChecked():
            lautwarnungen = False

        else:
            lautwarnungen = True

    def co2warnanaus(self):
        global co2warnungen
        warnungPopup.hide()
        if not self.actionco2warnungen.isChecked():
            co2warnungen = False
        else:
            co2warnungen = True

    def hellwarnanaus(self):
        global hellwarnungen
        warnungPopup.hide()
        if not self.actionhellwarnungen.isChecked():
            hellwarnungen = False
        else:
            hellwarnungen = True

    def allewarnaus(self):
        global tempwarnungen, lautwarnungen, co2warnungen, hellwarnungen
        warnungPopup.hide()
        tempwarnungen = False
        lautwarnungen = False
        co2warnungen = False
        hellwarnungen = False
        self.actiontempwarnungen.setChecked(0)
        self.actionlautwarnungen.setChecked(0)
        self.actionco2warnungen.setChecked(0)
        self.actionhellwarnungen.setChecked(0)

    def openhilfe(self):
        os.startfile('../src/info+hilfe/Standardprobleme.pdf')

    # live Funktionen für den dev-modus (zeit und werte)

    def updatetempce(self):
        global tempcelist, daten, temporotgrenz, tempogelbgrenz,\
            tempurotgrenz, tempugelbgrenz, tempampelfarbe, tempwarnungen

        # gibt den derzeitgigen Wert in das LCDWidget
        self.tempanzei.display(daten[1])
        # ampel umstellung für den entsprechenden wert
        if daten[1] < tempurotgrenz:
            self.temp_line.setPen(QColor(255, 0, 0))
            tempampelfarbe = 'rot'
            self.tempampel.setStyleSheet('background-color: rgb(0, 255, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            warnungPopup.warnungenTempniedrig()
        elif tempurotgrenz <= daten[1] <= tempugelbgrenz:
            self.temp_line.setPen(QColor(255, 255, 0))
            self.tempampel.setStyleSheet('background-color: rgb(255, 255, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            tempampelfarbe = 'gelb'
            if self.actiontempwarnungen.isChecked():
               tempwarnungen = True

        elif tempugelbgrenz < daten[1] <= tempogelbgrenz:
            self.temp_line.setPen(QColor(0, 255, 0))
            self.tempampel.setStyleSheet('background-color: rgb(0, 255, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            tempampelfarbe = 'gruen'
        elif tempogelbgrenz < daten[1] <= temporotgrenz:
            self.temp_line.setPen(QColor(255, 255, 0))
            self.tempampel.setStyleSheet('background-color: rgb(255, 255, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            tempampelfarbe = 'gelb'
            if self.actiontempwarnungen.isChecked():
               tempwarnungen = True

        elif daten[1] > temporotgrenz:
            self.temp_line.setPen(QColor(255, 0, 0))
            self.tempampel.setStyleSheet('background-color: rgb(255, 0, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            tempampelfarbe = 'rot'
            warnungPopup.warnungTemphoch()

        # muss angepasst werden an die Werte

        tempcelist[:-1] = tempcelist[1:]
        tempcelist[-1] = daten[1]

        self.temp_line.setData(tempcelist)  # graph wird mit der aktualisiereten Datenliste erzeugt
        if self.opanzeig.isChecked():
            self.devausgabe.append('\n' + 'tempupdate')

    def updateluftdruck(self):
        global luftdrucklist, daten, luftdruckogrenz, luftdruckugrenz

        #   gibt den derzeitgigen Wert in das LCDWidget
        self.luftdruckanzei.display(daten[2])
        #   ampel umstellung für den entsprechenden wert
        if daten[2] >= luftdruckogrenz:
            self.luftdruck_line.setPen(QColor(255, 0, 0))
            self.luftdruckampel.setStyleSheet('background-color: rgb(255, 0, 0);'
                                              'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
        elif daten[2] <= luftdruckugrenz:
            self.luftdruck_line.setPen(QColor(255, 255, 0))
            self.luftdruckampel.setStyleSheet('background-color: rgb(255, 255, 0);'
                                              'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
        else:
            self.luftdruck_line.setPen(QColor(0, 255, 0))
            self.luftdruckampel.setStyleSheet('background-color: rgb(0, 255, 0);'
                                              'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
        #   muss angepasst werden an die Werte

        luftdrucklist[:-1] = luftdrucklist[1:]
        luftdrucklist[-1] = daten[2]

        self.luftdruck_line.setData(luftdrucklist)  # graph wird mit der aktualisiereten Datenliste erzeugt
        if self.opanzeig.isChecked():
            self.devausgabe.append('luftdruckupdate')

    def updateco2(self):
        global co2list, daten, co2orotgrenz, co2ogelbgrenz, co2ampelfarbe, co2warnungen

        #   gibt den derzeitgigen Wert in das LCDWidget
        self.co2anzei.display(daten[3])
        #   ampel umstellung für den entsprechenden wert
        if daten[3] > co2orotgrenz:
            self.co2_line.setPen(QColor(255, 0, 0))
            self.co2ampel.setStyleSheet('background-color: rgb(255, 0, 0);'
                                        'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            co2ampelfarbe = 'rot'
            warnungPopup.warnungCo2()
            if self.actionAudiowarnsignal.isChecked():
                self.player.play()
        elif co2ogelbgrenz <= daten[3] <= co2orotgrenz:
            co2ampelfarbe = 'gelb'
            self.co2_line.setPen(QColor(255, 255, 0))
            self.co2ampel.setStyleSheet('background-color: rgb(255, 255, 0);'
                                        'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            if self.actionco2warnungen.isChecked():
                co2warnungen = True
        else:  # also <1000
            self.co2_line.setPen(QColor(0, 255, 0))
            self.co2ampel.setStyleSheet('background-color: rgb(0, 255, 0);'
                                        'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            co2ampelfarbe = 'gruen'
        # muss angepasst werden an die Werte

        co2list[:-1] = co2list[1:]
        co2list[-1] = daten[3]

        self.co2_line.setData(co2list)  # graph wird mit der aktualisiereten Datenliste erzeugt
        if self.opanzeig.isChecked():
            self.devausgabe.append('co2update')

    def updatelaut(self):
        global lautlist, daten, lautorotgrenz, lautogelbgrenz, lautampelfarbe, lautwarnungen

        # gibt den derzeitgigen Wert in das LCDWidget
        self.lautanzei.display(daten[4])
        # ampel umstellung für den entsprechenden wert
        if daten[4] > lautorotgrenz:
            self.laut_line.setPen(QColor(255, 0, 0))
            self.lautampel.setStyleSheet('background-color: rgb(255, 0, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            lautampelfarbe = 'rot'
            warnungPopup.warnungLautstaerke()
            if self.actionAudiowarnsignal.isChecked():
                self.player.play()
        elif lautogelbgrenz <= daten[4] <= lautorotgrenz:
            self.laut_line.setPen(QColor(255, 255, 0))
            self.lautampel.setStyleSheet('background-color: rgb(255, 255, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            lautampelfarbe = 'gelb'
            if self.actionlautwarnungen.isChecked():
                lautwarnungen = True
        else:  # also kleiner als 65
            self.laut_line.setPen(QColor(0, 255, 0))
            self.lautampel.setStyleSheet('background-color: rgb(0, 255, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            lautampelfarbe = 'gruen'
            if self.actionlautwarnungen.isChecked():
                lautwarnungen = True
        # muss angepasst werden an die Werte

        lautlist[:-1] = lautlist[1:]
        lautlist[-1] = daten[4]

        self.laut_line.setData(lautlist)  # graph wird mit der aktualisiereten Datenliste erzeugt
        if self.opanzeig.isChecked():
            self.devausgabe.append('lautupdate')

    def updatehell(self):
        global helllist, daten, hellurotgrenz, hellugelbgrenz, hellampelfarbe, hellwarnungen

        # gibt den derzeitgigen Wert in das LCDWidget
        self.hellanzei.display(daten[5])
        # ampel umstellung für den entsprechenden wert
        if daten[5] < hellurotgrenz:
            self.hell_line.setPen(QColor(255, 0, 0))
            self.hellampel.setStyleSheet('background-color: rgb(255, 0, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            hellampelfarbe = 'rot'
            warnungPopup.warnungLicht()
        elif hellurotgrenz <= daten[5] <= hellugelbgrenz:
            self.hell_line.setPen(QColor(255, 255, 0))
            self.hellampel.setStyleSheet('background-color: rgb(255, 255, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            hellampelfarbe = 'gelb'
            if self.actionhellwarnungen.isChecked():
                hellwarnungen = True
        else:  # groeßer als 300
            self.hell_line.setPen(QColor(0, 255, 0))
            self.hellampel.setStyleSheet('background-color: rgb(0, 255, 0);'
                                         'font: 14pt "MS Shell Dlg 2";color: rgb(0, 0, 0);')
            hellampelfarbe = 'gruen'
            if self.actionhellwarnungen.isChecked():
                hellwarnungen = True
        # muss angepasst werden an die Werte

        helllist[:-1] = helllist[1:]
        helllist[-1] = daten[5]

        self.hell_line.setData(helllist)  # graph wird mit der aktualisiereten Datenliste erzeugt
        if self.opanzeig.isChecked():
            self.devausgabe.append('hellupdate')

    def zeitausgabe(self):
        currenttime = QTime.currentTime()

        displaytxt = currenttime.toString('hh:mm:ss')

        self.uhr.setText(displaytxt)

    # bonusfunktionen

    def clickedonicon(self):
        self.show()

    def checkifdevcon(self):
        global deviceconnected

        if deviceconnected:

            self.istdevcon.setStyleSheet('background-color : darkgreen')
            self.istdevcon.setText('Verbunden')
            self.istsimpelcon.setStyleSheet('background-color : darkgreen')
            self.istsimpelcon.setText('Verbunden')
            self.comanzeig.setText(str(devicecom))
            self.anzahlcom.setText(str(len(COM)))
            if self.infoanzeig.isChecked():
                self.devausgabe.append('\n' + str(daten))

        else:
            self.istdevcon.setStyleSheet('background-color : red')
            self.istdevcon.setText('Nicht Verbunden')
            self.istsimpelcon.setStyleSheet('background-color : red')
            self.istsimpelcon.setText('Nicht Verbunden')
            self.comanzeig.setText('')
            self.anzahlcom.setText(str(len(COM)))

    def cleardevausgabe(self):
        self.devausgabe.clear()

    def changecolor(self):

        # if button is checked
        if self.darkmodebutton.isChecked():

            # setting background color to light-blue
            self.darkmodebutton.setStyleSheet("background-color : green")
            self.uimode.setStyleSheet('color: white;background-color : rgb(30, 27, 24)')
            self.uhr.setStyleSheet('color: white')

        # if it is unchecked
        else:

            # set background color back to light-grey
            self.darkmodebutton.setStyleSheet("color: black;background-color : darkgrey")
            self.uimode.setStyleSheet('color: black;background-color : white')
            self.uhr.setStyleSheet('color: black')

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Tray Program",
            "Fenster nun in der kleinen Taskleiste",
            QSystemTrayIcon.Information,
            1000)


def grafikdingens():
    '''Setup für das Hauptfenster '''
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())


def datenzeugs():
    '''Datenthread welcher sich um Verbindung, Datenabruf und Datenverarbeitung kümmert '''
    global daten

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

        dateinamein = str('savedluftdata/' + zeit + '.txt')
        speicher = open(dateinamein, "a")
        speicher.write('time,tempce,luftdruck,co2,laut,hell')  # auf göße anpassen
        speicher.close()
        return dateinamein

    def connect():
        """ stellt die Verbindung zu serial port auf """
        global deviceconnected, ser, devicecom, treiber
        if not deviceconnected:
            COM = [comport.device for comport in serial.tools.list_ports.comports()]
            print(COM)
            for e in COM:
                try:
                    ser = serial.Serial(str(e), baudrate=115200, timeout=2)
                    data = ser.readline().decode('ascii')
                    datalist = data.split(' ')
                    print(datalist)
                    comtestwert = float(datalist[0])
                    deviceconnected = True
                    devicecom = e
                    break
                except:
                    ser = None
                    deviceconnected = False
                    print(len(COM))
                    if COM == [''] and treiber == False:
                        os.startfile('../CP2102-windows-installer/pololu-cp2102-setup-x64.exe')
                        treiber = True
                    else:
                        treiber = True

        else:
            pass

    def datenverarbeitung():
        global daten, deviceconnected

        def datenabruf():
            global deviceconnected, ser
            """ empfängt die daten die vom esp32 gesendet werden,
                kombiniert sie mit der zeit
                und speicher die in der oben erstllen .txt datei"""

            try:

                data = ser.readline().decode('ascii')
                datalist = data.split(' ')
                time = datetime.datetime.now().strftime("%Y-%m-%d/%H:%M:%S")
                tempce = float(datalist[0])
                luftdruck = float(datalist[1])
                co2 = float(datalist[2])
                laut = float(datalist[3])
                hell = float(datalist[4])
                datentu = time, tempce, luftdruck, co2, laut, hell

            except:
                time = datetime.datetime.now().strftime("%Y-%m-%d/%H:%M:%S")
                datentu = (time, 22, 1000, 0, 0, 400)
                deviceconnected = False

            return datentu
            # gibt keinen error aus

        def speichern(dateiname, daten):
            """öffnet die datei schreibt die Daten in die .txt
            und schließt diese wieder"""
            datenstr = str(daten[0]) + ',' + str(daten[1]) + ',' + \
                       str(daten[2]) + ',' + str(daten[3]) + ',' + \
                       str(daten[4]) + ',' + str(daten[5])
            speicher = open(dateiname, "a")
            speicher.write('\n')
            speicher.write(str(datenstr))
            speicher.close()

        while True:
            connect()

            daten = datenabruf()

            speichern(dateiname, daten)

            time.sleep(1)

    dateiname = dateianlegen()
    datenverarbeitung()


gesamtapp = QtWidgets.QApplication(sys.argv)
warnungPopup = Warnungen()
aboutPopup = Aboutwindow()

# Erstelle neuen thread
datenthread = threading.Thread(target=datenzeugs, daemon=True)

# Starte Thread
datenthread.start()

# Start vom GUI
grafikdingens()
