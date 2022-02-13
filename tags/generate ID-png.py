# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 19:53:48 2022

@author: thlu
"""

import cv2
import cv2.aruco as aruco

d = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)

for i in range(50):
    cv2.imwrite('aruco-4x4_100-{:02d}.png'.format(i), aruco.drawMarker(d, i, 400))
