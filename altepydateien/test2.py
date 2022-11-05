# -*- coding: utf-8 -*-
"""
Various methods of drawing scrolling plots.
"""

import random
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('pyqtgraph example: Scrolling Plots')


# 2) Allow data to accumulate. In these examples, the array doubles in length
#    whenever it is full.
win.nextRow()

p4 = win.addPlot()
# Use automatic downsampling and clipping to reduce the drawing load

p4.setDownsampling(mode='peak')

p4.setClipToView(True)



curve4 = p4.plot()

data3 = np.empty(100)
ptr3 = 0


def update2():
    global data3, ptr3
    data3[ptr3] = random.randint(1,5) #zufälliger wert für die näcghste stelle
    ptr3 += 1   #erhöh die stelle
    if ptr3 >= data3.shape[0]: #wenn die listenlänge ereicht wird
        tmp = data3 # datenliste wird in temp gespeicher
        data3 = np.empty(data3.shape[0] * 2) # die datenlistenlänge wird verdoppelt
        data3[:tmp.shape[0]] = tmp #daten werden in die längere liste gepackt

    curve4.setData(data3[:ptr3])    # graph wird mitder aktualisiereten datenliste erzeugt

def update():   #führt das uptadet aus
    update2()


timer = pg.QtCore.QTimer() #timer wird qt timer klasse zugewiesen
timer.timeout.connect(update) #immer bei derpause wird update ausgeführt
timer.start(1000)    #timer aller (ms)

if __name__ == '__main__':
    pg.exec()