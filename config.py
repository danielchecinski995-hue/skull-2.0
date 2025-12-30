"""
Chainfall - Configuration constants
"""

# Display
SCREEN_WIDTH: int = 480
SCREEN_HEIGHT: int = 800
FPS: int = 60
TITLE: str = "Chainfall: Necropolis"

# Colors (Necromantic Palette)
BG_COLOR: tuple = (5, 5, 5)  # Pitch black/Darkest gray
BONE_WHITE: tuple = (220, 220, 210)
ASH_BEIGE: tuple = (180, 175, 160)
COLD_GREEN: tuple = (40, 180, 140)
MUTED_PURPLE: tuple = (140, 100, 180)

PLAYER_COLOR: tuple = (180, 40, 40) # Deep blood/heart red
PLAYER_GLOW: tuple = (100, 100, 100) # Steel grey
PROJECTILE_COLOR: tuple = (100, 255, 220) # Cold light
PROJECTILE_GLOW: tuple = (40, 180, 140)

# Player
PLAYER_WIDTH: int = 60
PLAYER_HEIGHT: int = 60 # Adjusted for sprite
PLAYER_SPEED: float = 400.0
PLAYER_Y_OFFSET: int = 60

# Projectile
PROJECTILE_RADIUS: int = 5
PROJECTILE_SPEED: float = 600.0
# Snake Physics (Horizontal Wave)
SNAKE_SPEED_X: float = 60.0      # Slowed down from 120.0
SNAKE_SPACING: float = 25.0
SNAKE_DROP_STEP: int = 50        # How much to drop down
SNAKE_LENGTH: int = 25           # Finite snake 
SPRING_STIFFNESS: float = 120.0
RETURN_FORCE: float = 40.0
DAMPING: float = 4.0
MASS: float = 1.0
