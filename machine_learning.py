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
        self.possibilities = generate(Learn.n_coups)
        np.random.shuffle(self.possibilities)
        self.explore = 0.
        self.jeu = MJ.Jeu(autorepeat=False, display=display)
        self.jeu.restart(Learn.coups_sautes)
        self.image = self.get_image()
        if new:
            self.nn = Regressor(layers=[Layer("Linear", units=(Learn.n_cell+Learn.n_coups)), Layer("Sigmoid", units=1000), Layer("Sigmoid")], learning_rate=0.01, n_iter=1)
            self.nn.fit(self.good_shape(self.image, self.possibilities[Learn.n_coups/2 - 1]), np.array([[0]]))
        else:
            self.nn = pickle.load(open('nn.pkl', 'rb'))
            self.nn.fit(self.good_shape(self.image, self.possibilities[Learn.n_coups/2 - 1]), np.array([[1]]))
        self.current_data_set = []

    def good_shape(self, image, instructions):#instructions est un tableau de 0 et 1 à n_coups éléments
        tab = np.zeros((1, (Learn.n_cell + Learn.n_coups)))
        tab[0, ::] = np.append(image.flatten(), instructions)
        return 10 * tab

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
                if a>0.99:
                    i=j
                    break
                elif (a>predicted_outcome[indice_max]):
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
        print str(sum(temps_total)*1. / num_iter) +" +/- "+ str(0.96 * np.sqrt(np.var(np.array(temps_total)) / num_iter)  )


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

    def set_display(self, boolean):
        self.display = boolean
        self.jeu = MJ.Jeu(autorepeat=False, display=self.display)
        self.jeu.restart(Learn.coups_sautes)
        self.image = self.get_image()

    def save_rd_train_set(self, num_iter=5000): # returns a set of situations, choice sequences, and outcomes
        #self.jeu.rand_init(40)
        train_set = []
        for i in xrange(num_iter):
            self.jeu.restart(100)
            im = self.get_image()
            choice = self.possibilities[rd.randint(0, 2**Learn.n_coups-1)]
            outcome = 1
            #print [b.position for b in self.jeu.missiles]
            for elt in choice:
                if (outcome == 1):
                    if elt:
                        instr = 'd'
                    else:
                        instr = 'q'
                    if (self.jeu.update_all(instr) == "Dead"):
                        outcome = 0
            train_set.append((im, choice, outcome))
        self.current_data_set = train_set
        return
        
    def intensive_train(self): 
        for training in self.current_data_set:
            im, choice, outcome = training
            self.nn.fit(self.good_shape(im, choice), np.array([[outcome]]))
        print "Commence à sauver"
        pickle.dump(self.nn, open('nn.pkl', 'wb'))
        print "NN Saved"
            
    def error_on_train_set(self):
        error = 0.
        for training in self.current_data_set:
            im, choice, outcome=training
            s = self.nn.predict(self.good_shape(im,choice))
            error += abs(s[0][0]-outcome)
        error = error / len(train_set)
        return error
        
    def auc_on_train_set(self):
        real_outputs = []    
        predicted_outputs = []
        for training in self.current_data_set:
            im, choice, outcome = training
            predicted_outputs.append(self.nn.predict(self.good_shape(im, choice))[0])
            real_outputs.append(outcome)
        fpr, tpr, thresholds = metrics.roc_curve(real_outputs, predicted_outputs)
        return metrics.auc(fpr, tpr)
            
            
a = Learn(new=True,display=False)

a.nn.learning_rate = 0.005

#
#for i in xrange(100):
#    print "training no " + str(i)
#    a.save_rd_train_set(num_iter=5000)
#    print "auc : " + str(a.auc_on_train_set())
#    for j in range(5):
#        a.intensive_train()



a.play(num_iter=100000)
