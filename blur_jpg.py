#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import os
from shutil import copyfile
import random
import cv2
from pymultilame import MyTools


def blur_jpg():
    mt = MyTools()
    shot_dir = '/media/data/3D/projets/semaphore_blend_yolo/shot_png_last'
    all_jpg_files = mt.get_all_files_list(shot_dir, '.png')
    print(len(all_jpg_files))

    shot_jpg_blur = '/media/data/3D/projets/semaphore_blend_yolo/shot_jpg_blur'
    
    # Un dossier part lettre
    L = "a bcdefghijklmnopqrstuvwxyz"
    for l in L:
        if l == " ": l = "space"
        directory = os.path.join(shot_jpg_blur, l)
        mt.create_directory(directory)

    for jpg in all_jpg_files:
        # lecture
        img = cv2.imread(jpg)

        # nouveau nom
        # /media/data/3D/projets/semaphore_blend_yolo/shot_jpg_blur/t/shot_317_t.jpg
        n = jpg.split(shot_dir)[1]
        nom = n[:-4]
        name = shot_jpg_blur + nom + '.jpg'
        print(name)

        # Fichiers txt
        txt = jpg[:-4] + '.txt' 
        print(txt)
        dst = shot_jpg_blur + nom + '.txt'
        print(dst)
        copyfile(txt, dst)

        # Flou
        k = random.randint(0, 5)
        if k != 0:
            img = cv2.blur(img, (k, k))
        # Ecriture
        cv2.imwrite(name, img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])


    
if __name__ == "__main__":
    blur_jpg()
