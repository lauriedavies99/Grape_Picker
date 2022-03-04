import cv2
import numpy as np

def empty(a):
    pass

def getContours(img):
    contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area>600:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,0.02*peri,True)
            objCor = len(approx)
            x,y,w,h = cv2.boundingRect(approx)
            cv2.rectangle(imgContour,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.rectangle(imgContour,(int((x+(w/2))+(w/8)),y),(int((x+(w/2))-(w/8)),int(y-(h/6))),(0,0,255),2)




path = 'Resources/Grapes3.png'
cv2.namedWindow("TrackBars")
cv2.resizeWindow("TrackBars",640,240)
cv2.createTrackbar("Hue Min","TrackBars",0,179,empty)
cv2.createTrackbar("Hue Max","TrackBars",38,179,empty)
cv2.createTrackbar("Sat Min","TrackBars",35,255,empty)
cv2.createTrackbar("Sat Max","TrackBars",255,255,empty)
cv2.createTrackbar("Val Min","TrackBars",117,255,empty)
cv2.createTrackbar("Val Max","TrackBars",255,255,empty)

while True:
    img = cv2.imread(path)
    imgContour = img.copy()
    Resize_img = cv2.resize(img,(400,400))
    imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    Resize_HSV = cv2.resize(imgHSV,(400,400))

    h_min = cv2.getTrackbarPos("Hue Min","TrackBars")
    h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")
    s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")
    s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")
    v_min = cv2.getTrackbarPos("Val Min", "TrackBars")
    v_max = cv2.getTrackbarPos("Val Max", "TrackBars")

    lower = np.array([h_min,s_min,v_min])
    upper = np.array([h_max,s_max,v_max])
    mask = cv2.inRange(imgHSV,lower,upper)
    Resize_mask = cv2.resize(mask,(400,400))
    imgResult = cv2.bitwise_and(img,img,mask=mask)

    imgGray = cv2.cvtColor(imgResult,cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(7,7),1)
    imgCanny = cv2.Canny(imgBlur,50,50)
    getContours(imgCanny)

    cv2.imshow("Result",img)
    cv2.imshow("Blur",imgContour)
    cv2.waitKey(1)
