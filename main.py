# main.py - Squelette Pygame de base

# ---------------------------
# Import des modules
# ---------------------------
import pygame
import sys

# ---------------------------
# Initialisation de Pygame
# ---------------------------
pygame.init()

# Création de la fenêtre principale
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Projet Pygame")
background_color = (0, 0, 0)  # Noir

# Configuration de l'horloge pour contrôler les FPS
clock = pygame.time.Clock()
FPS = 45

# ---------------------------
# Boucle principale du jeu
# ---------------------------
running = True

while running:
    # ---------------------------
    # Gestion des événements
    # ---------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # ---------------------------
    # Rafraîchissement de l'écran
    # ---------------------------
    screen.fill(background_color)
    
    # ---------------------------
    # Mise à jour de l'affichage
    # ---------------------------
    pygame.display.flip()
    
    # ---------------------------
    # Limitation du taux de rafraîchissement
    # ---------------------------
    clock.tick(FPS)

# ---------------------------
# Nettoyage et sortie propre
# ---------------------------
pygame.quit()
sys.exit()