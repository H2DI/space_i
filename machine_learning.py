# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 14:58:26 2015

Space invader

@author: h

"""

from Tkinter import *
import main_jeu as MJ
import numpy as np
import random as rd

from sknn.platform import gpu32

from sknn.mlp import Regressor, Layer
from sknn.backend import lasagne
import pickle



nx = 40
ny = 40

n_coups = 6

jeu = MJ.Jeu(autorepeat=False, display=False)

nn = pickle.load(open('nn.pkl', 'rb'))
#nn = Regressor(layers=[Layer("Sigmoid", units=(1600+n_coups)),Layer("Sigmoid",units=500), Layer("Sigmoid")], learning_rate=0.05, n_iter=10)


def good_shape(jeu, instructions):#instructions est un tableau de 0 et 1 à 7 éléments
    tab = np.zeros((1, (1600+n_coups)))
    tab[0,::] = np.append(jeu.get_image().flatten(), instructions)
    return tab

#appeler predict(tab) ou fit(tab, np.array([["OUTCOME"]]))
def generate(n):
    result = np.zeros((2**n,n))
    for i in xrange(1, 2**n):
        aux = i
        tab = np.zeros(n)
        for j in range(n):
            tab[j] = aux % 2
            aux = aux / 2
        result[i, ::]  = tab
    return result

possibilities = generate(n_coups)
predicted_outcome = np.zeros(2**(n_coups))

nn.fit(good_shape(jeu, possibilities[2**(n_coups-1)]) , np.array([[1]]))


for s in range(80):
    jeu.update_all('m')

num_iter = 1000

global score_moyen
global nombre_de_morts
score_moyen = 0
nombre_de_morts = 0

def restart_for_learning():
    global outcome
    global score_moyen
    global nombre_de_morts
    outcome = 0
    print score_moyen
    print nombre_de_morts
    score_moyen = (nombre_de_morts * score_moyen + jeu.temps) / float(nombre_de_morts + 1)
    nombre_de_morts += 1
    jeu.restart()
    for s in range(80):
        jeu.update_all('m')

global outcome

for s in xrange(num_iter):
    for i, elt in enumerate(possibilities):
        predicted_outcome[i] = nn.predict(good_shape(jeu, elt))
#print predicted_outcome
    i = np.argmax(predicted_outcome)
    r = rd.random()
    if (r < 0.5):
        i = int(rd.random() * 2**(n_coups))
    outcome = 1
    for elt in possibilities[i]:
        if (outcome == 1):
            if (jeu.update_all() == "Dead"):
                restart_for_learning()
            if elt:
                instr = 'd'
            else:
                instr = 'q'
            if (jeu.update_all(instr) == "Dead"):
                restart_for_learning
    tab = good_shape(jeu, possibilities[i])
    nn.fit(tab, np.array([[outcome]]))


pickle.dump(nn, open('nn.pkl', 'wb'))
print "Saved"
