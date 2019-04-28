#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import time
import textwrap
import numpy as np
import cv2

from pymultilame import MyTools

tools = MyTools()


def cvDrawBoxes(img, parts):
    """
    13 m
    pt1 (160, 137) pt2 (351, 424)
    
    xA = 7.84
    Rectangle englobant:
        [-5.20,  1.24], [ 3.26,  1.24],
        [ 3.26, -3.21], [-5.20, -3.21]
    Coordonnées du rectangle dans la vue cam en pixels
     [(532, 370), (186, 370), (186, 188), (532, 188)]

    Centre: 440.0 225.0
    pt1 (214, 113) pt2 (666, 337)
    """
    
    cx = float(parts[1]) * 640
    cy = float(parts[2]) * 640
    w = float(parts[3]) * 640
    h = float(parts[4]) * 640

    print("Centre:", cx, cy)  # 255 
    
    xmin = int(cx - w/2)
    ymin = int(cy - h/2)
    xmax = int(cx + w/2)
    ymax = int(cy + h/2)
    
    pt1 = (xmin, ymin)
    pt2 = (xmax, ymax)
    
    print("pt1", pt1, "pt2", pt2)
    
    cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
    return img


def without_letter(x):
    y = x[56:-6]
    y = textwrap.fill(str(y), 4)
    print(y)
    return y

rep = "/media/data/3D/projets/semaphore_blend_yolo/shot/"
#      01234567890123456789012345678901234567890123456789
pngs = tools.get_all_files_list(rep, "png")
#pngs = sorted(pngs, key=without_letter)

loop = 1
a = 0
t = time.time()
while loop:
    img = cv2.imread(pngs[a])
    line = tools.read_file(pngs[a][:-4] + ".txt")

    try:
        parts = line.split()
    except:
        parts = None
        
    if parts:
        img = cvDrawBoxes(img, parts)
        img_big = cv2.resize(img, (1280, 1280), interpolation=cv2.INTER_AREA)
        cv2.imshow("image", img_big)
        n = pngs[a].split("/media/data/3D/projets/semaphore_blend_yolo/shot/")
        name = "/media/data/3D/projets/semaphore_blend_yolo/shot_rect/" + n[1][2:-4] + "_rect.png"
        print(name)
        cv2.imwrite(name, img_big)

    if time.time() - t > 1:
        t = time.time()
        a += 1
    # Echap, attente, space
    k = cv2.waitKey(1000)
    if k == 32:
        a += 1
        if a == len(pngs):
            loop = 0
    if k == 27:
        loop = 0


cv2.destroyAllWindows()
