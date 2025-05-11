import math
import pygame

class Arc:
    def __init__(self, radius, angle_start, radius_speed, circle_pos, circle_color, arc_width, min_radius):
        self.radius = radius
        self.angle_start = angle_start
        self.radius_speed = radius_speed
        self.circle_pos = circle_pos
        self.circle_color = circle_color
        self.arc_width = arc_width
        self.min_radius = min_radius

    def update(self, dt):
        self.angle_start += self.radius_speed * dt
        self.angle_start %= (2 * math.pi)

    def draw(self, screen, arc_angle_span, arc_color):
        if self.radius >= self.min_radius:
            return
        arc_rect = pygame.Rect(
            self.circle_pos[0] - self.radius,
            self.circle_pos[1] - self.radius,
            2 * self.radius,
            2 * self.radius
        )
        pygame.draw.arc(
            screen,
            arc_color,
            arc_rect,
            self.angle_start,
            self.angle_start + arc_angle_span,
            self.arc_width
        )
