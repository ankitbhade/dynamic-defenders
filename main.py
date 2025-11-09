import pygame
import sys
from config import *
from player import Player
from enemy import EnemyManager

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dynamic Defenders")
clock = pygame.time.Clock()

# Game objects
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
enemy_manager = EnemyManager()

font = pygame.font.Font(None, 36)
game_over = False

# Track last DDA check
last_dda_wave = 0

# Delta time tracking
clock = pygame.time.Clock()
dt = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                # Restart
                player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
                enemy_manager = EnemyManager()
                game_over = False
                last_dda_wave = 0
    
    if not game_over:
        # Input and update
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        player.handle_input(keys, mouse_pos, mouse_pressed)
        player.update()
        
        # Update enemy manager with player position and delta time
        enemy_manager.set_player_pos(player.x, player.y)
        enemy_manager.update(dt)
        
        # Check collisions
        kills, player_hit = enemy_manager.check_collisions(player.projectiles, player.get_rect())
        player.score += kills * 10
        
        if player_hit:
            if player.take_damage():
                game_over = True
        
        # Apply DDA every DDA_CHECK_INTERVAL waves
        if enemy_manager.wave_count > last_dda_wave and enemy_manager.wave_count % DDA_CHECK_INTERVAL == 0:
            enemy_manager.apply_dda(player.lives)
            last_dda_wave = enemy_manager.wave_count
    
    # Draw
    screen.fill(BLACK)
    player.draw(screen)
    enemy_manager.draw(screen)
    
    # UI
    if not game_over:
        lives_text = font.render(f'Lives: {player.lives}', True, WHITE)
        score_text = font.render(f'Score: {player.score}', True, WHITE)
        wave_text = font.render(f'Wave: {enemy_manager.wave_count}', True, WHITE)
        spawn_text = font.render(f'Spawn Rate: {enemy_manager.spawn_rate/1000}s', True, YELLOW)
        
        screen.blit(lives_text, (10, 10))
        screen.blit(score_text, (10, 50))
        screen.blit(wave_text, (SCREEN_WIDTH - 150, 10))
        screen.blit(spawn_text, (SCREEN_WIDTH - 300, 50))
        
        info_font = pygame.font.Font(None, 24)
        instructions = info_font.render('WASD: Move | Space: Shoot', True, WHITE)
        screen.blit(instructions, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 30))
    else:
        game_over_font = pygame.font.Font(None, 72)
        game_over_text = game_over_font.render('GAME OVER', True, RED)
        score_text = font.render(f'Final Score: {player.score}', True, WHITE)
        restart_text = font.render('Press R to Restart', True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 50))
    
    pygame.display.flip()
    dt = clock.tick(FPS) / 1000.0

pygame.quit()
sys.exit()