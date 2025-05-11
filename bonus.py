import pygame
import math
import os

class Bonus:
    def __init__(self, pos, bonus_type):
        self.pos = pos
        self.bonus_type = bonus_type  # "bouclier", "epine", ou "vie"
        self.radius = 25  # Rayon du bonus
        self.active = True  # Indique si le bonus est actif
        self.image = self.load_image()

    def load_image(self):
        """Charge l'image correspondante au type de bonus."""
        image_paths = {
            "bouclier": "images_png\shield.png",
            "epine": "images_png\spikes.png",
            "vie": "images_png\heart.png"
        }
        image_path = image_paths.get(self.bonus_type)
        if image_path:
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (self.radius * 2, self.radius * 2))
        return None

    def draw(self, screen):
        """Dessine le bonus sur l'écran."""
        if self.image:
            screen.blit(self.image, (int(self.pos[0] - self.radius), int(self.pos[1] - self.radius)))

    def apply_bonus(self, ball):
        """Applique l'effet du bonus à la balle."""
        if self.bonus_type == "bouclier":
            ball.activate_shield()
        elif self.bonus_type == "epine":
            ball.activate_spikes()
        elif self.bonus_type == "vie":
            ball.increase_life()
        self.active = False
