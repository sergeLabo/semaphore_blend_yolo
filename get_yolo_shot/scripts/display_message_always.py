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
Affichage d'un message.
"""


import math
import mathutils
from random import uniform

from bge import logic as gl
from bge import events

from pymultilame import get_all_objects
from scripts.key_capture import input_one_chars, backspace, enter

            
def main():
    # Avance de la video
    video_refresh()
    # Shot ou message
    mode()

    all_obj = get_all_objects()
    
    # Saisie d'un texte
    input_text()

    # Affichage d'un message si enter
    if gl.enter == 1:
        message_display()

    # Gestion des affichages des textes
    set_all_text(all_obj)
    
    # Toujours partout, tempo 'shot' commence à 0
    gl.tempoDict.update()


def set_all_text(all_obj):
    # Texte saisi
    all_obj['Text']['Text'] = gl.captured_text
    all_obj['Text'].resolution = 64

    # Texte en cours
    all_obj['Text.001'].resolution = 64
    if gl.enter == 0: 
        all_obj['Text.001']['Text'] = "Saisir un texte"
    else:
        all_obj['Text.001']['Text'] = "Texte en cours d'affichage"

    # Lettre en cours
    all_obj['Text.002'].resolution = 64
    all_obj['Text.003'].resolution = 64
    if gl.enter == 0: 
        all_obj['Text.002']['Text'] = ""
        all_obj['Text.003']['Text'] = ""
    else:
        all_obj['Text.002']['Text'] = "Lettre en cours"
        all_obj['Text.003']['Text'] = gl.chars.upper()
    
    
def set_sun_color_energy():

    # 0.110 de face
    gl.sun[0].energy = uniform(0.01, 0.3)
    # 1.34 main
    gl.sun[1].energy = uniform(1.0, 2.2)
    # 1 lampe back
    gl.sun[2].energy = uniform(0.2, 1.3)
    # 1 lampe back
    gl.sun[3].energy = uniform(0.2, 1.3)

    # color 
    color = uniform(0.7, 1.0), uniform(0.7, 1.0), uniform(0.7, 1.0)
    for i in range(3):
        #print(gl.sun[i].color)
        gl.sun[i].color = color


def message_display():
    """Changement de lettre tous les 120 frames"""

    get_chars()
    print("Affichage de", gl.chars)
    display(gl.chars)
    
    if gl.tempoDict['display lettre'].tempo == 0:
        gl.lettre += 1
        set_sun_color_energy()

    if gl.lettre > len(gl.captured_text):
        gl.enter = 0
        gl.captured_text = ""
        gl.lettre = 0
        
    
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
        gl.chars = gl.captured_text[gl.lettre]
        gl.chars = gl.chars.lower()
    except:
        gl.chars = " "


def input_text():
    if not gl.enter:
        input_one_chars()
        backspace()
        enter()

    
def mode():

    if gl.keyboard.events[events.PAGEDOWNKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        # Page down pour message
        gl.mode = "shot"
        
    if gl.keyboard.events[events.PAGEUPKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        # Page up pour shot
        gl.mode = "message"


def video_refresh():
    """call this function every frame to ensure update of the texture."""
    # print("refresh")
    gl.my_video.refresh(True)
