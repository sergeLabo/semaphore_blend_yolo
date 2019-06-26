# Semaphore Blend Yolo

Un sémaphore a été construit dans le monde réel avec des pièces réalisées sur Imprimante 3D.
Ce projet crée ce même sémaphore dans le Blender Game Engine donc dans un monde virtuel dans lequel je suis dieu tout puissant. Ce sémaphore est parfait.
Cela permet d'obtenir 60 000 images pour l'apprentissage et le test de l'intelligence de Yolo Darknet V3.
Le BGE permet de faire varier les éclairage et leur couleurs, de le faire bouger et donner du random sur les angles des bras.

Par contre, le BGE ne permet une sortie d'image qu'en png. Il faut les convertir en jpg et les flouter en convolutive.

<img src="/doc/shot_106_y.png" width="400" height="400"><img src="/darknet/calcul_3/chart_big_var_12000.png" width="400" height="400">


### Contexte

Réalisé avec:

* Debian 10 Buster et Xubuntu 18.04 pour CUDA
* Blender 2.79b
* python 3.7
* opencv 3.4.5.20
* cuda-10-0
* libcudnn7=7.4.1.5-1+cuda10.0
* yolo darknet v3

### La documentation sur ressources.labomedia.org

* [Un vrai sémaphore reconnu avec Yolo Darknet](https://ressources.labomedia.org/y/yolo_darknet_avec_un_vrai_semaphore)
* [La reconnaissance sur un Nvidia Jetson Nano](https://ressources.labomedia.org/nvidia_jetson_nano)

### Le dossiers des images n'est pas dans ce dépôt.

### Installation

* [Installation de CUDA 10.0 sur Xubuntu 18.04](https://ressources.labomedia.org/y/yolo_darknet_sur_un_portable_optimus#installation_de_cuda_100_sur_xubuntu_1804)
* [Installation de YOLO Darknet](https://ressources.labomedia.org/y/yolo_darknet_sur_un_portable_optimus#installation_de_yolo_darknet)

#### Divers
uvcdynctrl est utilisé pour régler la caméra en python, et v4l2ucp permet de tester les réglages en temps réel
~~~~text
sudo apt install uvcdynctrl v4l2ucp
~~~~

### Lecture d'un message avec un vrai sémaphore
et une webcam Microsoft HD5000
* [Reconnaissance dans le monde réel](https://ressources.labomedia.org/y/yolo_darknet_avec_un_vrai_semaphore#reconnaissance_dans_le_monde_reel)

### Merci à:

* [La Labomedia](https://ressources.labomedia.org)
