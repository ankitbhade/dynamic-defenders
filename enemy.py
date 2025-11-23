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
        self.animation_frame = 0
        self.hit_flash = 0

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
        self.slow_radius = 100.0 / speed_factor
        
        # Apply arrive behavior
        self.arrive(target_x, target_y, dt)
        
        # Update position
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        self.animation_frame += 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
    
    def draw(self, screen):
        if self.is_boss:
            self.draw_boss(screen)
        else:
            self.draw_regular(screen)
    
    # Begin AI Generated
    def draw_regular(self, screen):
        # Alien-like enemy
        size = ENEMY_SIZE
        color = WHITE if self.hit_flash > 0 else RED
        
        # Body (octagon shape)
        body_points = []
        for i in range(8):
            angle = (math.pi * 2 / 8) * i + (self.animation_frame * 0.02)
            px = self.x + math.cos(angle) * size
            py = self.y + math.sin(angle) * size
            body_points.append((int(px), int(py)))
        
        # Glow
        pygame.draw.polygon(screen, (255, 100, 100), body_points, 2)
        pygame.draw.polygon(screen, color, body_points)
        
        # Eyes
        eye_offset = size * 0.3
        pygame.draw.circle(screen, BLACK, (int(self.x - eye_offset), int(self.y - eye_offset)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + eye_offset), int(self.y - eye_offset)), 3)
    
    def draw_boss(self, screen):
        # Larger, more menacing boss
        size = ENEMY_SIZE * 2
        color = WHITE if self.hit_flash > 0 else BLUE
        
        # Main body (hexagon)
        body_points = []
        for i in range(6):
            angle = (math.pi * 2 / 6) * i + (self.animation_frame * 0.01)
            px = self.x + math.cos(angle) * size
            py = self.y + math.sin(angle) * size
            body_points.append((int(px), int(py)))
        
        # Outer glow
        glow_points = []
        for i in range(6):
            angle = (math.pi * 2 / 6) * i + (self.animation_frame * 0.01)
            px = self.x + math.cos(angle) * (size + 5)
            py = self.y + math.sin(angle) * (size + 5)
            glow_points.append((int(px), int(py)))
        pygame.draw.polygon(screen, (100, 150, 255), glow_points, 3)
        
        # Main body
        pygame.draw.polygon(screen, color, body_points)
        
        # Inner core (pulsing)
        pulse_size = size * 0.5 + math.sin(self.animation_frame * 0.1) * 3
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(pulse_size), 2)
        
        # Health indicator (small bars)
        bar_width = 30
        bar_height = 4
        bar_x = int(self.x - bar_width / 2)
        bar_y = int(self.y - size - 10)
        
        # Background
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        # Health
        health_width = int((self.health / 3) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
    # End AI Generated

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + 100 or self.y < -100 or self.x < -100 or self.x > SCREEN_WIDTH + 100
    
    def get_rect(self):
        size = ENEMY_SIZE * (2 if self.is_boss else 1)
        return pygame.Rect(self.x - size, self.y - size, size * 2, size * 2)

    def take_damage(self):
        self.health -= 1
        self.hit_flash = 10
        return self.health <= 0

class PowerUp:
    def __init__(self, x, y, wave_spawned, power_type):
        self.x = x
        self.y = y
        self.size = 15
        self.wave_spawned = wave_spawned
        self.power_type = power_type
        self.animation_frame = 0
        self.float_offset = 0
    
    # Begin AI Generated
    def update(self):
        self.animation_frame += 1
        self.float_offset = math.sin(self.animation_frame * 0.1) * 5
    
    def draw(self, screen):
        y_pos = int(self.y + self.float_offset)
        
        if self.power_type == "heal":
            # Medical cross
            color = GREEN
            # Glow
            pygame.draw.circle(screen, (100, 255, 100), (self.x, y_pos), self.size + 3, 2)
            # Main circle
            pygame.draw.circle(screen, color, (self.x, y_pos), self.size)
            # Cross
            pygame.draw.rect(screen, WHITE, (self.x - 8, y_pos - 2, 16, 4))
            pygame.draw.rect(screen, WHITE, (self.x - 2, y_pos - 8, 4, 16))
        else:
            # Lightning bolt for speed
            color = YELLOW
            # Glow
            pygame.draw.circle(screen, (255, 255, 150), (self.x, y_pos), self.size + 3, 2)
            # Main circle
            pygame.draw.circle(screen, color, (self.x, y_pos), self.size)
            # Lightning symbol
            bolt_points = [
                (self.x, y_pos - 8),
                (self.x - 3, y_pos),
                (self.x + 2, y_pos),
                (self.x - 2, y_pos + 8)
            ]
            pygame.draw.lines(screen, WHITE, False, bolt_points, 2)
    # End AI Generated

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.spawn_rate = INITIAL_SPAWN_RATE
        self.last_spawn_time = 0
        self.wave_count = 0
        self.enemies_spawned = 0
        self.player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemy_speed_factor = 1.0
        self.powerups = []
        self.last_heal_powerup_wave = -1
        self.last_speed_powerup_wave = -1
    
    def set_player_pos(self, x, y):
        self.player_pos = (x, y)
    
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Spawn enemies based on spawn_rate
        if current_time - self.last_spawn_time > self.spawn_rate:
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

            is_boss = False
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
            
            # Heal power up every 3 waves
            if self.wave_count % 3 == 0 and self.wave_count != self.last_heal_powerup_wave and self.wave_count != 0:
                self.spawn_powerup("heal")
                self.last_heal_powerup_wave = self.wave_count

            # Speed boost every 5 waves
            if self.wave_count % 5 == 0 and self.wave_count != self.last_speed_powerup_wave and self.wave_count != 0:
                self.spawn_powerup("speed")
                self.last_speed_powerup_wave = self.wave_count

        for enemy in self.enemies[:]:
            enemy.update(self.player_pos[0], self.player_pos[1], dt, self.enemy_speed_factor)
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
        
        for p in self.powerups:
            p.update()
    
    def draw(self, screen):
        for p in self.powerups:
            p.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
    
    def check_collisions(self, projectiles, player_rect):
        kills = 0
        player_hit = False
        powerup_collected = None

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
                powerup_collected = p.power_type
                self.powerups.remove(p)
                break
        
        return kills, player_hit, powerup_collected

    def spawn_powerup(self, power_type):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 150)
        self.powerups.append(PowerUp(x, y, self.wave_count, power_type))
        print(f"{power_type.capitalize()} powerup spawned in wave {self.wave_count}")
 
    def apply_dda(self, player_lives, survival_time, score_rate):
        x = 2.0 # lives weight
        y = 1.0 # survival time weight
        z = 0.5 # score rate weight

        effective_time = math.log(survival_time + 1)

        if player_lives == 1:
            lives_effect = 0.3
        else:
            lives_effect = player_lives

        performance = (lives_effect * x) + (effective_time * y) + (score_rate * z)

        print(f"DDA: lives={player_lives}, time={survival_time:.1f}, "f"rate={score_rate:.2f}, perf={performance:.1f}")

        EASY_THRESHOLD = 4
        HARD_THRESHOLD = 7

        # if performance < EASY_THRESHOLD:
        #     self.spawn_rate = min(3000, self.spawn_rate + 200)
        #     self.enemy_speed_factor = max(0.7, self.enemy_speed_factor - 0.05)
        #     print(f"Easier: spawn={self.spawn_rate}, speed_factor={self.enemy_speed_factor:.2f}")
        # elif performance > HARD_THRESHOLD:
        #     self.spawn_rate = max(400, self.spawn_rate - 200)
        #     self.enemy_speed_factor = min(2.0, self.enemy_speed_factor + 0.05)
        #     print(f"Harder: spawn={self.spawn_rate}, speed_factor={self.enemy_speed_factor:.2f}")
        # else:
        #     print("Keeping balanced")
        print(f"No DDA Applied: spawn={self.spawn_rate}, speed_factor={self.enemy_speed_factor:.2f}")