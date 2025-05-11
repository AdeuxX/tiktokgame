# ---------------------------
# Import des modules
# ---------------------------
import pygame
import sys
import math
import random
import os
import time
import numpy as np
from moviepy import ImageSequenceClip

# ---------------------------
# Constantes globales
# ---------------------------
# Affichage
SCREEN_SIZE = (650, 1080)
BACKGROUND_COLOR = (0, 0, 0)
FPS = 60

# Cercle fixe (position de collision)
CIRCLE_POS = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
CIRCLE_RADIUS = 200
CIRCLE_COLOR = (255, 255, 255)

# Paramètres de l'arc tournant
ARC_ROTATION_SPEED = math.radians(30)  # 30°/s convertis en radians/s
ARC_ANGLE_SPAN = math.radians(300)     # 80% de 360° (288°) en radians
ARC_WIDTH = 5

# Boule mobile
BALL_RADIUS = 30
BALL_COLOR = (255, 255, 255)
GRAVITY = 500                      # px/s²
BOUNCE_RESTITUTION = 1.006

# Traînée
TRAIL_LENGTH = 10
TRAIL_RADIUS = 7
TRAIL_COLOR = (255, 0, 0, 102)        # RGBA : 40% d'opacité

# Rayon minimal pour dessiner les arcs
MIN_RADIUS = 500
RADIUS_MIN = 200

# ---------------------------
# Variables globales
# ---------------------------
compteur_destroyed_arc_blue = 0
compteur_destroyed_arc_red = 0
compteur_destroyed_arc = 0
compteur_rebond = 0
screen = None
clock = None
trail_surface = None
balls = []                            # Liste des boules
arc_angle_start = 0.0                 # Angle initial en radians
arcs = []                             # Liste des arcs
counter = 0                           # Compteur pour atteindre 90 en 61 secondes
game_over = False                     # Indique si le jeu est terminé
winner = None                         # Variable pour stocker le gagnant
firework_images = []
current_firework_frame = 0
firework_animation_speed = 0.5  # Vitesse de l'animation en secondes par image
# Variables globales supplémentaires
game_start_time = time.time()  # Temps de début du jeu
game_over_time_remaining = 0


# Noms des équipes
CHOIX_1 = "chocolatine"
CHOIX_2 = "pain au chocolat"

# Liste pour stocker les frames capturées
frames = []
# Classe Arc
class Arc:
    def __init__(self, radius, angle_start, radius_speed):
        self.radius = radius
        self.angle_start = angle_start
        self.radius_speed = radius_speed

def draw_text(text, font, color, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    return textobj, textrect

firework_images = []
firework_folder = "path_to_output_folder"  # Remplacez par le chemin de votre dossier de sortie

for filename in sorted(os.listdir(firework_folder)):
    if filename.endswith(".png"):
        img = pygame.image.load(os.path.join(firework_folder, filename))
        img = pygame.transform.scale(img, SCREEN_SIZE)
        firework_images.append(img)

def check_ball_collision(ball1, ball2):
    dx = ball1['pos'][0] - ball2['pos'][0]
    dy = ball1['pos'][1] - ball2['pos'][1]
    distance = math.hypot(dx, dy)

    if distance < BALL_RADIUS * 2:
        # Collision detected
        normal = (dx / distance, dy / distance)

        # Relative velocity
        rel_velocity = (ball1['velocity'][0] - ball2['velocity'][0],
                        ball1['velocity'][1] - ball2['velocity'][1])

        # Relative velocity in terms of the normal direction
        vel_along_normal = rel_velocity[0] * normal[0] + rel_velocity[1] * normal[1]

        # Do not resolve if balls are moving away
        if vel_along_normal > 0:
            return

        # Calculate restitution
        restitution = min(ball1.get('restitution', BOUNCE_RESTITUTION),
                          ball2.get('restitution', BOUNCE_RESTITUTION))

        # Calculate impulse scalar
        impulse = -(1 + restitution) * vel_along_normal
        impulse /= 2  # Assuming both balls have the same mass

        # Apply impulse
        impulse_vector = (impulse * normal[0], impulse * normal[1])

        ball1['velocity'][0] += impulse_vector[0]
        ball1['velocity'][1] += impulse_vector[1]
        ball2['velocity'][0] -= impulse_vector[0]
        ball2['velocity'][1] -= impulse_vector[1]

# ---------------------------
# Initialisation du jeu
# ---------------------------
def init():
    """
    Initialise les éléments graphiques et physiques.
    Crée la surface semi-transparente pour la traînée.
    """
    global screen, clock, trail_surface, arc_angle_start, balls, arcs, compteur_destroyed_arc, current_firework_frame

    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Jeu hypnotique - Arc tournant")

    clock = pygame.time.Clock()
    game_start_time = time.time()

        # Charger les images de feu d'artifice
    img = pygame.image.load("VZvx.gif")
    img = pygame.transform.scale(img, SCREEN_SIZE)
    firework_images.append(img)

    # Surface pour la traînée (avec canal alpha)
    trail_surface = pygame.Surface((2*TRAIL_RADIUS, 2*TRAIL_RADIUS), pygame.SRCALPHA)
    pygame.draw.circle(trail_surface, TRAIL_COLOR,
                      (TRAIL_RADIUS, TRAIL_RADIUS), TRAIL_RADIUS)

    # Charger les images pour les balles
    ball_image_red = pygame.image.load('Paris_Saint-Germain_Logo.svg.png')  # Remplacez par le chemin de votre image
    ball_image_red = pygame.transform.scale(ball_image_red, (BALL_RADIUS * 2, BALL_RADIUS * 2))

    ball_image_blue = pygame.image.load('png-transparent-inter-milan-2021-hd-logo-thumbnail.png')  # Remplacez par le chemin de votre image
    ball_image_blue = pygame.transform.scale(ball_image_blue, (BALL_RADIUS * 2, BALL_RADIUS * 2))

    # Initialisation des boules
    balls = [{
        'name': 'red',
        'pos': [CIRCLE_POS[0] + 90, CIRCLE_POS[1] - 370],
        'velocity': [10.0, 10.0],
        'trail': [],
        'color_ball': (229, 53, 23),
        'image': ball_image_red,
        'ball_size': 30
    },{
        'name': 'blue',
        'pos': [CIRCLE_POS[0] - 90, CIRCLE_POS[1] - 370],
        'velocity': [10.0, 10.0],
        'trail': [],
        'color_ball': (0, 128, 255),
        'image': ball_image_blue,
        'ball_size': 30
        }
    ]
    # Initialisation des arcs
    arcs = []
    nbr_arcs = 1  # Nombre d'arcs à créer
    one_purcent = 360 / nbr_arcs  # Angle de 1% de la rotation totale
    for i in range(nbr_arcs):
        radius = CIRCLE_RADIUS + 50*i  # Diminution uniforme du rayon
        #arcs.append(Arc(radius, 0.0,math.radians(45-(i*one_purcent))))
        arcs.append(Arc(radius, 0.0,math.radians(random.randint(10, 30))))

    arc_angle_start = 0.0  # Départ à 0 radians (vers la droite)

# ---------------------------
# Mise à jour physique (partie corrigée)
# ---------------------------
def update_physics(dt):
    global balls, arc_angle_start, arc, compteur_destroyed_arc, compteur_rebond,game_start_time, game_over_time_remaining, game_over, winner, compteur_destroyed_arc_red, compteur_destroyed_arc_blue, counter, game_over, winner, current_firework_frame, post_game_counter, post_game_duration

    if game_over:
        game_over_time_remaining -= dt
        if game_over_time_remaining <= 0:
            return False  # Indique que le jeu est terminé et prêt pour l'enregistrement
        return True  # Indique que le jeu continue
    current_time = time.time()
    elapsed_time = current_time - game_start_time

    balls_to_remove = []
    new_balls = []
    first_circle_radius = arcs[0].radius
    arc0 = arcs[0]  # Rayon du premier arc
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
        collision_distance = first_circle_radius - BALL_RADIUS

        if distance >= collision_distance:
            # Normale de collision (direction radiale)
            normal = (dx/distance, dy/distance) if distance > 0 else (0, 1)

            # Conversion en angle horaire pygame (y inversé)
            collision_angle = math.atan2(-normal[1], normal[0]) % (2 * math.pi)

            # Calcul des bornes de l'arc
            start = arc0.angle_start % (2 * math.pi)
            end = (start + ARC_ANGLE_SPAN) % (2 * math.pi)

            # Vérification de la collision avec l'arc
            if start < end:
                in_arc = start <= collision_angle < end
            else:
                in_arc = collision_angle >= start or collision_angle < end

            if in_arc:
                # Rebond sur l'arc
                compteur_rebond +=1
                dot = ball['velocity'][0] * normal[0] + ball['velocity'][1] * normal[1]
                ball['velocity'][0] -= (1 + BOUNCE_RESTITUTION) * dot * normal[0]
                ball['velocity'][1] -= (1 + BOUNCE_RESTITUTION) * dot * normal[1]

                # Correction de position
                overshoot = distance - collision_distance
                ball['pos'][0] -= normal[0] * overshoot
                ball['pos'][1] -= normal[1] * overshoot

            else:#sors de l'arc
                ball["ball_size"] -= 5
                if ball["ball_size"] < 5:  # Seuil de taille pour déclencher la fin de la partie
                    ball["ball_size"] = 5  # Assurez-vous que la balle ne devient pas trop petite
                    game_over = True
                    game_over_time_remaining = 62 - elapsed_time
                    # Déterminer le gagnant
                    if compteur_destroyed_arc_blue > compteur_destroyed_arc_red:
                        winner = CHOIX_1
                    elif compteur_destroyed_arc_red > compteur_destroyed_arc_blue:
                        winner = CHOIX_2
                    else:
                        winner = "Match nul"

                # Échappement par le trou
                ball['pos'] = [CIRCLE_POS[0], CIRCLE_POS[1]]
                if ball['name'] == 'red':
                    compteur_destroyed_arc_red +=1
                elif ball['name'] == 'blue':
                    compteur_destroyed_arc_blue +=1



        # Mise à jour de la traînée
        ball['trail'].append((int(ball['pos'][0]), int(ball['pos'][1])))
        if len(ball['trail']) > TRAIL_LENGTH:
            ball['trail'].pop(0)
        if elapsed_time >= 62:  # Exemple de condition pour "game over"
            game_over = True
            # Déterminer le gagnant
            if compteur_destroyed_arc_blue > compteur_destroyed_arc_red:
                winner = CHOIX_1
            elif compteur_destroyed_arc_red > compteur_destroyed_arc_blue:
                winner = CHOIX_2
            else:
                winner = "Match nul"

    # Check for collisions between balls
    for i, ball1 in enumerate(balls):
        for ball2 in balls[i+1:]:
            check_ball_collision(ball1, ball2)

    # Rotation de l'arc
    for arc in arcs :
        arc.angle_start += arc.radius_speed * dt
        arc.angle_start %= (2 * math.pi)

    # Effritement des cercles : diminution du rayon des arcs

    for arc in arcs:
        delta = arc0.radius - RADIUS_MIN
        arc.radius -= (delta*0.1*20) * dt  # Diminution du rayon

    # Mise à jour du compteur
    counter_increment = 90 / 61  # Incrément pour atteindre 90 en 51 secondes
    counter += counter_increment * dt
    if counter >= 90:
        counter = 90
        game_over = True
        # Déterminer le gagnant
        if compteur_destroyed_arc_blue > compteur_destroyed_arc_red:
            winner = CHOIX_1
        elif compteur_destroyed_arc_red > compteur_destroyed_arc_blue:
            winner = CHOIX_2
        else:
            winner = "Match nul"

        print(f"Victoire de l'équipe {winner}")
    return True

# ---------------------------
# Dessin des éléments
# ---------------------------

def draw():
    """Dessine l'arc tournant, les boules et leurs traînées"""
    global winner
    screen.fill(BACKGROUND_COLOR)

    for arc in arcs:
            if arc == arcs[0]:
                CIRCLE_COLOR =  (107, 142, 35)
            else:
                CIRCLE_COLOR = (255, 255, 255)
            if arc.radius >= MIN_RADIUS:
                # Ne pas dessiner si le rayon est trop petit
                continue
            arc_rect = pygame.Rect(
                CIRCLE_POS[0] - arc.radius,
                CIRCLE_POS[1] - arc.radius,
                2 * arc.radius,
                2 * arc.radius
            )

            pygame.draw.arc(
                screen,
                CIRCLE_COLOR,
                arc_rect,
                arc.angle_start,
                arc.angle_start + ARC_ANGLE_SPAN,
                ARC_WIDTH
            )

    # Dessin des traînées et boules
    for ball in balls:
        # Traînée
        if ball['name'] == 'blue':
            trail_surface = pygame.Surface((2 * TRAIL_RADIUS, 2 * TRAIL_RADIUS), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (0, 0, 255, 102), (TRAIL_RADIUS, TRAIL_RADIUS), TRAIL_RADIUS)
        elif ball['name'] == 'red':
            trail_surface = pygame.Surface((2 * TRAIL_RADIUS, 2 * TRAIL_RADIUS), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (255, 0, 0, 102), (TRAIL_RADIUS, TRAIL_RADIUS), TRAIL_RADIUS)
        else:
            trail_surface = pygame.Surface((2 * TRAIL_RADIUS, 2 * TRAIL_RADIUS), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, TRAIL_COLOR, (TRAIL_RADIUS, TRAIL_RADIUS), TRAIL_RADIUS)
        for pos in ball['trail']:
            screen.blit(trail_surface, (pos[0] - TRAIL_RADIUS, pos[1] - TRAIL_RADIUS))
        # Boule avec image
        pygame.draw.circle(screen, ball['color_ball'], (int(ball['pos'][0]), int(ball['pos'][1])), ball['ball_size'])
    # Affichage du chronomètre et des scores
    font = pygame.font.Font(None, 74)  # Police par défaut, taille 74

    # Fonction pour dessiner du texte avec un contour
    def draw_text_with_outline(screen, text, font, color, outline_color, x, y):
        global winner
        # Rendu du texte principal
        text_surface = font.render(text, True, color)

        # Rendu du contour
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                outline_surface = font.render(text, True, outline_color)
                outline_rect = outline_surface.get_rect(center=(x + dx, y + dy))
                screen.blit(outline_surface, outline_rect)

        # Rendu du texte principal
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    # Affichage du nom et du score de l'équipe 1
    draw_text_with_outline(screen, f"{CHOIX_1}", font, (0, 128, 255), (255, 255, 255), SCREEN_SIZE[0] // 4, SCREEN_SIZE[1] // 3 - 150)

    # Affichage du nom et du score de l'équipe 2
    draw_text_with_outline(screen, f"{CHOIX_2}", font, (229, 53, 23), (255, 255, 255), 3 * SCREEN_SIZE[0] // 4, SCREEN_SIZE[1] // 3 - 150)


    # Affichage du message de victoire
    if game_over:
        winner_text = f"Victoire de l'équipe"
        winner2_text = f"{winner}"
        score_texte = f"{compteur_destroyed_arc_blue} - {compteur_destroyed_arc_red}"
        draw_text_with_outline(screen, winner_text, font, (255, 255, 0), (0, 0, 0), SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
        draw_text_with_outline(screen, winner2_text, font, (255, 255, 0), (0, 0, 0), SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 50)
        draw_text_with_outline(screen, score_texte, font, (255, 255, 0), (0, 0, 0), SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 100)

                # Affichage de l'animation de feu d'artifice
        if firework_images:
            screen.blit(firework_images[int(current_firework_frame)], (0, 0))
    
    # Capturer la frame actuelle
    frame = pygame.surfarray.array3d(screen)
    frame = np.transpose(frame, (1, 0, 2))
    frames.append(frame)


# ---------------------------
# Programme principal
# ---------------------------
if __name__ == "__main__":
    init()

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        dt = clock.tick(FPS) / 1000.0
        running = update_physics(dt)
        draw()
        pygame.display.flip()

    # Arrêter la musique
    pygame.mixer.music.stop()

    # Sauvegarder les frames en tant que vidéo
    if frames:
        clip = ImageSequenceClip(frames, fps=FPS)
        clip.write_videofile("output.mp4")

    pygame.quit()
    sys.exit()
