'''
Dieses Programm wurde für die BELL, 'Erstellen eines Raumklimamesssytems' von Derik Fritz-Pester und Tim Lehmitz,
in Informatik am Gothold-Ephraim-Lessing-Gymnasium-Kamenz
konzipiert.
Micorpython-Version: 1.17
Asugabe: Temperatur, Druck, CO2-Gehalt, Lautstaerke, Helligkeit
'''
# Importieren der Bibliotheken
from SensorBibliothek import *
import time

#Definieren der Objekte zu den Klassen der Sensoren
sensorMulti       = EE895()
sensorHelligkeit  = BH1750()
sensorLautstaerke = GroveLoudnessSensor()

#definieren der Variablen für die Ausgabewerte
helligkeit        = 250
lautstaerke       = 24
co2               = 0
temperatur        = 0
druck             = 0

#Variablen zur Bildung der arithmetischen Mittel für ein wählbares Zeitintervall
VERZOEGERUNGSZEIT_SEKUNDEN = 2
#AUFLOESUNG nicht höher als 8
AUFLOESUNG                 = 9                                         

while True:
    lautstaerkeRechnung       = 0
    
    co2         = sensorMulti.messenCO2()                                            #Messvorgang für den EE895 Sensor aus der SensorBibliothek
    temperatur  = sensorMulti.messenTEMP()
    druck       = sensorMulti.messenP()
    
    #Anpassung an Messzeit vom BH1750() mindestens 120ms, falls AUFLOESUNG>8
    if AUFLOESUNG > 8:
        AUFLOESUNG = 8
    
    #Messreihe zur Glättung der Lautstaerke- und Helligkeitswerte
    for zeit in range(VERZOEGERUNGSZEIT_SEKUNDEN):
        
        helligkeitRechnung        = 0
        
        for aufloesung in range(AUFLOESUNG):
            helligkeitRechnung = sensorHelligkeit.messen(2) + helligkeitRechnung
            lautstaerkeRechnung = sensorLautstaerke.messen() + lautstaerkeRechnung
            time.sleep_ms(int(1000 / AUFLOESUNG))
        
        helligkeit  = helligkeitRechnung / (AUFLOESUNG )
        
        print(round(temperatur, 1), int(druck), co2, int(lautstaerke), round(helligkeit, 1))                       #Ausgabe der Daten über printbefehl an GUI -> Reihenfolge durch GUI Progtramm bestimmt
    lautstaerke = lautstaerkeRechnung / (AUFLOESUNG * VERZOEGERUNGSZEIT_SEKUNDEN)
