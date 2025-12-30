"""
Chainfall - Entity Module (Following segment logic)
"""
import pygame
import math

class EntityModule:
    def __init__(self, parent, distance=40, integrity=50, image=None):
        self.parent = parent  # Can be EntityCore or another EntityModule
        self.distance = distance
        self.image = image

        # Position - start behind parent
        parent_pos = parent.get_position()
        self.x = parent_pos[0]
        self.y = parent_pos[1] + distance

        # History for smooth following
        self.position_history = [(self.x, self.y)] * 10

        # Size
        self.radius = 18

        # Stats
        self.max_integrity = integrity
        self.integrity = self.max_integrity
        self.active = True

        # Visual
        self.color = (255, 120, 80)
        self.glow_color = (200, 80, 40)

        # Child module (for chaining)
        self.child = None

    def update(self, dt):
        if not self.active:
            return

        # Get parent position
        parent_pos = self.parent.get_position()

        # Calculate direction to parent
        dx = parent_pos[0] - self.x
        dy = parent_pos[1] - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            # Normalize direction
            dx /= dist
            dy /= dist

            # Move to maintain fixed distance from parent
            if dist > self.distance:
                # Too far - move closer
                move_dist = (dist - self.distance) * 8 * dt
                self.x += dx * move_dist
                self.y += dy * move_dist
            elif dist < self.distance * 0.8:
                # Too close - push away
                move_dist = (self.distance - dist) * 5 * dt
                self.x -= dx * move_dist
                self.y -= dy * move_dist

        # Update child if exists
        if self.child:
            self.child.update(dt)

    def take_damage(self, amount):
        self.integrity -= amount
        if self.integrity <= 0:
            self.active = False
            return True  # Destroyed
        return False

    def draw(self, screen):
        if not self.active:
            return

        # Draw connection line to parent
        parent_pos = self.parent.get_position()
        pygame.draw.line(screen, (80, 80, 80),
                        (int(parent_pos[0]), int(parent_pos[1])),
                        (int(self.x), int(self.y)), 3)

        if self.image:
             # Draw sprite centered
             rect = self.image.get_rect(center=(int(self.x), int(self.y)))
             screen.blit(self.image, rect)
        else:
            # Draw glow
            pygame.draw.circle(screen, self.glow_color, (int(self.x), int(self.y)), self.radius + 4)
            # Draw module
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # Draw integrity bar
        bar_width = self.radius * 2
        bar_height = 4
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.radius - 10

        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        fill_width = (self.integrity / self.max_integrity) * bar_width
        pygame.draw.rect(screen, (100, 255, 100), (bar_x, bar_y, fill_width, bar_height))

        # Draw child
        if self.child:
            self.child.draw(screen)

    def get_position(self):
        return (self.x, self.y)

    def get_radius(self):
        return self.radius

    def get_all_modules(self):
        """Get this module and all children as a flat list"""
        modules = [self]
        if self.child and self.child.active:
            modules.extend(self.child.get_all_modules())
        return modules
