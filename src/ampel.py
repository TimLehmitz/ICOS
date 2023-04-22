from PyQt5.QtCore import QTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTime, Qt


# Ampeln
"""
Ampels sind zurzeit nicht funktionsfähig --> udatefunktion muss überarbeitet werden



"""

class Ampel(QLabel):
    """Basis Ampelklasse vererbt an die spezifischen Ampeln """

    def __init__(self):
        super().__init__()
        self.ampelfarb = 'gruen'
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


class Hellampel(Ampel):
    """Ampel für die Helligkeit """

    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        global hellampelfarbe

        rec = min(self.width() * 3, self.height())

        painter = QPainter(self)

        def zeichnekreise(farbe='gruen'):
            if farbe == 'gruen':

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

        zeichnekreise(farbe=self.ampelfarb)

        painter.end()


class Tempampel(Ampel):
    """Ampel für die Temperatur """
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        global tempampelfarbe
        rec = min(self.width() * 3, self.height())

        painter = QPainter(self)

        def zeichnekreise(farbe='gruen'):
            if farbe == 'gruen':

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

        zeichnekreise(farbe=self.ampelfarb)

        painter.end()


class Lautampel(Ampel):
    """ Ampel für die Lautstärke """
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        global lautampelfarbe
        rec = min(self.width() * 3, self.height())

        painter = QPainter(self)

        def zeichnekreise(farbe='gruen'):
            if farbe == 'gruen':

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

        zeichnekreise(farbe=self.ampelfarb)

        painter.end()


class Co2ampel(Ampel):
    """Ampel für den Co2-Gehalt """
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        global co2ampelfarbe
        rec = min(self.width() * 3, self.height())

        painter = QPainter(self)

        def zeichnekreise(farbe='gruen'):
            if farbe == 'gruen':

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

        zeichnekreise(farbe=self.ampelfarb)

        painter.end()
