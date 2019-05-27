#!python3
# -*- coding: UTF-8 -*-


"""
Webcam devant le sémaphore .
Le sémaphore maintient les lettres 2 secondes.
Il faut régler la taille de la pile en fonction du FPS.

brightness = 133
saturation = 163
exposure_auto = 0
exposure_absolute = 156
taille de la pile = 25 ["pile"]["size"]
"""


import os, sys
import re
import time
import textwrap
import cv2
import numpy as np
import darknet
from webcam import apply_all_cam_settings, apply_cam_setting
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
    """Reset du message avec espace"""

    def __init__(self, cam, calcul, conf, thresh=0.5, hier_thresh=0.5, nms=0.45):
        """cam = numéro de cam
        calcul = 1 ou 2 ou 3 (2 semble le meilleur)
        pile = environ le FPS, une lettre doit être maintenus 1 seconde pour
        être validée
        un intru dans la pile redéclenche l'attente d'une lettre
        """

        if calcul == 1:
            configPath = "./calcul_1/calcul_1_9000_jpg_90_small_var.cfg"
            weightPath = "./calcul_1/calcul_1_9000_jpg_90_small_var.weights"
            metaPath   = "./calcul_1/obj.data"
        elif calcul == 2:
            configPath = "./calcul_2/calcul_2_54000_jpg_90_small_var.cfg"
            weightPath = "./calcul_2/calcul_2_54000_jpg_90_small_var.weights"
            metaPath   = "./calcul_2/obj.data"
        elif calcul == 3:
            configPath = "./calcul_3/calcul_3_12000_jpg_100_big_var.cfg"
            weightPath = "./calcul_3/calcul_3_12000_jpg_100_big_var.weights"
            metaPath   = "./calcul_3/obj.data"
        else:
            print("Tu es dans un espace parallèle !")

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

        self.cam = cam
        self.cap = cv2.VideoCapture(self.cam)

        # L'objet config de darknet.ini
        self.cf = cf

        self.brightness = self.cf.conf['HD5000']['brightness']
        self.saturation = self.cf.conf['HD5000']['saturation']
        self.exposure_auto = self.cf.conf['HD5000']['exposure_auto']
        self.exposure_absolute = self.cf.conf['HD5000']['exposure_absolute']
        self.pile_size = self.cf.conf['pile']['size']
        self.contrast = self.cf.conf['HD5000']['contrast']
        self.w_bal_temp_aut = self.cf.conf['HD5000']['w_bal_temp_aut']
        self.power_line_freq = self.cf.conf['HD5000']['power_line_freq']
        self.white_bal_temp = self.cf.conf['HD5000']['white_bal_temp']
        self.backlight_compensation = self.cf.conf['HD5000']['backlight_compensation']

        # Trackbars
        self.create_trackbar()
        self.set_init_tackbar_position()

        # Create an image we reuse for each detect
        self.darknet_image = darknet.make_image(darknet.network_width(self.netMain),
                                                darknet.network_height(self.netMain),
                                                3)
        self.msg = ""

        # Pile de 25
        self.create_pile()
        self.new = 0
        self.loop = 1

        # Paramêtres de detections
        self.thresh = thresh
        self.hier_thresh = hier_thresh
        self.nms = nms

    def create_pile(self):
        self.lettres_pile = PileFIFO(self.pile_size)
        print("Création d'une pile FIFO de:", self.pile_size)

    def create_trackbar(self):
        """
        brightness        min=30 max=255 step=1 default=133
        saturation        min=0 max=200 step=1 default=83
        exposure_auto     min=0 max=3 default=1
        exposure_absolute min=5 max=20000 step=1 default=156
        contrast          min=0 max=10 step=1
        w_bal_temp_aut    min=0 max=1
        power_line_freq   min=0 max=2
        white_bal_temp    min=2800 max=10000
        backlight_compensation min=0 max=10 step=1
        pile_size         min=1 max=60 step=1
        """
        cv2.namedWindow('Reglage')
        self.reglage_img = np.zeros((10, 1000, 3), np.uint8)

        cv2.createTrackbar('brightness', 'Reglage', 30, 255, self.onChange_brightness)
        cv2.createTrackbar('contrast', 'Reglage', 0, 10, self.onChange_contrast)
        cv2.createTrackbar('saturation', 'Reglage', 0, 200, self.onChange_saturation)
        cv2.createTrackbar('w_bal_temp_aut', 'Reglage', 0, 1, self.onChange_w_bal_temp_aut)
        cv2.createTrackbar('power_line_freq', 'Reglage', 0, 2, self.onChange_power_line_freq)
        cv2.createTrackbar('white_bal_temp', 'Reglage', 2800, 10000, self.onChange_white_bal_temp)
        cv2.createTrackbar('backlight_compensation', 'Reglage', 0, 10, self.onChange_backlight_compensation)
        cv2.createTrackbar('exposure_auto', 'Reglage', 0, 3, self.onChange_exposure_auto)
        cv2.createTrackbar('exposure_absolute', 'Reglage', 5, 20000, self.onChange_exposure_absolute)

        cv2.createTrackbar('pile_size', 'Reglage', 1, 60, self.onChange_pile_size)

    def set_init_tackbar_position(self):
        """setTrackbarPos(trackbarname, winname, pos) -> None"""

        cv2.setTrackbarPos('brightness', 'Reglage', self.brightness)
        cv2.setTrackbarPos('saturation', 'Reglage', self.saturation)
        cv2.setTrackbarPos('exposure_auto', 'Reglage', self.exposure_auto)
        cv2.setTrackbarPos('exposure_absolute', 'Reglage', self.exposure_absolute)

        cv2.setTrackbarPos('contrast', 'Reglage', self.contrast)
        cv2.setTrackbarPos('w_bal_temp_aut', 'Reglage', self.w_bal_temp_aut)
        cv2.setTrackbarPos('power_line_freq', 'Reglage', self.power_line_freq)
        cv2.setTrackbarPos('white_bal_temp', 'Reglage', self.white_bal_temp)
        cv2.setTrackbarPos('backlight_compensation', 'Reglage', self.backlight_compensation)

        cv2.setTrackbarPos('pile_size', 'Reglage', self.pile_size)

    def onChange_brightness(self, brightness):
        """min=30 max=255 step=1 default=133
        """
        if brightness < 30: brightness = 30
        self.brightness = brightness
        self.save_change('HD5000', 'brightness', brightness)

    def onChange_saturation(self, saturation):
        """min=0 max=200 step=1 default=83
        """
        self.saturation = saturation
        self.save_change('HD5000', 'saturation', saturation)

    def onChange_exposure_auto(self, exposure_auto):
        """min=0 max=3 default=1
        """
        self.exposure_auto = exposure_auto
        self.save_change('HD5000', 'exposure_auto', exposure_auto)

    def onChange_exposure_absolute(self, exposure_absolute):
        """min=5 max=20000 step=1 default=156
        """
        self.exposure_absolute = exposure_absolute
        self.save_change('HD5000', 'exposure_absolute', exposure_absolute)

    def onChange_contrast(self, contrast):
        """min=0 max=10 step=1
        """
        self.contrast =contrast
        self.save_change('HD5000', 'contrast', contrast)

    def onChange_w_bal_temp_aut(self, w_bal_temp_aut):
        """min=0 max=1
        """
        self.w_bal_temp_aut = w_bal_temp_aut
        self.save_change('HD5000', 'w_bal_temp_aut', w_bal_temp_aut)

    def onChange_power_line_freq(self, power_line_freq):
        """min=0 max=2
        """
        self.power_line_freq = power_line_freq
        self.save_change('HD5000', 'power_line_freq', power_line_freq)

    def onChange_white_bal_temp(self, white_bal_temp):
        """white_bal_temp    min=2800 max=10000
        """
        if white_bal_temp < 2800: white_bal_temp = 2800
        self.white_bal_temp = white_bal_temp
        self.save_change('HD5000', 'white_bal_temp', white_bal_temp)

    def onChange_backlight_compensation(self, backlight_compensation):
        """min=0 max=10 step=1
        """
        self.backlight_compensation = backlight_compensation
        self.save_change('HD5000', 'backlight_compensation', backlight_compensation)

    def onChange_pile_size(self, pile_size):
        """min=1 max 60
        """
        if pile_size == 0: pile_size = 1
        self.pile_size = pile_size
        self.save_change('pile', 'size', pile_size)
        self.create_pile()

    def save_change(self, section, key, value):

        self.cf.save_config(section, key, value)
        if section == 'HD5000':
            apply_cam_setting(self.cam, key, value)

    def detect(self):
        while self.loop:

            # Capture des positions des sliders
            self.brightness = cv2.getTrackbarPos('brightness','Reglage')
            self.saturation = cv2.getTrackbarPos('saturation','Reglage')
            self.exposure_auto = cv2.getTrackbarPos('exposure_auto','Reglage')
            self.exposure_absolute = cv2.getTrackbarPos('exposure_absolute','Reglage')
            self.contrast = cv2.getTrackbarPos('contrast','Reglage')
            self.w_bal_temp_aut = cv2.getTrackbarPos('w_bal_temp_aut','Reglage')
            self.power_line_freq = cv2.getTrackbarPos('power_line_freq','Reglage')
            self.white_bal_temp = cv2.getTrackbarPos('white_bal_temp','Reglage')
            self.backlight_compensation = cv2.getTrackbarPos('backlight_compensation','Reglage')
            self.pile_size = cv2.getTrackbarPos('pile_size','Reglage')

            ret, frame_read = self.cap.read()
            frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)

            # Image carrée
            frame_rgb = crop(frame_rgb)

            frame_resized = cv2.resize(frame_rgb,
                                       (darknet.network_width(self.netMain),
                                        darknet.network_height(self.netMain)),
                                        interpolation=cv2.INTER_LINEAR)

            darknet.copy_image_from_bytes(self.darknet_image, frame_resized.tobytes())
            # detect_image(net, meta, im, thresh=0.5, hier_thresh=0.5, nms=0.45, debug=False)
            detections, tag, confiance = darknet.detect_image(self.netMain,
                                                              self.metaMain,
                                                              self.darknet_image,
                                                              self.thresh,
                                                              self.hier_thresh,
                                                              self.nms)

            try:
                image = cvDrawBoxes(detections, frame_resized)
            except:
                image = frame_read

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (900, 900), interpolation=cv2.INTER_LINEAR)

            # Lettre lue
            self.lettres_pile.append(tag)
            lettre = self.lettres_pile.all_identical()
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

            # Affichage des trackbars
            cv2.imshow('Reglage', self.reglage_img)

            # Affichage du message
            msg_img = put_text(image, "Message:", (20, 25))
            msg_img = put_text(image, self.msg, (20, 150))

            cv2.imshow('Demo', image)

            # Attente
            k = cv2.waitKey(3)
            # Espace pour reset du message
            if k == 32:
                self.msg = ""
            # Echap pour quitter
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
                     [255, 0, 0],
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
    # A couper de chaque coté
    c = abs(int((a - b)/2))

    return img[0:b, c:c+b]


if __name__ == "__main__":
    try:
        cam = int(sys.argv[1])
    except:
        print("Le 1er argument est le numéro de webcam")
    if cam not in [0,1,2,3,4,5,6]:
        print("Le 1er argument est le numéro de webcam")
        print("Le numéro de cam est 0 ou 1 ou 2 ou 3 ou 4 ou 5 ou 6")
        
    try:
        calcul = int(sys.argv[2])
    except:
        print("Le 2ème argument est le choix du calcul")
        print("Les valeurs possibles sont 1 ou 2 ou 3")
    if calcul not in [1, 2, 3]:
        print("Le 2ème argument est le choix du calcul")
        print("Les valeurs possibles sont 1 ou 2 ou 3")

    try:
        thresh = float(sys.argv[3])
    except:
        print("Le 3ème argument est thresh")
        print("Les valeurs possibles sont entre 0 et 1")
    if 0 < thresh > 1:
        print("Le 3ème argument est thresh")
        print("Les valeurs possibles sont entre 0 et 1")

    try:
        hier_thresh = float(sys.argv[4])
    except:
        print("Le 4ème argument est hier_thresh")
        print("Les valeurs possibles sont entre 0 et 1")
    if 0 < hier_thresh > 1:
        print("Le 4ème argument est hier_thresh")
        print("Les valeurs possibles sont entre 0 et 1")

    try:
        nms = float(sys.argv[5])
    except:
        print("Le 5ème argument est nms")
        print("Les valeurs possibles sont entre 0 et 1")
    if 0 < nms > 1:
        print("Le 5ème argument est nms")
        print("Les valeurs possibles sont entre 0 et 1")

    print(  "Camera:", cam, "\n",
            "Calcul:", calcul, "\n",
            "thresh", thresh, "\n",
            "hier_thresh", hier_thresh, "\n",
            "nms", nms)

    dossier = os.getcwd()
    cf = MyConfig(dossier + "/darknet.ini")
    conf = cf.conf
    apply_all_cam_settings(conf["HD5000"], cam)

    # cam = numéro de cam, calcul=1 ou 2 ou 3 voir wiki
    yolo = YOLO(cam, calcul, cf, thresh, hier_thresh, nms)
    yolo.detect()
