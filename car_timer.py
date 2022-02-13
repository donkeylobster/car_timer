# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 19:07:27 2022

@author: thlu
"""

import numpy as np
import cv2
import cv2.aruco as aruco
import time
import marker_timing

markers_seen = marker_timing.Active_markers([])

cap = cv2.VideoCapture(0)
out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (640,480))



# font for displaying text (below)
font = cv2.FONT_HERSHEY_SIMPLEX
font_size = 0.8
font_thickness = 2

state = 0

box = 0 # Numbers of corners marked
box_points = np.array([[0,0],
                       [0,0],
                       [0,0],
                       [0,0]])

point = (1,1)

# mouse callback function
def mouse_events_handler(event,x,y,flags,param):
    global box, box_points, point

    if box < 4:
        if event==cv2.EVENT_LBUTTONDOWN:
            box_points[box]=x,y
            box += 1

    if event==cv2.EVENT_MOUSEMOVE:
        point = x,y


cv2.namedWindow('cam')
cv2.setMouseCallback('cam',mouse_events_handler)

# load the overlay image. size should be smaller than video frame size
img = cv2.imread('tags/aruco-4x4_100-42.png')
down_points = (30, 30)
img = cv2.resize(img, down_points, interpolation= cv2.INTER_LINEAR)
img_height, img_width, _ = img.shape


text = ""
time_last = 0


###------------------ ARUCO TRACKER ---------------------------
while (True):
    # Get image from camara
    ret, frame = cap.read()

    # measure FPS
    time_new = time.time()
    fps = 1/(time_new-time_last)
    time_last = time_new

    # Resize frame
    frame_height, frame_width, _ = frame.shape
    scale = 1.5
    newsize = (int(frame_width*scale), int(frame_height*scale))
    frame = cv2.resize(frame, newsize, interpolation= cv2.INTER_LINEAR)


    # Add overlay image at mouse pointer
    try:
        # x,y = point
        # frame[ y:y+img_height , x:x+img_width ] = img
        cv2.circle(frame,point,3,(255,0,0),-1)
    except:
        # x,y = (1,1)
        # frame[ y:y+img_height , x:x+img_width ] = img
        pass


    if state < 100:
        #------------------------------- Mark points for box ----------------
        print("\rUse mouse to plot box. Need {} more points".format(4-box), end="")
        if box >= 4:
            state = 100

    elif state < 200:
        print("\rUse mouse to plot box. Need {} more points".format(4-box))
        print("box done")
        state = 200

    elif state < 300:
        # ----------------------------Detect markers---------------------------


        # operations on the frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        # set dictionary size depending on the aruco marker selected
        # aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_100)
    
        # detector parameters can be set here (List of detection parameters[3])
        parameters = aruco.DetectorParameters_create()
        # parameters.adaptiveThreshConstant = 10
    
        # lists of ids and the corners belonging to each id
        corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    
    
        # if any IDs is found:
        if np.all(ids != None):
    
            # draw a square around the markers
            aruco.drawDetectedMarkers(frame, corners, ids)

            for i, markerid in enumerate(ids):
                markerid = markerid.item()
                # Test if marker is inside box
                # Er der en nemmere måde at lave numpy array om til native array?
                # PolygonTest vil ikke have numpy typer i marker_center
                tt = tuple(corners[i].mean(1)[0].astype(int))
                marker_center = tuple([x.item() for x in tt])
                marker_in_box = cv2.pointPolygonTest(box_points, marker_center, False)
                if marker_in_box > 0:
                    print("\rMarker {} is inside box  ".format(markerid), end="")
                    markers_seen.update(markerid, True)
                else:
                    print("\rMarker {} is outside box".format(markerid), end="")
                    markers_seen.update(markerid, False)
        else:
            pass
            # code to show 'No Ids' when no markers are found
            # cv2.putText(frame, "No Ids", (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
            # print("\rNo markers found in image        ", end="")

        # Get text to draw in frame
        text = markers_seen.status_text()


    # --------------------- Draw box on image -------------------------------
    if box == 1:
        cv2.circle(frame,tuple(box_points[0]),3,(255,0,0),-1)
    elif box > 1 and box <= 4:
        for i in range(box-1):
            cv2.line(frame,
                     tuple(box_points[i]),
                     tuple(box_points[i+1]),
                     color=(255,0,0),thickness=3)
    if box >= 4:
        cv2.line(frame,
                 tuple(box_points[0]),
                 tuple(box_points[3]),
                 color=(255,0,0),thickness=3)

    # ------------------------ Add text ---------------------------------
    if text:
        textl = text.split('\n')
        y = 0
        for line in textl:
            textsize = cv2.getTextSize(line, font, font_size, font_thickness)[0]
            y += textsize[1]+8
            x = 2
            for l in line.split('\t'):
                textsize = cv2.putText(frame, l, (x,y), font, font_size, (0,255,0), font_thickness, cv2.LINE_AA)
                x += 200

    fps_str = "{:.0f}".format(fps)
    cv2.putText(frame, fps_str, (newsize[0]-60 ,newsize[1]-20), font, font_size, (0,255,0), font_thickness, cv2.LINE_AA)


    # display the resulting frame
    cv2.imshow('cam',frame)
    frame = cv2.resize(frame, (640, 480))
    out.write(frame)

    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()
