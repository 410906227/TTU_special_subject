#!/usr/bin/env python
# coding: utf-8

import cv2
import sys
import pyautogui
import os
import time;

cap = cv2.VideoCapture(sys.argv[1])
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print('Frame count:', frame_count)

if (cap.isOpened()== False):
  print("Error opening video stream or file")

ii = 0
direction = 1
keyb = ' '
frame = ""
speed = 300
co = (0, 255, 0) # BGR

x1 = y1 = x2 = y2 = -1
xx = yy = ww = hh = -1
f1 = f2 = -1

def onclick(event, x, y, flags, param):
    global x1, y1, x2, y2, xx, yy, ww, hh, frame

    #if x < xx or y < yy or x >= xx+ww or y >= yy+hh:
    #    return
    if event == cv2.EVENT_LBUTTONDOWN:
        print("CLK-left :", x, y)
        if x1 < 0:
            x1 = x
            y1 = y
        elif x2 < 0:
            x2 = x
            y2 = y
        else:
            d1 = abs(x1-x)+abs(y1-y)
            d2 = abs(x2-x)+abs(y2-y)
            if d1 < d2:
                x1 = x
                y1 = y
            else:
                x2 = x
                y2 = y

    #elif event == cv2.EVENT_RBUTTONUP:
    #    print("CLK-right:", x, y)
    #    x2 = x
    #    y2 = y

    if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
        if x1 > x2:
            x = x1
            x1 = x2
            x2 = x
        if y1 > y2:
            y = y1
            y1 = y2
            y2 = y

def cron_image():
    global cap, x1, y1, x2, y2, f1, f2

    ts = str(int(time.time()))

    #cron_image
    action = input("Enter an action: ")
    dir = action+"_"+ts+"_"+str(f1)+"-"+str(f2)
    path = "data/source_images3/"+dir
    if not os.path.isdir(path):
        os.mkdir(path)

    for j in range(f1, f2+1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, j)
        ret, frame = cap.read()
        ROI = frame[y1:y2, x1:x2]
        cv2.imwrite(path+"/"+"{:05d}".format(j)+".jpg", ROI) # Save frame as JPG file

    with open("data/source_images3/valid_images.txt", "a+") as file:
        file.write(dir+"\n")
        file.write(str(f1)+" "+str(f2)+"\n\n")

    print("action write at path="+path)

while cap.isOpened():
    # Capture frame-by-frame

    print("**", ii)
    if ii < 0 or ii >= frame_count:
        while True:
            keyb = cv2.waitKey(100) & 0xFF    # wait_Key(msec)
            if keyb == ord(' '):
                direction = 1 if ii < 0 else -1
                ii = 0 if ii < 0 else frame_count-1
                break
            elif keyb == ord('q'):
                break
    if keyb == ord('q'):
        break

    cap.set(cv2.CAP_PROP_POS_FRAMES, ii)
    ret, frame = cap.read()
    if ret != True:
        break

    #cv2.putText(frame, str(ii)+" : "+str(speed),
    #           (xx+20, yy+hh-260), fontScale=1.5, fontFace=cv2.FONT_HERSHEY_PLAIN,
    #           color=(255, 255, 255), thickness=2)

    sf1 = str(f1) if f1 >=0 else ""
    sf2 = str(f2) if f2 >=0 else ""

    sx1 = str(x1) if x1 >=0 else ""
    sy1 = str(y1) if y1 >=0 else ""
    sx2 = str(x2) if x2 >=0 else ""
    sy2 = str(y2) if y2 >=0 else ""
    cv2.putText(frame, "["+sf1+" , "+sf2+"] - ("+sx1+","+sy1+" , "+sx2+","+sy2+")  " + str(ii)+" , "+str(speed), (20, 20), fontScale=1.5, fontFace=cv2.FONT_HERSHEY_PLAIN, color=(255, 255, 255), thickness=2)

    if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
        cv2.rectangle(frame, (x1, y1), (x2, y2), co, 2, cv2.LINE_AA)

    if x1 > 0 and y1 > 0:
        cv2.circle(frame, (x1, y1), 3, co, 2)
    if x2 > 0 and y2 > 0:
        cv2.circle(frame, (x2, y2), 3, co, 2)

    #cv2.imwrite("data/"+"{:05d}".format(ii)+".jpg", frame) # Save frame as JPG file
    ii = ii+direction

    # Display the resulting frame
    cv2.imshow('Frame',frame)

    cv2.setMouseCallback("Frame", onclick)

    if xx < 0:
        r = cv2.getWindowImageRect('Frame')
        xx = r[0]
        yy = r[1]
        ww = r[2]
        hh = r[3]
        print("***", xx, yy, ww, hh) # *** (0, 254, 1280, 720) = (x, y, w, h)

    # Press Q on keyboard to  exit
    keyb = cv2.waitKey(speed) & 0xFF    # wait_Key(msec)
    if keyb == ord('q'):
        break

    elif keyb == ord('c'):
        x1 = y1 = x2 = y2 = -1
        f1 = f2 = -1

    elif keyb == ord('b'):
        direction = -1 if direction == 1 else 1

    elif keyb == ord('+') or keyb == ord('='):
        if speed > 10:
            speed = speed - 10

    elif keyb == ord('-'):
        if speed < 1000:
            speed = speed + 10

    elif keyb == ord('a'):
        f1 = ii
    elif keyb == ord('z'):
        f2 = ii

    elif keyb == ord('i'):
        print("~~~~")
        ii = int(input("Enter a number: "))

    elif keyb == ord('p') or keyb == ord(' '):
        while True:
            #pos = pyautogui.position()
            #print("**", pos)

            keyb = cv2.waitKey(100) & 0xFF    # wait_Key(msec)
            if keyb == ord(' '):
                break
            elif keyb == ord('c'):
                x1 = y1 = x2 = y2 = 0
            elif keyb == ord('b'):
                direction = -1 if direction == 1 else 1
                break
            elif keyb == ord('a'):
                f1 = ii
            elif keyb == ord('z'):
                f2 = ii
            elif keyb == ord('x'):
                if f1 >= 0 and f2 >= 0:
                    cron_image()
                    f1 = f2 = -1
                    #break
            elif keyb == 82:
                print("up", keyb)
                direction = -1
                ii = ii-1
                cap.set(cv2.CAP_PROP_POS_FRAMES, ii)
                ret, frame = cap.read()
                cv2.imshow('Frame',frame)
            elif keyb == 84:
                print("down", keyb)
                direction = 1
                ii = ii+1
                cap.set(cv2.CAP_PROP_POS_FRAMES, ii)
                ret, frame = cap.read()
                cv2.imshow('Frame',frame)

    elif keyb == 82:
        print("UP", keyb)
        direction = -1

    elif keyb == 84:
        print("DOWN", keyb)
        direction = 1

# When everything done, release the video capture object
cap.release()
# Closes all the frames
cv2.destroyAllWindows()
