import pygame
import random
import math
from config import *

class Enemy:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        # Arrive behavior
        self.max_speed = 100.0
        self.max_acceleration = 200.0
        self.target_radius = 5.0
        self.slow_radius = 100.0
        self.time_to_target = 0.1
    
    def arrive(self, target_x, target_y, dt):
        # Direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If we're at the target, stop
        if distance < self.target_radius:
            self.vel_x = 0
            self.vel_y = 0
            return
        
        # Calculate target speed based on distance
        if distance > self.slow_radius:
            target_speed = self.max_speed
        else:
            # Slow down as we approach
            target_speed = self.max_speed * (distance / self.slow_radius)
        
        # Target velocity
        target_vel_x = (dx / distance) * target_speed
        target_vel_y = (dy / distance) * target_speed
        
        # Acceleration to reach target velocity
        accel_x = (target_vel_x - self.vel_x) / self.time_to_target
        accel_y = (target_vel_y - self.vel_y) / self.time_to_target
        
        # Limit acceleration
        accel_mag = math.sqrt(accel_x * accel_x + accel_y * accel_y)
        if accel_mag > self.max_acceleration:
            accel_x = (accel_x / accel_mag) * self.max_acceleration
            accel_y = (accel_y / accel_mag) * self.max_acceleration
        
        # Update velocity
        self.vel_x += accel_x * dt
        self.vel_y += accel_y * dt
    
    def update(self, target_x, target_y, dt):
        # Apply arrive behavior
        self.arrive(target_x, target_y, dt)
        
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (int(self.x - ENEMY_SIZE), int(self.y - ENEMY_SIZE), ENEMY_SIZE * 2, ENEMY_SIZE * 2))
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + 100 or self.y < -100 or self.x < -100 or self.x > SCREEN_WIDTH + 100
    
    def get_rect(self):
        return pygame.Rect(self.x - ENEMY_SIZE, self.y - ENEMY_SIZE, ENEMY_SIZE * 2, ENEMY_SIZE * 2)

# Begin AI Generated
class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.spawn_rate = INITIAL_SPAWN_RATE
        self.last_spawn_time = 0
        self.wave_count = 0
        self.enemies_spawned = 0
        self.player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    
    def set_player_pos(self, x, y):
        self.player_pos = (x, y)
    
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Spawn enemies based on spawn_rate
        if current_time - self.last_spawn_time > self.spawn_rate:
            # Spawn from random side around the screen
            side = random.choice(['top', 'bottom', 'left', 'right'])
            
            if side == 'top':
                x = random.randint(0, SCREEN_WIDTH)
                y = -ENEMY_SIZE
            elif side == 'bottom':
                x = random.randint(0, SCREEN_WIDTH)
                y = SCREEN_HEIGHT + ENEMY_SIZE
            elif side == 'left':
                x = -ENEMY_SIZE
                y = random.randint(0, SCREEN_HEIGHT)
            else:  # right
                x = SCREEN_WIDTH + ENEMY_SIZE
                y = random.randint(0, SCREEN_HEIGHT)
            
            self.enemies.append(Enemy(x, y))
            self.last_spawn_time = current_time
            self.enemies_spawned += 1
            
            # Waves (every 5 enemies = 1 wave)
            if self.enemies_spawned % 5 == 0:
                self.wave_count += 1
        
        # Update enemies with arrive behavior
        for enemy in self.enemies[:]:
            enemy.update(self.player_pos[0], self.player_pos[1], dt)
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
    
    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)
    
    def check_collisions(self, projectiles, player_rect):
        kills = 0
        player_hit = False
        
        # Check projectile hits
        for projectile in projectiles[:]:
            proj_rect = pygame.Rect(projectile.x - PROJECTILE_SIZE, projectile.y - PROJECTILE_SIZE, 
                                    PROJECTILE_SIZE * 2, PROJECTILE_SIZE * 2)
            for enemy in self.enemies[:]:
                if proj_rect.colliderect(enemy.get_rect()):
                    self.enemies.remove(enemy)
                    projectiles.remove(projectile)
                    kills += 1
                    break
        
        # Check player hits
        for enemy in self.enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                self.enemies.remove(enemy)
                player_hit = True
                break
        
        return kills, player_hit
# End AI Generated
    
    def apply_dda(self, player_lives):
        # Only adjust every DDA_CHECK_INTERVAL waves
        if self.wave_count % DDA_CHECK_INTERVAL == 0 and self.wave_count > 0:
            if player_lives == 1:
                # Player struggling - make easier (spawn slower)
                self.spawn_rate = min(3000, self.spawn_rate + 200)
                print(f"DDA: Lives={player_lives}, Making easier! Spawn rate: {self.spawn_rate}ms")
            elif player_lives == 3:
                # Player doing well - make harder (spawn faster)
                self.spawn_rate = max(400, self.spawn_rate - 200)  # Changed from 800 to 300
                print(f"DDA: Lives={player_lives}, Making harder! Spawn rate: {self.spawn_rate}ms")
            else:
                # Lives = 2, keep it balanced
                print(f"DDA: Lives={player_lives}, Keeping balanced. Spawn rate: {self.spawn_rate}ms")