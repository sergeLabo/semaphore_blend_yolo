# semaphore blend yolo

Un sémaphore a été construit dans le monde réél avec des pièces réalisées sur Imprimante 3D.
Ce projet crée ce même sémaphore dans le Blender Game Engine donc dans un monde virtuel. Ce sémaphore est parfait.
Cela permet d'obtenir 60 000 images pour l'apprentissage et le test de l'intelligence de Yolo Darknet V3.
Le BGE permet de faire varier les éclairage et leur couleurs, de le faire bouger et donner du random sur les angles des bras.


<img src="/doc/shot_106_y.png" width="300" height="300">

### Contexte

Réalisé avec:

* Debian 10 Buster
* Blender 2.79b
* python3.7


### La documentation sur ressources.labomedia.org

[Un vrai sémaphore reconnu avec Yolo Darknet](https://ressources.labomedia.org/2019_04/yolo_darknet_avec_un_vrai_semaphore)

### Dossiers des images

Les images ne sont pas dans ce dépôt.

### Installation

### pip3

~~~text
sudo apt install python3-pip
~~~

#### pymultilame

~~~text
sudo pip3 install -e git+https://github.com/sergeLabo/pymultilame.git#egg=pymultilame
~~~

Mise à jour:
~~~text
sudo pip3 install --upgrade git+https://github.com/sergeLabo/pymultilame.git#egg=pymultilame
~~~

#### Blender 2.79b mais pas 2.80 qui n'a plus de BGE

~~~text
sudo apt install blender
~~~

### Utilisation

Important: Ne pas déplacer ou agrandir la fenêtre de Blender pendant que les
images défilent.

#### Contrôle de la pertinence des fichiers txt
Avec le script control.py du dossier control

### Merci à:

* [La Labomedia](https://ressources.labomedia.org)
