"""
Jeu hypnotique - Pygame
Simulation d'une boule rebondissant dans un arc tournant avec traînée visuelle.

Contrôles : Aucune interaction nécessaire, la simulation est entièrement automatique.
"""

# ---------------------------
# Import des modules
# ---------------------------
import pygame
import sys
import math
import random

# ---------------------------
# Constantes globales
# ---------------------------
# Affichage
SCREEN_SIZE = (1920, 1080)
BACKGROUND_COLOR = (0, 0, 0)
FPS = 45

# Cercle fixe (position de collision)
CIRCLE_POS = (960, 540)
CIRCLE_RADIUS = 400
CIRCLE_COLOR = (255, 255, 255)

# Paramètres de l'arc tournant
ARC_ROTATION_SPEED = math.radians(30)  # 30°/s convertis en radians/s
ARC_ANGLE_SPAN = math.radians(335)     # 80% de 360° (288°) en radians
ARC_WIDTH = 1

# Boule mobile
BALL_RADIUS = 20
BALL_COLOR = (255, 255, 255)
GRAVITY = 1000                        # px/s²
BOUNCE_RESTITUTION = 1

# Traînée
TRAIL_LENGTH = 30
TRAIL_RADIUS = 4
TRAIL_COLOR = (255, 0, 0, 102)        # RGBA : 40% d'opacité

# ---------------------------
# Variables globales
# ---------------------------
screen = None
clock = None
trail_surface = None
balls = []                            # Liste des boules
arc_angle_start = 0.0                 # Angle initial en radians

# ---------------------------
# Initialisation du jeu
# ---------------------------
def init():
    """
    Initialise les éléments graphiques et physiques.
    Crée la surface semi-transparente pour la traînée.
    """
    global screen, clock, trail_surface, arc_angle_start, balls
    
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Jeu hypnotique - Arc tournant")
    
    clock = pygame.time.Clock()
    
    # Surface pour la traînée (avec canal alpha)
    trail_surface = pygame.Surface((2*TRAIL_RADIUS, 2*TRAIL_RADIUS), pygame.SRCALPHA)
    pygame.draw.circle(trail_surface, TRAIL_COLOR, 
                      (TRAIL_RADIUS, TRAIL_RADIUS), TRAIL_RADIUS)
    
    # Initialisation des boules
    balls = [{
        'pos': [CIRCLE_POS[0] + 60, CIRCLE_POS[1]],
        'velocity': [10.0, 10.0],
        'trail': []
    }]
    arc_angle_start = 0.0  # Départ à 0 radians (vers la droite)

# ---------------------------
# Mise à jour physique (partie corrigée)
# ---------------------------
def update_physics(dt):
    global balls, arc_angle_start
    
    balls_to_remove = []
    new_balls = []
    
    # Itération sécurisée sur une copie de la liste
    for ball in balls.copy():
        # Application de la gravité
        ball['velocity'][1] += GRAVITY * dt
        
        # Mise à jour position
        ball['pos'][0] += ball['velocity'][0] * dt
        ball['pos'][1] += ball['velocity'][1] * dt
        
        # Calcul distance au centre
        dx = ball['pos'][0] - CIRCLE_POS[0]
        dy = ball['pos'][1] - CIRCLE_POS[1]
        distance = math.hypot(dx, dy)
        collision_distance = CIRCLE_RADIUS - BALL_RADIUS
        
        if distance >= collision_distance:
            # Normale de collision (direction radiale)
            normal = (dx/distance, dy/distance) if distance > 0 else (0, 1)
            
            # Conversion en angle horaire pygame (y inversé)
            collision_angle = math.atan2(-normal[1], normal[0]) % (2 * math.pi)
            
            # Calcul des bornes de l'arc
            start = arc_angle_start % (2 * math.pi)
            end = (start + ARC_ANGLE_SPAN) % (2 * math.pi)
            
            # Vérification de la collision avec l'arc
            if start < end:
                in_arc = start <= collision_angle < end
            else:
                in_arc = collision_angle >= start or collision_angle < end
                
            if in_arc:
                # Rebond sur l'arc
                dot = ball['velocity'][0] * normal[0] + ball['velocity'][1] * normal[1]
                ball['velocity'][0] -= (1 + BOUNCE_RESTITUTION) * dot * normal[0]
                ball['velocity'][1] -= (1 + BOUNCE_RESTITUTION) * dot * normal[1]
                
                # Correction de position
                overshoot = distance - collision_distance
                ball['pos'][0] -= normal[0] * overshoot
                ball['pos'][1] -= normal[1] * overshoot
            else:
                # Échappement par le trou
                balls_to_remove.append(ball)
                
                # Création de nouvelles boules
                original_speed = math.hypot(ball['velocity'][0], ball['velocity'][1])
                for _ in range(2):
                    # Position aléatoire près du centre
                    angle = random.uniform(0, 2 * math.pi)
                    radius = random.uniform(50, 100)
                    x = CIRCLE_POS[0] + radius * math.cos(angle)
                    y = CIRCLE_POS[1] + radius * math.sin(angle)
                    
                    # Direction vers le centre (vecteur unitaire)
                    dir_x = CIRCLE_POS[0] - x
                    dir_y = CIRCLE_POS[1] - y
                    length = math.hypot(dir_x, dir_y)
                    if length > 0:
                        dir_x /= length
                        dir_y /= length
                    
                    new_ball = {
                        'pos': [x, y],
                        'velocity': [0,0],
                        'trail': []
                    }
                    new_balls.append(new_ball)
        
        # Mise à jour de la traînée
        ball['trail'].append((int(ball['pos'][0]), int(ball['pos'][1])))
        if len(ball['trail']) > TRAIL_LENGTH:
            ball['trail'].pop(0)
    
    # Suppression sécurisée des boules
    for ball in balls_to_remove:
        if ball in balls:
            balls.remove(ball)
    balls.extend(new_balls)
    
    # Rotation de l'arc
    arc_angle_start += ARC_ROTATION_SPEED * dt
    arc_angle_start %= (2 * math.pi)

# ---------------------------
# Dessin des éléments
# ---------------------------
def draw():
    """Dessine l'arc tournant, les boules et leurs traînées"""
    screen.fill(BACKGROUND_COLOR)
    
    # Dessin de l'arc tournant
    arc_rect = pygame.Rect(
        CIRCLE_POS[0] - CIRCLE_RADIUS,
        CIRCLE_POS[1] - CIRCLE_RADIUS,
        2 * CIRCLE_RADIUS,
        2 * CIRCLE_RADIUS
    )
    pygame.draw.arc(
        screen,
        CIRCLE_COLOR,
        arc_rect,
        arc_angle_start,
        arc_angle_start + ARC_ANGLE_SPAN,
        ARC_WIDTH
    )
    
    # Dessin des traînées et boules
    for ball in balls:
        # Traînée
        for pos in ball['trail']:
            screen.blit(trail_surface, (pos[0] - TRAIL_RADIUS, pos[1] - TRAIL_RADIUS))
        # Boule
        pygame.draw.circle(screen, BALL_COLOR,
                          (int(ball['pos'][0]), int(ball['pos'][1])),
                          BALL_RADIUS, 2)

# ---------------------------
# Programme principal
# ---------------------------
if __name__ == "__main__":
    init()
    
    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Contrôle du taux de rafraîchissement
        dt = clock.tick(FPS) / 1000.0
        
        # Mise à jour physique
        update_physics(dt)
        
        # Rendu graphique
        draw()
        pygame.display.flip()

    # Nettoyage final
    pygame.quit()
    sys.exit()