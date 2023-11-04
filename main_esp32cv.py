import asyncio
import cv2 # pip install opencv-python
import cvzone #pip install cvzone
from cvzone.HandTrackingModule import HandDetector
import serial  #pip install pyserial
import re

from icecream import ic # pip install icecream

port = '/dev/ttyUSB0'

try:
    esp32 = serial.Serial(port, 115200, timeout=1)
    print("successful connected ")
except Exception:
    print(" problem with serial communication")

cap = cv2.VideoCapture(0)

cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.7)

aux = cv2.imread("images/logo.png")
aux = cv2.resize(aux, (256,256))
on = cv2.imread("images/onled.png")
on = cv2.resize(on, (256,256))
off = cv2.imread("images/offled.png")
off = cv2.resize(off, (256,256))
ox, oy = 800, 250

async def weather_task():

    while True:
        data = esp32.readline()
        print(data.decode('utf'))
        recv = data.decode('utf')
        ic(type(recv))
        ic('recv: ', recv)
        ic(re.search("x", str(recv)))
        if len(recv) != 0 and re.search("x", recv) != None:
            sensors = recv.split("x")
            print("temp: ", float(sensors[1]), "hum :", float(sensors[0]))
            print(sensors)
            print("--------")
            return float(sensors[0]), float(sensors[1])



async def main(sensor):
    while True:
        sucess, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, draw=False, flipType=False)

        # ---------- user interface for showing humidity and temperature  -----------
        cv2.rectangle(img, (150, 200), (710, 600), (0, 255, 255), 3 )
        img, bbox0 = cvzone.putTextRect(img, "Living Room", [170, 250], 2, colorR=(0,255,255), colorT=(0, 0, 0), offset=3, font=cv2.FONT_HERSHEY_DUPLEX)

        img, bbox2 = cvzone.putTextRect(img, f"temperature: {float(sensor[0])} C", [200, 400], 1, border=2,
                                        colorR=(0, 255, 255), colorT=(0, 0, 0), font=cv2.FONT_HERSHEY_DUPLEX)
        img, bbox3 = cvzone.putTextRect(img, f"humidity: {float(sensor[1])} %", [200, 500], 1, border=2,
                                        colorR=(0, 255, 255), colorT=(0, 0, 0), font=cv2.FONT_HERSHEY_DUPLEX)

        # ---------- user interface to control lamp  -----------
        img, bbox = cvzone.putTextRect(img, "TURN ON", [200, 100], 2, 2, offset=50, border=5)
        img, bbox1 = cvzone.putTextRect(img, "TURN OFF", [500, 100], 2, 2, offset=50, border=5)
        h, w, _ = on.shape

        img[oy: oy + h, ox:ox + w] = aux

        # -------------------- backend : handle events   -------
        ic("humidity-temp: ", sensor)

        if hands:
            lmlist = hands[0]['lmList']        #take fisrt hand available

            cursor = lmlist[8]
            top_index = lmlist[8][0:2]     #top index(x1, y1)
            top_major = lmlist[12][0:2] # top majeur (x2, y2)
            length, info, img = detector.findDistance(top_index, top_major, img, scale=0)

            x1, y1, x2, y2 = bbox  # turn on bbox or area
            x3, y3, x4, y4 = bbox1 # turn off bbox or area

            if length < 70:  #condition to consider that you click
                print("you clicked")

            # if ox < cursor[0] < ox + w and oy < cursor[1] < oy + h:  #condition to consider that you click button
            #     print("inside Image or area of led state")

                if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:      # you are in the turn on button area
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)
                    esp32.write(bytes('1', 'utf-8')) # send command to turn on the lamp in the serial port
                    img[oy: oy + h, ox:ox + w] = on # update image
                    print("turn on")

                if x3 < cursor[0] < x4 and y3 < cursor[1] < y4:    #you are in the turn off button area
                    cv2.rectangle(img, (x3, y3), (x4, y4), (0, 0, 255), cv2.FILLED)
                    esp32.write(bytes('0', 'utf-8'))  # send command to turn off the lamp in the serial port
                    img[oy: oy + h, ox:ox + w] = off  # update image
                    print("turn off")


        esp32.flush()
        cv2.imshow("AR SCREEN", img)
        cv2.waitKey(1)


# Create an event loop
loop = asyncio.get_event_loop()

returned_value = loop.run_until_complete(weather_task())
loop.run_until_complete(main(returned_value))
