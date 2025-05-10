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
CIRCLE_RADIUS = 200
CIRCLE_COLOR = (255, 255, 255)

# Paramètres de l'arc tournant
ARC_ROTATION_SPEED = math.radians(30)  # 30°/s convertis en radians/s
ARC_ANGLE_SPAN = math.radians(320)     # 80% de 360° (288°) en radians
ARC_WIDTH = 5

# Boule mobile
BALL_RADIUS = 20
BALL_COLOR = (255, 255, 255)
GRAVITY = 500                      # px/s²
BOUNCE_RESTITUTION = 1.006

# Traînée
TRAIL_LENGTH = 10
TRAIL_RADIUS = 7
TRAIL_COLOR = (255, 0, 0, 102)        # RGBA : 40% d'opacité

# Rayon minimal pour dessiner les arcs
MIN_RADIUS = 750
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

# Classe Arc
class Arc:
    def __init__(self, radius, angle_start, radius_speed):
        self.radius = radius
        self.angle_start = angle_start
        self.radius_speed = radius_speed

def draw_text(text, font, color, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x+50, y+50)

# ---------------------------
# Initialisation du jeu
# ---------------------------
def init():
    """
    Initialise les éléments graphiques et physiques.
    Crée la surface semi-transparente pour la traînée.
    """
    global screen, clock, trail_surface, arc_angle_start, balls, arcs, compteur_destroyed_arc

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
        'name': 'red',
        'pos': [CIRCLE_POS[0] + 90, CIRCLE_POS[1] - 370],
        'velocity': [10.0, 10.0],
        'trail': [],
        'color_ball': (229, 53, 23)
    },{
        'name': 'blue',
        'pos': [CIRCLE_POS[0] - 90, CIRCLE_POS[1] - 370],
        'velocity': [10.0, 10.0],
        'trail': [],
        'color_ball': (0, 128, 255)   
        }
    ]

    # Initialisation des arcs
    arcs = []
    nbr_arcs = 300  # Nombre d'arcs à créer
    one_purcent = 360 / nbr_arcs  # Angle de 1% de la rotation totale
    for i in range(nbr_arcs):
        radius = CIRCLE_RADIUS + 50*i  # Diminution uniforme du rayon
        arcs.append(Arc(radius, 0.0,math.radians(45-(i*one_purcent))))
        #arcs.append(Arc(radius, 0.0,math.radians(random.randint(10, 30))))


    arc_angle_start = 0.0  # Départ à 0 radians (vers la droite)
# ---------------------------
# Mise à jour physique (partie corrigée)
# ---------------------------
def update_physics(dt):
    global balls, arc_angle_start, arc, compteur_destroyed_arc, compteur_rebond, compteur_destroyed_arc_red, compteur_destroyed_arc_blue

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

            else:
                # Échappement par le trou
                balls_to_remove.append(ball)
                arcs.remove(arcs[0])  # Suppression de l'arc correspondant
                if ball['name'] == 'red':
                    compteur_destroyed_arc_red +=1
                elif ball['name'] == 'blue':
                    compteur_destroyed_arc_blue +=1
                compteur_destroyed_arc +=1
                # Création de nouvelles boules
                for _ in range(2):
                    # Position aléatoire près du centre
                    angle = random.uniform(0, 2 * math.pi)
                    radius = random.uniform(50, 100)
                    x = CIRCLE_POS[0] + radius * math.cos(angle)
                    y = CIRCLE_POS[1] + radius * math.sin(angle)

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

    # Rotation de l'arc
    for arc in arcs : 
        arc.angle_start += arc.radius_speed * dt
        arc.angle_start %= (2 * math.pi)


    # Effritement des cercles : diminution du rayon des arcs
    
    for arc in arcs:
        delta = arc0.radius - RADIUS_MIN
        arc.radius -= (delta*0.1*20) * dt  # Diminution du rayon


    # Commentaire : L'effet "effritement" des cercles est simulé en réduisant progressivement le rayon de chaque arc.
    # Lorsque le rayon devient négatif, l'arc est supprimé de la liste, créant ainsi un effet de disparition progressive.
    # De plus, si une boule se trouve à l'intérieur du cercle d'un arc mais en dehors de la zone de l'arc,
    # l'arc est immédiatement retiré de la liste, simulant ainsi sa disparition.

# ---------------------------
# Dessin des éléments
# ---------------------------

def draw():
    """Dessine l'arc tournant, les boules et leurs traînées"""
    screen.fill(BACKGROUND_COLOR)
    # Dessin des arcs supplémentaires
    # Affichage du compteur d'arcs détruits
    font = pygame.font.Font(None, 74)  # Police par défaut, taille 74
    text_surface_arc_destroyed_blue = font.render(str(compteur_destroyed_arc_blue), True, (0, 0, 255))  # Blanc
    text_surface_arc_destroyed_red = font.render(str(compteur_destroyed_arc_red), True, (255,0 ,0 ))  # Blanc
    text_surface_rebond = font.render(str(compteur_rebond), True, (255, 255, 255))
    text_rect_destroyed_blue = text_surface_arc_destroyed_blue.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2))
    text_rect_destroyed_red = text_surface_arc_destroyed_red.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 100))
    text_rect_rebond = text_surface_rebond.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 100))
    screen.blit(text_surface_arc_destroyed_blue, text_rect_destroyed_blue)
    screen.blit(text_surface_arc_destroyed_red, text_rect_destroyed_red)
   # screen.blit(text_surface_rebond, text_rect_rebond)
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

    # Commentaire : Seuls les arcs avec un rayon supérieur ou égal à MIN_RADIUS sont dessinés.
    # Cela permet de filtrer les arcs trop petits et de ne pas les afficher.

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
        # Boule
        pygame.draw.circle(screen, ball['color_ball'],
                          (int(ball['pos'][0]), int(ball['pos'][1])),
                          BALL_RADIUS, 0)

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
