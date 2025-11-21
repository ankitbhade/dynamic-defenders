import pygame
import random
import math
from config import *

class Enemy:
    def __init__(self, x, y, is_boss=False):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.is_boss = is_boss
        self.health = 3 if is_boss else 1

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
    
    def update(self, target_x, target_y, dt, speed_factor):
        self.max_speed = 100.0 * speed_factor
        self.max_acceleration = 200.0 * speed_factor
        self.slow_radius = 100.0 / speed_factor  # less slowing at higher difficulty
        # Apply arrive behavior
        self.arrive(target_x, target_y, dt)
        
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
    
    def draw(self, screen):
        color = BLUE if self.is_boss else RED
        size = ENEMY_SIZE * (2 if self.is_boss else 1)
        pygame.draw.rect(screen, color, (int(self.x - size), int(self.y - size), size * 2, size * 2))
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + 100 or self.y < -100 or self.x < -100 or self.x > SCREEN_WIDTH + 100
    
    def get_rect(self):
        size = ENEMY_SIZE * (2 if self.is_boss else 1)
        return pygame.Rect(self.x - size, self.y - size, size * 2, size * 2)


    def take_damage(self):
        self.health -= 1
        return self.health <= 0   # True if dead

class PowerUp:
    def __init__(self, x, y, wave_spawned):
        self.x = x
        self.y = y
        self.size = 15
        self.wave_spawned = wave_spawned
    
    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.size)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)


class EnemyManager:
    # Begin AI Generated
    def __init__(self):
        self.enemies = []
        self.spawn_rate = INITIAL_SPAWN_RATE
        self.last_spawn_time = 0
        self.wave_count = 0
        self.enemies_spawned = 0
        self.player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemy_speed_factor = 1.0
        self.powerups = []
        self.last_powerup_wave = 0

    
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

            # boss flag
            is_boss = False

            # Spawn bosses if difficulty is hard
            if self.enemy_speed_factor > 1.25:
                enemies_into_wave = self.enemies_spawned % 5
                if enemies_into_wave == 0:  
                    is_boss = True
            
            self.enemies.append(Enemy(x, y, is_boss))
            self.last_spawn_time = current_time
            self.enemies_spawned += 1
            
            # Waves (every 5 enemies = 1 wave)
            if self.enemies_spawned % 5 == 0:
                self.wave_count += 1
                self.powerups = [p for p in self.powerups if p.wave_spawned == self.wave_count]
            
            # Spawn a powerup every 3 waves
            if self.wave_count % 3 == 0 and self.wave_count != self.last_powerup_wave:
                self.spawn_powerup()
                self.last_powerup_wave = self.wave_count

        # Update enemies with arrive behavior
        for enemy in self.enemies[:]:
            enemy.update(self.player_pos[0], self.player_pos[1], dt, self.enemy_speed_factor)
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
    
    def draw(self, screen):
        for p in self.powerups:
            p.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
    
    def check_collisions(self, projectiles, player_rect):
        kills = 0
        player_hit = False
        powerup_collected = False

        # Check projectile hits
        for projectile in projectiles[:]:
            proj_rect = pygame.Rect(projectile.x - PROJECTILE_SIZE, projectile.y - PROJECTILE_SIZE, PROJECTILE_SIZE * 2, PROJECTILE_SIZE * 2)
            for enemy in self.enemies[:]:
                if proj_rect.colliderect(enemy.get_rect()):
                    projectiles.remove(projectile)
                    if enemy.take_damage():
                        self.enemies.remove(enemy)
                        kills += 1
                    break
        
        # Check player hits
        for enemy in self.enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                self.enemies.remove(enemy)
                player_hit = True
                break

        # Check power up collections
        for p in self.powerups[:]:
            if player_rect.colliderect(p.get_rect()):
                self.powerups.remove(p)
                powerup_collected = True
                break
        
        return kills, player_hit, powerup_collected
    # End AI Generated

    def spawn_powerup(self):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 150)
        self.powerups.append(PowerUp(x, y, self.wave_count))
        print("Powerup spawned in wave", self.wave_count)
 
    def apply_dda(self, player_lives, survival_time, score_rate):
        x = 2.0  # lives weight
        y = 1.0  # survival time weight
        z = 0.5  # score rate weight

        effective_time = math.log(survival_time + 1)

        if player_lives == 1:
            lives_effect = 0.3
        else:
            lives_effect = player_lives

        performance = (lives_effect * x) + (effective_time * y) + (score_rate * z)

        print(f"DDA: lives={player_lives}, time={survival_time:.1f}, "f"rate={score_rate:.2f}, perf={performance:.1f}")

        EASY_THRESHOLD = 4
        HARD_THRESHOLD = 7

        if performance < EASY_THRESHOLD:
            # Player struggling
            self.spawn_rate = min(3000, self.spawn_rate + 200)
            self.enemy_speed_factor = max(0.6, self.enemy_speed_factor - 0.05)
            print(f"Easier: spawn={self.spawn_rate}, speed_factor={self.enemy_speed_factor:.2f}")
        elif performance > HARD_THRESHOLD:
            # Player doing well
            self.spawn_rate = max(400, self.spawn_rate - 200)
            self.enemy_speed_factor = min(2.0, self.enemy_speed_factor + 0.05)
            print(f"Harder: spawn={self.spawn_rate}, speed_factor={self.enemy_speed_factor:.2f}")
        else:
            print("Keeping balanced")