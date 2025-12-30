"""
Chainfall - Combat system (collision, knockback, damage numbers)
"""
import pygame
import math
import random

class DamageNumber:
    def __init__(self, x, y, damage):
        self.x = x
        self.y = y
        self.damage = damage
        self.lifetime = 0.8
        self.timer = 0
        self.velocity_y = -80
        self.velocity_x = random.uniform(-30, 30)
        self.active = True
        self.font = None

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.lifetime:
            self.active = False
            return

        self.y += self.velocity_y * dt
        self.x += self.velocity_x * dt
        self.velocity_y += 100 * dt  # Gravity

    def draw(self, screen, font):
        if not self.active:
            return

        alpha = 1.0 - (self.timer / self.lifetime)
        color = (255, 255, 100)

        text = font.render(str(int(self.damage)), True, color)
        text.set_alpha(int(alpha * 255))
        screen.blit(text, (int(self.x) - text.get_width() // 2, int(self.y)))


class CombatManager:
    def __init__(self):
        self.damage_numbers = []
        self.font = None
        self.projectile_damage = 10

    def init_font(self):
        if self.font is None:
            self.font = pygame.font.Font(None, 28)

    def check_collisions(self, projectile_manager, entity_manager):
        """Check projectile-entity collisions"""
        self.init_font()
        hits = []

        projectiles = projectile_manager.get_projectiles()
        entities = entity_manager.get_entities()

        for projectile in projectiles:
            if not projectile.active:
                continue

            px, py = projectile.x, projectile.y
            pr = projectile.radius

            # Check against all entities (segments)
            for entity in entities:
                if not entity.active:
                    continue

                # Get position safely
                if hasattr(entity, 'get_position'):
                    ex, ey = entity.get_position()
                else:
                    ex, ey = entity.x, entity.y
                
                er = entity.get_radius() if hasattr(entity, 'get_radius') else 5

                if self._circle_collision(px, py, pr, ex, ey, er):
                    self._apply_hit(projectile, entity, entity_manager)
                    hits.append(entity)
                    # One projectile hits one target for now
                    break

        return hits

    def _circle_collision(self, x1, y1, r1, x2, y2, r2):
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < r1 + r2

    def _apply_hit(self, projectile, target, entity_manager=None):
        """Apply hit effects to target."""
        projectile.active = False
        
        destroyed = False
        
        # Trigger Global Hit-Stop (Caterpillar Logic)
        if entity_manager and hasattr(entity_manager, 'notify_hit'):
            entity_manager.notify_hit()
        
        # Visual Shake on specific segment
        if hasattr(target, 'hit'):
            target.hit() # Just sets visual shake timer
        
        return destroyed

    def _apply_knockback(self, projectile, target):
        """Apply generic knockback force"""
        # Direction from projectile to target
        if hasattr(target, 'get_position'):
             tx, ty = target.get_position()
        else:
             tx, ty = target.x, target.y
             
        dx = tx - projectile.x
        dy = ty - projectile.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            dx /= dist
            dy /= dist

        knockback_force = 15
        if hasattr(target, 'velocity_x'):
            target.velocity_x += dx * knockback_force
            target.velocity_y += dy * knockback_force
        elif hasattr(target, 'x') and not hasattr(target, 'hit'):
             # Don't push segments directly if they have 'hit' method
            target.x += dx * knockback_force * 0.3
            target.y += dy * knockback_force * 0.3

    def update(self, dt):
        for dn in self.damage_numbers:
            dn.update(dt)

        self.damage_numbers = [dn for dn in self.damage_numbers if dn.active]

    def check_player_collision(self, player, entity_manager):
        """Check if any entity hits the player (Game Over condition)"""
        entities = entity_manager.get_entities()
        player_rect = getattr(player, 'rect', None)
        
        # If player doesn't have rect, use position/radius approx
        px, py = player.x, player.y
        pr = 20 # Approximate player hitbox radius

        for entity in entities:
             if hasattr(entity, 'get_position'):
                 ex, ey = entity.get_position()
             else:
                 ex, ey = entity.x, entity.y
             
             er = entity.get_radius() if hasattr(entity, 'get_radius') else 15

             if self._circle_collision(px, py, pr, ex, ey, er):
                 return True
        return False

    def draw(self, screen):
        self.init_font()
        for dn in self.damage_numbers:
            dn.draw(screen, self.font)
