#!/bin/bash
# -*- coding: UTF-8 -*-


export PATH=/usr/local/cuda-10.0/bin${PATH:+:${PATH}}

python3 get_semaphore_message.py 0 2 0.5 0.5 0.45
