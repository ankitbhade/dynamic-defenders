import pygame
import math
from config import *

class Projectile:
    def __init__(self, x, y, angle, speed_multiplier=1.0):
        self.x = x
        self.y = y
        speed = PROJECTILE_SPEED * speed_multiplier
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        self.trail = []
        self.frame = 0
    
    def update(self):
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 5:
            self.trail.pop(0)    
        self.x += self.vel_x
        self.y += self.vel_y
        self.frame += 1
    
    # Begin AI Generated
    def draw(self, screen):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            size = PROJECTILE_SIZE * (i / len(self.trail))
            color = (255, 255, 100 + int(155 * (i / len(self.trail))))
            pygame.draw.circle(screen, color, pos, max(2, int(size)))
        
        # Draw main projectile with glow
        glow_color = (255, 255, 150)
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), PROJECTILE_SIZE + 2)
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), PROJECTILE_SIZE)
    # End AI Generated

    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lives = PLAYER_LIVES
        self.score = 0
        self.projectiles = []
        self.last_shot_time = 0
        self.mouse_x = x
        self.mouse_y = y
        self.projectile_speed_multiplier = 1.0
        self.animation_frame = 0
        self.hit_flash = 0
    
    def handle_input(self, keys, mouse_pos, mouse_pressed):
        self.mouse_x, self.mouse_y = mouse_pos
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += PLAYER_SPEED
        
        self.x = max(PLAYER_SIZE, min(self.x, SCREEN_WIDTH - PLAYER_SIZE))
        self.y = max(PLAYER_SIZE, min(self.y, SCREEN_HEIGHT - PLAYER_SIZE))
        
        if mouse_pressed[0]:
            self.shoot()
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > FIRE_COOLDOWN:
            dx = self.mouse_x - self.x
            dy = self.mouse_y - self.y
            angle = math.atan2(dy, dx)
            
            self.projectiles.append(Projectile(self.x, self.y, angle, self.projectile_speed_multiplier))
            self.last_shot_time = current_time
    
    def update(self):
        self.animation_frame += 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        
        for projectile in self.projectiles[:]:
            projectile.update()
            if projectile.is_off_screen():
                self.projectiles.remove(projectile)
    
    # Begin AI Generated
    def draw(self, screen):
        # Draw spaceship player
        ship_color = WHITE if self.hit_flash > 0 else CYAN
        
        # Calculate rotation angle towards mouse
        dx = self.mouse_x - self.x
        dy = self.mouse_y - self.y
        angle = math.atan2(dy, dx)
        
        # Ship body (main triangle)
        size = PLAYER_SIZE
        # Front point
        front_x = self.x + math.cos(angle) * size
        front_y = self.y + math.sin(angle) * size
        # Back left
        back_left_x = self.x + math.cos(angle + 2.5) * (size * 0.6)
        back_left_y = self.y + math.sin(angle + 2.5) * (size * 0.6)
        # Back right
        back_right_x = self.x + math.cos(angle - 2.5) * (size * 0.6)
        back_right_y = self.y + math.sin(angle - 2.5) * (size * 0.6)
        
        # Draw glow
        glow_points = [
            (int(front_x), int(front_y)),
            (int(back_left_x), int(back_left_y)),
            (int(back_right_x), int(back_right_y))
        ]
        pygame.draw.polygon(screen, (100, 200, 255), glow_points, 3)
        
        # Draw main ship
        ship_points = [
            (int(front_x), int(front_y)),
            (int(back_left_x), int(back_left_y)),
            (int(back_right_x), int(back_right_y))
        ]
        pygame.draw.polygon(screen, ship_color, ship_points)
        
        # Engine glow (animated)
        if self.animation_frame % 6 < 3:
            engine_color = (255, 150, 0)
        else:
            engine_color = (255, 100, 0)
        
        engine_x = self.x - math.cos(angle) * (size * 0.4)
        engine_y = self.y - math.sin(angle) * (size * 0.4)
        pygame.draw.circle(screen, engine_color, (int(engine_x), int(engine_y)), 4)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
    # End AI Generated
    
    def get_rect(self):
        return pygame.Rect(self.x - PLAYER_SIZE, self.y - PLAYER_SIZE, PLAYER_SIZE * 2, PLAYER_SIZE * 2)
    
    def take_damage(self):
        self.lives -= 1
        self.hit_flash = 30
        return self.lives <= 0