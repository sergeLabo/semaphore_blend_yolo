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

    def __init__(self, cam, calcul, conf):
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

        # Paramètres de detections
        self.thresh = self.cf.conf['darknet']['thresh']
        self.hier_thresh = self.cf.conf['darknet']['hier_thresh']
        self.nms = self.cf.conf['darknet']['nms']

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
        thresh            min 0 max 1
        hier_thresh       min 0 max 1
        nms               min 0 max 1
        """
        cv2.namedWindow('Reglage')
        self.reglage_img = np.zeros((10, 1000, 3), np.uint8)

        cv2.createTrackbar('brightness', 'Reglage', 0, 255, self.onChange_brightness)
        cv2.createTrackbar('contrast', 'Reglage', 0, 10, self.onChange_contrast)
        cv2.createTrackbar('saturation', 'Reglage', 0, 200, self.onChange_saturation)
        cv2.createTrackbar('w_bal_temp_aut', 'Reglage', 0, 1, self.onChange_w_bal_temp_aut)
        cv2.createTrackbar('power_line_freq', 'Reglage', 0, 2, self.onChange_power_line_freq)
        cv2.createTrackbar('white_bal_temp', 'Reglage', 2800, 10000, self.onChange_white_bal_temp)
        cv2.createTrackbar('backlight_compensation', 'Reglage', 0, 10, self.onChange_backlight_compensation)
        cv2.createTrackbar('exposure_auto', 'Reglage', 0, 3, self.onChange_exposure_auto)
        cv2.createTrackbar('exposure_absolute', 'Reglage', 5, 20000, self.onChange_exposure_absolute)

        cv2.createTrackbar('threshold', 'Reglage', 0, 100, self.onChange_thresh)
        # ~ cv2.createTrackbar('hier_thresh', 'Reglage', 0, 100, self.onChange_hier_thresh)
        # ~ cv2.createTrackbar('nms', 'Reglage', 0, 100, self.onChange_nms)

        cv2.createTrackbar('pile_size', 'Reglage', 0, 60, self.onChange_pile_size)

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

        cv2.setTrackbarPos('threshold', 'Reglage', self.thresh)
        # ~ cv2.setTrackbarPos('hier_thresh', 'Reglage', self.hier_thresh)
        # ~ cv2.setTrackbarPos('nms', 'Reglage', self.nms)

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

    def onChange_thresh(self, thresh):
        """min=1 max=100 step=1 default=0.5"""
        if thresh == 0: thresh = 5
        if thresh == 100: thresh = 95
        self.thresh = int(thresh)
        self.save_change('darknet', 'thresh', self.thresh)

    def onChange_hier_thresh(self, hier_thresh):
        """min=1 max=100 step=1 default=0.5"""
        if hier_thresh == 0: hier_thresh = 5
        if hier_thresh == 100: hier_thresh = 95
        self.hier_thresh = int(hier_thresh)
        self.save_change('darknet', 'hier_thresh', self.hier_thresh)

    def onChange_nms(self, nms):
        """min=1 max=100 step=1 default=0.5"""
        if nms == 0: nms = 5
        if nms == 100: nms = 95
        self.nms = int(nms)
        self.save_change('darknet', 'nms', self.nms)

    def onChange_pile_size(self, pile_size):
        """min=1 max 60
        """
        if pile_size == 0: pile_size = 1
        self.pile_size = int(pile_size)
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
            self.thresh = cv2.getTrackbarPos('threshold','Reglage')
            # ~ self.hier_thresh = cv2.getTrackbarPos('hier_thresh','Reglage')
            # ~ self.nms = cv2.getTrackbarPos('nms','Reglage')
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
                                                              self.thresh/100,
                                                              self.hier_thresh/100,
                                                              self.nms/100)

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

            # Rafraichissement du message
            if len(self.msg) > 100:
               self.msg = ""

            # A la ligne, tous les ln charactères
            ln = 20
            msg = textwrap.fill(self.msg, ln)
            msg = msg.splitlines()

            # Affichage du message
            put_text(image, "Message:", (20, 45))
            for i in range(len(msg)):
                y = int(105 + 50*i)
                put_text(image, msg[i], (20, y))

            put_text(image, "Espace: reset du message", (20, 870))

            # Affichage du Semaphore
            cv2.imshow('Semaphore', image)
            # Affichage des trackbars
            cv2.imshow('Reglage', self.reglage_img)

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

    cv2.putText(img,
                text,
                (xy[0], xy[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                2.0,
                [255, 0, 0],
                2,
                cv2.LINE_AA)


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

    print(  "Camera:", cam, "\n",
            "Calcul:", calcul, "\n")

    dossier = os.getcwd()
    cf = MyConfig(dossier + "/darknet.ini")
    conf = cf.conf
    apply_all_cam_settings(conf["HD5000"], cam)

    # cam = numéro de cam, calcul=1 ou 2 ou 3 voir wiki
    yolo = YOLO(cam, calcul, cf)
    yolo.detect()
