import pygame
import sys
import math
from config import *
from player import Player
from enemy import EnemyManager

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dynamic Defenders")
clock = pygame.time.Clock()

player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
enemy_manager = EnemyManager()

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 72)
title_font = pygame.font.Font(None, 96)
game_state = "start"
start_time = pygame.time.get_ticks()

# Track last DDA check
last_dda_wave = 0
dt = 0
final_survival_time = 0

# Projectile boost tracking
projectile_boost_active = False
projectile_boost_end_time = 0

# Begin AI Generated
# Background stars
stars = []
for _ in range(100):
    x = pygame.math.Vector2(
        random.randint(0, SCREEN_WIDTH),
        random.randint(0, SCREEN_HEIGHT)
    )
    speed = random.uniform(0.5, 2.0)
    size = random.randint(1, 3)
    stars.append({'pos': x, 'speed': speed, 'size': size})

def draw_background(screen, dt):
    # Draw animated starfield
    for star in stars:
        # Move star down
        star['pos'].y += star['speed'] * 60 * dt
        
        # Wrap around
        if star['pos'].y > SCREEN_HEIGHT:
            star['pos'].y = 0
            star['pos'].x = random.randint(0, SCREEN_WIDTH)
        
        # Draw star with twinkle effect
        brightness = 150 + int(50 * math.sin(pygame.time.get_ticks() * 0.005 + star['pos'].x))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (int(star['pos'].x), int(star['pos'].y)), star['size'])

def draw_ui_with_outline(screen, text, font, x, y, color, outline_color=BLACK):
    # Draw outline
    for dx in [-2, 0, 2]:
        for dy in [-2, 0, 2]:
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                screen.blit(outline_surf, (x + dx, y + dy))
    # Draw main text
    text_surf = font.render(text, True, color)
    screen.blit(text_surf, (x, y))
# End AI Generated

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "start" and event.key == pygame.K_SPACE:
                # start
                game_state = "playing"
                start_time = pygame.time.get_ticks()
            elif game_state == "game_over" and event.key == pygame.K_r:
                # restart
                player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
                enemy_manager = EnemyManager()
                game_state = "playing"
                last_dda_wave = 0
                projectile_boost_active = False
                projectile_boost_end_time = 0
                start_time = pygame.time.get_ticks()
    
    if game_state == "playing":
        current_survival_time = (pygame.time.get_ticks() - start_time) / 1000
        if current_survival_time > 0:
            score_rate = player.score / current_survival_time
        else:
            score_rate = 0

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        player.handle_input(keys, mouse_pos, mouse_pressed)
        player.update()
        
        enemy_manager.set_player_pos(player.x, player.y)
        enemy_manager.update(dt)
        
        kills, player_hit, powerup = enemy_manager.check_collisions(player.projectiles, player.get_rect())

        # Powerup collection
        if powerup == "heal" and player.lives < 3:
            player.lives += 1
            print("Player healed! Lives =", player.lives)
        elif powerup == "speed":
            projectile_boost_active = True
            projectile_boost_end_time = pygame.time.get_ticks() + 10000
            player.projectile_speed_multiplier = 2.0
            print("Projectile speed boost activated!")

        player.score += kills * 10
        
        if player_hit:
            if player.take_damage():
                final_survival_time = (pygame.time.get_ticks() - start_time) / 1000
                game_state = "game_over"
        
        # Apply DDA
        if enemy_manager.wave_count > last_dda_wave and enemy_manager.wave_count % DDA_CHECK_INTERVAL == 0:
            enemy_manager.apply_dda(player.lives, current_survival_time, score_rate)
            last_dda_wave = enemy_manager.wave_count

        # temporary projectile speed boost
        if projectile_boost_active:
            if pygame.time.get_ticks() > projectile_boost_end_time:
                projectile_boost_active = False
                player.projectile_speed_multiplier = 1.0
                print("Projectile speed boost ended")

    screen.fill(SPACE_BLACK)
    draw_background(screen, dt)
    
    if game_state == "start":
        # START SCREEN
        draw_ui_with_outline(screen, 'DYNAMIC DEFENDERS', title_font, SCREEN_WIDTH // 2 - 370, 150, (255, 100, 200))
        
        subtitle = 'Survive waves of enemies!'
        draw_ui_with_outline(screen, subtitle, font, SCREEN_WIDTH // 2 - 150, 250, YELLOW)
        
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        start_color = (int(255 * pulse), int(255 * pulse), int(255 * pulse))
        draw_ui_with_outline(screen, 'Press SPACE to Start', font, SCREEN_WIDTH // 2 - 120, 500, start_color)
    
    elif game_state == "playing":
        player.draw(screen)
        enemy_manager.draw(screen)
        
        current_survival_time = (pygame.time.get_ticks() - start_time) / 1000
    
        # Lives (left side)
        lives_text = f'Lives: {player.lives}'
        draw_ui_with_outline(screen, lives_text, font, 10, 10, RED)
        
        # Score
        score_text = f'Score: {player.score}'
        draw_ui_with_outline(screen, score_text, font, 10, 50, YELLOW)
        
        # Time
        time_text = f'Time: {current_survival_time:.1f}s'
        draw_ui_with_outline(screen, time_text, font, 10, 90, WHITE)
        
        # Wave
        wave_text = f'Wave: {enemy_manager.wave_count}'
        draw_ui_with_outline(screen, wave_text, font, SCREEN_WIDTH - 200, 10, CYAN)
        
        # Spawn rate indicator
        spawn_text = f'Spawn (s): {enemy_manager.spawn_rate/1000:.1f}s'
        draw_ui_with_outline(screen, spawn_text, font, SCREEN_WIDTH - 200, 50, YELLOW)
    
        # Begin AI Generated
        # Show boost status with pulsing effect
        if projectile_boost_active:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            boost_color = (255, int(255 * pulse), 0)
            boost_text = 'Projectile Speed Boost Active!'
            draw_ui_with_outline(screen, boost_text, font, SCREEN_WIDTH // 2 - 150, 10, boost_color)
        
        instructions = 'WASD: Move | Mouse: Aim | Left Click: Shoot'
        draw_ui_with_outline(screen, instructions, small_font, SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT - 30, WHITE)

    elif game_state == "game_over":
        player.draw(screen)
        enemy_manager.draw(screen)
        current_survival_time = final_survival_time
        # Game Over screen with arcade style
        # Title
        draw_ui_with_outline(screen, 'GAME OVER', large_font, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100, RED)
        
        # Stats
        score_text = f'Final Score: {player.score}'
        draw_ui_with_outline(screen, score_text, font, SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2, YELLOW)
        
        wave_final_text = f'Waves Survived: {enemy_manager.wave_count}'
        draw_ui_with_outline(screen, wave_final_text, font, SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 40, CYAN)
        
        time_final_text = f'Time: {final_survival_time:.1f}s'
        draw_ui_with_outline(screen, time_final_text, font, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 + 80, WHITE)
        
        # Restart instruction (pulsing)
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        restart_color = (int(255 * pulse), int(255 * pulse), int(255 * pulse))
        restart_text = 'Press R to Restart'
        draw_ui_with_outline(screen, restart_text, font, SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 130, restart_color)
        # End AI Generated

    pygame.display.flip()
    dt = clock.tick(FPS) / 1000.0

pygame.quit()
sys.exit()