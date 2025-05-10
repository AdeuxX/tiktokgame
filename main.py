# main.py - Simulation de boule avec gravité, rebonds et traînée

# ---------------------------
# Import des modules
# ---------------------------
import pygame
import sys
import math
import time

# ---------------------------
# Initialisation de Pygame
# ---------------------------
pygame.init()

# Création de la fenêtre principale
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Simulation physique circulaire")
background_color = (0, 0, 0)  # Noir

# Configuration de l'horloge
clock = pygame.time.Clock()
FPS = 45

# ---------------------------
# Constantes physiques
# ---------------------------
GRAVITY = 1000  # px/s²
BOUNCE_RESTITUTION = 1.01  # Rebond parfait

# ---------------------------
# Configuration des objets
# ---------------------------
# Cercle fixe (trajectoire)
CIRCLE_POS = (960, 540)
CIRCLE_RADIUS = 400
CIRCLE_COLOR = (255, 255, 255)

# Boule mobilegit 
BALL_RADIUS = 20
BALL_COLOR = (255, 255, 255)
ball_pos = [
    CIRCLE_POS[0] + 60,
    CIRCLE_POS[1]  # Positionne au centre du cercle
]
ball_velocity = [10.0, 10.0]

# ---------------------------
# Configuration de la traînée
# ---------------------------
TRAIL_LENGTH = 30  # Nombre de points dans la traînée
TRAIL_RADIUS = 4   # Taille des points de traînée
# Rouge avec 40% d'opacité (102 = 255 * 0.4)
TRAIL_COLOR = (255, 0, 0, 102)

# Création d'une surface semi-transparente pour les points de traînée
# On utilise SRCALPHA pour activer le canal alpha pixel par pixel
trail_surface = pygame.Surface((2 * TRAIL_RADIUS, 2 * TRAIL_RADIUS), pygame.SRCALPHA)
pygame.draw.circle(trail_surface, TRAIL_COLOR, (TRAIL_RADIUS, TRAIL_RADIUS), TRAIL_RADIUS)

# Liste pour stocker les positions historiques de la boule
trail_positions = []

# ---------------------------
# Boucle principale du jeu
# ---------------------------
running = True

while running:
    dt = clock.tick(FPS) / 1000.0

    # Gestion des événements (inchangée)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---------------------------
    # Mise à jour physique
    # ---------------------------
    ball_velocity[1] += GRAVITY * dt
    ball_pos[0] += ball_velocity[0] * dt
    ball_pos[1] += ball_velocity[1] * dt

    # ---------------------------
    # Collisions
    # ---------------------------
    dx = ball_pos[0] - CIRCLE_POS[0]
    dy = ball_pos[1] - CIRCLE_POS[1]
    distance = math.hypot(dx, dy)
    collision_distance = CIRCLE_RADIUS - BALL_RADIUS  # 420 px

    if distance >= collision_distance:
        if distance > 0:
            normal = (dx / distance, dy / distance)
        else:
            normal = (0, 1)

        dot_product = ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1]
        ball_velocity[0] -= (1 + BOUNCE_RESTITUTION) * dot_product * normal[0]
        ball_velocity[1] -= (1 + BOUNCE_RESTITUTION) * dot_product * normal[1]

        overshoot = distance - collision_distance
        ball_pos[0] -= normal[0] * overshoot
        ball_pos[1] -= normal[1] * overshoot

    # ---------------------------
    # Mise à jour de la traînée
    # ---------------------------
    # Ajoute la position actuelle (convertie en entiers pour l'affichage)
    trail_positions.append((int(ball_pos[0]), int(ball_pos[1])))
    
    # Garde seulement les N dernières positions
    if len(trail_positions) > TRAIL_LENGTH:
        trail_positions.pop(0)

    # ---------------------------
    # Dessin des éléments
    # ---------------------------
    screen.fill(background_color)
    
    # Dessin du cercle de trajectoire
    pygame.draw.circle(screen, CIRCLE_COLOR, CIRCLE_POS, CIRCLE_RADIUS, 1)
    
    # Dessin de la traînée
    for pos in trail_positions:
        # On centre la surface de traînée sur la position historique
        screen.blit(trail_surface, (pos[0] - TRAIL_RADIUS, pos[1] - TRAIL_RADIUS))
    
    # Dessin de la boule principale (par dessus la traînée)
    pygame.draw.circle(screen, BALL_COLOR, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS, 2)

    # ---------------------------
    # Mise à jour écran
    # ---------------------------
    pygame.display.flip()

# ---------------------------
# Nettoyage
# ---------------------------
pygame.quit()
sys.exit()