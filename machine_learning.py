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

from sklearn import metrics
from sknn.mlp import Regressor, Layer
from sknn.backend import lasagne
import pickle


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
    
class Learn:
    
    nx = 20
    ny = 20
    n_cell = nx * ny
    n_coups = 8
    coups_sautes = 60

    def __init__(self, new=False, display=False):
        self.possibilities=generate(Learn.n_coups)
        self.explore = 0.2
        self.jeu = MJ.Jeu(autorepeat=False, display=display)
        self.jeu.restart(Learn.coups_sautes)
        self.image = self.get_image()
        if new:
            self.nn = Regressor(layers=[Layer("Sigmoid", units=(Learn.n_cell+Learn.n_coups)),Layer("Sigmoid", units=300), Layer("Sigmoid")], learning_rate=0.05, n_iter=1)
            self.nn.fit(self.good_shape(self.possibilities[Learn.n_coups/2 - 1]), np.array([[1]]))
        else:
            self.nn = pickle.load(open('nn.pkl', 'rb'))
            self.nn.fit(self.good_shape(self.possibilities[Learn.n_coups/2 - 1]), np.array([[1]]))

    def good_shape(self, instructions):#instructions est un tableau de 0 et 1 à 7 éléments
        tab = np.zeros((1, (Learn.n_cell + Learn.n_coups)))
        a = self.image
        tab[0, ::] = np.append(a.flatten(), instructions)
        return tab


    def learn(self, num_iter=1000, disp_mean_t=False):
        predicted_outcome = np.zeros(2**Learn.n_coups)
        t = 0.
        n_morts = 0
        for s in xrange(num_iter):
            outcome = 1
            for i, elt in enumerate(self.possibilities):
                predicted_outcome[i] = self.nn.predict(self.good_shape(elt))
            i = np.argmax(predicted_outcome)
            r = rd.random()
            if (r < self.explore):
                i = int(rd.random() * 2**(Learn.n_coups))
            for elt in self.possibilities[i]:
                if (outcome == 1):
                    if elt:
                        instr = 'd'
                    else:
                        instr = 'q'
                    if (self.jeu.update_all(instr) == "Dead"):
                        outcome = 0
                        n_morts += 1
                        if disp_mean_t:
                            t =  (t * (n_morts - 1) + self.jeu.temps) / n_morts
                            print t, self.jeu.temps
                        self.jeu.restart(Learn.coups_sautes)
            self.image = self.get_image()
            tab = self.good_shape(self.possibilities[i])
            self.nn.fit(tab, np.array([[outcome]]))
        pickle.dump(self.nn, open('nn.pkl', 'wb'))
        print "NN Saved"
        
        
    def auc(self, num_iter=10000):
        real_outputs = []
        predicted_outputs = []
        for s in xrange(num_iter):
            outcome = 1
            poss = self.possibilities
            i = rd.randint(0, len(poss))
            elt = poss[i]
            predicted_outputs.append(self.nn.predict(self.good_shape(elt)))
            r = rd.random()
            if (r < 1):
                i = int(rd.random() * 2**(Learn.n_coups))
            for elt in possibilities[i]:
                if (outcome == 1):
                    if elt:
                        instr = 'd'
                    else:
                        instr = 'q'
                    if (jeu.update_all(instr) == "Dead"):
                        outcome = 0
                        self.jeu.restart(Learn.coups_sautes)
            real_outputs.append(outcome)
            self.image = self.get_image()        
        fpr, tpr, thresholds = metrics.roc_curve(real_outputs, predicted_outputs)
        return metrics.auc(fpr, tpr)
    
    def benchmark(self, num_iter=1000):
        temps_total = []
        t = 0
        while t < num_iter:
            self.jeu.restart(Learn.coups_sautes)
            while(True):
                r = rd.random()
                if r < 0.5:
                    instr = 'q'
                else:
                    instr = 'd'
                if self.jeu.update_all(instr) == "Dead":
                    t += 1
                    temps_total.append(self.jeu.temps)
                    self.jeu.restart()
                    break
        self.image = self.get_image()
        print str(sum(temps_total) / num_iter.) + " +/- "+ str(0.96 * np.sqrt(np.var(np.array(temps_total)) / num_iter)  )

    def get_image(self):
        nx_im, ny = 2 * Learn.nx, Learn.ny
        tab = np.zeros((nx_im, ny))
        x, y = self.jeu.joueur.position
        for elt in self.jeu.missiles:
            x_m, y_m = elt.position
            x_p = x_m - (x - 0.5) 
            if (y_m < 0.5):
                tab[int(nx_im * x_p) % nx_im, int(ny * y_m)] = 1
        x = 0.5 * nx_im
        y = y * ny
        for i in xrange(5):
            for j in xrange(5):
                tab[x+i-5, y+j-5] = -1
        return tab[10:30, ::]


#==============================================================================
# predicted_outputs = []
# real_outputs = []
# 
# for s in xrange(num_iter):
#     #for i, elt in enumerate(possibilities):
#         #predicted_outcome[i] = nn.predict(good_shape(jeu, elt))
#     #i = np.argmax(predicted_outcome)
#     r = rd.random()
#     if (r < 1):
#         i = int(rd.random() * 2**(n_coups))
#     outcome = 1
#     predicted_outcome = nn.predict(good_shape(jeu, possibilities[i]))
#     for elt in possibilities[i]:
#         if (outcome == 1):
#             if (jeu.update_all() == "Dead"):
#                 restart_for_learning()
#             if elt:
#                 instr = 'd'
#             else:
#                 instr = 'q'
#             if (jeu.update_all(instr) == "Dead"):
#                 restart_for_learning()
#     tab = good_shape(jeu, possibilities[i])
#     predicted_outputs.append(predicted_outcome[0])
#     real_outputs.append(outcome)
#     #nn.fit(tab, np.array([[outcome]]))
# 
# 
# fpr, tpr, thresholds = metrics.roc_curve(real_outputs, predicted_outputs)
# print metrics.auc(fpr, tpr)
# 
# 
# 
# pickle.dump(nn, open('nn.pkl', 'wb'))
# print "Saved"
#==============================================================================
