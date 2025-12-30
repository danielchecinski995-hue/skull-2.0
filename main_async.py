"""
Chainfall - Main game loop and state control
"""
import pygame
import sys
from player import Player
from projectile import ProjectileManager
from entity_core import EntityManager
from combat import CombatManager
from progression import ProgressionManager
from difficulty import DifficultyManager

# Game constants
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
FPS = 60
BG_COLOR = (15, 15, 20)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chainfall")
    clock = pygame.time.Clock()

    # Load Assets
    try:
        assets = {
            'player': pygame.image.load('assets/player.png').convert_alpha(),
            'enemy': pygame.image.load('assets/enemy.png').convert_alpha(),
            'projectile': pygame.image.load('assets/projectile.png').convert_alpha(),
            'orb': pygame.image.load('assets/orb.png').convert_alpha(),
            # Background is solid color now
        }
        
        # Scale assets to appropriate sizes
        assets['player'] = pygame.transform.scale(assets['player'], (60, 60))
        assets['enemy'] = pygame.transform.scale(assets['enemy'], (40, 40))
        assets['projectile'] = pygame.transform.scale(assets['projectile'], (16, 24))
        assets['orb'] = pygame.transform.scale(assets['orb'], (20, 20))
    except Exception as e:
        print(f"Error loading assets: {e}")
        assets = {}

    # Initialize game objects
    player = Player(SCREEN_WIDTH, SCREEN_HEIGHT, assets.get('player'))
    projectile_manager = ProjectileManager(assets.get('projectile'))
    entity_manager = EntityManager(SCREEN_WIDTH, SCREEN_HEIGHT, assets.get('enemy'))
    combat_manager = CombatManager()
    progression_manager = ProgressionManager(SCREEN_WIDTH, SCREEN_HEIGHT, assets.get('orb'))
    difficulty_manager = DifficultyManager()

    # Spawn initial enemy
    entity_manager.spawn_entity(difficulty_manager.get_spawn_params())

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            progression_manager.handle_input(event, player, combat_manager)

        # Get keyboard state for continuous movement
        keys = pygame.key.get_pressed()

        # Update (pause if upgrade screen active)
        if not progression_manager.upgrade_active:
            player.update(dt, keys)
            player.try_fire(projectile_manager)
            projectile_manager.update(dt)
            entity_manager.update(dt)
            difficulty_manager.update(dt)
            hits = combat_manager.check_collisions(projectile_manager, entity_manager)
            combat_manager.update(dt)

            # Spawn energy orbs from destroyed targets
            for target in hits:
                if not target.active:
                    progression_manager.spawn_orb(target.x, target.y, 15)

            # Spawn new enemies based on difficulty
            current_count = len(entity_manager.get_entities())
            if difficulty_manager.should_spawn() and current_count < difficulty_manager.max_enemies:
                entity_manager.spawn_entity(difficulty_manager.get_spawn_params())

            # Always have at least one enemy
            if current_count == 0:
                entity_manager.spawn_entity(difficulty_manager.get_spawn_params())

        progression_manager.update(dt, player)

        # Render
        screen.fill(BG_COLOR)
        entity_manager.draw(screen)
        projectile_manager.draw(screen)
        player.draw(screen)
        combat_manager.draw(screen)
        progression_manager.draw(screen)

        # Draw difficulty indicator
        font = pygame.font.Font(None, 24)
        diff_text = font.render(f"Wave {difficulty_manager.get_difficulty_level()}", True, (150, 150, 150))
        screen.blit(diff_text, (SCREEN_WIDTH - diff_text.get_width() - 20, 40))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
