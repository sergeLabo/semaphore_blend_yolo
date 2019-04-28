#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

########################################################################
# This file is part of Semaphore Blend Yolo.
#
# Semaphore Blend Yolo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Semaphore Blend Yolo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
########################################################################


"""
Lancé à chaque frame durant tout le jeu.
"""

import os
from time import sleep
import math
import mathutils
from random import uniform

from bge import logic as gl
from bge import render

from pymultilame import MyTools


L = "a bcdefghijklmnopqrstuvwxyz"
# ["a", " ", ....]
LETTRES = list(L)


def main():
    # Avance de la video
    video_refresh()

    if gl.numero % gl.empty_every == 0:
        gl.empty = 1
    else:
        gl.empty = 0
    if gl.tempoDict['shot'].tempo == gl.chars_change:
        gl.chars = get_chars()
        display(gl.chars)
        # glissement rotation à chaque nouveau caractère
        if not gl.static:
            scale = scale_semaphore()
            position_semaphore(scale)
            rotation_semaphore()
            set_sun_color_energy()
    if gl.tempoDict['shot'].tempo == gl.make_shot - 10:
        gl.rect = get_semaphore_world_englobage()
    if gl.tempoDict['shot'].tempo == gl.make_shot - 8:        
        gl.centre_dimension_relatif = centre_dimension_rect_relatif(gl.rect)
    if gl.tempoDict['shot'].tempo == gl.make_shot - 6:       
        save_txt_file(gl.centre_dimension_relatif)
    if gl.tempoDict['shot'].tempo == gl.make_shot:
        make_shot()

    # Fin du jeu à nombre_shot_total
    end()

    # Toujours partout, tempo 'shot' commence à 0
    gl.tempoDict.update()


def set_sun_color_energy():

    # 0.110 de face
    gl.sun[0].energy = uniform(0.05, 0.2)
    # 1.34 main
    gl.sun[1].energy = uniform(0.8, 1.8)
    # 1 lampe back
    gl.sun[2].energy = uniform(0.5, 1.3)

    color = uniform(0.8, 1), uniform(0.5, 1), uniform(0.8, 1)
    for i in range(3):
        gl.sun[i].color = color
        
    # #print(gl.sun[0].energy, gl.sun[1].energy, gl.sun[2].energy)
    # #print(gl.sun[0].color)
    
def save_txt_file(centre_dimension_relatif):
    """<object-class> <x> <y> <width> <height>
    centre_dimension_relatif = c, abs(w), abs(h)
    """
    
    # Get indice avant modif liste
    lettre = gl.chars
    indice = LETTRES.index(lettre)

    # pour avoir dossier clair
    if lettre == " ":
        lettre = "space"

    fichier = os.path.join(gl.shot_directory,
                            lettre,
                            'shot_' + str(gl.numero) + '_' + lettre + '.txt')
    if not gl.empty:
        data =  str(indice) + " " \
                + str(centre_dimension_relatif[0][0]) + " " \
                + str(centre_dimension_relatif[0][1]) + " " \
                + str(centre_dimension_relatif[1]) + " " \
                + str(centre_dimension_relatif[2]) + " " \
                + "\n"
    else:
        data = ""
    gl.tools.write_data_in_file(data, fichier, "w")


def position_semaphore(scale):
    """Déplacement vertical z et horizontal x
    scale = uniform(0.2, 1.1)"""
    
    gl.x = uniform(-1.5*scale, 1.5*scale)
    gl.y = 14
    gl.z = uniform(-8*scale, -6*scale)

    # J'applique
    gl.semaphore.worldPosition[0] = gl.x
    if not gl.empty:
        gl.semaphore.worldPosition[2] = gl.z
    else:
        gl.semaphore.worldPosition[2] = -100


def scale_semaphore():

    sx = uniform(0.5, 1.2)
    sy = sx
    sz = sx
    
    gl.semaphore.worldScale = sx, sy, sz

    return sx


def rotation_semaphore():
    """gl.rotation_semaphore de global.ini non utilisé"""

    rot = gl.rotation_semaphore_variation
    # angle en radians
    alpha = uniform(-rot, rot)
    beta = uniform(-rot, rot)
    gamma = uniform(-rot, rot)
    
    # Set objects orientation with alpha, beta, gamma in radians
    rot_en_euler = mathutils.Euler([alpha, beta, gamma])
    # Apply to objects world orientation
    gl.semaphore.localOrientation = rot_en_euler.to_matrix()

    
def display(chars):
    """Affichage de la lettre par rotation des bras."""

    # 180, 90, 0
    angles = get_angles(chars)

    xyz = gl.bras_central.localOrientation.to_euler()
    xyz[1] = math.radians(angles[0])
    gl.bras_central.localOrientation = xyz.to_matrix()

    xyz = gl.bras_gauche.localOrientation.to_euler()
    xyz[1] = math.radians(angles[1])
    gl.bras_gauche.localOrientation = xyz.to_matrix()

    xyz = gl.bras_droit.localOrientation.to_euler()
    xyz[1] = math.radians(angles[2])
    gl.bras_droit.localOrientation = xyz.to_matrix()


def get_semaphore_world_englobage():
    """rect est un plan qui englobe le semaphore"""
    
    # Coordonnées de tous les cubes
    all_cubes_coord = []
    for i in range(10):
        all_cubes_coord.append(gl.cube[i].worldPosition)

    # Recherche des plus petit x et z
    zero = []
    deux = []
    for p in all_cubes_coord:
        # j'ajoute tous les 0
        zero.append(p[0])
        # j'ajoute tous les 2
        deux.append(p[2])

    # tri des zero et des deux
    # le 1er est le plus petit, le dernier le plus grand
    zero.sort()
    deux.sort()
    gauche = zero[0]
    droit = zero[-1]
    bas = deux[0]
    haut = deux[-1]

    # Coordonées du rectangle englobant
    Y = 13.59
    rect = [[gauche, Y, haut],
            [droit, Y, haut],
            [droit, Y, bas],
            [gauche, Y, bas]]

    # Position des cubes au coin
    for i in range(4):
        gl.coin[i].worldPosition = rect[i]

    return rect
    

def centre_dimension_rect_relatif(rect):
    """
    9i
    Rectangle englobant:
     [[-3.63, 13.59, 2.66],
     [1.34, 13.59, 2.66],
     [1.34, 13.59, -0.58],
     [-3.63, 13.59, -0.58]]
    Coordonnées du rectangle dans la vue cam en pixels
     [(468, 428), (264, 428), (264, 295), (468, 295)]
    Coordonnées du centre: [366.0, 361.5]

    """
    
    cdr = []
    #print("Rectangle englobant:\n    ", rect)
    for i in range(4):
        cdr.append(get_M_position_in_cam_output_in_pixels(rect[i]))
    #print("Coordonnées du rectangle dans la vue cam en pixels\n    ", cdr)

    # rogne le rectangle si sort du 640x640
    cdr = crop_rectangle(cdr)
    
    # Calcul du centre et dimension en pixels
    w = cdr[1][0] - cdr[0][0]
    h = cdr[3][1] - cdr[0][1]
    c = [(cdr[1][0] + cdr[0][0])/2, (cdr[3][1] + cdr[0][1])/2]
    #print("Coordonnées du centre:", c)
    
    # en relatif de la taille de l'image
    w /= 640
    h /= 640
    c[0] /= 640
    c[1] /= 640
    
    return c, abs(w), abs(h)


def crop_rectangle(cdr):
    for p in cdr:
        if p[0] < 0:
            p[0] = 0
            print("Crop")
        if p[0] > 640:
            p[0] = 640
            print("Crop")
        if p[1] < 0:
            p[1] = 0
            print("Crop")
        if p[1] > 640:
            p[1] = 640
            print("Crop")
    return cdr

    
def get_M_position_in_cam_output_in_pixels(M):
    """M = [M[0], M[1], M[2]]
    La vue est carrée:
    Origine         (0, 0)   pour A(-7.84, 13.59, 7.84)
    Coin droit haut (640,0)  pour B( 7.84, 13.59, 7.84)
    tg_beta = 0,57689
    
    """

    demi = gl.size / 2
    xB = 7.84
    yB = 13.59
    tg_beta = xB / yB
    
    xM, yM, zM = M[0], M[1], M[2]

    # Si yM = 13.59
    x_cam = int(demi * (1 + (xM/xB)))
    y_cam = int(demi * (1 - (zM/xB)))

    # Si plus reculé
    x_cam = x_cam - (yM - 13.59)*tg_beta
    y_cam = y_cam - (yM - 13.59)*tg_beta
    
    return [x_cam, y_cam]

    
def get_angles(chars):
    try:
        angles = gl.lettre_table[chars]
        angles = angles_variation(angles)
    except:
        angles = (0, 0, 0)
    return angles


def angles_variation(angles):
    """Variation de qq degrés sur chaque angle
    Petite bidouille car angles = tuple de 3 non  modifiable
    """

    d = gl.lettre_angle_variation
    a = angles[0]
    a += uniform(-d, d)
    b = angles[1]
    b += uniform(-d, d)
    c = angles[2]
    c += uniform(-d, d)
    
    return (a, b ,c)
    

def get_chars():
    try:
        chars = gl.text_str[gl.lettre]
        chars = chars.lower()
    except:
        gl.lettre = 0
        chars = gl.text_str[gl.lettre]
        chars = chars.lower()

    gl.lettre += 1
    return chars


def make_shot():
    name_file_shot = get_name_file_shot()
    render.makeScreenshot(name_file_shot)
    print("Shot n°", gl.numero, name_file_shot )
    gl.numero += 1


def get_name_file_shot():
    """/media/data/3D/projets/semaphore_blend_yolo/shot/a/shot_0_a.png"""

    if gl.chars == " ": gl.chars = "space"
    
    gl.name_file_shot = os.path.join(gl.shot_directory,
                                     gl.chars,
                                     'shot_' + str(gl.numero) + '_' + gl.chars + '.png')

    return gl.name_file_shot


def video_refresh():
    """call this function every frame to ensure update of the texture."""
    # print("refresh")
    gl.my_video.refresh(True)


def end():
    if gl.numero == gl.nombre_shot_total:
        gl.endGame()
