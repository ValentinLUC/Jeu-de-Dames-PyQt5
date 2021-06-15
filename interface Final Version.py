## Import des modules ##
import sys, os, subprocess, random, string, pyautogui       # To install pyautogui: pip install pyautogui in the terminal
from PyQt5.QtMultimedia import *                    # En cas de problème d'import, enlever l'unique ligne 1060 environ (méthode stopMusic)
# import PyQt5                                      # ou mettez la commentaire
from typing import Tuple  
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Change Directory for VS Code
# os.chdir("C:/Users/valen/OneDrive/Bureau/Jeu De Dames")     # changer en fonction de son arborescence si nécessaire

# Variables globales 
partie = 1
pionsRestantJoueur1 = 10
pionsRestantJoueur2 = 10
nbrTours = 1
nbrScreenshot = 1
nbrTab = 1
pion1 = None 
pion2 = None 
Damier = dict()
miamourafle = False
list_pion = []
pion_clickable1, pion_clickable2 = [], []
latestMoves = []

## Classe permettant de gérer les couleurs ##

class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        self.myPalette = self.palette()
        # self.setFixedWidth(50)
        # self.setFixedHeight(50)
        self.myPalette.setColor(QPalette.Window, QColor(color))
        self.setPalette(self.myPalette)

####################################################################

####################################################################

## fonction d'arbre ##

def add(arbre, parent_name, son_name, test_mode = False):
    son = [son_name, []]
    if not(vide(arbre)):
        parent_cie = deep_search(arbre, parent_name)
        if test_mode:
            print("parent_cie :", parent_cie)
        parent_cie[1].append(son)
        if test_mode:
            print("add :", arbre)
        return arbre
    else:
        return son

def deep_search(arbre, target, test_mode =  False): # tested and approuved
    if test_mode:
        print("target :", target, "arbre :", arbre) 
    if get_racine(arbre) == target:
        return arbre
    elif not(feuille(arbre)):
        for i in get_foret(arbre):
            if get_racine(i) == target:
                return i
            else:
                cas = deep_search(i, target)
                if cas in (0, 1):
                    continue
                else:
                    return cas
        return 1
    else:
        return 0

def hauteur(arbre): # le chemin le plus long de la racine à une feuille
    if not vide(arbre) and feuille(arbre):
        return 0
    else:
        return 1 + max([hauteur(sousarbre) for sousarbre in arbre[1]])

def get_racine(arbre):
    return arbre[0]

def get_foret(arbre):
    if vide(arbre) :
        return
    else:
        return arbre[1]

def feuille(arbre):
    return len(arbre[1]) == 0

def vide(arbre):
    return len(arbre) == 0

def get_fils(arbre): # renvoie [] si pas de fils
    return [get_racine(sousarbre) for sousarbre in get_foret(arbre)]

## Classe gérant le fonctionnement du jeux ##

def inBoundaries(coord):
        if type(coord) == tuple and len(coord) == 2:
            if 0 < coord[0] < 10 and 0 < coord[1] < 10:
                return True
            else:
                return False
        else:
            print("Error_inBoundaries : entry not conform")
            return False

######### C'est fontionel, enfin !!!! #########
def create_tree(bouton, turn, bouton_racine = None, test_mode = False): # créer l'arbre d'un pion
    global Damier
    if (bouton.stat == turn and bouton_racine == None) or (bouton.stat == 0 and bouton_racine != None): # premier est un pion & ya pas encore de racine
        if bouton.can_eat(test_mode):                                                                            # deuxième est une case vide mais il y a un bouton racine mtnt
            for pion in bouton.eatable():                                                               # => pour éviter de rebondir sur des pions aliés

                if test_mode:
                    print("bouton.eatable, pion, bouton_racine :", bouton.eatable(), pion, bouton_racine)

                if bouton_racine == None: # je modifie l'arbre du premier bouton que je check => pas de prob 

                    if test_mode:
                        print("Bouton_racine == None")
                        
                    bouton.tree = add(bouton.tree, bouton.coord, pion, test_mode=test_mode) # je l'ajoute à mon arbre

                    Damier[(bouton.coord[0] + ((pion[0] - bouton.coord[0]) // 2), bouton.coord[1] + ((pion[1] - bouton.coord[1]) // 2))].mangé = True 
                    # le pion sauté est marqué comme "mangé" pour ne plus être target par .can_eat() et .eatable() 
                    # => plus besoin de blacklist qui empêche de revenir sur une case sur laquelle on est déjà allé, ie on ne peut plus "bouclé" :\ plus ce probleme avec le statu "mangé"

                    if test_mode:
                        print("pion 'mangé' :", Damier[(bouton.coord[0] + ((pion[0] - bouton.coord[0]) // 2), bouton.coord[1] + ((pion[1] - bouton.coord[1]) // 2))].coord)

                    create_tree(Damier[pion], turn, bouton, test_mode=test_mode) # et je continue ma rafle

                    if test_mode:
                        print("Damier[pion].tree final :", Damier[bouton.coord].tree, bouton.coord)

                    # reset des statuts mangé à False, cette section n'est atteinte qu'à la sortie de la fonction originale (celle à la couche de récursivité 0)
                    if test_mode:
                        print("statut mangé reset")

                    for pion in Damier:
                        if Damier[pion].mangé == True:
                            Damier[pion].mangé = False

                    # Fin de la fonction

                else: # c'est plus l'arbre du bouton que je check que je dois modifier mais le premier, d'où "bouton_racine"

                    if test_mode:
                        print("bouton_racine.tree =", bouton_racine.tree)

                    bouton_racine.tree = add(bouton_racine.tree, bouton.coord, pion, test_mode=test_mode)
                    Damier[(bouton.coord[0] + ((pion[0] - bouton.coord[0]) // 2), bouton.coord[1] + ((pion[1] - bouton.coord[1]) // 2))].mangé = True # on marque comme mangé

                    if test_mode:
                        print("pion 'mangé' :", Damier[(bouton.coord[0] + ((pion[0] - bouton.coord[0]) // 2), bouton.coord[1] + ((pion[1] - bouton.coord[1]) // 2))].coord)

                    create_tree(Damier[pion], turn, bouton_racine, test_mode=test_mode)
    else:
        print("bouton.stat != turn || 0")

## non fini ## 
# def create_tree_dame(bouton, turn, bouton_racine = None, test_mode = False): # créer l'arbre d'une dame
#     global Damier
#     if (bouton.stat == turn and bouton_racine == None) or (bouton.stat == 0 and bouton_racine != None): 
#         if bouton.can_eat_dame(test_mode): 
#             for pion in bouton.eatable_dame(): 

#                 if test_mode:
#                     print("bouton.eatable, pion, bouton_racine :", bouton.eatable(), pion, bouton_racine)

#                 if bouton_racine == None: 

#                     if test_mode:
#                         print("Bouton_racine == None")
                        
#                     bouton.tree = add(bouton.tree, bouton.coord, pion, test_mode=test_mode) 

#                     Damier[(bouton.coord[0] + ((pion[0] - bouton.coord[0]) // 2), bouton.coord[1] + ((pion[1] - bouton.coord[1]) // 2))].mangé = True 

#                     if test_mode:
#                         print("pion 'mangé' :", Damier[(bouton.coord[0] + ((pion[0] - bouton.coord[0]) // 2), bouton.coord[1] + ((pion[1] - bouton.coord[1]) // 2))].coord)

#                     create_tree(Damier[pion], turn, bouton, test_mode=test_mode) 

#                     if test_mode:
#                         print("Damier[pion].tree final :", Damier[bouton.coord].tree, bouton.coord)


#                     if test_mode:
#                         print("statut mangé reset")

#                     for pion in Damier:
#                         if Damier[pion].mangé == True:
#                             Damier[pion].mangé = False

#                     # Fin de la fonction

#                 else: 

#                     if test_mode:
#                         print("bouton_racine.tree =", bouton_racine.tree)

#                     bouton_racine.tree = add(bouton_racine.tree, bouton.coord, pion, test_mode=test_mode)
#                     Damier[(bouton.coord[0] + ((pion[0] - bouton.coord[0]) // 2), bouton.coord[1] + ((pion[1] - bouton.coord[1]) // 2))].mangé = True # on marque comme mangé

#                     if test_mode:
#                         print("pion 'mangé' :", Damier[(bouton.coord[0] + ((pion[0] - bouton.coord[0]) // 2), bouton.coord[1] + ((pion[1] - bouton.coord[1]) // 2))].coord)

#                     create_tree(Damier[pion], turn, bouton_racine, test_mode=test_mode)
#     else:
#         print("bouton.stat != turn || 0")

## actualisation des trees ennemis, reset des trees aliés et calcul des hauteurs des trees pour le tour suivant ##
def create_trees(test_mode = False):
    global nbrTours
    turn = (nbrTours + 1) % 2 + 1 # 1 = blanc ; 2 = noir
    for pion in Damier:
        if Damier[pion].stat == turn: # /!\ faut placer cette fonction après nbrTour += 1 /!\
            create_tree(Damier[pion], turn, None, test_mode) # turn = ennemi puisque l'actualisation se fait pdt le tour d'avant, cad quand ce n'est pas le propriétaire des pions qui joue
            Damier[pion].hauteur = hauteur(Damier[pion].tree)
            # print(Damier[pion].stat, Damier[pion].coord, Damier[pion].tree, Damier[pion].hauteur)
        elif Damier[pion].stat == turn + 3:
            print("fonction nécessaire à la création des arbres des dames non finies")
            # create_tree_dame(Damier[pion], turn, None, test_mode)
            # Damier[pion].hauteur = hauteur(Damier[pion].tree)
            
            # print("Dame :", Damier[pion].stat, Damier[pion].coord, Damier[pion].tree, Damier[pion].hauteur)
        else:
            Damier[pion].reset_tree()
    # print("")

## donne la liste des noeuds présent dans les chemin menant à/aux feuille(s) à la hauteur max ##
def noeuds_in_chemin_max(tree, hmax, h = 0, test_mode = False): # /!\ renvoie (h, list), il faut donc récupérer uniquement list : _, list = noeuds_in_chemin_max()
    list_chemin_max = []
    if test_mode:
        print("arbre :", tree) 

    if not(feuille(tree)):
        list_chemin_max.append(get_racine(tree))
        for i in get_foret(tree):
            h, temp = noeuds_in_chemin_max(i, hmax, h + 1, test_mode=test_mode)

            if test_mode:
                print("h, temp :", h, temp)

            list_chemin_max += temp

        if test_mode:
                print("list_chemin_max :", list_chemin_max)

        if list_chemin_max == []:
            return h - 1, [] 
        else:
            return h - 1, list_chemin_max
            
    else:
        if h == hmax:
            list_chemin_max.append(get_racine(tree))
            if test_mode:
                print("hmax atteint :", h, list_chemin_max)
            return h - 1, list_chemin_max # pas de trimage sur cette branche
        else:
            if test_mode:
                print("hmax non atteint :", h, list_chemin_max)
            return h - 1, [] # trime-moi cette branche

## ne garde que les noeuds de la list_noeuds_ok donnée par noeuds_in_chemin_max(), et enlève le reste ("taillage" de l'arbre) ##
def taillade(tree, hmax, list_noeuds_ok ,test_mode = False):
    if test_mode:
        print(tree)
    if not(feuille(tree)):
        for i in get_foret(tree).copy():

            if test_mode:
                print("i :", i)
                print("fils :", get_fils(tree))

            if not(get_racine(i) in list_noeuds_ok):
                tree[1].pop(get_fils(tree).index(get_racine(i)))
                if test_mode:
                    print("tree après pop :", tree)
            else:
                if test_mode:
                    print("else :", tree)
                taillade(i, hmax, list_noeuds_ok, test_mode=test_mode)
    if test_mode:
        print("Fin")


class Bouton(QPushButton):

    def __init__(self):
        super().__init__()
        self.setFixedWidth(70)
        self.setFixedHeight(70)
        self.stat = 0 # 0 = case vide ; 1 = pion blanc ; 2 = pion noir ; 3 = case noir ; 4 = dame blanche ; 5 = dame noire 
        self.coord = None # statut par défaut pour les cases noires #racisme 
        self.tree = [self.coord, []] # stockage de l'arbre des possibilité de rafle 
        self.hauteur = 0 
        self.mangé = False 
        self.initUI() 

    def initUI(self):
        self.clicked.connect(self.on_click)
        self.display()

    def on_click(self): # coord des pions à déplacer
        global pion1, pion2, Damier, miamourafle, nbrTours, list_pion, pion_clickable1, pion_clickable2, pionsRestantJoueur1, pionsRestantJoueur2, latestMoves
        turn = (nbrTours + 1) % 2 + 1 # 1 = blanc ; 2 = noir
        # print(self.coord)         

        # Check Déplacement

        if len(list_pion) == 0:
            miamourafle = False
        else:
            miamourafle = True

        if not(miamourafle): # pas de pion à manger, déplacement normal

            if pion1 == None and self.coord != None and Damier[self.coord].stat != 0:
                pion1 = self.coord

                # create_tree(Damier[pion1], turn, None, test_mode=True)   # temporaire, juste là pour tester facilement create_tree()
                # print(">\t", Damier[pion1].tree)                           # (ici, l'arbre est créer quand on selection le premier pion, cf console)
                # Damier[pion1].tree = [pion1, []]                             # attention, si le bouton cliqué a déjà un arbre, ça fait de la merde 
                # print("mangé ?",Damier[pion1].mangé)

            elif pion1 != None and self.coord != None: 
                pion2 = self.coord
            
            if pion2 != None:
                if Damier[pion1].stat == 1 and turn == 1 and pion2[0] - pion1[0] == 1 and abs(pion2[1] - pion1[1]) == 1 and Damier[pion2].stat == 0:

                    # print(pion1, pion2, "deplacement")
                    move_ = pion1, pion2, "deplacement"

                    self.move()
                    nbrTours += 1
                    create_trees()
                elif Damier[pion1].stat == 2 and turn == 2 and pion2[0] - pion1[0] == -1 and abs(pion2[1] - pion1[1]) == 1 and Damier[pion2].stat == 0:

                    # print(pion1, pion2, "deplacement")
                    move_ = pion1, pion2, "deplacement"

                    self.move()
                    nbrTours += 1
                    create_trees()
                else:
                    pion1, pion2 = None, None

                latestMoves.append(move_)


        else: # miamourafle = True ici 

            # print("A", list_pion, pion_clickable1, pion_clickable2)
            if pion1 == None and len(pion_clickable1) == 0:
                # print("here1")
                for tree in list_pion:
                    pion_clickable1.append(get_racine(tree))

                if self.coord in pion_clickable1:
                    # print("pion1 ok")
                    pion1 = self.coord 

                    for tree in list_pion:
                        if get_racine(tree) == pion1:
                            pion_clickable2 = get_fils(tree)
            
            elif pion1 == None and len(pion_clickable1) != 0:
                # print("here2")
                if self.coord in pion_clickable1:
                    # print("pion1 ok bis")
                    pion1 = self.coord 
                
                    for tree in list_pion:
                        if get_racine(tree) == pion1:
                            pion_clickable2 = get_fils(tree)

            elif pion1 != None and self.coord in pion_clickable2: 
                # print("here3, pion2 ok")
                pion2 = self.coord 
                pion_clickable1, pion_clickable2 = [], []
                move_ = pion1, pion2, "rafle"

                latestMoves.append(move_)
                # print(latestMove)

                if turn == 1:
                    pionsRestantJoueur2 -= 1
                else:
                    pionsRestantJoueur1 -= 1

                if len(list_pion) > 1:                                    # s'il y a plusieur arbre dans list_pion
                    for tree in list_pion:                                # on prend l'arbre choisi lors de la selection de pion1 et on prend le fils choisi (pion2)
                        if get_racine(tree) == pion1:                     # et on met ce fils, donc avec sa descendance, dans list_pion (de la forme : [<tree pion2>])
                            list_pion = [deep_search(tree, pion2)]  #
                else:
                    list_pion = [deep_search(list_pion[0], pion2)]  # sinon on prend l'arbre dans list_pion et on enlève la racine en cherchant le fils choisi (pion2)

                if Damier[pion1].stat in (1, 2): # on enlève le pion manger, ici c'est la case entre pion1 et pion2 : cas des pions normaux
                    Damier[(pion1[0] + ((pion2[0] - pion1[0]) // 2), pion1[1] + ((pion2[1] - pion1[1]) // 2))].erase()
                elif Damier[pion1].stat in (4, 5): # on enlève le pion manger, ici c'est la seul case non libre entre pion1 et pion2 : cas des dames
                    print("Cas des dames pas encore implémenté, le pion mangé n'est pas enlevé")
                else:
                    print("Error_selection_pion2 : pion2 stat isn't 1, 2, 4, 5")
                self.move() # il est après car il reset pion1 et pion2 à None, ce qui nique le branchement conditionnel au dessus s'il est mis juste avant celui-ci 
                
            else:
                # print("no here3 :",pion1, pion2)
                pion1, pion2 = None, None
                
            # print("B", list_pion, pion_clickable1, pion_clickable2)
            # print("B2", len(list_pion) == 1, get_fils(list_pion[0]))
            if len(list_pion) == 1 and get_fils(list_pion[0]) == []: # <=> si ya qu'un seul arbre dans list_pion et que cet arbre est un feuille, ça veut dire que la rafle est fini
                miamourafle = False                                  # puisqu'il n'y a plus de pion à manger après celui qui vient d'être mangé, ie ya plus d'enfant à la racine de l'arbre
                nbrTours += 1                                        # on passe donc au tour suivant et on recréer les arbres
                create_trees()                                       # s'il n'y a pas qu'un seul arbre dans list_pion, ça veut dire que le bouton selectionné n'était pas le bon
                list_pion = []                                       # ie il ne respectait pas la règle : "on doit manger le plus de pion possible", et n'était donc pas une racine
                pion_clickable1, pion_clickable2 = [], []            # des arbres ayant la taille max présent dans list_pion. cf pavé en dessous commençant par list_tree_max = []
            # print(pion1, pion2, "miamourafle :", miamourafle)        
            # print("C", list_pion, pion_clickable1, pion_clickable2)     
        

        if not(miamourafle):
            for j in range(10):     # convertion des pions sur la ligne finale en dames
                if (0, j) in Damier:
                    if Damier[(0, j)].stat == 2:
                        Damier[(0, j)].stat = 5
            for j in range(10):
                if (9, j) in Damier:
                    if Damier[(9, j)].stat == 1:
                        Damier[(9, j)].stat == 4


            # le pavé mentioné au dessus
            list_tree_max = [] # les arbres et leurs hauteurs sont générés arrivé ici, il faut donc faire du tri pour choper le/les pion(s) ayant l'arbre avec la plus grande hauteur 
            for pion in Damier:
                list_tree_max.append(Damier[pion].hauteur)
            hmax = max(list_tree_max)
            if hmax == 0:
                list_pion = []
            else:
                for pion in Damier:
                    if Damier[pion].hauteur == hmax:
                        # print("avant trimage :", Damier[pion].tree)
                        _, list_noeuds_ok = noeuds_in_chemin_max(Damier[pion].tree, hmax) # car ça renvoie (h, list) et on ne veut que la liste
                        taillade(Damier[pion].tree, hmax, list_noeuds_ok) # on enlève les branches qui n'atteigne pas hmax, ie on "taile" les arbres
                        # print("après trimage :",Damier[pion].tree)
                        list_pion.append(Damier[pion].tree)
                # print("list_pion init :", list_pion,"hmax :", hmax)

    ########### Méthodes annexes #############

    def can_eat(self, test_mode = False):
        global nbrTours
        ennemi_turn = nbrTours % 2 + 1

        if test_mode:
            print(self.coord)

        for i in (1, -1):
            for j in (1, -1):
                if inBoundaries((self.coord[0] + i, self.coord[1] + j)) and Damier[(self.coord[0] + i, self.coord[1] + j)].stat == ennemi_turn and Damier[(self.coord[0] + i, self.coord[1] + j)].mangé == False:
                    if inBoundaries((self.coord[0] + 2*i, self.coord[1] + 2*j)) and Damier[(self.coord[0] + 2*i, self.coord[1] + 2*j)].stat == 0:

                        if test_mode:
                            print("can eat")

                        return True

        if test_mode:
            print("can't eat")

        return False

    # def can_eat_dame(self, test_mode = False):
    #     global nbrTours
    #     ennemi_turn = nbrTours % 2 + 1

    #     if test_mode:
    #         print(self.coord)

    #     for i in (1, -1):
    #         for j in (1, -1):
    #             if inBoundaries((self.coord[0] + i, self.coord[1] + j)) and Damier[(self.coord[0] + i, self.coord[1] + j)].stat == ennemi_turn and Damier[(self.coord[0] + i, self.coord[1] + j)].mangé == False:
    #                 if inBoundaries((self.coord[0] + 2*i, self.coord[1] + 2*j)) and Damier[(self.coord[0] + 2*i, self.coord[1] + 2*j)].stat == 0:

    #                     if test_mode:
    #                         print("can eat")

    #                     return True

    #     if test_mode:
    #         print("can't eat")

    #     return False

    def eatable(self):
        global nbrTours
        ennemi_turn = nbrTours % 2 + 1

        list_pion = []
        for i in (1, -1):
            for j in (1, -1):
                if inBoundaries((self.coord[0] + i, self.coord[1] + j)) and Damier[(self.coord[0] + i, self.coord[1] + j)].stat == ennemi_turn and Damier[(self.coord[0] + i, self.coord[1] + j)].mangé == False:
                    if inBoundaries((self.coord[0] + 2*i, self.coord[1] + 2*j)) and Damier[(self.coord[0] + 2*i, self.coord[1] + 2*j)].stat == 0:
                        list_pion.append((self.coord[0] + 2*i, self.coord[1] + 2*j))
        return list_pion

    # def eatable_dame(self):
    #     global nbrTours
    #     ennemi_turn = nbrTours % 2 + 1

    #     list_pion = []
    #     for i in (1, -1):
    #         for j in (1, -1):
    #             if inBoundaries((self.coord[0] + i, self.coord[1] + j)) and Damier[(self.coord[0] + i, self.coord[1] + j)].stat == ennemi_turn and Damier[(self.coord[0] + i, self.coord[1] + j)].mangé == False:
    #                 if inBoundaries((self.coord[0] + 2*i, self.coord[1] + 2*j)) and Damier[(self.coord[0] + 2*i, self.coord[1] + 2*j)].stat == 0:
    #                     list_pion.append((self.coord[0] + 2*i, self.coord[1] + 2*j))
    #     return list_pion

    def move(self): 
        global pion1, pion2, Damier

        Damier[pion2].stat = Damier[pion1].stat
        Damier[pion1].stat = 0
        Damier[pion1].display()
        Damier[pion2].display()

        pion1, pion2 = None, None

    def update(self):
        self.reset_tree()
        self.display()

    def reset_tree(self):
        self.tree = [self.coord, []]
        self.hauteur = 0

    def erase(self):
        self.stat = 0
        self.display()

    def display(self): # les pions doivent être sur les cases noires
        if self.stat == 0: # case vide
            self.setIcon(QIcon())
            self.setStyleSheet("*{background-color: black;}" + "*:hover{border: 2px solid '#FF1111';}")
        elif self.stat == 1: # pion blanc
            self.setIcon(QIcon("img/white_checkers.png"))
            self.setIconSize(QSize(50,50))
        elif self.stat == 2: # pion noir
            self.setIcon(QIcon("img/black_checkers.png"))
            self.setIconSize(QSize(50,50))
        elif self.stat == 3: # case noir
            self.setIcon(QIcon())
            self.setStyleSheet("background-color: white")
        elif self.stat == 4: # dame blanche
            self.setIcon(QIcon("img/icon.png"))
            self.setIconSize(QSize(50,50))
        elif self.stat == 5: # dame noir
            self.setIcon(QIcon("img/icon.png"))
            self.setIconSize(QSize(50,50))
        else:
            print("Error_Bouton_stat")


## Classe gérant le Menu Principal ##

class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(600,600,600,600)
        self.setWindowTitle("Jeu de Dames")
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("img/checkers.jpg"))
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setScaledContents(True)

        # Combo Box
        self.combo = QComboBox()
        self.combo.addItem('Joueur VS Joueur')
        self.combo.addItem('Joueur VS IA')
        self.combo.activated[str].connect(self.onActivated)     # comboBox activé quand on selectionne un mode de jeu
        self.mode = None              # De base, il sera initialisé à None ce qui correspond au mode Joueur VS Joueur

        # Style de la ComboBox
        self.combo.setStyleSheet(
        '''
        *{
            border: 3px solid '#BC006C';
            border-radius: 25px;
            font-size: 15px;
            color: 'black';
            padding: 10px 200px;
            padding-left: 250px ;
            margin: 10px 10px;
        }
        *:hover{
            background: 'white';
        }
        '''
    )
        self.combo.setCursor(QCursor(Qt.PointingHandCursor))    # change cursor when we are on the button
        # Button widget
        self.pageLayout = QGridLayout()     # define a grid
        self.button = QPushButton("PLAY")   # declare the button Play
        self.pageLayout.addWidget(self.combo)
        self.pageLayout.addWidget(self.logo)    # add the photo to the layout
        self.pageLayout.addWidget(self.button)  # then the button
        self.button.setStyleSheet(
        '''
        *{
            border: 3px solid '#BC006C';
            border-radius: 25px;
            font-size: 15px;
            color: 'black';
            padding: 15px 0;
            margin: 0px 0px;
        }
        *:hover{
            background: '#BC006C';
        }
        '''
    )
        self.button.setCursor(QCursor(Qt.PointingHandCursor)) # change cursor when we are on the button
        
        # # Button callback
        self.button.clicked.connect(self.startGame)     # show something when clicked / use the method startGame
        
        self.widget = QWidget()                        
        self.widget.setLayout(self.pageLayout)      
        self.setCentralWidget(self.widget)      

    def onActivated(self, text):       # Mode de Jeu activé
        self.mode = text               
        
    def startGame(self):
        if self.mode == 'Joueur VS Joueur' or self.mode == None:
            print('Partie Joueur VS Joueur lancée')
            app.setWindowIcon(QIcon('img/icon.jpg'))
            self.window = CheckersGame()
            self.window.move(1100, 10)
            self.window.show()
            app.exec_()
        else:
            QMessageBox.information(self, "Attention", "Jeu contre IA non implémenté")
            # print('Jeu contre IA non implémenté')

####################################################################

## Classe du Jeu avec le Menu ##

class CheckersGame(Menu):
    def __init__(self):
        super().__init__()
        global nbrTours
        # self.setGeometry(700,700,700,700)
        # self.showFullScreen()
        self.setWindowTitle("Partie " + str(partie))
        self.setMaximumSize(700,700)    # Permet d'enlever la possibilité de plein écran

        # Toolbar & Menu

        ## Définition de la Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16,16))
        self.addToolBar(self.toolbar)

        ## Génération des différentes actions
        self.restart = QAction(QIcon("img/restart.png"), "Nouvelle Partie", self)
        self.restart.setStatusTip("Lance une nouvelle partie")
        self.restart.setShortcut(QKeySequence("Ctrl+N"))
        self.restart.triggered.connect(self.newGame)

        self.charger = QAction(QIcon("img/contact.png"), "Charger une Partie", self)
        self.charger.setStatusTip("Charger une Partie")
        self.charger.setShortcut(QKeySequence("Ctrl+E"))
        self.charger.triggered.connect(self.chargeGame)

        self.save = QAction(QIcon("img/sauvegarder.png"), "Sauvegarder la Partie", self)
        self.save.setStatusTip("Sauvegarder la Partie")
        self.save.setShortcut(QKeySequence("Ctrl+S"))
        self.save.triggered.connect(self.saveGame)

        self.screenshot = QAction(QIcon("img/camera.png"), "Screenshot", self)
        self.screenshot.setStatusTip("Prend un screenshot")
        self.screenshot.setShortcut(QKeySequence("Ctrl+C"))
        self.screenshot.triggered.connect(self.Screenshot)

        self.quit = QAction(QIcon("img/puissance.png"), "Quitter", self)
        self.quit.setStatusTip("Quitte le jeu")
        self.quit.setShortcut(QKeySequence("Ctrl+X"))
        self.quit.triggered.connect(self.quitGame)

        self.randomMusic = QAction(QIcon("img/melanger.png"), "Lance une musique aléatoire", self)
        self.randomMusic.setStatusTip("Lance une musique aléatoire")
        self.randomMusic.triggered.connect(self.launchRandomMusic)

        self.stop = QAction(QIcon("img/silencieux.png"), "Arrêter la musique", self)
        self.stop.setStatusTip("Arrêter la musique")
        self.stop.triggered.connect(self.stopMusic)

        self.music = QAction(QIcon("img/la-musique.png"), "Lancer le lecteur audio", self)
        self.music.setStatusTip("Lance le lecteur audio")
        self.music.triggered.connect(self.launchMusic)

        self.Move = QAction(QIcon("img/arrow-180"),"Afficher le dernier déplacement effectuée", self)
        self.Move.setStatusTip("Affichage du dernier déplacement effectué")
        self.Move.triggered.connect(self.latestMove)

        self.moves = QAction(QIcon("img/blue-folder-horizontal-open.png"), "Afficher tous les déplacements de la partie", self)
        self.moves.setStatusTip("Affichage de tous les déplacements de la partie")
        self.moves.triggered.connect(self.gameMoves)

        self.previousGame = QAction(QIcon("img/blue-folder-import"),"Afficher tous les déplacements d'une partie déjà effectuée", self)
        self.previousGame.setStatusTip("Affichage de tous les déplacements d'une partie déjà effectuée")
        self.previousGame.triggered.connect(self.previousGameMoves)

        self.saveMoves = QAction(QIcon("img/box-label.png"),"Enregistrer l'historique de la partie", self)
        self.saveMoves.setStatusTip("Enregistre l'historique de la partie")
        self.saveMoves.triggered.connect(self.saveGameMoves)

        self.rules = QAction(QIcon("img/rules.png"), "Manuel de Jeu", self)
        self.rules.setStatusTip("Les règles du Jeu de Dames")
        self.rules.triggered.connect(self.Rules)

        self.about = QAction(QIcon("img/info.png"), "À propos", self)
        self.about.setStatusTip("À propos")
        self.about.triggered.connect(self.aboutUs)

        self.restartProgram = QAction(QIcon("img/arrow-circle-double-135.png"), "Relance le programme", self)
        self.restartProgram.setStatusTip("Relance le programme")
        self.restartProgram.setShortcut(QKeySequence("Ctrl+R"))
        self.restartProgram.triggered.connect(self.newLaunch)

        self.abandon = QAction(QIcon("img/poubelle.png"), "Abandonner la partie", self)
        self.abandon.setStatusTip("Abandonne la partie")
        self.abandon.setShortcut(QKeySequence("Ctrl+G"))
        self.abandon.triggered.connect(self.giveUp)
        
        self.setStatusBar(QStatusBar())

        ## Ajout à la Toolbar
        self.toolbar.addAction(self.restart)
        self.toolbar.addAction(self.charger)
        self.toolbar.addAction(self.save)
        self.toolbar.addAction(self.screenshot)
        self.toolbar.addAction(self.randomMusic)
        self.toolbar.addAction(self.stop)
        self.toolbar.addAction(self.music)
        self.toolbar.addAction(self.abandon)
        self.toolbar.addAction(self.moves)
        self.toolbar.addAction(self.rules)
        self.toolbar.addAction(self.about)
        self.toolbar.addAction(self.quit)

        ## Création du menu et ajout des actions avec séparateurs
        self.menuFichier = self.menuBar().addMenu("Fichier")
        self.menuFichier.addAction(self.restart)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.charger)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.save)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.restartProgram)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.quit)

        self.menuEdition = self.menuBar().addMenu("Edition")
        self.menuEdition.addAction(self.screenshot)
        self.menuEdition.addSeparator()
        self.menuEdition.addAction(self.abandon)

        self.menuMusique = self.menuBar().addMenu("Musique")
        self.menuMusique.addAction(self.randomMusic)
        self.menuMusique.addSeparator()
        self.menuMusique.addAction(self.stop)
        self.menuMusique.addSeparator()
        self.menuMusique.addAction(self.music)
        self.menuMusique.addSeparator()

        self.menuHistorique = self.menuBar().addMenu("Historique")
        self.menuHistorique.addAction(self.Move)
        self.menuHistorique.addSeparator()
        self.menuHistorique.addAction(self.moves)
        self.menuHistorique.addSeparator()
        self.menuHistorique.addAction(self.previousGame)
        self.menuHistorique.addSeparator()
        self.menuHistorique.addAction(self.saveMoves)

        self.menuAbout = self.menuBar().addMenu("Aide")
        self.menuAbout.addAction(self.rules)
        self.menuAbout.addSeparator()
        self.menuAbout.addAction(self.about)
        self.menuAbout.addSeparator()

        ###################################

        # Organisation de la page
        self.pageLayout = QVBoxLayout()

        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(10,10,10,10)
        
        # Création du Timer
        self.current_time = QTime(00,00,00)     # on initialise le temps à 00:00:00
        self.timer = QTimer()                   # on déclare le timer
        self.timer.start(1000)                  
        self.timer.timeout.connect(self.timerEvent)     # toutes les secondes on fait appelle à la méthode timerEvent
        self.label = QLabel('<strong> Temps écoulé : </strong>', self)       # on déclare le label qui montrera le temps
        self.label.setAlignment(Qt.AlignRight)

        # Affichage des pions restants et des tours joués
        self.pions1 = QLabel('<strong> Nombre de pions restants : </strong> <ul> <li> Joueur 1 : ' + str(pionsRestantJoueur1)) 
        self.pions2 = QLabel('<ul> <li> Joueur 2 : ' + str(pionsRestantJoueur2))
        self.tours = QLabel('<strong> Nombre de tours effectués : </strong>' + str(nbrTours))
        
        # Stacked Layout pour l'affichage du tour des joueurs
        self.stackedLayout = QStackedLayout()

        ## Bouton Joueur 1
        self.tourJoueur1 = QPushButton('Joueur 1')
        self.tourJoueur1.setStyleSheet('QPushButton {background-color: #317AC1 ; color: white }')
        self.tourJoueur1.setFixedWidth(90)
        self.tourJoueur1.setFixedHeight(40)
        self.tourJoueur1.clicked.connect(self.changeColor)
        self.tourJoueur1.setCursor(QCursor(Qt.PointingHandCursor))

        ## Bouton Joueur 2
        self.tourJoueur2 = QPushButton('Joueur 2')
        self.tourJoueur2.setStyleSheet('QPushButton {background-color: #24D26D ; color: white }')
        self.tourJoueur2.setFixedWidth(90)
        self.tourJoueur2.setFixedHeight(40)
        self.tourJoueur2.clicked.connect(self.changeColor)
        self.tourJoueur2.setCursor(QCursor(Qt.PointingHandCursor))

        ## Ajout des boutons
        self.stackedLayout.addWidget(self.tourJoueur1)
        self.stackedLayout.addWidget(self.tourJoueur2)
        self.stackedLayout.setCurrentIndex(0)
        ########################################

        self.pageLayout.addWidget(self.label)
        self.pageLayout.addWidget(self.pions1)
        self.pageLayout.addWidget(self.pions2)
        self.pageLayout.addWidget(self.tours)
        self.pageLayout.addLayout(self.gridLayout)
        self.pageLayout.addLayout(self.stackedLayout)    

        # Création du damier
        global Damier

        for j in range (10):
            for i in range(10):
                if (i+j)%2 == 1:
                    # self.layout.addWidget(Color('black'),i, j)
                    if 0 <= i < 4 :
                        self.button = Bouton() #case blanche w/ pion blanc
                        self.button.stat = 1
                        self.button.coord = (i, j)
                        self.button.update()
                        self.gridLayout.addWidget(self.button, i, j)
                    elif 6 <= i < 11 :
                        self.button = Bouton() #case blanche w/ pion noir
                        self.button.stat = 2
                        self.button.coord = (i, j)
                        self.button.update()
                        self.gridLayout.addWidget(self.button, i, j)
                    else:
                        self.button = Bouton() #case blanche /w pion
                        self.button.stat = 0
                        self.button.coord = (i, j)
                        self.button.update()
                        self.gridLayout.addWidget(self.button, i, j)
                    
                    Damier[(i, j)] = self.button 
                else:
                    # self.layout.addWidget(Color('white'),i, j)
                    button = Bouton() #case noire /w pion
                    button.stat = 3 
                    button.display()
                    self.gridLayout.addWidget(button, i, j)

            self.widget = QWidget()
            self.widget.setLayout(self.pageLayout)
            self.setCentralWidget(self.widget)

            # Implémentation des onglets plutôt que de nouvelles fenetres

            # # Initialize tab screen
            self.tabs = QTabWidget()        # Pas fonctionnel encore
            # self.tabs.setTabsClosable(True)
            # self.tabs.tabCloseRequested.connect(self.close)
            # self.tabs.setMovable(True)

            # # Create first tab
            # self.tabs.addTab(self, "Partie")
            # self.tabs.setTabShape(1)
            # self.tab1 = QWidget()
            # self.tabs.addTab(self.tab1, "Partie 1")
            # self.pageLayout.addWidget(self.tabs)
            # ##############

            self.widget = QWidget()
            self.widget.setLayout(self.pageLayout)
            self.setCentralWidget(self.widget)

            ################

    def update_stats(self):
        self.pions1.setText('<strong> Nombre de pions restants : </strong> <ul> <li> Joueur 1 : ' + str(pionsRestantJoueur1)) 
        self.pions2.setText('<ul> <li> Joueur 2 : ' + str(pionsRestantJoueur2))
        self.tours.setText('<strong> Nombre de tours effectués : </strong>' + str(nbrTours))

    def newTab(self):
        global nbrTab
        nbrTab += 1
        self.tab = QWidget()
        self.tabs.addTab(self.tab, "Partie" + str(nbrTab))
        self.pageLayout.addWidget(self.tabs)
        self.setLayout(self.pageLayout)

    def changeColor(self):
        # print('Couleur changée')
        index = self.stackedLayout.currentIndex()
        if index == 0 :
            self.stackedLayout.setCurrentIndex(1)
        elif index == 1: 
            self.stackedLayout.setCurrentIndex(0)
    
    def giveUp(self):
        joueur = self.stackedLayout.currentIndex()+1
        if joueur == 1:
            self.victory(2)
        else:
            self.victory(1)

    def timerEvent(self):
        self.current_time = self.current_time.addSecs(1)    # on ajoute une seconde au current_time
        self.label.setText("<strong>Temps écoulé : </strong> " + self.current_time.toString("hh:mm:ss"))  # on change le label en fonction
        self.label.setAlignment(Qt.AlignRight) # on change le label en fonction
    
    def aboutUs(self):
        self.aPropos = About()
        self.aPropos.show()
    
    def newGame(self):
        global partie
        partie += 1
        app.setWindowIcon(QIcon('img/icon.jpg'))
        self.window = CheckersGame()
        self.window.move(100*partie, 20)
        self.window.show()
        app.exec_()
    
    def newLaunch(self):        # Permet de relancer le programme
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)

    def Rules(self):
        self.rulesOfTheGame = Handbook()
        self.rulesOfTheGame.move(5,20)
        self.rulesOfTheGame.show()
    
    def Screenshot(self):
        global nbrScreenshot
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.widget.winId())
        screenshot.save('screenshot(' + str(nbrScreenshot) + ').jpg', 'jpg')
        nbrScreenshot += 1
    
    def latestMove(self):
        global latestMoves
        # print(latestMoves, nbrTours)
        QMessageBox.information(self, "Dernier mouvement effectué", str(latestMoves[nbrTours-2]))
        # La case (0,0) se trouve en haut en gauche du damier
    
    def gameMoves(self):
        global latestMoves
        QMessageBox.information(self, "Dernier mouvement effectué", str(latestMoves))
        # La case (0,0) se trouve en haut en gauche du damier
    
    def previousGameMoves(self):
        QMessageBox.information(self, "Non implémenté", "Pas eu le temps d'implémenté ceci !")
    
    def saveGameMoves(self):
        global Damier
        name = QFileDialog.getSaveFileName(self, 'Save File')
        if name[0] != '' :
            file = open(name[0],"w")
            text = str(latestMoves) 
            file.write(text)
            file.close()
        else:  
            pass
    
    def chargeGame(self):
        global Damier, partie, nbrTours, pion1, pion2, miamourafle, list_pion,pion_clickable1, pion_clickable2
        pion1 = None 
        pion2 = None 
        miamourafle = False
        list_pion = []
        pion_clickable1, pion_clickable2 = [], []
        name = QFileDialog.getOpenFileName(self, 'Open File')
        if name[0] != '' :
            file = open(name[0],'r')
            # self.editor()
            # with file:
            text = file.readlines()
            liste = []
            liste2 = []
            for line in text:
                liste.append(line.splitlines())
                line2 = line.translate(line.maketrans('', '', string.punctuation))
                words = line2.split()
                liste2.append(words)

            for j in range (10):
                for i in range(10):
                    for k in liste2:
                        if (i, j) == (int(k[1]), int(k[2])):
                            self.button = Bouton() 
                            self.button.stat = int(k[0])
                            self.button.coord = (i, j)
                            self.button.update()
                            self.gridLayout.addWidget(self.button, i, j)
                            break

                Damier[(i, j)] = self.button 

                self.widget = QWidget()
                self.widget.setLayout(self.pageLayout)
                self.setCentralWidget(self.widget)
            
            create_trees() 
        
    def saveGame(self):
        global Damier
        name = QFileDialog.getSaveFileName(self, 'Save File')
        if name[0] != '' :
            file = open(name[0],"w")
            for pion in Damier:
                text = str(Damier[pion].stat) + ' ' + str(Damier[pion].coord) + '\n'
                file.write(text)
            file.close()
        else:  
            pass

    def launchRandomMusic(self): 
        nbr = random.randint(1, 5)
        QSound.play("music/" + str(nbr) + ".wav")

    def stopMusic(self):
        QMessageBox.information(self, "Attention", "<p> Aucun moyen d'arrêter la musique avec QSound, <br> \
        offrant seulement la possibilité de jouer du son. <br> <br> \
        Toutefois, nous pouvons mettre le volume à 0 <br> grâce au module Pyautogui. </p>")
        pyautogui.press('volumemute')
    
    def launchMusic(self):
        self.lecteurAudio = LecteurAudio()
        self.lecteurAudio.move(750,300)
        self.lecteurAudio.show()
    
    def victory(self, joueur):
        QMessageBox.information(self, "Victoire", "Victoire du Joueur " + str(joueur) + ' ! ')
    
    def quitGame(self):
        sys.exit(app.exec_()) # terminate the app

####################################################################

## Classe du à propos / pour se présenter ##

class About(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('À propos de nous')
        self.label = QLabel()
        self.label.setText("Nous sommes Valentin LUC et Lyam LIENARD, deux élèves de l'ESME Sudria en SPE. <br> <br>  \
        Le but de ce projet d'IHM est d’appliquer nos connaissances dans le langage Python et en <br> \
        algorithmique afin de réaliser non seulement un jeu de Dames à deux joueurs humains, <br> \
        mais aussi avec un joueur ordinateur, tout ceci en utilisant la librairie <a href='https://fr.wikipedia.org/wiki/PyQt'> PyQt5</a>.  <br> <br> \
        La durée de ce projet a été d'un mois. ")
        self.label.setAlignment(Qt.AlignTop)
        self.label.setContentsMargins(20,20,20,20)
        self.setGeometry(200, 200, 200, 50)
        self.setCentralWidget(self.label)

####################################################################

## Classe du manuel de Jeu ##

class Handbook(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Manuel du Jeu')
        self.label = QLabel()
        self.label.setText("\
        <h1 > <center> Règles du Jeu de Dames </center></h1> \
            <p> <center> <i> Dans ce jeu, toutes les règles ne sont présentes. Par exemple, le cas d'égalité, qui n'apparait que très rarement, ne sera pas implémentée ici. </center></i> </p>  \
            <h2>Introduction et Matériel</h2> \
                <ul> <li>Le damier est divisé en 10×10 cases. </li> \
                <li> Seules les cases noires sont utilisées (on ne pose pas les pions sur les cases blanches). </li> \
                <li>Comme aux échecs, la case en bas à droite est toujours blanche. </li> \
                <li>Comme aux échecs, les Blancs commencent. </li> \
                <li>Le jeu de Dames se joue avec 40 pions en tout : 20 blancs et 20 noirs. </li> </ul> \
            <h2>Déplacement des Pièces</h2> \
            <p> Il n’existe que deux types de pièces aux Dames : Les Pions et les Dames. </p> \
                <h3> PION : </h3> \
                    <ul> <li> Le Pion se déplace diagonalement d’une seule case. </li> \
                    <li> Le Pion se déplace toujours sur une case libre. </li> \
                    <li> Le Pion ne recule pas. </li> \
                    <li> Lorsque le Pion atteint la dernière rangée (la dernière ligne horizontale), il devient une Dame. </li> \
                    <li> Lorsque le Pion est promu Dame, c’est au Tour de l’adversaire. </li> </ul> \
                <h3> DAME : </h3> \
                    <ul> <li> La Dame avance diagonalement d’autant que cases qu’elle désire.</li> \
                    <li> La Dame peut avancer, mais également reculer. </li> </ul> \
            <h2> Captures : </h2> \
                <ul> <li> Les prises sont obligatoires. En un mot, aux Dames, si vous pouvez manger des Pions (ou des Dames), vous êtes obligés de le faire ! </li> \
                <li> Les prises qu’elles soient exécutées par des Pions ou des Dames se font devant, mais aussi derrière. En gros, un Pion peut reculer en mangeant ! </li> \
                <li> Le Pion capture en diagonale en sautant la case adjacente occupée par le Pion ennemi pour arriver par dessus ce dernier qu’il mange et atterrit sur la case libre juste derrière. <br> En gros, le Pion saute par dessus l’ennemi se trouvant à côté de lui (diagonalement). </li> \
                <li> Les Dames quant à elles sautent les Pièces ennemies sans qu’elles n’aient besoin d’être juxtaposées à ces dernières. <br> Elles peuvent également atterrir où elles le souhaitent sur la même diagonale (mais pas forcément juste derrière la pièce capturée comme doit le faire le Pion). </li> \
                <li> Lorsqu’un Pion capture, s’il se retrouve de nouveau en diagonal d’une pièce adverse il doit re-capturer. Cela s’appelle, la rafle. </li> \
                <li> Toute pièce capturée est enlevée du damier. </li> \
                <li> La Dame doit également capturer à l’infini si elle le peut. </li> \
                <li> Si vous avez le choix entre plusieurs rafles, vous devez obligatoirement opter pour la rafle vous rapportant le plus de pions. <br> Même si vous avez la possibilité de tuer deux Dames, vous devrez capturer les Tris Pions car ils sont plus nombreux.  </li> </ul> \
            <h2> Victoire : </h2> \
                <p> Aux Dames, vous gagnez si : </p> \
                <ul> <li> Votre adversaire abandonne. </li> \
                <li> Ne peut plus jouer alors que c'est le tour de votre adversaire (contrairement aux échecs où il y aurait Pat, c’est à dire partie nulle). </li> \
                <li> Si l’adversaire n’a plus de pièces. </li> </ul> \
        ")
        self.label.setAlignment(Qt.AlignTop)
        self.label.setContentsMargins(20,20,20,20)
        self.setGeometry(500, 500, 500, 500)
        self.setCentralWidget(self.label)

####################################################################

    # Attention !
    # Cette classe s'inspire de quelque chose trouvé sur GitHub et a été 
    # simplement adapté et intégré, ici, à notre Jeu de Dames.

class LecteurAudio(QMainWindow):

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.title = 'PyTunes'
        self.left = 300
        self.top = 300
        self.width = 300
        self.height = 150
        self.color = 1  # 0: dark mode 1: light mode
        self.userAction = -1  # 0: stopped, 1: playing 2: paused
        self.initUI()

    def initUI(self):
        # Add file menu
        menubar = self.menuBar()
        filemenu = menubar.addMenu('File')
        windowmenu = menubar.addMenu('Window')

        fileAct = QAction('Open File', self)
        folderAct = QAction('Open Folder', self)
        themeAct = QAction('Toggle light/dark theme', self)

        fileAct.setShortcut('Ctrl+O')
        folderAct.setShortcut('Ctrl+D')
        themeAct.setShortcut('Ctrl+T')

        filemenu.addAction(fileAct)
        filemenu.addAction(folderAct)
        windowmenu.addAction(themeAct)

        fileAct.triggered.connect(self.openFile)
        folderAct.triggered.connect(self.addFiles)
        themeAct.triggered.connect(self.toggleColors)

        self.addControls()

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.toggleColors()
        self.show()

    def addControls(self):
        wid = QWidget(self)
        self.setCentralWidget(wid)
        # Add song controls
        volumeslider = QSlider(Qt.Horizontal, self)
        volumeslider.setFocusPolicy(Qt.NoFocus)
        volumeslider.valueChanged[int].connect(self.changeVolume)
        volumeslider.setValue(100)
        playBtn = QPushButton('Play')  # play button
        pauseBtn = QPushButton('Pause')  # pause button
        stopBtn = QPushButton('Stop')  # stop button
        # Add playlist controls
        prevBtn = QPushButton('Prev')
        shuffleBtn = QPushButton('Shuffle')
        nextBtn = QPushButton('Next')
        # Add button layouts
        controlArea = QVBoxLayout()  # centralWidget
        controls = QHBoxLayout()
        playlistCtrlLayout = QHBoxLayout()
        # Add buttons to song controls layout
        controls.addWidget(playBtn)
        controls.addWidget(pauseBtn)
        controls.addWidget(stopBtn)
        # Add buttons to playlist controls layout
        playlistCtrlLayout.addWidget(prevBtn)
        playlistCtrlLayout.addWidget(shuffleBtn)
        playlistCtrlLayout.addWidget(nextBtn)
        # Add to vertical layout
        controlArea.addWidget(volumeslider)
        controlArea.addLayout(controls)
        controlArea.addLayout(playlistCtrlLayout)
        wid.setLayout(controlArea)
        # Connect each signal to their appropriate function
        playBtn.clicked.connect(self.playhandler)
        pauseBtn.clicked.connect(self.pausehandler)
        stopBtn.clicked.connect(self.stophandler)

        prevBtn.clicked.connect(self.prevSong)
        shuffleBtn.clicked.connect(self.shufflelist)
        nextBtn.clicked.connect(self.nextSong)

        self.statusBar()
        self.playlist.currentMediaChanged.connect(self.songChanged)

    def openFile(self):
        song = QFileDialog.getOpenFileName(self, "Open Song", "", "Sound Files (*.mp3 *.ogg *.wav *.m4a)")

        if song[0] != '':
            url = QUrl.fromLocalFile(song[0])
            if self.playlist.mediaCount() == 0:
                self.playlist.addMedia(QMediaContent(url))
                self.player.setPlaylist(self.playlist)
                self.player.play()
                self.userAction = 1
            else:
                self.playlist.addMedia(QMediaContent(url))

    def addFiles(self):
        if self.playlist.mediaCount() != 0:
            self.folderIterator()
        else:
            self.folderIterator()
            self.player.setPlaylist(self.playlist)
            self.player.playlist().setCurrentIndex(0)
            self.player.play()
            self.userAction = 1
    
    def folderIterator(self):
        folderChosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', '~')
        if folderChosen != None:
            it = QDirIterator(folderChosen)
            it.next()
            while it.hasNext():
                if it.fileInfo().isDir() == False and it.filePath() != '.':
                    fInfo = it.fileInfo()
                    if fInfo.suffix() in ('mp3', 'ogg', 'wav', 'm4a'):
                        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
                it.next()
            if it.fileInfo().isDir() == False and it.filePath() != '.':
                fInfo = it.fileInfo()
                if fInfo.suffix() in ('mp3', 'ogg', 'wav', 'm4a'):
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
    
    def playhandler(self):
        if self.playlist.mediaCount() == 0:
            self.openFile()
        elif self.playlist.mediaCount() != 0:
            self.player.play()
            self.userAction = 1

    def pausehandler(self):
        self.userAction = 2
        self.player.pause()

    def stophandler(self):
        self.userAction = 0
        self.player.stop()
        self.playlist.clear()
        self.statusBar().showMessage("Stopped and cleared playlist")

    def changeVolume(self, value):
        self.player.setVolume(value)

    def prevSong(self):
        if self.playlist.mediaCount() == 0:
            self.openFile()
        elif self.playlist.mediaCount() != 0:
            self.player.playlist().previous()
    
    def shufflelist(self):
        self.playlist.shuffle()

    def nextSong(self):
        if self.playlist.mediaCount() == 0:
            self.openFile()
        elif self.playlist.mediaCount() != 0:
            self.player.playlist().next()
    
    def songChanged(self, media):
        if not media.isNull():
            url = media.canonicalUrl()
            self.statusBar().showMessage(url.fileName())

    def toggleColors(self):
        app.setStyle("Fusion")
        palette = QPalette()
        if self.color == 0:
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(235, 101, 54))
            palette.setColor(QPalette.Highlight, QColor(235, 101, 54))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.color = 1
        elif self.color == 1:
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, QColor(240, 240, 240))
            palette.setColor(QPalette.AlternateBase, Qt.white)
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, Qt.white)
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(66, 155, 248))
            palette.setColor(QPalette.Highlight, QColor(66, 155, 248))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.color = 0

####################################################################

### Démarrage de l'application ###

app = QCoreApplication.instance()
if app is None:
    app = QApplication(sys.argv)
    # app.setStyle('Windows')

app.setWindowIcon(QIcon('img/icon.jpg'))
window = Menu()
window.move(1150, 177)
window.show()
app.exec_()

