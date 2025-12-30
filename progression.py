"""
Chainfall - Progression system (experience, upgrades)
"""
import pygame
import random
import math

class EnergyOrb:
    def __init__(self, x, y, value=10, image=None):
        self.x = x
        self.y = y
        self.value = value
        self.image = image
        self.radius = 8
        self.active = True
        self.lifetime = 5.0
        self.timer = 0

        # Movement
        self.velocity_y = -50
        self.gravity = 80

        # Visual
        self.color = (100, 255, 200)
        self.glow_color = (50, 200, 150)
        self.pulse = 0

    def update(self, dt, player_x, player_y):
        self.timer += dt
        if self.timer >= self.lifetime:
            self.active = False
            return

        # Pulse animation
        self.pulse += dt * 5

        # Initial upward movement with gravity
        self.velocity_y += self.gravity * dt
        self.y += self.velocity_y * dt

        # Magnet effect towards player when close
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 150:
            # Attract to player
            speed = 300 * (1 - dist / 150)
            if dist > 0:
                self.x += (dx / dist) * speed * dt
                self.y += (dy / dist) * speed * dt

    def draw(self, screen):
        if not self.active:
            return

        pulse_offset = math.sin(self.pulse) * 2
        glow_radius = int(self.radius + 4 + pulse_offset)

        if self.image:
             # Draw sprite centered
             rect = self.image.get_rect(center=(int(self.x), int(self.y)))
             screen.blit(self.image, rect)
        else:
            pygame.draw.circle(screen, self.glow_color, (int(self.x), int(self.y)), glow_radius)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


class Upgrade:
    def __init__(self, name, description, stat, value):
        self.name = name
        self.description = description
        self.stat = stat
        self.value = value


class ProgressionManager:
    def __init__(self, screen_width, screen_height, orb_image=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.orb_image = orb_image

        # Experience
        self.experience = 0
        self.level = 1
        self.exp_to_next = 100

        # Orbs
        self.orbs = []

        # Upgrade state
        self.upgrade_active = False
        self.upgrade_options = []
        self.selected_upgrade = 0

        # Stats that can be upgraded
        self.stats = {
            'damage': 10,
            'fire_rate': 0.15,
            'projectile_speed': 600,
            'move_speed': 400
        }

        # Available upgrades pool
        self.upgrade_pool = [
            Upgrade("Power Shot", "+25% damage", 'damage', 1.25),
            Upgrade("Rapid Fire", "+20% fire rate", 'fire_rate', 0.8),
            Upgrade("Swift Shot", "+15% projectile speed", 'projectile_speed', 1.15),
            Upgrade("Quick Step", "+15% move speed", 'move_speed', 1.15),
        ]

        # Font
        self.font = None
        self.title_font = None

    def init_fonts(self):
        if self.font is None:
            self.font = pygame.font.Font(None, 28)
            self.title_font = pygame.font.Font(None, 42)

    def spawn_orb(self, x, y, value=10):
        self.orbs.append(EnergyOrb(x, y, value, self.orb_image))

    def update(self, dt, player):
        if self.upgrade_active:
            return  # Pause during upgrade selection

        # Update orbs
        for orb in self.orbs:
            orb.update(dt, player.x, player.y)

            # Check collection
            if orb.active:
                dx = player.x - orb.x
                dy = player.y - orb.y
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < player.width / 2 + orb.radius:
                    self.experience += orb.value
                    orb.active = False

                    # Check level up
                    if self.experience >= self.exp_to_next:
                        self.level_up()

        self.orbs = [o for o in self.orbs if o.active]

    def level_up(self):
        self.level += 1
        self.experience -= self.exp_to_next
        self.exp_to_next = int(self.exp_to_next * 1.5)

        # Show upgrade selection
        self.upgrade_active = True
        self.selected_upgrade = 0
        self.upgrade_options = random.sample(self.upgrade_pool, min(3, len(self.upgrade_pool)))

    def handle_input(self, event, player, combat_manager):
        if not self.upgrade_active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.selected_upgrade = (self.selected_upgrade - 1) % len(self.upgrade_options)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.selected_upgrade = (self.selected_upgrade + 1) % len(self.upgrade_options)
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.apply_upgrade(player, combat_manager)

    def apply_upgrade(self, player, combat_manager):
        upgrade = self.upgrade_options[self.selected_upgrade]

        # Apply stat modification
        if upgrade.stat == 'damage':
            combat_manager.projectile_damage = int(combat_manager.projectile_damage * upgrade.value)
        elif upgrade.stat == 'fire_rate':
            player.fire_rate *= upgrade.value
        elif upgrade.stat == 'projectile_speed':
            self.stats['projectile_speed'] = int(self.stats['projectile_speed'] * upgrade.value)
        elif upgrade.stat == 'move_speed':
            player.speed = int(player.speed * upgrade.value)

        self.upgrade_active = False

    def draw(self, screen):
        self.init_fonts()

        # Draw orbs
        for orb in self.orbs:
            orb.draw(screen)

        # Draw XP bar
        bar_width = self.screen_width - 40
        bar_height = 12
        bar_x = 20
        bar_y = 20

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height), border_radius=6)
        # Fill
        fill_ratio = self.experience / self.exp_to_next
        pygame.draw.rect(screen, (100, 255, 200), (bar_x, bar_y, bar_width * fill_ratio, bar_height), border_radius=6)
        # Border
        pygame.draw.rect(screen, (100, 255, 200), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=6)

        # Level text
        level_text = self.font.render(f"LV {self.level}", True, (255, 255, 255))
        screen.blit(level_text, (bar_x, bar_y + bar_height + 5))

        # Draw upgrade selection if active
        if self.upgrade_active:
            self._draw_upgrade_screen(screen)

    def _draw_upgrade_screen(self, screen):
        # Darken background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("LEVEL UP!", True, (100, 255, 200))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))

        subtitle = self.font.render("Choose an upgrade", True, (200, 200, 200))
        screen.blit(subtitle, (self.screen_width // 2 - subtitle.get_width() // 2, 150))

        # Draw upgrade options
        option_width = 120
        option_height = 150
        spacing = 20
        total_width = len(self.upgrade_options) * option_width + (len(self.upgrade_options) - 1) * spacing
        start_x = (self.screen_width - total_width) // 2

        for i, upgrade in enumerate(self.upgrade_options):
            x = start_x + i * (option_width + spacing)
            y = 220

            # Box
            color = (100, 255, 200) if i == self.selected_upgrade else (80, 80, 80)
            pygame.draw.rect(screen, color, (x, y, option_width, option_height), 3, border_radius=8)

            if i == self.selected_upgrade:
                pygame.draw.rect(screen, (30, 60, 50), (x + 3, y + 3, option_width - 6, option_height - 6), border_radius=6)

            # Name
            name_text = self.font.render(upgrade.name, True, (255, 255, 255))
            name_x = x + (option_width - name_text.get_width()) // 2
            screen.blit(name_text, (name_x, y + 20))

            # Description
            desc_text = self.font.render(upgrade.description, True, (180, 180, 180))
            desc_x = x + (option_width - desc_text.get_width()) // 2
            screen.blit(desc_text, (desc_x, y + 60))

        # Instructions
        inst = self.font.render("A/D to select, SPACE to confirm", True, (150, 150, 150))
        screen.blit(inst, (self.screen_width // 2 - inst.get_width() // 2, 420))
