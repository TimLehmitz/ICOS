from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

# Create the icon
icon = QIcon("icon.png")

clipboard = QApplication.clipboard()
dialog = QColorDialog()

def copy_color_hex():
    if dialog.exec_():
        color = dialog.currentColor()
        clipboard.setText(color.name())

def copy_color_rgb():
    if dialog.exec_():
        color = dialog.currentColor()
        clipboard.setText("rgb(%d, %d, %d)" % (
            color.red(), color.green(), color.blue()
        ))

def copy_color_hsv():
    if dialog.exec_():
        color = dialog.currentColor()
        clipboard.setText("hsv(%d, %d, %d)" % (
            color.hue(), color.saturation(), color.value()
        ))

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

# Create the menu
menu = QMenu()
action1 = QAction("Hex")
action1.triggered.connect(copy_color_hex) #wenn gedrückt führew command aus
menu.addAction(action1)

action2 = QAction("RGB")
action2.triggered.connect(copy_color_rgb) #wenn gedrückt führew command aus
menu.addAction(action2)

action3 = QAction("HSV")
action3.triggered.connect(copy_color_hsv) #wenn gedrückt führew command aus
menu.addAction(action3)

quit = QAction("Quit") #quit ist eine action wird angezeigt mit namen quit
quit.triggered.connect(app.quit) #wenn auf quit gedrückt dann schließe (quit)
menu.addAction(quit) #zum menü ein schlater mit quit

# Add the menu to the tray
tray.setContextMenu(menu)

app.exec_()
