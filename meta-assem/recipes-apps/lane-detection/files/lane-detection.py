import cv2
import numpy as np

############################### Functions (unchanged)
def thresholding(img):
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lowerWhite = np.array([0, 0, 200])  # Adjusted for better white detection
    upperWhite = np.array([255, 30, 255])
    maskWhite = cv2.inRange(imgHsv, lowerWhite, upperWhite)
    return maskWhite

def warpImg(img, points, w, h, inv=False):
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    matrix = cv2.getPerspectiveTransform(pts2, pts1) if inv else cv2.getPerspectiveTransform(pts1, pts2)
    imgWarp = cv2.warpPerspective(img, matrix, (w, h))
    return imgWarp

def nothing(a):
    pass

def initializeTrackbars(intialTracbarVals, wT=480, hT=240):
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 360, 240)
    cv2.createTrackbar("Width Top", "Trackbars", intialTracbarVals[0], wT//2, nothing)
    cv2.createTrackbar("Height Top", "Trackbars", intialTracbarVals[1], hT, nothing)
    cv2.createTrackbar("Width Bottom", "Trackbars", intialTracbarVals[2], wT//2, nothing)
    cv2.createTrackbar("Height Bottom", "Trackbars", intialTracbarVals[3], hT, nothing)

def valTrackbars(wT=480, hT=240):
    widthTop = cv2.getTrackbarPos("Width Top", "Trackbars")
    heightTop = cv2.getTrackbarPos("Height Top", "Trackbars")
    widthBottom = cv2.getTrackbarPos("Width Bottom", "Trackbars")
    heightBottom = cv2.getTrackbarPos("Height Bottom", "Trackbars")
    points = np.float32([(widthTop, heightTop), (wT-widthTop, heightTop),
                         (widthBottom, heightBottom), (wT-widthBottom, heightBottom)])
    return points

def drawPoints(img, points):
    for x in range(0, 4):
        cv2.circle(img, (int(points[x][0]), int(points[x][1])), 15, (0, 0, 255), cv2.FILLED)
    return img

def getHistogram(img, display=False, minPer=0.1, region=1):
    if region == 1:
        histValues = np.sum(img, axis=0)
    else:
        histValues = np.sum(img[img.shape[0]//region:, :], axis=0)

    maxValue = np.max(histValues)
    minValue = minPer * maxValue
    indexArray = np.where(histValues >= minValue)
    basePoint = int(np.average(indexArray)) if indexArray[0].size > 0 else img.shape[1]//2

    if display:
        imgHist = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
        for x, intensity in enumerate(histValues):
            color = (255, 0, 255) if intensity > minValue else (0, 0, 255)
            y_start = img.shape[0]
            y_end = img.shape[0] - int(intensity // 255 // region)  # Critical fix
            cv2.line(imgHist, (x, y_start), (x, y_end), color, 1)
        cv2.circle(imgHist, (basePoint, img.shape[0]), 20, (0, 255, 255), cv2.FILLED)
        return basePoint, imgHist
    return basePoint

def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver
######################## Main
curveList = []
avgVal = 10

def getLaneCurve(img, display=2):
    imgCopy = img.copy()
    imgResult = img.copy()
    
    ### STEP 1 – Thresholding
    imgThres = thresholding(img)
    
    ### STEP 2 – Warping
    hT, wT, c = img.shape
    points = valTrackbars()
    imgWarp = warpImg(imgThres, points, wT, hT)
    imgWarpPoints = drawPoints(imgCopy, points)
    
    ### STEP 3 – Histogram (Key Modification)
    # Get lane center at bottom region (near the car)
    middlePoint, imgHist = getHistogram(imgWarp, display=True, minPer=0.5, region=4)
    
    # Calculate deviation from image center
    imageCenter = wT // 2
    deviation = middlePoint - imageCenter
    curveRaw = deviation

    ### STEP 4 – Averaging
    curveList.append(curveRaw)
    if len(curveList) > avgVal:
        curveList.pop(0)
    curve = int(sum(curveList) / len(curveList))
    
    ### STEP 5 – Lane Departure Warning (Improved Logic)
    LANE_DEPARTURE_THRESHOLD = 45  # Adjusted threshold (pixels from center)
    warning_text = ""
    warning_color = (0, 255, 0)  # Green
    
    if abs(curve) > LANE_DEPARTURE_THRESHOLD:
        warning_color = (0, 0, 255)  # Red
        if curve > 0:
            warning_text = "WARNING: Drifting Right!"
        else:
            warning_text = "WARNING: Drifting Left!"
    else:
        warning_text = "Lane Position: Safe"

    ### STEP 6 – Display (Updated Visualization)
    if display != 0:
        imgInvWarp = warpImg(imgWarp, points, wT, hT, inv=True)
        imgInvWarp = cv2.cvtColor(imgInvWarp, cv2.COLOR_GRAY2BGR)
        imgInvWarp[0:hT//3, 0:wT] = 0, 0, 0
        imgLaneColor = np.zeros_like(img)
        imgLaneColor[:] = 0, 255, 0
        imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
        imgResult = cv2.addWeighted(imgResult, 1, imgLaneColor, 1, 0)
        midY = 450
        
        # Draw curve value
        cv2.putText(imgResult, str(curve), (wT//2-80, 85), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
        
        # Draw lane departure warning
        cv2.putText(imgResult, warning_text, (10, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, warning_color, 2)
        
        # Draw lane indicators
        cv2.line(imgResult, (wT//2, midY), (wT//2+(curve*3), midY), (255, 0, 255), 5)
        cv2.line(imgResult, ((wT//2+(curve*3)), midY-25), (wT//2+(curve*3), midY+25), (0, 255, 0), 5)
        
        # Draw lane boundaries
        for x in range(-30, 30):
            w = wT//20
            cv2.line(imgResult, (w*x+int(curve//50), midY-10),
                    (w*x+int(curve//50), midY+10), (0, 0, 255), 2)
            
        # Add departure warning visualization
        if abs(curve) > LANE_DEPARTURE_THRESHOLD:
            # Add red border when lane departure is detected
            border_thickness = 10
            imgResult = cv2.rectangle(imgResult, (0, 0), (wT, hT), warning_color, border_thickness)
        
        # Add additional visualization for lane center and car position
        cv2.circle(imgResult, (imageCenter, hT-10), 15, (255, 0, 0), cv2.FILLED)  # Car position
        cv2.circle(imgResult, (middlePoint, hT-10), 15, (0, 255, 0), cv2.FILLED)  # Lane center

    if display == 2:
        imgStacked = stackImages(0.7, ([img, imgWarpPoints, imgWarp],
                                     [imgHist, imgLaneColor, imgResult]))
        cv2.imshow('ImageStack', imgStacked)
    elif display == 1:
        cv2.imshow('Result', imgResult)

    ### NORMALIZATION (Optional)
    curve_normalized = curve / (wT//2)  # Normalize to [-1, 1] range
    if curve_normalized > 1: curve_normalized = 1
    if curve_normalized < -1: curve_normalized = -1
    
    return curve_normalized, warning_text

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture('vid1.mp4')
    intialTracbarVals = [102, 80, 20, 214]
    initializeTrackbars(intialTracbarVals)
    
    frameCounter = 0
    while True:
        frameCounter += 1
        if cap.get(cv2.CAP_PROP_FRAME_COUNT) == frameCounter:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frameCounter = 0

        _, img = cap.read()
        img = cv2.resize(img, (480, 240))
        curve, warning = getLaneCurve(img, display=1)
        print(f"Curve: {curve}, Status: {warning}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
