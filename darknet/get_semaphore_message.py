#!python3
# -*- coding: UTF-8 -*-


"""
Webcam devant le sémaphore .
Le sémaphore maintient les lettres 2 secondes.
Il faut régler la taille de la pile en fonction du FPS.
"""


import re
import time
import cv2
import numpy as np
import os
import textwrap
import darknet
from webcam import apply_all_cam_settings
from pymultilame import MyConfig


class PileFIFO:
    """
    Pile FIFO pour trouver la récurrence d'une lettre
    """
    def __init__(self, size):
        """size définit la hauteur de la pile."""

        self.queue = []
        self.size = size
        self.average = 0

    def append(self, new):
        """Ajoute pour avoir une pile constante de size valeurs."""

        # Ajout dans la liste à la fin
        self.queue.append(new)

        # Remplissage de la pile avec la première valeur au premier ajout
        while len(self.queue) < self.size:
            self.queue.append(new)

        # Suppression du plus ancien si la pile fait size + 1
        if len(self.queue) > self.size:
            self.queue.pop(0)

    def all_identical(self):
        """Tous les items de la liste sont-ils les mêmes
        p = [a, a, a] retourne a
        p = [a, b, a] retourne ""
        set() supprime les éléments en double
        si pas de doublons, on trouve 1 !
        """
        if len(set(self.queue)) == 1:
            if self.queue[0] is not None:
                return self.queue[0]
            else:
                return None
        else:
            return None


class YOLO:

    def __init__(self, cam, calcul):

        if calcul == 1:
            configPath = "./calcul_1/calcul_1_9000_jpg_90_small_var.cfg"
            weightPath = "./calcul_1/calcul_1_9000_jpg_90_small_var.weights"
            metaPath   = "./calcul_1/obj.data"
        if calcul == 2:
            configPath = "./calcul_2/calcul_2_54000_jpg_90_small_var.cfg"
            weightPath = "./calcul_2/calcul_2_54000_jpg_90_small_var.weights"
            metaPath   = "./calcul_2/obj.data"
        if calcul == 3:
            configPath = "./calcul_3/calcul_3_12000_jpg_100_big_var.cfg"
            weightPath = "./calcul_3/calcul_3_12000_jpg_100_big_var.weights"
            metaPath   = "./calcul_3/obj.data"
            
        self.netMain = darknet.load_net_custom(configPath.encode("ascii"),
                                                weightPath.encode("ascii"),
                                                0,
                                                1)
        self.metaMain = darknet.load_meta(metaPath.encode("ascii"))

        with open(metaPath) as metaFH:
            metaContents = metaFH.read()
            match = re.search("names *= *(.*)$", metaContents,
                              re.IGNORECASE | re.MULTILINE)
            if match:
                result = match.group(1)
            else:
                result = None
            try:
                if os.path.exists(result):
                    with open(result) as namesFH:
                        namesList = namesFH.read().strip().split("\n")
                        self.altNames = [x.strip() for x in namesList]
            except TypeError:
                print("Erreur self.altNames")

        self.cap = cv2.VideoCapture(cam)

        # Create an image we reuse for each detect
        self.darknet_image = darknet.make_image(darknet.network_width(self.netMain),
                                                darknet.network_height(self.netMain),
                                                3)
        self.msg = ""
        # Pile de 20
        self.tags_pile = PileFIFO(25)
        self.new = 0
        self.loop = 1

    def detect(self):
        while self.loop:
            # image blanche de 600x600
            msg_img = np.zeros((600, 800, 3), np.uint8)

            prev_time = time.time()
            ret, frame_read = self.cap.read()
            frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)

            # Image carrée
            frame_rgb = crop(frame_rgb)

            frame_resized = cv2.resize(frame_rgb,
                                       (darknet.network_width(self.netMain),
                                        darknet.network_height(self.netMain)),
                                       interpolation=cv2.INTER_LINEAR)

            darknet.copy_image_from_bytes(self.darknet_image, frame_resized.tobytes())
            detections, tag, confiance = darknet.detect_image(self.netMain, self.metaMain, self.darknet_image)

            try:
                image = cvDrawBoxes(detections, frame_resized)
            except:
                image = frame_read

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (900, 900),
                               interpolation=cv2.INTER_LINEAR)
            cv2.imshow('Demo', image)

            # tags
            self.tags_pile.append(tag)
            lettre = self.tags_pile.all_identical()

            if lettre is not None:
                if not self.new:
                    if lettre == "space":
                        lettre = " "
                    self.msg += lettre
                    self.new = 1
            else:
                self.new = 0

            # A la ligne, tous les ln charactères
            ln = 80
            self.msg = textwrap.fill(self.msg, ln)
        
            # Affichage
            msg_img = put_text(msg_img, "Message:", (20, 75))
            msg_img = put_text(msg_img, self.msg, (20, 150))
            cv2.imshow('Message', msg_img)

            # ~ print("FPS =", round(1/(time.time()-prev_time), 2),
                  # ~ "    Lettre lue", tag, confiance)

            # Echap et attente
            k = cv2.waitKey(3)
            if k == 27:
                self.loop = 0

        self.cap.release()


def put_text(img, text, xy):
    """
    Adding Text to Images:
        Text data that you want to write
        Position coordinates of where you want put it (i.e. bottom-left corner
        where data starts).
        Font type (Check cv.putText() docs for supported fonts)
        Font Scale (specifies the size of font)
        regular things like color, thickness, lineType etc. For better look,
        lineType = cv.LINE_AA is recommended.

    We will write OpenCV on our image in white color.
    font = cv.FONT_HERSHEY_SIMPLEX
    cv.putText(img, 'OpenCV', (10, 500), font, 4, (255,255,255), 2, cv.LINE_AA)
    """

    img = cv2.putText(img,
                     text,
                     (xy[0], xy[1]),
                     cv2.FONT_HERSHEY_SIMPLEX,
                     1.0,
                     [0, 255, 0],
                     2)
    return img


def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img):
    for detection in detections:
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
        cv2.putText(img,
                    detection[0].decode() +
                    " [" + str(round(detection[1] * 100, 2)) + "]",
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    [0, 255, 0], 2)
    return img


def crop(img):
    """Coupe les 2 cotés pour avoir une image carrée
    x = int((a - b)/2)
    y = 0
    frame = frame[y:y+h, x:x+w]
    """

    a = img.shape[1]  # 640
    b = img.shape[0]  # 480
    x = int((a - b)/2)
    y = 0
    w, h = b, b
    # img[y:y+h, x:x+w]
    return img[0:480, 80:80+480]


if __name__ == "__main__":
    dossier = os.getcwd()
    cf = MyConfig(dossier + "/darknet.ini")
    conf = cf.conf
    apply_all_cam_settings(conf["HD5000"], cam=0)

    # cam = numéro de cam, calcul=1 ou 2 ou 3 voir wiki
    yolo = YOLO(cam=0, calcul=2)
    yolo.detect()
