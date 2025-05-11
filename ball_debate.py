import math
import pygame
import random
import time

class Ball:
    def __init__(self, name, pos, velocity, color_ball, image, ball_size, life, circle_pos, gravity, bounce_restitution, trail_length, trail_radius, trail_color, ball_radius, arc_angle_span, state):
        self.name = name
        self.pos = pos
        self.velocity = velocity
        self.trail = []
        self.init_color_ball = color_ball
        self.color_ball = color_ball
        self.image = image
        self.ball_size = ball_size
        self.life = life
        self.circle_pos = circle_pos
        self.gravity = gravity
        self.bounce_restitution = bounce_restitution
        self.trail_length = trail_length
        self.trail_radius = trail_radius
        self.trail_color = trail_color
        self.ball_radius = ball_radius
        self.arc_angle_span = arc_angle_span
        self.state = state  # Ajout d'un attribut pour l'état de la balle
        self.spike_length = 10  # Longueur des épines
        self.spike_number = 8   # Nombre d'épines
        self.spike_duration = 7  # Durée d'activation des épines en secondes
        self.shield_duration = 14  # Durée d'activation du bouclier en secondes

    def increase_life(self):
        """Augmente la vie de la balle de 1."""
        self.life += 1
        self.ball_size += 5  # Augmente la taille de la balle
         
    def decrease_life(self):
        """Diminue la vie de la balle de 1."""
        if not(self.state=="bouclier"):
            self.life -= 1
            self.ball_size -= 5
            if self.ball_size == 0:
                return False
        self.state = "normal"
        self.color_ball = self.init_color_ball
        return True
    def update(self, dt, arc0, first_circle_radius, bonuses):
        global compteur_rebond, compteur_destroyed_arc_blue, compteur_destroyed_arc_red, game_over, winner, game_start_time, game_over_time_remaining

        # Application de la gravité
        self.velocity[1] += self.gravity * dt

                # Vérifier si les épines sont toujours actives
        if self.state == "epine" and (time.time() - self.spike_start_time) > self.spike_duration:
            self.state = "normal"
        # Mise à jour position
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt

        for bonus in bonuses:
            if self.check_collision_with_bonus(bonus) and bonus.active:
                bonus.apply_bonus(self)

        # Calcul distance au centre
        dx = self.pos[0] - self.circle_pos[0]
        dy = self.pos[1] - self.circle_pos[1]
        distance = math.hypot(dx, dy)
        collision_distance = first_circle_radius - self.ball_radius

        if distance >= collision_distance:
            # Normale de collision (direction radiale)
            normal = (dx/distance, dy/distance) if distance > 0 else (0, 1)

            # Conversion en angle horaire pygame (y inversé)
            collision_angle = math.atan2(-normal[1], normal[0]) % (2 * math.pi)

            # Calcul des bornes de l'arc
            start = arc0.angle_start % (2 * math.pi)
            end = (start + self.arc_angle_span) % (2 * math.pi)

            # Vérification de la collision avec l'arc
            if start < end:
                in_arc = start <= collision_angle < end
            else:
                in_arc = collision_angle >= start or collision_angle < end

            if in_arc:
                # Rebond sur l'arc
                dot = self.velocity[0] * normal[0] + self.velocity[1] * normal[1]
                self.velocity[0] -= (1 + self.bounce_restitution) * dot * normal[0]
                self.velocity[1] -= (1 + self.bounce_restitution) * dot * normal[1]

                # Correction de position
                overshoot = distance - collision_distance
                self.pos[0] -= normal[0] * overshoot
                self.pos[1] -= normal[1] * overshoot
            
            else:#sors de l'arc 
                return False

        # Mise à jour de la traînée
        self.trail.append((int(self.pos[0]), int(self.pos[1])))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
        return True
    
    def check_collision_with_bonus(self, bonus):
        """Vérifie la collision entre la balle et un bonus."""
        dx = self.pos[0] - bonus.pos[0]
        dy = self.pos[1] - bonus.pos[1]
        distance = math.hypot(dx, dy)
        return distance < self.ball_radius + bonus.radius
    
    def activate_spikes(self):
        """Active les épines et enregistre le temps de début."""
        self.state = "epine"
        self.color_ball = self.init_color_ball
        self.spike_start_time = time.time()

    def activate_shield(self):
        """Active le bouclier et enregistre le temps de début."""
        self.state = "bouclier"
        self.shield_start_time = time.time()

    def draw(self, screen):
        # Traînée
        if self.name == 'blue':
            trail_surface = pygame.Surface((2 * self.trail_radius, 2 * self.trail_radius), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (0, 0, 255, 102), (self.trail_radius, self.trail_radius), self.trail_radius)
        elif self.name == 'red':
            trail_surface = pygame.Surface((2 * self.trail_radius, 2 * self.trail_radius), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (255, 0, 0, 102), (self.trail_radius, self.trail_radius), self.trail_radius)
        else:
            trail_surface = pygame.Surface((2 * self.trail_radius, 2 * self.trail_radius), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, self.trail_color, (self.trail_radius, self.trail_radius), self.trail_radius)

        for pos in self.trail:
            screen.blit(trail_surface, (pos[0] - self.trail_radius, pos[1] - self.trail_radius))

        # Boule avec image
        if self.state == "epine":
            self.draw_spikes(screen)
        elif self.state == "bouclier":
            self.color_ball = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        pygame.draw.circle(screen, self.color_ball, (int(self.pos[0]), int(self.pos[1])), self.ball_size)

    def draw_spikes(self, screen):
        for i in range(self.spike_number):
            angle = 2 * math.pi * i / self.spike_number
            spike_x = self.pos[0] + math.cos(angle) * (self.ball_size + self.spike_length)
            spike_y = self.pos[1] + math.sin(angle) * (self.ball_size + self.spike_length)
            pygame.draw.line(screen, (255, 255, 255), (int(self.pos[0]), int(self.pos[1])), (int(spike_x), int(spike_y)), 2)

def check_ball_collision(ball1, ball2):
    dx = ball1.pos[0] - ball2.pos[0]
    dy = ball1.pos[1] - ball2.pos[1]
    distance = math.hypot(dx, dy)

    if distance < ball1.ball_radius * 2:
        # Collision detected
        normal = (dx / distance, dy / distance)

        # Relative velocity
        rel_velocity = (ball1.velocity[0] - ball2.velocity[0],
                        ball1.velocity[1] - ball2.velocity[1])

        # Relative velocity in terms of the normal direction
        vel_along_normal = rel_velocity[0] * normal[0] + rel_velocity[1] * normal[1]

        # Do not resolve if balls are moving away
        if vel_along_normal > 0:
            return True

        # Calculate restitution
        restitution = min(ball1.bounce_restitution if hasattr(ball1, 'bounce_restitution') else ball1.bounce_restitution,
                          ball2.bounce_restitution if hasattr(ball2, 'bounce_restitution') else ball2.bounce_restitution)

        # Calculate impulse scalar
        impulse = -(1 + restitution) * vel_along_normal
        impulse /= 2  # Assuming both balls have the same mass

        # Apply impulse
        impulse_vector = (impulse * normal[0], impulse * normal[1])

        ball1.velocity[0] += impulse_vector[0]
        ball1.velocity[1] += impulse_vector[1]
        ball2.velocity[0] -= impulse_vector[0]
        ball2.velocity[1] -= impulse_vector[1]

        # Logique pour les épines
        if ball1.state == "epine":
            if not(ball2.decrease_life()):
                return False
            ball1.state = "normal" # Assurez-vous que la taille ne devient pas négative
            print(ball1.state)
        elif ball2.state == "epine":
            if not(ball1.decrease_life()):
                return False
            ball2.state = "normal"
            print(ball2.state)  # Assurez-vous que la taille ne devient pas négative
    return True

