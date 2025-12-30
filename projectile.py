"""
Chainfall - Projectile management
"""
import pygame

class Projectile:
    def __init__(self, x, y, image=None):
        self.x = x
        self.y = y
        self.image = image
        self.radius = 5
        self.speed = 600  # pixels per second
        self.color = (255, 220, 100)
        self.glow_color = (255, 180, 50)
        self.active = True

    def update(self, dt):
        self.y -= self.speed * dt

        # Deactivate if off screen
        if self.y < -self.radius:
            self.active = False

    def draw(self, screen):
        if self.image:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.image, rect)
        else:
            # Draw glow
            pygame.draw.circle(screen, self.glow_color, (int(self.x), int(self.y)), self.radius + 3)
            # Draw core
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


class ProjectileManager:
    def __init__(self, image=None):
        self.projectiles = []
        self.image = image

    def spawn(self, x, y):
        self.projectiles.append(Projectile(x, y, self.image))

    def update(self, dt):
        for projectile in self.projectiles:
            projectile.update(dt)

        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, screen):
        for projectile in self.projectiles:
            projectile.draw(screen)

    def get_projectiles(self):
        return self.projectiles
