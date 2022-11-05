
import time
import random
import esp32

x = 0
luftfeucht = 50
tempfa = 50
co2 = 800
laut = 50
hell = 50

while x < 100:
    tempfa = esp32.raw_temperature()
    tempce = (tempfa - 32) * 5 / 9
    luftfeucht = luftfeucht + random.randint(-1, 1)
    co2 = co2 + random.randint(-50, 50)
    laut = laut + random.randint(-5, 5)
    hell = hell + random.randint(-5, 5)

    print(tempce, luftfeucht, co2, laut, hell)
    x = x + 1
    time.sleep(1)