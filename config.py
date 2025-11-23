import random

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPACE_BLACK = (10, 10, 30)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (100, 150, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

# Player settings
PLAYER_SIZE = 20
PLAYER_SPEED = 5
PLAYER_LIVES = 3

# Projectile settings
PROJECTILE_SIZE = 5
PROJECTILE_SPEED = 7
FIRE_COOLDOWN = 250

# Enemy settings
ENEMY_SIZE = 20
ENEMY_SPEED = 2
INITIAL_SPAWN_RATE = 2000

# DDA settings
DDA_CHECK_INTERVAL = 1  # Check lives every wave