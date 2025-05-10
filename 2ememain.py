import pygame
import sys
import math
import random

# Initialisation de Pygame
pygame.init()

# Définition des constantes
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAVITY = 0.5

# Création de la fenêtre Pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jeu Hypnotique")

# Chargement de la police
font = pygame.font.SysFont('Arial', 24)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0
        self.vy = 0

    def update(self):
        # Application de la gravité
        self.vy += GRAVITY

        # Mise à jour de la position
        self.x += self.vx
        self.y += self.vy

        # Rebond sur les bords de l'écran
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            self.vx *= -1
        if self.y - self.radius <= 0 or self.y + self.radius >= SCREEN_HEIGHT:
            self.vy *= -1

    def draw(self, surface):
        # Dessiner la balle
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)

        # Ajouter une lueur autour de la balle
        for i in range(5, 0, -1):
            alpha = int(255 * (i / 5) * 0.5)
            glow_color = (255, 255, 255, alpha)
            glow_surface = pygame.Surface((self.radius * 2 * i, self.radius * 2 * i), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (self.radius * i, self.radius * i), self.radius * i)
            surface.blit(glow_surface, (int(self.x - self.radius * i), int(self.y - self.radius * i)))

class Arc:
    def __init__(self, center_x, center_y, radius, thickness, start_angle=None, color=WHITE):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.thickness = thickness
        self.start_angle = start_angle if start_angle is not None else random.uniform(0, 2 * math.pi)
        self.end_angle = self.start_angle + 2 * math.pi * 0.8  # 80% du cercle
        self.color = color
        self.rotation_speed = 0.001
        self.pulse_speed = 0.01
        self.pulse_direction = 1
        self.pulse_amount = 0

    def draw(self, surface):
        rect = pygame.Rect(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        pygame.draw.arc(surface, self.color, rect, self.start_angle, self.end_angle, self.thickness)

    def update(self, shrink_factor):
        self.radius -= shrink_factor
        if self.radius < 0:
            self.radius = 0

        # Rotation lente des arcs
        self.start_angle += self.rotation_speed
        self.end_angle += self.rotation_speed

        # Pulsation douce de la taille des arcs
        self.pulse_amount += self.pulse_speed * self.pulse_direction
        if self.pulse_amount > 5 or self.pulse_amount < -5:
            self.pulse_direction *= -1
        self.radius += self.pulse_amount

    def is_in_hole(self, ball):
        distance = math.sqrt((self.center_x - ball.x) ** 2 + (self.center_y - ball.y) ** 2)
        if abs(distance - self.radius) < ball.radius:
            angle = math.atan2(ball.y - self.center_y, ball.x - self.center_x)
            if angle < 0:
                angle += 2 * math.pi
            if not (self.start_angle <= angle <= self.end_angle):
                return True
        return False

class Game:
    def __init__(self):
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 20)
        self.arcs = []
        self.destroyed_arcs = 0
        self.initialize_arcs()

    def initialize_arcs(self):
        initial_radius = 500
        thickness = 3
        for i in range(100):
            # Calcul de la couleur dégradée
            color_intensity = int(255 * (1 - i / 100))
            color = (255, color_intensity, 255)  # Rouge à violet
            self.arcs.append(Arc(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, initial_radius - i * 5, thickness, color=color))

    def update(self):
        self.ball.update()
        arcs_to_remove = []
        for i, arc in enumerate(self.arcs):
            arc.update(0.1)
            if arc.is_in_hole(self.ball):
                arcs_to_remove.append(i)

        # Retirer les arcs détruits
        for i in sorted(arcs_to_remove, reverse=True):
            self.arcs.pop(i)
            self.destroyed_arcs += 1

    def draw(self, surface):
        surface.fill(BLACK)
        draw_text(f"Arcs détruits : {self.destroyed_arcs}", font, WHITE, surface, 10, 10)
        self.ball.draw(surface)
        for arc in self.arcs:
            arc.draw(surface)

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
