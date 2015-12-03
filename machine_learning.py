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
    n_coups = 6
    coups_sautes = 60

    def __init__(self, new=False, display=False):
        self.possibilities = generate(Learn.n_coups)
        self.explore = 0.
        self.jeu = MJ.Jeu(autorepeat=False, display=display)
        self.jeu.restart(Learn.coups_sautes)
        self.image = self.get_image()
        if new:
            self.nn = Regressor(layers=[Layer("Linear", units=(Learn.n_cell+Learn.n_coups)), Layer("Sigmoid", units=800), Layer("Sigmoid")], learning_rate=0.01, n_iter=1)
            self.nn.fit(self.good_shape(self.image, self.possibilities[Learn.n_coups/2 - 1]), np.array([[0]]))
        else:
            self.nn = pickle.load(open('nn.pkl', 'rb'))
            self.nn.fit(self.good_shape(self.image, self.possibilities[Learn.n_coups/2 - 1]), np.array([[1]]))


    def good_shape(self, image, instructions):#instructions est un tableau de 0 et 1 à n_coups éléments
        tab = np.zeros((1, (Learn.n_cell + Learn.n_coups)))
        tab[0, ::] = np.append(image.flatten(), instructions)
        return 10 * tab


    def learn(self, num_iter=1000, print_auc=False):
        predicted_outcome = np.zeros(2**Learn.n_coups)
        for s in xrange(num_iter):
            self.image = self.get_image()
            if (s%100 == 0):
                print s
            outcome = 1
            for i, elt in enumerate(self.possibilities):
                predicted_outcome[i] = self.nn.predict(self.good_shape(self.image, elt))[0][0]
            #print predicted_outcome
            i = np.argmax(predicted_outcome)
            r = rd.random()
            if (r < self.explore):
                i = int(rd.random() * 2**(Learn.n_coups))
            for elt in self.possibilities[i]:
                if (outcome == 1):
                    if elt == 1:
                        instr = 'd'
                    elif elt == 0:
                        instr = 'q'
                    if (self.jeu.update_all(instr) == "Dead"):
                        outcome = 0
                        self.jeu.restart(Learn.coups_sautes)
            tab = self.good_shape(self.image, self.possibilities[i])
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
            predicted_outputs.append(self.nn.predict(self.good_shape(self.image, elt))[0])
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
        #t = " "
        for i in xrange(2):
            for j in xrange(2):
                tab[x+i-1, y+j-1] = 0
#        for i in xrange (nx_im / 2):
#            print t
#            t = " "
#            for j in xrange(ny):
#                t += " " + str(tab[10+i][j])
        return tab[10:30, ::]

    def set_display(self, boolean):
        self.display = boolean
        self.jeu = MJ.Jeu(autorepeat=False, display=self.display)
        self.jeu.restart(Learn.coups_sautes)
        self.image = self.get_image()

    def save_rd_train_set(self, num_iter=20000, overwrite=False, train_file=None): # returns a set of situations, choice sequences, and outcomes
        self.jeu.restart(Learn.coups_sautes)        
        if train_file:
            train_set = pickle.load(open(train_file, "rb" ))
        else:
            train_set = pickle.load(open("/Users/Maxime/space_i/train_set.csv", "rb" ))
        if overwrite:
            train_set = []
        for i in xrange(num_iter):
            self.jeu.restart(100)
            im = self.get_image()
            choice = self.possibilities[rd.randint(0, 2**Learn.n_coups-1)]
            outcome = 1
            for elt in choice:
                if (outcome == 1):
                    if elt:
                        instr = 'd'
                    else:
                        instr = 'q'
                    if (self.jeu.update_all(instr) == "Dead"):
                        outcome = 0
            train_set.append((im, choice, outcome))
        if train_file:
            pickle.dump(train_set, open(train_file, "wb"))
        else:
            print "Dataset créé"
            pickle.dump(train_set, open("/Users/Maxime/space_i/train_set.csv", "wb"))
        return
        
    def intensive_train(self, train_file=None): # trainfile is a string
        if train_file:
            train_set = pickle.load(open(train_file, "rb"))
        else:
            train_set = pickle.load(open("/Users/Maxime/space_i/train_set.csv", "rb" ))
        for training in train_set:
            im, choice, outcome = training
            self.nn.fit(self.good_shape(im, choice), np.array([[outcome]]))
        pickle.dump(self.nn, open('nn.pkl', 'wb'))
        print "NN Saved"
            
    def error_on_train_set(self):
        train_set = pickle.load(open("/Users/Maxime/space_i/train_set.csv", "rb" ))
        error = 0.
        for training in train_set:
            im, choice, outcome=training
            s = self.nn.predict(self.good_shape(im,choice))
            #print s[0][0], outcome
            error += abs(s[0][0]-outcome)
        error = error / len(train_set)
        return error
        
    def auc_on_train_set(self):
        train_set = pickle.load(open("/Users/Maxime/space_i/train_set.csv", "rb" ))
        real_outputs = []    
        predicted_outputs = []
        for training in train_set:
            im, choice, outcome = training
            predicted_outputs.append(self.nn.predict(self.good_shape(im, choice))[0])
            real_outputs.append(outcome)
        fpr, tpr, thresholds = metrics.roc_curve(real_outputs, predicted_outputs)
        return metrics.auc(fpr, tpr)
            
            
        
a = Learn(new=False, display=False)
a.save_rd_train_set(num_iter=1000, overwrite=True)

for i in xrange(100):
    print "training no " +  str(i)
    #a.save_rd_train_set(num_iter=5000, overwrite=True)
    a.learn(num_iter=1000)
    #print "auc : " + str(a.auc_on_train_set())
    #for j in range(10):
        #a.intensive_train()

