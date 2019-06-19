#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
Capture d'un texte au clavier
"""

from time import sleep

from bge import events
from bge import logic as gl


ALL_KEYS = {events.AKEY: "A",
            events.BKEY: "B",
            events.CKEY: "C",
            events.DKEY: "D",
            events.EKEY: "E",
            events.FKEY: "F",
            events.GKEY: "G",
            events.HKEY: "H",
            events.IKEY: "I",
            events.JKEY: "J",
            events.KKEY: "K",
            events.LKEY: "L",
            events.MKEY: "M",
            events.NKEY: "N",
            events.OKEY: "O",
            events.PKEY: "P",
            events.QKEY: "Q",
            events.RKEY: "R",
            events.SKEY: "S",
            events.TKEY: "T",
            events.UKEY: "U",
            events.VKEY: "V",
            events.WKEY: "W",
            events.XKEY: "X",
            events.YKEY: "Y",
            events.ZKEY: "Z",
            events.SPACEKEY: " "}


def input_one_chars():
    """ALL_KEYS = { events.AKEY: 'A',  ... """

    for key, val in ALL_KEYS.items():
        if gl.keyboard.events[key] == gl.KX_INPUT_JUST_ACTIVATED:
            gl.captured_text += val
            if len(gl.captured_text) % 26 == 0:
                gl.captured_text += "\n"
            if len(gl.captured_text) > 50:
                gl.captured_text = ""


def special_keys():
    """Pas utilisé"""
    
    if gl.keyboard.events[events.PAD1] == gl.KX_INPUT_JUST_ACTIVATED:
        gl.one = 1
        gl.two = 0
        gl.enter = 0
        print("gl.one", gl.one)

    if gl.keyboard.events[events.PAD2] == gl.KX_INPUT_JUST_ACTIVATED:
        gl.two = 1
        gl.one = 0
        gl.enter = 0
        gl.captured_text = ""
        gl.captured_lettre = 0
        print("gl.two", gl.two)


def enter():
    if gl.keyboard.events[events.ENTERKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        gl.enter = 1
        print("gl.enter", gl.enter)


def backspace():
    if gl.keyboard.events[events.BACKSPACEKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        gl.backspace = 1
        print("gl.backspace", gl.backspace)
        try:
            gl.captured_text = gl.captured_text[:-1]
        except:
            gl.captured_text = ""


def input_text():
    input_one_chars()
    backspace()
    enter()
