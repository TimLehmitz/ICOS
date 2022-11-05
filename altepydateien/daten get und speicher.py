# -*- coding: utf-8 -*-
import serial
import datetime
import time
import pyqtgraph as pg
import numpy as np
import threading
#from pyqtgraph.Qt import QtCore, QtGui

daten = '2021-08-16/16:58:04', 56.1, 51.0, 669.0, 50.0, 69.0
def grafikdingens():
    global tempcelist, luftfeuchtlist, co2list, lautlist, helllist
    global tempcegraposi, luftfeuchtgraposi, co2graposi, lautgraposi, hellgraposi
    global daten

    win = pg.GraphicsLayoutWidget(show=True)
    titel = 'Graphen für alle 5 werte'
    win.setWindowTitle(titel)
    win.setMinimumSize(1000, 1000)
    win.move(920,0)

    # 2) Allow data to accumulate. In these examples, the array doubles in length
    #    whenever it is full. tempce, luftfeucht, co2,    laut,   hell
    tempcegra = win.addPlot()
    win.nextRow()
    luftfeuchtgra = win.addPlot()
    win.nextRow()
    co2gra = win.addPlot()
    win.nextRow()
    lautgra = win.addPlot()
    win.nextRow()
    hellgra = win.addPlot()
    # Use automatic downsampling and clipping to reduce the drawing load

    tempcegra.setDownsampling(mode='peak')
    luftfeuchtgra.setDownsampling(mode='peak')
    co2gra.setDownsampling(mode='peak')
    lautgra.setDownsampling(mode='peak')
    hellgra.setDownsampling(mode='peak')

    tempcegra.setClipToView(True)
    luftfeuchtgra.setClipToView(True)
    co2gra.setClipToView(True)
    lautgra.setClipToView(True)
    hellgra.setClipToView(True)

    ctempcegra = tempcegra.plot()
    cluftfeuchtgra = luftfeuchtgra.plot()
    cco2gra = co2gra.plot()
    clautgra = lautgra.plot()
    chellgra = hellgra.plot()

    tempcegra.setLabel('bottom', 'Time', 's')
    luftfeuchtgra.setLabel('bottom', 'Time', 's')
    co2gra.setLabel('bottom', 'Time', 's')
    lautgra.setLabel('bottom', 'Time', 's')
    hellgra.setLabel('bottom', 'Time', 's')


    tempcelist = np.zeros(100)
    luftfeuchtlist = np.zeros(100)
    co2list = np.zeros(100)
    lautlist = np.zeros(100)
    helllist = np.zeros(100)

    tempcegraposi = 0
    luftfeuchtgraposi = 0
    co2graposi = 0
    lautgraposi = 0
    hellgraposi = 0


    def updatetempce(daten):
        global tempcelist, tempcegraposi

        tempcelist[tempcegraposi] = daten[1]  # zufälliger wert für die näcghste stelle

        tempcegraposi += 1  # erhöh die stelle
        if tempcegraposi >= tempcelist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = tempcelist  # datenliste wird in temp gespeicher
            tempcelist = np.empty(tempcelist.shape[0] * 2)  # die datenlistenlänge wird verdoppelt
            tempcelist[:tmp.shape[0]] = tmp  # daten werden in die längere liste gepackt

        ctempcegra.setData(tempcelist[:tempcegraposi])  # graph wird mitder aktualisiereten datenliste erzeugt
    def updateluftfeucht(daten):
        global luftfeuchtlist, luftfeuchtgraposi

        luftfeuchtlist[luftfeuchtgraposi] = daten[2]  # zufälliger wert für die näcghste stelle
        luftfeuchtgraposi += 1  # erhöh die stelle
        if luftfeuchtgraposi >= luftfeuchtlist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = luftfeuchtlist  # datenliste wird in temp gespeicher
            luftfeuchtlist = np.empty(luftfeuchtlist.shape[0] * 2)  # die datenlistenlänge wird verdoppelt
            luftfeuchtlist[:tmp.shape[0]] = tmp  # daten werden in die längere liste gepackt

        cluftfeuchtgra.setData(luftfeuchtlist[:luftfeuchtgraposi])  # graph wird mitder aktualisiereten datenliste erzeugt
    def updateco2(daten):
        global co2list, co2graposi

        co2list[co2graposi] = daten[3]  # zufälliger wert für die näcghste stelle
        co2graposi += 1  # erhöh die stelle
        if co2graposi >= co2list.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = co2list  # datenliste wird in temp gespeicher
            co2list = np.empty(co2list.shape[0] * 2)  # die datenlistenlänge wird verdoppelt
            co2list[:tmp.shape[0]] = tmp  # daten werden in die längere liste gepackt

        cco2gra.setData(co2list[:co2graposi])  # graph wird mitder aktualisiereten datenliste erzeugt
    def updatelaut(daten):
        global lautlist, lautgraposi

        lautlist[lautgraposi] = daten[4]  # zufälliger wert für die näcghste stelle
        lautgraposi += 1  # erhöh die stelle
        if lautgraposi >= lautlist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = lautlist  # datenliste wird in temp gespeicher
            lautlist = np.empty(lautlist.shape[0] * 2)  # die datenlistenlänge wird verdoppelt
            lautlist[:tmp.shape[0]] = tmp  # daten werden in die längere liste gepackt

        clautgra.setData(lautlist[:lautgraposi])  # graph wird mitder aktualisiereten datenliste erzeugt
    def updatehell(daten):
        global helllist, hellgraposi
        helllist[hellgraposi] = daten[5]  # zufälliger wert für die näcghste stelle
        hellgraposi += 1  # erhöh die stelle
        if hellgraposi >= helllist.shape[0]:  # wenn die listenlänge ereicht wird
            tmp = helllist  # datenliste wird in temp gespeicher
            helllist = np.empty(helllist.shape[0] * 2)  # die datenlistenlänge wird verdoppelt
            helllist[:tmp.shape[0]] = tmp  # daten werden in die längere liste gepackt

        chellgra.setData(helllist[:hellgraposi])  # graph wird mitder aktualisiereten datenliste erzeugt

    def update():  # führt das uptadet aus
        updatelaut(daten)
        updatehell(daten)
        updatetempce(daten)
        updateluftfeucht(daten)
        updateco2(daten)



    timer = pg.QtCore.QTimer()  # timer wird qt timer klasse zugewiesen
    timer.timeout.connect(update)  # immer bei derpause wird update ausgeführt
    timer.start(1000)  # timer aller (ms)
    pg.exec()
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
                    i = ' '     # möglichst keine Leerzeichen (was ist noich offen)
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
        speicher.write('') # auf göße anpassen
        speicher.close()
        return dateiname

    def connect():
        """ stellt die Verbindung zu serial port auf"""
        ser = serial.Serial('COM3', baudrate=115200, timeout=1)
        return ser


    def datenverarbeitung():
        global daten

        def datenabruf():
            """ empfängt die daten die vom esp32 gesendet werden, kombiniert sie mit der zeit
            und speicher die in der oben erstllen .txt datei"""

            data = ser.readline().decode('ascii')
            datalist = data.split(' ')
            time = datetime.datetime.now().strftime("%Y-%m-%d/%H:%M:%S")

            tempce = float(datalist[0])
            luftfeucht = float(datalist[1])
            co2 = float(datalist[2])
            laut = float(datalist[3])
            hell = float(datalist[4])

            datentu = time, tempce, luftfeucht, co2, laut, hell

            return datentu




        def speichern(dateiname, daten):
            """öffnet die datei schreibt die Daten in die .txt und schließt diese wieder"""
            datenstr = str(daten[0]) + ' ' + str(daten[1]) + ' ' + str(daten[2]) + ' ' + str(daten[3]) + ' ' + str(daten[4]) + ' ' + str(daten[5])
            speicher = open(dateiname, "a")
            speicher.write('\n')
            speicher.write(str(datenstr))
            speicher.close()

        while True:
            daten = datenabruf()

            print(daten)


            speichern(dateiname, daten)


    dateiname = dateianlegen()
    ser = connect()
    datenverarbeitung()


class datenthread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("Starting " + self.name)
        datenzeugs()
        print("Exiting " + self.name)


class grafikthread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("Starting " + self.name)
        grafikdingens()
        print("Exiting " + self.name)


# Create new threads
thread1 = datenthread(1, "datenthread")
thread2 = grafikthread(2, "grafikthread")

# Start new Threads
thread1.start()
thread2.start()
thread1.join()
thread2.join()
print("Exiting Main Thread")