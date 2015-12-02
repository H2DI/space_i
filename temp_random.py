# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 14:38:58 2015

@author: h
"""

from Tkinter import *
import main_jeu as MJ
import numpy as np
import random as rd

jeu = MJ.Jeu(autorepeat=False, display=False)

temps_total = []
t = 0

while t < 1000:
    for s in range(60):
        jeu.update_all('m')
    while(True):
        r = rd.random()
        if r < 0.5:
            instr = 'q'
        else:
            instr = 'd'
        if jeu.update_all(instr) == "Dead":
            t += 1
            temps_total.append(jeu.temps)
            jeu.restart()
            break

print str(sum(temps_total) / 1000.) + " +/- "+ str(0.96 * np.sqrt(np.var(np.array(temps_total)) / 1000)  )