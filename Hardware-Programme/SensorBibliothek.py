'''
Diese Bibliothek wurde für die BELL, 'Erstellen eines Raumklimamesssytems' von Derik Fritz-Pester und Tim Lehmitz,
in Informatik am Gothold-Ephraim-Lessing-Gymnasium-Kamenz
konzipiert.
Micorpython-Version: 1.17
Sie fügt die Klassen für die einzelnen Sensoren hinzu, welche lauten:
    GroveLoudnessSensor()
    BH1750()
'''
#Importieren der benötigten Bibliotheken
from machine import *
from time import*
from math import*

class GroveLoudnessSensor(object):
    '''
    Klasse für den Grove Loudness Sensor.
    Er misst den Schalldruckpegel oder auch Lautstaerke genannt.
    Sie fügt folgende Funktionen hinzu:
        lesen()
        messen()  
    '''
    def __init__(self):
        '''Initialisierung der Klasse groveLoudnessSensor und des Sensors''' 
        
        self.Sensor = ADC(Pin(34))               #Pin für Datenabfrage wird festgelegt
        self.Sensor.atten(ADC.ATTN_0DB)          #Spannungsumfang bei Abfrage von 0V - 1V 
        self.Sensor.width(ADC.WIDTH_10BIT)       #Datendichte auf 10Bit, d.h. von 0-1023 festgelegt

    def lesen(self):
        '''Die Daten des Sensors werden gelesen'''
        self.wert = self.Sensor.read()
        return self.wert
    
    def messen(self):
        '''Die Daten werden mit Umwandlung in der Variable dB ausgegeben'''
        self.lesen()
        #regressierte Funktionen für Grove Loudness Sensor mit Umrechnung in dB
        if self.wert <= 258.98:
            self.dB = 1.8593*pow(e, 0.0135*self.wert)
        
        elif 258.98 < self.wert < 991.08:
            self.dB = 16.777*log(self.wert)-31.884
        
        else:
            self.dB = 62.396*log(self.wert)-346.6
        
        return self.dB

class BH1750(object):
    '''
    Klasse für den Helligkeitsssensor BH1750.
    Sie fügt folgende Funktionen hinzu:
        lesenH1()
        messenH1()
    '''
    #Definieren von einigen Konstanten aus dem Datenblatt
    POWER_AN  = 0x01
    POWER_AUS = 0x00
    RESET     = 0x07
    ADDRESSE  = 0x23
    #Modus 1 der konstant misst, Minimalwert ist 1 lux, Messungzeit = 120ms
    CONTINUOUSLY_HIGH_RESOLUTION_MODE_1 = 0x2710
    #Modus 2 der konstant misst, Minimlawert ist 0,5 lux, Messzeit = 120ms
    CONTINUOUSLY_HIGH_RESOLUTION_MODE_2 = 0x2711
    

    
    def __init__(self):
        '''
        Es findet die initialisierung der I2C Verbindung statt.
        Weiter wichtige Variablen und Listen für die Klasse werden definiert.
        '''
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(23))
        self.highByte          = 0
        self.lowByte           = 0
        self.listeHighByte     = []
        self.listeLowByte      = []
        self.listeMessung      = []
        self.listeLowHigh      = []
        self.zaehlerFusion     = 0
        self.zaehlerUmrechnung = 0
        self.luxWert           = 0
        self.luxWertRechnung   = 0
        self.MODUS_LESEN       = 0
        self.MODUS             = 0

    def lesen(self, MODUS_LESEN):
        '''
        Die Daten werden mit dem ausgewählten Modus gelesen.
        zu übergebender Funktionsparameter: MODUS_LESEN
        Dafür wird eine Liste mit dem gesamten Datensatz in Dezimalzahl zurückgegeben.
        '''
        self.messung       = self.i2c.readfrom_mem(self.ADDRESSE, MODUS_LESEN , 2)
        self.listeMessung  = list(self.messung)
        return self.listeMessung

    
    
    def messen(self, MODUS):
        '''
        Die Daten werden mit gelesen und aufbereitet.
        zu übergebender Funktionsparameter: MODUS --> 1 ; 2
        Die Ausgabe erfolgt in der Einheit lux als Integer.
        '''
        self.luxWert         = 0
        self.luxWertRechnung = 0
        self.listeLowHigh    = []
        
        if MODUS == 'H1' or  MODUS == 1:                                                   # Auswahlverfahren des Modi
            self.lesen(self.CONTINUOUSLY_HIGH_RESOLUTION_MODE_1)
        
        elif MODUS == 'H2' or MODUS == 2:
            self.lesen(self.CONTINUOUSLY_HIGH_RESOLUTION_MODE_2)
        
        else:
            print('ERROR: Es gibt diesen Modus nicht.')
            

        self.listeHighByte   = list(bin(self.listeMessung[0]))                              #Erstellen einer High Byte Liste für Datenverarbeitung(siehe Datenblatt)
        for i in range(2):                                                                  #Löschen unwichtiger Listenelemente [0,b] - verbleibende Ausagabeelemente im string Format
            del self.listeHighByte[0]
        if len(self.listeHighByte) < 8:                                                     #Prüfung ob Liste auf Byte Größe
            for l in range(8-len(self.listeHighByte)):                 
                self.listeHighByte.insert(0, 0)                                             #Auffüllen der Liste vor den Ausgabeelementen mit 0
        self.listeHighByte.reverse()                                                        #Umdrehen der Liste für weiter Verarbeitung
        
        self.listeLowByte    = list(bin(self.listeMessung[1]))                              #analoges Verfahren wie High Byte, hier mit Low Byte
        for i in range(2):
            del self.listeLowByte[0]
        if len(self.listeLowByte) < 8:
            for l in range(8-len(self.listeLowByte)):
                self.listeLowByte.insert(0, 0)
        self.listeLowByte.reverse()
        
        for self.zaehlerFusion in range(16):                                                 #Die beiden Byte Listen werden nach dem Schema 'Low Byte - High Byte' zusammengefügt - Resultat 2 Byte Liste
            if self.zaehlerFusion < 8:                                                       #Element 0 - 7 von Low Byte Liste hinzugefügt
                self.listeLowHigh.append(self.listeLowByte[self.zaehlerFusion])
                self.zaehlerFusion = self.zaehlerFusion+ 1 
            elif self.zaehlerFusion > 7:                                                      #Elemente 8 - 15 von High Byte Liste hinzugefügt
                self.listeLowHigh.append(self.listeHighByte[self.zaehlerFusion-8])
                self.zaehlerFusion = self.zaehlerFusion+ 1                          
        
        for self.zaehlerUmrechnung in range(16):                                              #Anwendung Umrechnungsformel - jedes Listenelement betrachtet
            if int(self.listeLowHigh[self.zaehlerUmrechnung]) == 1:                           #Prüfung ob Listenelement Wert 1
                self.luxWertRechnung = pow(2, self.zaehlerUmrechnung) + self.luxWertRechnung  
                self.zaehlerUmrechnung = self.zaehlerUmrechnung + 1
            else:
                pass
        self.luxWert = self.luxWertRechnung / 1.2                                             #Umrechnung
        
        return self.luxWert                                                                   #Rückgabe des Wertes in lux

class EE895(object):
    '''
    Klasse für den EE895-M16HV2 zum lesen der Werte.
    Sie fügt folgende Funktionen hinzu:
    
    '''
    def __init__(self):
        '''
        Es findet die initialisierung der I2C Verbindung statt.
        '''
        self.i2c2            = I2C(1, scl = Pin(26), sda = Pin(27), freq = 100000)
        self.bytearrayEE895 = 0
        self.co2            = 0
        self.temp           = 0
        self.p              = 0
        
    def lesen(self):
        '''
        Liest den Wert der Messung und gibt ihn als bytearray aus.
        Das Messintervall ist standartmäßig auf 15 Sekunden eingestellt.
        '''
        self.i2c2.writeto(0x5E, b'\x00')
        self.bytearrayEE895  = self.i2c2.readfrom(0x5E, 12)
        return self.bytearrayEE895
        
    
    def messenCO2(self):
        '''
        Die Funktion liest die Daten für den CO2-Wert aus und rechnet diese um.
        Die Ausgabe erfolg in ppm (particle per million).
        Nutzt die Funktion lesen().
        '''
        
        self.lesen()
        self.co2 =  self.bytearrayEE895[0] << 8 | self.bytearrayEE895[1]
        
        return self.co2
    
    def messenTEMP(self):
        '''
        Die Funktion liest die Daten für den Temperatur-Wert aus und rechnet diese um.
        Die Ausgabe erfolg in Grad Celsius.
        Nutzt die Funktion lesen().
        '''
        
        self.lesen()
        self.temp = (self.bytearrayEE895[2] << 8 | self.bytearrayEE895[3]) / 100
        
        return self.temp
    
    
    def messenP(self):
        '''
        Die Funktion liest die Daten für den Druck-Wert aus und rechnet diese um.
        Die Ausgabe erfolg in mbar (milli bar).
        Nutzt die Funktion lesen().
        '''
        
        self.lesen()
        self.p = (self.bytearrayEE895[6] << 8 | self.bytearrayEE895[7]) / 10
        
        return self.p
        