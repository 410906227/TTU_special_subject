import argparse
import time
from collections import deque
import cv2
import imutils
import numpy as np
from imutils.video import VideoStream
import ImageChops

# 命令列引數
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to video")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

# 綠色球的HSV色域空間範圍
colorLower = (0,  0, 200)
colorUpper = (180, 50, 255)
#colorLower = ( 0,  0, 221) # greenLower = (29, 86, 6)
#colorUpper = (180, 30, 255) # greenUpper = (64, 255, 255)
# greenLower = (29, 86, 6)
# greenUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])

# 判斷是讀入的影片檔案，還是攝像頭實時採集的，這裡作區分是因為兩種情況下後面的有些操作是有區別的
if args.get("video", None) is None:
    useCamera = True
    print("video is none, use camera...")
    vs = VideoStream(src=0).start()
else:
    useCamera = False
    vs = cv2.VideoCapture(args["video"])
    time.sleep(2.0)

    frame0 = vs.read()

while True:
    frame = vs.read()
    
    # 攝像頭返回的資料格式為(幀資料)，而從影片抓取的格式為(grabbed, 幀資料)，grabbed表示是否讀到了資料
    frame = frame if useCamera else frame[1]

    # 對於從影片讀取的情況，frame為None表示資料讀完了
    if frame is None:
        break

    diff = ImageChops.difference(frame, frame0)
    frame0 = frame.copy()
    frame = diff

    # resize the frame(become small) to process faster(increase FPS)
    #frame = imutils.resize(frame, width=600)
    # blur the frame to reduce high frequency noise, and allow
    # us to focus on the structural objects inside the frame
    # 通過高斯濾波去除掉一些高頻噪聲，使得重要的資料更加突出
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    # convert frame to HSV color space
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # handles the actual localization of the green ball in the frame
    # inRange的作用是根據閾值進行二值化:閾值內的畫素設定為白色(255)，閾值外的設定為黑色(0)
    mask = cv2.inRange(hsv, colorLower, colorUpper)

    # A series of erosions and dilations remove any small blobs that may be left on the mask
    # 腐蝕(erode)和膨脹(dilate)的作用:
    # 1. 消除噪聲;
    # 2. 分割(isolate)獨立的影象元素，以及連線(join)相鄰的元素;
    # 3. 尋找影象中的明顯的極大值區域或極小值區域
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # 尋找輪廓，不同opencv的版本cv2.findContours返回格式有區別，
    # 所以呼叫了一下imutils.grab_contours做了一些相容性處理
    
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use it to compute the minimum enclosing circle
        # and centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        # 對於01二值化的影象，m00即為輪廓的面積, 一下公式用於計算中心距
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame, then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

        pts.appendleft(center)

    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # compute the thickness of the line and draw the connecting line
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(300) & 0xFF

    if key == ord("q"):
        break

if useCamera:
    vs.stop()
else:
    vs.release()

cv2.destroyAllWindows()
