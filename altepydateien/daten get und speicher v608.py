#die schleichfe is noch im daten abruf und speichern ausserhalb
from threading import Thread
import serial
import datetime
import time


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
    speicher.write('time,   tempce, luftfeucht, co2,    laut,   hell')
    speicher.close()
    return dateiname


dateiname = dateianlegen()


def connect():
    """ stellt die Verbindung zu serial port auf"""
    ser = serial.Serial('COM4', baudrate=115200, timeout=1)
    return ser


ser = connect()


def datenabruf():
    """ empfängt die daten die vom esp32 gesendet werden, kombiniert sie mit der zeit
    und speicher die in der oben erstllen .txt datei"""
    while True:
        data = ser.readline().decode('ascii')
        datalist = data.split(' ')
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        tempce = float(datalist[0])
        luftfeucht = float(datalist[1])
        co2 = float(datalist[2])
        laut = float(datalist[3])
        hell = float(datalist[4])
        datentu = time, tempce, luftfeucht, co2, laut, hell
        return datentu


datentu = datenabruf()

def speichern(dateiname, daten):
    """öffnet die datei schreibt die Daten in die .txt und schließt diese wieder"""
    speicher = open(dateiname, "a")
    speicher.write('\n')
    speicher.write(str(daten))
    speicher.close()

speichern(dateiname, datentu)


#if __name__ == '__main__':
 #   Thread(target = datenabruf()).start()
  #  Thread(target = ).start()
