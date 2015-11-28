# space_i
Small attempt to write a space invader in python...


ok ok ^^ alors pour l'apprentissage y'a plusieurs façons de voir le truc... et surtout plusieurs choses à apprendre.
D'abord, tuer un méchant fixé : input position de notre bot, position du méchant. output : il est mort avant nous. 
Ensuite, éviter les missiles. Input : position des missiles adverses, position de notre bot. Output : on est mort ou pas.
Enfin : apprendre à cibler un méchant.
Une fois qu'on a appris ces trois trucs, on cherche à maximiser le score avec en mettant une énorme pénalité sur notre mort.
Avec une méthode comme ça on divise l'apprentissage, c'est un peu supervisé donc c'est pas optimal; mais c'est très facile à faire.

Une autre méthode serait juste de maximiser le score en mettant une pénalité sur notre mort. Je sais pas si ça peut bien marcher avec un simple process gaussien mais on peut tenter. Autrement, faudrait peut être utiliser des réseaux de neurone


YEAH C4EST D BAR
