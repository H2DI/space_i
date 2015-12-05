# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 14:58:26 2015

Space invader

@author: h

"""
from sknn.platform import cpu64
from Tkinter import *
import main_jeu as MJ
import numpy as np
import random as rd
from sklearn import metrics
from sknn.mlp import Regressor, Layer
from sknn.backend import lasagne
import pickle

    
class Learn:
    
    nx = 20
    ny = 20
    n_cell = nx * ny
    coups_sautes = 60
    
    #This calculates the distance between two images
    def dist(self, prediction, im3):
        err = 0.
        for i in xrange(len(prediction)):
            err += abs(prediction[i] - im3[i])
        return err / len(prediction)

    def good_shape_2(self, im1, im2):#Good shape for the input (two images)
        tab = np.zeros((1, (Learn.n_cell*2)))
        tab[0, ::] = np.append(im1.flatten(), im2.flatten())
        return tab
    
    def good_shape_1(self, im3):#Good shape for the output (1 image)
        tab = np.zeros((1, (Learn.n_cell)))
        tab[0, ::] = im3.flatten()
        return tab

    def __init__(self, new=False, display=False):
        #       self.possibilities = generate(Learn.n_coups)
#        np.random.shuffle(self.possibilities)
        self.jeu = MJ.Jeu(autorepeat=False, display=display)
        self.jeu.restart(Learn.coups_sautes)
        self.previous_image = self.get_image()
        self.jeu.update_all()
        self.current_image=self.get_image()
        if new:
            self.nn = Regressor(layers=[Layer("Linear", units=(Learn.n_cell*2)), Layer("Linear", units=Learn.n_cell*4), Layer("Linear",units=Learn.n_cell)], learning_rate=0.01, n_iter=1)
            self.nn.fit(self.good_shape_2(self.previous_image, self.current_image), self.good_shape_1(self.current_image))
        else:
            self.nn = pickle.load(open('nn_image_prediction.pkl', 'rb'))
            self.nn.fit(self.good_shape_2(self.previous_image, self.current_image), self.good_shape_1(self.current_image))
        self.current_data_set = []
    

    def play(self, num_iter=1000):
        self.set_display(True)
        predicted_outcome = np.zeros(2**Learn.n_coups)
        for s in xrange(num_iter):
            self.image = self.get_image()
            if (s%100 == 0):
                print s
            outcome = 1
            indice_max=0
            for j, elt in enumerate(self.possibilities):
                a = self.nn.predict(self.good_shape(self.image, elt))[0][0]
                predicted_outcome[j] = a
                if (a>predicted_outcome[indice_max]):
                    indice_max=j
            i=indice_max
            elt = self.possibilities[i][0]
            if (outcome == 1):
                if elt == 1:
                    instr = 'd'
                elif elt == 0:
                    instr = 'q'
                if (self.jeu.update_all(instr) == "Dead"):
                    outcome = 0
                    self.jeu.restart(Learn.coups_sautes)   



    def get_image(self):
        nx_im, ny = 2 * Learn.nx, Learn.ny
        tab = np.ones((nx_im, ny))/2.
        x, y = self.jeu.joueur.position
        x,y=self.jeu.joueur.position
        for elt in self.jeu.missiles:
            x_m, y_m = elt.position
            x_p = x_m - (x - 0.5) 
            if (y_m < 0.5):
                tab[int(nx_im * x_p) % nx_im, int(ny * y_m)] = -1

        return tab[10:30, ::]

    def save_rd_train_set(self, num_iter=5000): # returns a set of situations, choice sequences, and outcomes
        train_set = []
        for i in xrange(num_iter):
            self.jeu.restart(100)
            im1 = self.get_image().flatten()
            self.jeu.update_all()
            im2=self.get_image().flatten()
            self.jeu.update_all()
            im3=self.get_image().flatten()
            train_set.append((im1, im2, im3))
        self.current_data_set = train_set
        return
        
    def intensive_train(self): 
        for training in self.current_data_set:
            im1, im2, im3 = training
            self.nn.fit(self.good_shape_2(im1, im2), self.good_shape_1(im3))
        print "Commence à sauver"
        pickle.dump(self.nn, open('nn_image_prediction.pkl', 'wb'))
        print "NN Saved"
            
    def error_on_train_set(self):
        error = 0.
        for training in self.current_data_set:
            im1, im2, im3=training
            s = self.nn.predict(self.good_shape_2(im1, im2))[0]
            if (rd.random()<0.01):
                print "Differences : "
                print np.max(abs(s-im3))
            error += self.dist(s,im3)
        error = error / len(self.current_data_set)
        return error



a = Learn(new=False)

#a.nn.learning_rate = 0.001


for i in xrange(100):
    print "training no " + str(i)
    a.save_rd_train_set(num_iter=500)
    print "error : " + str(a.error_on_train_set())
    for j in range(5):
        a.intensive_train()



