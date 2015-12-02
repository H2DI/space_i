# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 14:58:26 2015

Space invader

@author: h
"""

#import Tkinter as tk
import random as rd

class Mechant:
    
    m_size = 0.05 # le méchant est carré de côté j_size
    
    def __init__(self):
        self.position = self._init_position()
        self.vitesse = self._init_vitesse()
        
    def _init_position(self):
        r = rd.random()* (1 - 2 * Mechant.m_size / 2) + Mechant.m_size / 2 #ramener entre m_size/2 et 1-m_size/2
        return  r, 0.9
    
    def _init_vitesse(self):
        r = rd.random()
        if r > 0.5:
            return 0.03 / 6 , 0
        else:
            return - 0.03 / 6, 0
        
    def bouger(self , delta_t): # change la vitesse si au bord
        x, y = self.position
        vx, vy = self.vitesse
        if x < Mechant.m_size / 2 or x > 1 - Mechant.m_size / 2:
            self.vitesse = -vx, vy
        vx, vy = self.vitesse
        self.position = x + vx * delta_t / 50, y + vy * delta_t / 50
        return
    
    def tirer(self):
        Missile(self.position, direction=-1)
        return
    
    def afficher(self):
        return
            

class Joueur:
    
    j_size = 0.05 # le joueur est carré de côté j_size 0.05
    vitesse = 0.1 / 6
    
    def __init__(self):
        self.position = 0.5, 0.1
        self.vies = 0
        self.alive = True
    
    def reinitialiser(self):
        self.position = 0.5, 0.1
        self.vies = 0
        self.alive = True
    
    def bouger(self, i, delta_t):
        x, y = self.position
        if -Joueur.j_size / 2 < x < 1 + Joueur.j_size / 2:
            self.position = x + i * Joueur.vitesse * delta_t / 50, y
        elif -Joueur.j_size / 2 > x:
            self.position = 1., y
        elif x > 1 + Joueur.j_size / 2:  
            self.position = 0, y

    def touched(self):
        if self.vies > 0:
            self.vies -= 1
        else:
            self.alive = False
        

class Missile:
    
    v_missile = 0.1 / 6
    missile_size = 0.01
    
    def __init__(self, position, direction=1):
        self.position = position
        self.vitesse = direction * Missile.v_missile # direction is 1 or -1
        return
    
    # le joueur est carré de côté j_size
    def detecter_collision_joueur(self, joueur):
        if (self.vitesse <= 0):
            x, y = joueur.position
            x_mis, y_mis = self.position
            return abs(x - x_mis) < Joueur.j_size / 2  and abs(y - y_mis) < Joueur.j_size / 2
    
    def detecter_collision_mechant(self, mechant):
        if (self.vitesse >= 0):
            x, y = mechant.position
            x_mis, y_mis = self.position
            if abs(x - x_mis) < Mechant.m_size / 2  and abs(y - y_mis) < Mechant.m_size / 2:
                print "Méchant tué en : " + str((x, y, x_mis, y_mis))
                return True
    
    def tirer(self):
        Missile(self.position, direction=1)
        return
    
    def bouger(self, delta_t):
         x, y = self.position
         self.position = x, y + self.vitesse * delta_t / 50
    
    def out_of_bounds(self):
        x, y = self.position
        return not(-0.1 < y < 1.1)
    
        
    
    
        
        
    