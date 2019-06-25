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
Ce script est appelé par main_init.main dans blender
Il ne tourne qu'une seule fois pour initier lss variables
qui seront toutes des attributs du bge.logic (gl)
Seuls les attributs de logic sont stockés en permanence.
"""


import os
from time import sleep

from bge import logic as gl
from bge import texture
from bge import render

from pymultilame import blendergetobject
from pymultilame import Tempo, MyConfig, MyTools

from scripts.get_texte import get_text_str_from_blender
from scripts.angleSemaphore import lettre_table


def get_conf():
    """Récupère la configuration depuis le fichier *.ini."""
    gl.tools =  MyTools()
    
    # Chemin courrant
    abs_path = gl.tools.get_absolute_path(__file__)
    print("Chemin courrant", abs_path)

    # Nom du script
    name = os.path.basename(abs_path)
    print("Nom de ce script:", name)

    # Abs path de semaphore sans / à la fin
    parts = abs_path.split("/semaphore_blend_yolo/")
    print("Recherche de semaphore_blend_yolo:", parts)
    gl.root = os.path.join(parts[0], "semaphore_blend_yolo")
    print("Path de semaphore_blend_yolo:", gl.root)

    # Dossier *.ini
    ini_file = os.path.join(gl.root, "global.ini")
    gl.ma_conf = MyConfig(ini_file)
    gl.conf = gl.ma_conf.conf

    print("\nConfiguration du jeu semaphore_blend_yolo:")
    print(gl.conf, "\n")


def set_variable():
    # mode create_shot ou display message
    gl.mode = "message"
    gl.two = 1
    gl.one = 0
    gl.enter = 0
    gl.backspace = 0
    gl.captured_text = ""
    gl.captured_lettre = 0
    gl.angles_previous = 0, 0, 0
    
    # Image vide: 1 tous les 270
    gl.empty = 0
    gl.empty_every = int(gl.conf['blend']['empty_every'])
    
    # Taille de l'image définie dans blender output et global.ini
    gl.size = gl.conf['blend']['size']

    # Variation sur les angles des lettres
    gl.lettre_angle_variation = gl.conf['blend']['lettre_angle_variation']
    # Variation sur les rotations du semaphore
    gl.rotation_semaphore_variation = gl.conf['blend']['rotation_semaphore_variation']

    # Calcul encombrement
    gl.rect = None
    gl.centre_dimension_relatif = None
    
    # Numero de shot de 0 à infini
    gl.numero = 0

    # Numéro du cycle de lecture des textes
    gl.cycle = 0

    # nombre de shot total
    gl.nombre_shot_total = gl.conf['blend']['total']

    # conversion lettre vers angle
    gl.lettre_table = lettre_table

    # Numéro de frame dans le cycle de chaque lettre
    gl.chars = ""
    gl.chars_change = gl.conf['blend']['chars_change']

    # Numéro de frame dans le cycle de chaque lettre
    gl.make_shot = gl.conf['blend']['make_shot']

    # Position de départ du semaphore
    gl.x = 0
    gl.y = 0
    gl.z = 0

    # Déplacement du semaphore
    gl.static = gl.conf['blend']['static']


def create_directories():
    """
    Création de n dossiers
    /media/data/3D/projets/semaphore_blend_yolo/shot/a/shot_0_a.png
    """

    # Dossier d'enregistrement des images
    gl.shot_directory = os.path.join(gl.root, 'shot')
    print("Dossier des shots:", gl.shot_directory)

    # Si le dossier n'existe pas, je le crée
    gl.tools.create_directory(gl.shot_directory)

    # Un dossier part lettre
    L = "a bcdefghijklmnopqrstuvwxyz"
    for l in L:
        if l == " ": l = "space"
        directory = os.path.join(gl.shot_directory, l)
        gl.tools.create_directory(directory)


def set_tempo():
    tempo_liste = [ ("shot", int(gl.conf['blend']['shot_every'])),
                    ("frame", 99999999999),
                    ("display lettre", 180)]

    # Comptage des frames par lettre
    gl.tempoDict = Tempo(tempo_liste)


def get_texte():
    # Récup des textes du dossier texte
    dossier = os.path.join(gl.root, 'get_yolo_shot', 'scripts', 'texte')
    print("Dossier des textes", dossier)
    
    # Le texte à lire
    gl.text_str = get_text_str_from_blender(dossier)
    print('Longueur du texte =', len(gl.text_str))

    # L'indice de la lettre à lire
    gl.lettre = 0


def get_cube_obj():
    all_obj = blendergetobject.get_all_objects()
    gl.cube = []
    for i in range(10):
        gl.cube.append(all_obj['Cube.00' + str(i)])

    gl.coin = []
    for i in range(4):
        gl.coin.append(all_obj['Cube.0' + str(10 + i)])    

    gl.cube_14 = all_obj['Cube.014']
    gl.cube_15 = all_obj['Cube.015']
    gl.cube_16 = all_obj['Cube.016']
    
    
def get_lamp_obj():
    """
    'NORMAL', 'SPOT', 'SUN', '__class__', '__contains__', '__delattr__',
    '__delitem__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__',
    '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__',
    '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__',
    '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__',
    '__str__', '__subclasshook__', 'actuators', 'addDebugProperty',
    'alignAxisToVect', 'angularDamping', 'angularVelocity',
    'angularVelocityMax', 'angularVelocityMin', 'applyForce', 'applyImpulse',
    'applyMovement', 'applyRotation', 'applyTorque', 'attrDict', 'children',
    'childrenRecursive', 'collisionCallbacks', 'collisionGroup',
    'collisionMask', 'color', 'controllers', 'currentLodLevel', 'debug',
    'debugRecursive', 'disableRigidBody', 'distance', 'enableRigidBody',
    'endObject', 'energy', 'get', 'getActionFrame', 'getActionName',
    'getAngularVelocity', 'getAxisVect', 'getDistanceTo', 'getLinearVelocity',
    'getPhysicsId', 'getPropertyNames', 'getReactionForce', 'getVectTo',
    'getVelocity', 'groupMembers', 'groupObject', 'invalid', 'isPlayingAction',
    'isSuspendDynamics', 'layer', 'life', 'linVelocityMax', 'linVelocityMin',
    'lin_attenuation', 'linearDamping', 'linearVelocity',
    'localAngularVelocity', 'localInertia', 'localLinearVelocity',
    'localOrientation', 'localPosition', 'localScale', 'localTransform',
    'mass', 'meshes', 'name', 'occlusion', 'orientation', 'parent',
    'playAction', 'position', 'quad_attenuation', 'rayCast', 'rayCastTo',
    'record_animation', 'reinstancePhysicsMesh', 'removeParent', 'replaceMesh',
    'restoreDynamics', 'scaling', 'scene', 'sendMessage', 'sensors',
    'setActionFrame', 'setAngularVelocity', 'setCollisionMargin', 'setDamping',
    'setLinearVelocity', 'setOcclusion', 'setParent', 'setVisible',
    'shadowBias', 'shadowBindId', 'shadowBleedBias', 'shadowClipEnd',
    'shadowClipStart', 'shadowColor', 'shadowFrustumSize', 'shadowMapType',
    'shadowMatrix', 'spotblend', 'spotsize', 'state', 'stopAction',
    'suspendDynamics', 'timeOffset', 'type', 'useShadow', 'visible',
    'worldAngularVelocity', 'worldLinearVelocity', 'worldOrientation',
    'worldPosition', 'worldScale', 'worldTransform'
    """
    all_obj = blendergetobject.get_all_objects()
    gl.sun = []
    for i in range(4):
        gl.sun.append(all_obj['Sun.00' + str(i)])

    # Energy 0.11000001430511475 Color [1.0, 1.0, 1.0]
    print("Energy", gl.sun[0].energy, "Color", gl.sun[0].color)

    
def get_semaphore_objet():
    all_obj = blendergetobject.get_all_objects()
    gl.bras_central = all_obj['main']
    gl.bras_gauche = all_obj['gauche']
    gl.bras_droit = all_obj['droit']
    gl.semaphore = all_obj['semaphore']
    gl.plane = all_obj['Plane']

        
def set_video():
    # identify a static texture by name
    matID = texture.materialID(gl.plane, 'MAblack')
    
    # create a dynamic texture that will replace the static texture
    gl.my_video = texture.Texture(gl.plane, matID)

    # define a source of image for the texture, here a movie
    try:
        film = "Astrophotography-Stars-Sunsets-Sunrises-Storms.ogg"
        movie = os.path.join(gl.root, "video", film)
        print('Movie =', movie)
    except:
        print("Une video valide doit être définie !")
            
    try:
        s = os.path.getsize(movie)
        print("Taille du film:", s)
    except:
        print("Problème avec la durée du film !")
    
    gl.my_video.source = texture.VideoFFmpeg(movie)
    gl.my_video.source.scale = False

    # Infinite loop
    gl.my_video.source.repeat = -1

    # Vitesse normale: < 1 ralenti, > 1 accélère
    gl.my_video.source.framerate = 1.4
    
    # quick off the movie, but it wont play in the background
    gl.my_video.source.play()


def main():
    """Lancé une seule fois à la 1ère frame au début du jeu par main_once."""

    print("Initialisation des scripts lancée un seule fois au début du jeu.")

    # Récupération de la configuration
    get_conf()

    # l'ordre est important
    set_variable()
    create_directories()
    set_tempo()
    get_texte()
    get_semaphore_objet()
    get_cube_obj()
    set_video()
    get_lamp_obj()
    
    print("Le bonjour des mondoshawan !")
