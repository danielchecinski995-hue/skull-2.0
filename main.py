"""
Chainfall - Main Game Loop (Async for Pygbag)
"""
import pygame
import asyncio
from player import Player
from projectile import ProjectileManager
from entity_core import EntityManager
from combat import CombatManager
from progression import ProgressionManager
from difficulty import DifficultyManager
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR

async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chainfall")
    clock = pygame.time.Clock()

    # Load Assets
    try:
        assets = {
            'player': pygame.image.load('assets/player.png').convert_alpha(),
            'enemy': pygame.image.load('assets/enemy.png').convert_alpha(),
            'enemy_head': pygame.image.load('assets/enemy_head.png').convert_alpha(),
            'projectile': pygame.image.load('assets/projectile.png').convert_alpha(),
            'orb': pygame.image.load('assets/orb.png').convert_alpha(),
            # Background is solid color now
        }
        
        # Scale assets to appropriate sizes
        assets['player'] = pygame.transform.scale(assets['player'], (60, 60))
        assets['enemy'] = pygame.transform.scale(assets['enemy'], (40, 40))
        assets['enemy_head'] = pygame.transform.scale(assets['enemy_head'], (60, 60))  # Head is 1.5x larger
        assets['projectile'] = pygame.transform.scale(assets['projectile'], (16, 24))
        assets['orb'] = pygame.transform.scale(assets['orb'], (20, 20))
    except Exception as e:
        print(f"Error loading assets: {e}")
        assets = {}

    # Initialize game objects
    player = Player(SCREEN_WIDTH, SCREEN_HEIGHT, assets.get('player'))
    projectile_manager = ProjectileManager(assets.get('projectile'))
    entity_manager = EntityManager(SCREEN_WIDTH, SCREEN_HEIGHT, assets.get('enemy'), assets.get('enemy_head'))
    combat_manager = CombatManager()
    progression_manager = ProgressionManager(SCREEN_WIDTH, SCREEN_HEIGHT, assets.get('orb'))
    difficulty_manager = DifficultyManager()

    # Spawn initial enemy (handled by EntityManager in Horizontal Wave mode)

    # Spawn initial enemy (handled by EntityManager in Horizontal Wave mode)
    
    running = True
    game_over = False
    font_game_over = pygame.font.Font(None, 74)

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    # Quick reset (re-init modules)
                    player = Player(SCREEN_WIDTH, SCREEN_HEIGHT, assets.get('player'))
                    entity_manager = EntityManager(SCREEN_WIDTH, SCREEN_HEIGHT, assets.get('enemy'), assets.get('enemy_head'))
                    game_over = False

        keys = pygame.key.get_pressed()

        # Update managers
        if not game_over:
            if not progression_manager.upgrade_active:
                player.update(dt, keys)
                player.try_fire(projectile_manager)
                projectile_manager.update(dt)
                entity_manager.update(dt)
                difficulty_manager.update(dt)
                hits = combat_manager.check_collisions(projectile_manager, entity_manager)
                combat_manager.update(dt)

                # Check Game Over
                if combat_manager.check_player_collision(player, entity_manager):
                    game_over = True
                    print("GAME OVER")

                # Spawn energy orbs from destroyed targets
                for target in hits:
                    if not target.active:
                        progression_manager.spawn_orb(target.x, target.y, 15)

            progression_manager.update(dt, player)

        # Render
        screen.fill(BG_COLOR)
        entity_manager.draw(screen)
        projectile_manager.draw(screen)
        player.draw(screen)
        combat_manager.draw(screen)
        progression_manager.draw(screen)

        if game_over:
            text = font_game_over.render("GAME OVER", True, (255, 50, 50))
            rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(text, rect)
            
            sub_text = pygame.font.Font(None, 36).render("Press R to Restart", True, (200, 200, 200))
            sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
            screen.blit(sub_text, sub_rect)

        pygame.display.flip()
        
        # Async Sleep for Browser Event Loop
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
