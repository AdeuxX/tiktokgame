import pygame
import sys
import math
import random
import os
import time
import numpy as np
from moviepy import ImageSequenceClip
from datetime import datetime
from ball_debate import *
from arc import *
from draw import *
from bonus import *
# ---------------------------
# Constantes globales
# ---------------------------
# Affichage
SCREEN_SIZE = (650, 1080)
BACKGROUND_COLOR = (0, 0, 0)
FPS = 60

# Cercle fixe (position de collision)
CIRCLE_POS = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
CIRCLE_RADIUS = 300
CIRCLE_COLOR = (255, 255, 255)

# Paramètres de l'arc tournant
ARC_ROTATION_SPEED = math.radians(30)  # 30°/s convertis en radians/s
ARC_ANGLE_SPAN = math.radians(320)     # 80% de 360° (288°) en radians
ARC_WIDTH = 5

# Boule mobile
BALL_RADIUS = 30
BALL_COLOR = (255, 255, 255)
GRAVITY = 500                      # px/s²
BOUNCE_RESTITUTION = 1

# Traînée
TRAIL_LENGTH = 10
TRAIL_RADIUS = 7
TRAIL_COLOR = (255, 0, 0, 102)        # RGBA : 40% d'opacité

# Rayon minimal pour dessiner les arcs
MIN_RADIUS = 400
RADIUS_MIN = 300

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
arcs = []                             # Liste des arcs
bonuses = []                           # Liste des bonus
counter = 0                           # Compteur pour atteindre 90 en 61 secondes
game_over = False                     # Indique si le jeu est terminé
winner = None                         # Variable pour stocker le gagnant
game_start_time = time.time()  # Temps de début du jeu
game_over_time_remaining = 0
last_bonus_time = time.time()  # Temps du dernier bonus généré

# Noms des équipes
CHOIX_1 = "chocolatine"
CHOIX_2 = "pain au chocolat"

# Liste pour stocker les frames capturées
frames = []

post_game_counter = 0
post_game_duration = 10
frames = []

#Firework images
firework_images = []
current_firework_frame = 0
firework_animation_speed = 0.5  # Vitesse de l'animation en secondes par image
firework_images = []
firework_folder = "splited_gif/firework"  # Remplacez par le chemin de votre dossier de sortie
for filename in sorted(os.listdir(firework_folder)):
    if filename.endswith(".png"):
        img = pygame.image.load(os.path.join(firework_folder, filename))
        img = pygame.transform.scale(img, SCREEN_SIZE)
        firework_images.append(img)
def init():
    """
    Initialise les éléments graphiques et physiques.
    Crée la surface semi-transparente pour la traînée.
    """
    global screen, clock, trail_surface, arc_angle_start, balls, arcs, compteur_destroyed_arc, current_firework_frame, game_start_time, firework_images

    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Jeu hypnotique - Arc tournant")

    clock = pygame.time.Clock()
    game_start_time = time.time()
    # Surface pour la traînée (avec canal alpha)
    trail_surface = pygame.Surface((2*TRAIL_RADIUS, 2*TRAIL_RADIUS), pygame.SRCALPHA)
    pygame.draw.circle(trail_surface, TRAIL_COLOR,
                      (TRAIL_RADIUS, TRAIL_RADIUS), TRAIL_RADIUS)

    # Initialisation des boules
    balls = [
        Ball('red', [CIRCLE_POS[0] + 90, CIRCLE_POS[1] - 370], [10.0, 10.0], (229, 53, 23), None, 30, 6, CIRCLE_POS, GRAVITY, BOUNCE_RESTITUTION, TRAIL_LENGTH, TRAIL_RADIUS, TRAIL_COLOR, BALL_RADIUS, ARC_ANGLE_SPAN,"normal"),
        Ball('blue', [CIRCLE_POS[0] - 90, CIRCLE_POS[1] - 370], [10.0, 10.0], (0, 128, 255), None, 30, 6, CIRCLE_POS, GRAVITY, BOUNCE_RESTITUTION, TRAIL_LENGTH, TRAIL_RADIUS, TRAIL_COLOR, BALL_RADIUS, ARC_ANGLE_SPAN,"normal"),
    ]

    # Initialisation des arcs
    arcs = []
    nbr_arcs = 1  # Nombre d'arcs à créer
    one_purcent = 360 / nbr_arcs  # Angle de 1% de la rotation totale
    for i in range(nbr_arcs):
        radius = CIRCLE_RADIUS + 50*i  # Diminution uniforme du rayon
        arcs.append(Arc(radius, 0.0, math.radians(random.randint(10, 30)), CIRCLE_POS, CIRCLE_COLOR, ARC_WIDTH, MIN_RADIUS))

    arc_angle_start = 0.0  # Départ à 0 radians (vers la droite)

def generate_bonus():
    """Génère un nouveau bonus aléatoire."""
    bonus_types = ["bouclier", "epine","epine","epine", "vie","vie","vie","vie","vie","vie","bouclier","bouclier" ]
    bonus_type = random.choice(bonus_types)
    pos = (random.randint(CIRCLE_POS[0]-CIRCLE_RADIUS+50,CIRCLE_POS[0]+CIRCLE_RADIUS-50), random.randint(CIRCLE_POS[1]-CIRCLE_RADIUS+50,CIRCLE_POS[1]+CIRCLE_RADIUS-50))
    return Bonus(pos, bonus_type)

def update_physics(dt):
    global balls, arc_angle_start, compteur_destroyed_arc,last_bonus_time,bonuses, compteur_rebond, game_start_time, game_over_time_remaining, game_over, winner, compteur_destroyed_arc_red, compteur_destroyed_arc_blue, counter, current_firework_frame

    if game_over:
        current_firework_frame += firework_animation_speed
        if current_firework_frame >= len(firework_images):
            current_firework_frame = 0
        game_over_time_remaining -= dt
        if game_over_time_remaining <= 0:
            return False  # Indique que le jeu est terminé et prêt pour l'enregistrement
        return True  # Indique que le jeu continue

    current_time = time.time()
    elapsed_time = current_time - game_start_time

    
    # Génération de bonus toutes les 3 secondes
    if current_time - last_bonus_time > 3:
        bonuses.append(generate_bonus())
        last_bonus_time = current_time

    first_circle_radius = arcs[0].radius
    arc0 = arcs[0]  # Rayon du premier arc
    for ball in balls:
         if not(ball.update(dt, arc0, first_circle_radius, bonuses)) :#une balle est sortie 
            ball.pos = [SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2]
            angle = random.uniform(0, 2 * math.pi)
            ball.velocity = [ball.velocity[0] * math.cos(angle), ball.velocity[1] * math.sin(angle)]
            if not(ball.decrease_life()):
                game_over = True
                winner = ball.name

    # Check for collisions between balls
    for i, ball1 in enumerate(balls):
        for ball2 in balls[i+1:]:
            if not(check_ball_collision(ball1, ball2)):#une balle est morte
                game_over = True
                winner = ball.name
    
    # Rotation de l'arc
    for arc in arcs:
        arc.update(dt)
    # Effritement des cercles : diminution du rayon des arcs
    for arc in arcs:
        delta = arc0.radius - RADIUS_MIN
        arc.radius -= (delta*0.1*20) * dt  # Diminution du rayon

    # Mise à jour du compteur
    counter_increment = 90 / 60  # Incrément pour atteindre 90 en 51 secondes
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

def draw():
    """Dessine l'arc tournant, les boules et leurs traînées"""
    global winner
    screen.fill(BACKGROUND_COLOR)

    for arc in arcs:
        if arc == arcs[0]:
            CIRCLE_COLOR = (107, 142, 35)
        else:
            CIRCLE_COLOR = (255, 255, 255)
        arc.draw(screen, ARC_ANGLE_SPAN, CIRCLE_COLOR)

    for ball in balls:
        ball.draw(screen)
        draw_health(screen, ball, SCREEN_SIZE)

    for bonus in bonuses:
        if bonus.active:
            bonus.draw(screen)

    # Affichage du chronomètre et des scores
    font = pygame.font.Font(None, 74)  # Police par défaut, taille 74

    # Affichage du nom et du score de l'équipe 1
    draw_text_with_outline(screen, f"{CHOIX_1}", font, (0, 128, 255), (255, 255, 255), SCREEN_SIZE[0] // 4, SCREEN_SIZE[1] // 3 - 150)

    # Affichage du nom et du score de l'équipe 2
    draw_text_with_outline(screen, f"{CHOIX_2}", font, (229, 53, 23), (255, 255, 255), 3 * SCREEN_SIZE[0] // 4, SCREEN_SIZE[1] // 3 - 150)

    # Affichage du message de victoire
    if game_over:
        if firework_images:
            screen.blit(firework_images[int(current_firework_frame)], (0, 0))
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

    # Créer le dossier de sortie s'il n'existe pas
    output_dir = "output_videos_debate"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Générer le nom du fichier avec la date et l'heure actuelles
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_filename = f"{CHOIX_1}-{compteur_destroyed_arc_blue}-{compteur_destroyed_arc_red}-{CHOIX_2}-{current_time}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    # Sauvegarder les frames en tant que vidéo
    if frames:
        clip = ImageSequenceClip(frames, fps=FPS)
        clip.write_videofile(output_path)

    pygame.quit()
    sys.exit()
