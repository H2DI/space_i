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
    n_coups = 4
    coups_sautes = 60

    def __init__(self, new=False, display=False):
        self.possibilities=generate(Learn.n_coups)
        self.explore = 0.8
        self.jeu = MJ.Jeu(autorepeat=False, display=display)
        self.jeu.restart(Learn.coups_sautes)
        self.image = self.get_image()
        if new:
            self.nn = Regressor(layers=[Layer("Linear", units=(Learn.n_cell+Learn.n_coups)),Layer("Linear", units=800), Layer("Sigmoid")], learning_rate=0.1, n_iter=1)
            self.nn.fit(self.good_shape(self.possibilities[Learn.n_coups/2 - 1]), np.array([[0]]))
        else:
            self.nn = pickle.load(open('nn.pkl', 'rb'))
            self.nn.fit(self.good_shape(self.possibilities[Learn.n_coups/2 - 1]), np.array([[1]]))

    def good_shape(self, instructions):#instructions est un tableau de 0 et 1 à 7 éléments
        tab = np.zeros((1, (Learn.n_cell + Learn.n_coups)))
        a = self.image
        tab[0, ::] = np.append(a.flatten(), instructions)
        return tab


    def learn(self, num_iter=1000, disp_mean_t=False,print_auc=False):
        predicted_outcome = np.zeros(2**Learn.n_coups)
        t = 0.
        n_morts = 0
        for s in xrange(num_iter):
            if (s%100==0):
                print s
            outcome = 1
            for i, elt in enumerate(self.possibilities):
                predicted_outcome[i] = self.nn.predict(self.good_shape(elt))
            print predicted_outcome
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
            if (s % 1000 == 0):
                if print_auc:
                    print  "New auc is : ", learn.auc(num_iter=10000)
                pickle.dump(self.nn, open('nn.pkl', 'wb'))
                print "NN Saved"
        
        
    def auc(self, num_iter=10000):
        real_outputs = []
        predicted_outputs = []
        for s in xrange(num_iter):
            outcome = 1
            poss = self.possibilities
            i = rd.randint(0, len(poss)-1)
            elt = poss[i]
            predicted_outputs.append(self.nn.predict(self.good_shape(elt))[0])
            r = rd.random()
            if (r < 0.8):
                i = int(rd.random() * 2**(Learn.n_coups))
            for elt in self.possibilities[i]:
                if (outcome == 1):
                    if elt:
                        instr = 'd'
                    else:
                        instr = 'q'
                    if (self.jeu.update_all(instr) == "Dead"):
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
        print str(sum(temps_total)*1. / num_iter) + " +/- "+ str(0.96 * np.sqrt(np.var(np.array(temps_total)) / num_iter)  )

    def get_image(self):
        nx_im, ny = 2 * Learn.nx, Learn.ny
        tab = np.ones((nx_im, ny))/2.
        x, y = self.jeu.joueur.position
        for elt in self.jeu.missiles:
            x_m, y_m = elt.position
            x_p = x_m - (x - 0.5) 
            if (y_m < 0.5):
                tab[int(nx_im * x_p) % nx_im, int(ny * y_m)] = 1
        x = 0.5 * nx_im
        y = y * ny
        for i in xrange(2):
            for j in xrange(2):
                tab[x+i-1, y+j-1] = 0
#        for i in xrange (nx_im/2):
#            print t
#            t=" "
#            for j in xrange(ny):
#                t+=" " + str(tab[10+i][j])
        return tab[10:30, ::]

    def set_display(self, bool):
        self.display=bool
        self.jeu = MJ.Jeu(autorepeat=False, display=self.display)
        self.jeu.restart(Learn.coups_sautes)
        self.image = self.get_image()

learn=Learn(new=True, display=True)
learn.learn(num_iter=10000, disp_mean_t=False)
