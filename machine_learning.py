# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 14:58:26 2015

Space invader

@author: h

"""

from Tkinter import *
import main_jeu as MJ
import random as rd
import theano


Jeu = MJ.Jeu(autorepeat=False)

for i in xrange(100000):
    m = 'd'
    i = rd.random()
    if (i < 0.333):
        m='m'
    elif (i < 0.6666):
        m='q'
    s = Jeu.update_all(m)
    if not(s == "Dead"):
        print s
    else:
        Jeu.restart()

