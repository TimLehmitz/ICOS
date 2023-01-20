'''Diese Programm dient zur Kalibrierung des Grove Loudness Sensors'''
from SensorBibliothek import *
from machine import *

sensorLaut = GroveLoudnessSensor()
messwert   = 0
kalibrierungsWert = 0
zaehler = 1

datei = open('Kalibreirungswerte.txt', 'r')
for i in range(30*10):
    for i in range(5):
        messwert = sensorLaut.lesen() + messwert
        sleep_ms(200)
    print(messwert/(5*zaehler))
    zaehler = 1 + zaehler
kalibrierungsWert = messwert / (5 * 30*10)
print(kalibrierungsWert)
#datei.write('\r\nKalibrierungswert: ')
#datei.write(str(kalibrierungsWert))