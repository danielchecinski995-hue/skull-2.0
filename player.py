"""
Chainfall - Player movement and firing logic
"""
import pygame

class Player:
    def __init__(self, screen_width, screen_height, image=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = image

        # Player dimensions
        self.width = 60
        self.height = 60 if image is None else image.get_height()

        # Position (centered horizontally, near bottom)
        self.x = screen_width / 2
        self.y = screen_height - 60

        # Movement
        self.speed = 400  # pixels per second
        self.velocity_x = 0

        # Firing
        self.fire_rate = 0.15  # seconds between shots
        self.fire_timer = 0

        # Visual
        self.color = (100, 200, 255)
        self.glow_color = (50, 150, 255)

    def update(self, dt, keys):
        # Horizontal movement
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed

        # Apply movement with delta time
        self.x += self.velocity_x * dt

        # Screen bounds
        half_width = self.width / 2
        if self.x < half_width:
            self.x = half_width
        if self.x > self.screen_width - half_width:
            self.x = self.screen_width - half_width

        # Update fire timer
        if self.fire_timer > 0:
            self.fire_timer -= dt

    def try_fire(self, projectile_manager):
        if self.fire_timer <= 0:
            projectile_manager.spawn(self.x, self.y - self.height / 2)
            self.fire_timer = self.fire_rate

    def draw(self, screen):
        if self.image:
             # Draw sprite centered
            rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, rect)
        else:
            # Draw glow effect
            glow_rect = pygame.Rect(
                self.x - self.width / 2 - 4,
                self.y - self.height / 2 - 4,
                self.width + 8,
                self.height + 8
            )
            pygame.draw.rect(screen, self.glow_color, glow_rect, border_radius=6)

            # Draw main body
            main_rect = pygame.Rect(
                self.x - self.width / 2,
                self.y - self.height / 2,
                self.width,
                self.height
            )
            pygame.draw.rect(screen, self.color, main_rect, border_radius=4)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width,
            self.height
        )
