import pygame
import math
from config import *

class Projectile:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vel_x = math.cos(angle) * PROJECTILE_SPEED
        self.vel_y = math.sin(angle) * PROJECTILE_SPEED
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
    
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), PROJECTILE_SIZE)
    
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
    
    def handle_input(self, keys, mouse_pos, mouse_pressed):
        # Store mouse position
        self.mouse_x, self.mouse_y = mouse_pos
        
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += PLAYER_SPEED
        
        # Keep on screen
        self.x = max(PLAYER_SIZE, min(self.x, SCREEN_WIDTH - PLAYER_SIZE))
        self.y = max(PLAYER_SIZE, min(self.y, SCREEN_HEIGHT - PLAYER_SIZE))
        
        # Shoot with mouse
        if mouse_pressed[0]:
            self.shoot()
    
    # Begin AI Generated
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > FIRE_COOLDOWN:
            # Calculate angle to mouse
            dx = self.mouse_x - self.x
            dy = self.mouse_y - self.y
            angle = math.atan2(dy, dx)
            
            self.projectiles.append(Projectile(self.x, self.y, angle))
            self.last_shot_time = current_time
    
    def update(self):
        for projectile in self.projectiles[:]:
            projectile.update()
            if projectile.is_off_screen():
                self.projectiles.remove(projectile)
    
    def draw(self, screen):
        # Draw player
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), PLAYER_SIZE)
        
        # Draw aiming line
        dx = self.mouse_x - self.x
        dy = self.mouse_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            # Normalize and extend
            line_length = 30
            end_x = self.x + (dx / dist) * line_length
            end_y = self.y + (dy / dist) * line_length
            pygame.draw.line(screen, YELLOW, (int(self.x), int(self.y)), (int(end_x), int(end_y)), 3)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
    
    def get_rect(self):
        return pygame.Rect(self.x - PLAYER_SIZE, self.y - PLAYER_SIZE, PLAYER_SIZE * 2, PLAYER_SIZE * 2)
    # End AI Generated
    
    def take_damage(self):
        self.lives -= 1
        return self.lives <= 0