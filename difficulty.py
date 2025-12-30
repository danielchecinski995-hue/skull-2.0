"""
Chainfall - Difficulty scaling system
"""

class DifficultyManager:
    def __init__(self):
        self.game_time = 0
        self.difficulty_level = 1

        # Base values
        self.base_module_count = 3
        self.base_core_integrity = 100
        self.base_module_integrity = 50
        self.base_enemy_speed = 150
        self.base_spawn_delay = 5.0

        # Current values
        self.module_count = self.base_module_count
        self.core_integrity = self.base_core_integrity
        self.module_integrity = self.base_module_integrity
        self.enemy_speed = self.base_enemy_speed
        self.spawn_delay = self.base_spawn_delay

        # Spawn timer
        self.spawn_timer = 0
        self.max_enemies = 1

    def update(self, dt):
        self.game_time += dt
        self.spawn_timer += dt

        # Increase difficulty every 30 seconds
        new_level = int(self.game_time / 30) + 1
        if new_level > self.difficulty_level:
            self.difficulty_level = new_level
            self._scale_difficulty()

    def _scale_difficulty(self):
        """Scale difficulty based on current level"""
        level = self.difficulty_level

        # Module count: +1 every 2 levels
        self.module_count = self.base_module_count + (level - 1) // 2

        # Integrity scaling: +20% per level
        integrity_mult = 1.0 + (level - 1) * 0.2
        self.core_integrity = int(self.base_core_integrity * integrity_mult)
        self.module_integrity = int(self.base_module_integrity * integrity_mult)

        # Speed scaling: +10% per level (capped at 2x)
        speed_mult = min(2.0, 1.0 + (level - 1) * 0.1)
        self.enemy_speed = int(self.base_enemy_speed * speed_mult)

        # Spawn delay reduction: -10% per level (minimum 2 seconds)
        self.spawn_delay = max(2.0, self.base_spawn_delay * (0.9 ** (level - 1)))

        # Max enemies: +1 every 3 levels
        self.max_enemies = 1 + (level - 1) // 3

    def should_spawn(self):
        """Check if it's time to spawn a new enemy"""
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            return True
        return False

    def get_spawn_params(self):
        """Get parameters for spawning a new entity"""
        return {
            'module_count': self.module_count,
            'core_integrity': self.core_integrity,
            'module_integrity': self.module_integrity,
            'speed': self.enemy_speed
        }

    def get_difficulty_level(self):
        return self.difficulty_level
