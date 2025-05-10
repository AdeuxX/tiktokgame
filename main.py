# main.py - Simulation de boule sur trajectoire circulaire

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
pygame.display.set_caption("Simulation de mouvement circulaire")
background_color = (0, 0, 0)  # Noir

# Configuration de l'horloge pour contrôler les FPS
clock = pygame.time.Clock()
FPS = 45

# ---------------------------
# Configuration des objets
# ---------------------------
# Cercle fixe (trajectoire)
CIRCLE_POS = (960, 540)       # Centre de l'écran
CIRCLE_RADIUS = 400
CIRCLE_COLOR = (255, 255, 255)

# Boule mobile
BALL_RADIUS = 20
BALL_COLOR = (255, 255, 255)
ball_pos = [CIRCLE_POS[0], CIRCLE_POS[1] - CIRCLE_RADIUS]  # Position initiale au sommet
ball_velocity = [0, 0]  # Vitesse initiale (vx, vy)

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
    # Dessin des éléments
    # ---------------------------
    screen.fill(background_color)
    
    # Dessin du cercle de trajectoire
    pygame.draw.circle(screen, CIRCLE_COLOR, CIRCLE_POS, CIRCLE_RADIUS, 1)  # Dernier paramètre = épaisseur
    
    # Dessin de la boule mobile
    pygame.draw.circle(screen, BALL_COLOR, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)
    
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