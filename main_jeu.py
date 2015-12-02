# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 15:36:17 2015

Space invader

@author: h
"""


from Tkinter import *

import random as rd
from math import sqrt
import space_i as SI
import numpy as np


T = 600 # Taille de la fenêtre

def convert_coordinates((x, y)): # Convertit les coordonnées du jeu pour les réajuster dans la fenêtre
    return T * x, T * (1 - y)

def appartient(l,x):
    for elt in l:
        if elt==x:
            return True
    return False

class Jeu(Tk):
    
    delta_t = 25 # Durée d'une frame, en ms
    
    def __init__(self, autorepeat=True,display=True):
        Tk.__init__(self)
        print "Jeu créé"
        self.joueur = SI.Joueur()
        self.mechants = []
        for i in xrange(10):
            self.mechants.append(SI.Mechant())
        self.temps = 0
        self.missiles = []
        self.score = 0
        self.display=display
        self.instruction='m'
        self.dead_screen = False
        self.frame = Frame(self, width=T, height=T)
        self.canvas = Canvas(self, width=T, height=T, bg="black")
        self.canvas.pack()
        self.canvas.create_text(T-50, T-50, text="Vies : "+str(self.joueur.vies), fill="white", tag="vie")
        self.canvas.create_text(100, T-50, text="Temps (score) : "+str(self.temps) + " ("+str(self.score) + ")", fill="white", tag="score")
        self.autorepeat = autorepeat
        self.update_all()        
        
    def restart(self):
        print "Restart"
        self.joueur.reinitialiser()
        self.mechants = []
        for i in xrange(10):
            self.mechants.append(SI.Mechant())
        self.missiles = []
        self.score = 0
        self.temps = 0
        self.instruction = 'm'
        self.dead_screen = False
        self.canvas.config(bg="black")
        self.canvas.pack()
        self.canvas.itemconfigure("vie", text="Vies : "+str(self.joueur.vies))
        self.canvas.itemconfigure("score", text="Temps (score) : "+str(self.temps) + " ("+str(self.score) + ")", fill="white")
        self.canvas.delete("dead")
    
        
    def implement_action(self):
        #print self.instruction
        if self.instruction == 'd':
            self.joueur.bouger(1, Jeu.delta_t)
        elif self.instruction == 'q':
            self.joueur.bouger(-1, Jeu.delta_t)
        elif self.instruction == 'z':
            self.instruction='m'
            self.missiles.append(SI.Missile(self.joueur.position, direction=1))
                
    def update_all(self,instruction='m'):
        self.instruction=instruction
        self.temps += 1
        if not(self.joueur.alive):
            return "Dead"
        if self.display:
            self.afficher()
        #print len(self.missiles)
        self.implement_action()
        r = rd.random()
        if (r < 0.04 and len(self.mechants)<40):
            self.mechants.append(SI.Mechant())
        mechants_to_delete = []
        missiles_to_delete = []
        for j, missile in enumerate(self.missiles):
            missile.bouger(Jeu.delta_t)
            if missile.out_of_bounds():
                missiles_to_delete.append(j)
            elif missile.detecter_collision_joueur(self.joueur):
                self.joueur.touched()
                missiles_to_delete.append(j)
        for i, mechant in enumerate(self.mechants):
            mechant.bouger(Jeu.delta_t)
            r = rd.random()
            if (r<0.04 and len(self.missiles)<100):
                self.missiles.append(SI.Missile(mechant.position, direction=-1))
            for j, missile in enumerate(self.missiles):
                if missile.detecter_collision_mechant(mechant):
                    self.score += 1
                    if not(appartient(mechants_to_delete,i)):
                        mechants_to_delete = [i] + mechants_to_delete
                    if not(appartient(missiles_to_delete,j)):
                        missiles_to_delete = [j] + missiles_to_delete
        for elt in mechants_to_delete:
            self.mechants.pop(elt)
        for elt in missiles_to_delete:
            self.missiles.pop(elt)
        if self.autorepeat:
            self.canvas.after(Jeu.delta_t, self.update_all)
        #else:
            #return self.temps,self.joueur.vies,self.get_image()
    
    
    def get_image(self):
        nx=40
        ny=40
        tab = np.zeros((nx, ny))
        for elt in self.missiles:
            x, y = elt.position
            if (y<0.5):
                tab[int(nx*x),int(ny*y)] = 1
        x,y=self.joueur.position
        x=x*nx
        y=y*ny
        for i in xrange(5):
            for j in xrange(5):
                tab[x+i-5,y+j-5]=-1
        return tab
    
    
    
    
    
    def afficher(self):
        if not(self.joueur.alive):
            if not(self.dead_screen): # S'active à l'instant où on meurt
                self.dead_screen = True
                self.canvas.configure(bg="red")
                self.canvas.create_text(T / 2 , T / 2, text="WASTED", fill="white", tag="dead", font=("Purisa", 32))
                self.canvas.create_text(T / 2 - 3 , T / 2 + 30, text="Restart?", fill="white", tag="dead")
                self.canvas.tag_bind('dead', '<Button-1>', self.restart)
                self.canvas.pack()
        else:
            self.canvas.itemconfigure("score", text="Temps (score) : "+str(self.temps / 10) + " ("+str(self.score) + ")")
            self.canvas.itemconfigure("vie", text="Vies : "+str(self.joueur.vies))
            self.canvas.delete("missiles")
            self.canvas.delete("mechants")
            self.canvas.delete("joueur")
            self.afficher_joueur(self.joueur)
            for mechant in self.mechants:
                self.afficher_mechant(mechant)
            for missile in self.missiles:
                self.afficher_missile(missile)
            self.canvas.update()
        return
        
    def afficher_mechant(self, mechant):
        (x,y) = convert_coordinates(mechant.position)
        c = SI.Mechant.m_size * T / 2
        #print (x+c),(y+c),(y-c),(x-c)
        self.canvas.create_rectangle(x+c, y+c, x-c, y-c, fill="red", tag="mechants")
    
    def afficher_missile(self, missile):
        (x,y) = convert_coordinates(missile.position)
        c = SI.Missile.missile_size * T / 2
        self.canvas.create_rectangle(x+c, y+c, x-c, y-c, fill="yellow", tag="missiles")
        
    def afficher_joueur(self, joueur):
        (x,y) = convert_coordinates(joueur.position)
        c = SI.Joueur.j_size * T / 2
        #print (x+c),(y+c),(y-c),(x-c)
        self.canvas.create_rectangle(x+c, y+c, x-c, y-c, fill="white", tag="joueur")

#Jeu(autorepeat=True).mainloop()