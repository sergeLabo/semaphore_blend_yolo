#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import os
from shutil import copyfile
import cv2
from pymultilame import MyTools


def convert_png_to_jpg():
    mt = MyTools()
    shot_dir = '/media/data/3D/projets/semaphore_blend_yolo/shot_0'
    all_png_files = mt.get_all_files_list(shot_dir, '.png')
    print(len(all_png_files))

    #           /media/data/3D/projets/semaphore_blend_yolo/shot_jpg
    shot_jpg = '/media/data/3D/projets/semaphore_blend_yolo/shot_jpg'
    
    # Un dossier part lettre
    L = "a bcdefghijklmnopqrstuvwxyz"
    for l in L:
        if l == " ": l = "space"
        directory = os.path.join(shot_jpg, l)
        mt.create_directory(directory)

    for png in all_png_files:
        # lecture
        img = cv2.imread(png)

        # nouveau nom
        # /media/data/3D/projets/semaphore_blend_yolo/shot_jpg/t/shot_317_t.jpg
        n = png.split(shot_dir)[1]
        nom = n[:-4]
        name = shot_jpg + nom + '.jpg'
        print(name)

        # Fichiers txt
        txt = png[:-4] + '.txt' 
        print(txt)
        dst = shot_jpg + nom + '.txt'
        print(dst)
        copyfile(txt, dst)
        
        # Ecriture
        cv2.imwrite(name, img, [int(cv2.IMWRITE_JPEG_QUALITY), 98])


    
if __name__ == "__main__":
    convert_png_to_jpg()
