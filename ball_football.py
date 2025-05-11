import math
import pygame

class Ball:
    def __init__(self, name, pos, velocity, color_ball, image, ball_size, life, circle_pos, gravity, bounce_restitution, trail_length, trail_radius, trail_color, ball_radius, arc_angle_span):
        self.name = name
        self.pos = pos
        self.velocity = velocity
        self.trail = []
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

    def update(self, dt, arc0, first_circle_radius):
        global compteur_rebond, compteur_destroyed_arc_blue, compteur_destroyed_arc_red, game_over, winner, game_start_time, game_over_time_remaining

        # Application de la gravité
        self.velocity[1] += self.gravity * dt

        # Mise à jour position
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt

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
            else:
                return False


        # Mise à jour de la traînée
        self.trail.append((int(self.pos[0]), int(self.pos[1])))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
        return True 
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
        screen.blit(self.image, (int(self.pos[0] - self.ball_radius), int(self.pos[1] - self.ball_radius)))

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
            return

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
