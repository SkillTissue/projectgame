from ctypes.wintypes import HPALETTE
import math
from multiprocessing import spawn
import pygame
from sys import exit
from settings import * 
from csv import reader
import random
from os import walk

pygame.init()
pygame.mixer.init(44100, -16, 2, 2048)

#Creating the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('THE GAME')

#images. lots of images.
top_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_18.png").convert_alpha(), (1,2))
bottom_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_46.png").convert_alpha(), (1,2))
right_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_17.png").convert_alpha(), (1,2))
left_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_19.png").convert_alpha(), (1,2))
topright_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_23.png").convert_alpha(), (1,2))
topleft_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_24.png").convert_alpha(), (1,2))
left_wall_connect_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_31.png").convert_alpha(), (1,2))
right_wall_connect_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_30.png").convert_alpha(), (1,2))
topright_black_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_38.png").convert_alpha(), (1,2))
topleft_black_wall_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_39.png").convert_alpha(), (1,2))
torch_img = pygame.transform.scale_by(pygame.image.load("tiles/separated/sprite_39.png").convert_alpha(), (1,2))
boundary_block_img = pygame.image.load("tiles/separated/skyBlock.png").convert_alpha()
plain_bg = pygame.image.load("black bg.png").convert()

pygame.display.set_caption("THE GAME")
clock = pygame.time.Clock()

#loads images
background = pygame.image.load("thegame.png").convert()

#fonts
font = pygame.font.Font("font/BrokenConsole.ttf", 20)
small_font = pygame.font.Font("font/BrokenConsole.ttf", 15)
title_font = pygame.font.Font("font/BrokenConsole.ttf", 60)
score_font = pygame.font.Font("font/BrokenConsole.ttf", 50)

#sounds
bulletSound = pygame.mixer.Sound("sounds/bullets.wav")
footsteps = pygame.mixer.Sound("sounds/footsteps.wav")
slimeSound = pygame.mixer.Sound("sounds/slimey.wav")
slimeDeath = pygame.mixer.Sound("sounds/slime_death.wav")
pygame.mixer.music.load("sounds/ANewMorning.ogg")
pygame.mixer.music.set_volume(0.25)

pygame.mixer.music.play(-1)

bulletSound.set_volume(0.2)
slimeSound.set_volume(0.2)
slimeDeath.set_volume(2)

game_active = True
beat_game = False
current_time = 0
level_over_time = 0
ready_to_spawn = False
display_countdown_time = False
first_level = True
def hitboxcollide(sprite1, sprite2):
    return sprite1.base_slime_rect.colliderect(sprite2.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("sprite.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.35)
        self.base_player_image = self.image

        self.pos = pos
        self.vec_pos = pygame.math.Vector2(pos)
        self.base_player_rect = self.base_player_image.get_rect(center = pos)
        self.rect = self.base_player_rect.copy()
        self.moving = False
        self.footsteps_cooldown = 0

        self.player_speed = 10 
        self.shoot = False
        self.shoot_cooldown = 0

        self.health = 100

        self.gun_barrel_offset = pygame.math.Vector2(45,25)

    def player_rotation(self): 
        self.mouse_coords = pygame.mouse.get_pos() 

        self.x_change_mouse_player = (self.mouse_coords[0] - (WIDTH // 2))
        self.y_change_mouse_player = (self.mouse_coords[1] - (HEIGHT // 2))
        self.angle = int(math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player)))
        self.angle = (self.angle) % 360 # if this stop working add 360 in the brackets

        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center = self.base_player_rect.center)

    
    def user_input(self):   
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.velocity_y = -self.player_speed
        if keys[pygame.K_s]:
            self.velocity_y = self.player_speed
        if keys[pygame.K_d]:
            self.velocity_x = self.player_speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.player_speed

        if self.velocity_x != 0 and self.velocity_y != 0: # moving diagonally
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]: 
            self.shoot = True
            self.is_shooting() 
        else:
            self.shoot = False

        if event.type == pygame.KEYUP:
            if pygame.mouse.get_pressed() == (1, 0, 0):
                self.shoot = False
        
        if keys[pygame.K_w]:
            self.moving = True
        elif keys[pygame.K_s]:
            self.moving = True
        elif keys[pygame.K_d]:
            self.moving = True
        elif keys[pygame.K_a]:
            self.moving = True
        else:
            self.moving = False

        if event.type == pygame.KEYUP:
            if keys[pygame.K_w]:
                self.moving = False
            elif keys[pygame.K_s]:
                self.moving = False
            elif keys[pygame.K_d]:
                self.moving = False
            elif keys[pygame.K_a]:
                self.moving = False
             
        

    def is_shooting(self):
        if self.shoot_cooldown == 0 and self.shoot:
            bulletSound.play()
            spawn_bullet_pos = self.vec_pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            self.shoot_cooldown = 10
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)

    def move(self):
        self.base_player_rect.centerx += self.velocity_x
        self.checkcollision("horizontal")

        self.base_player_rect.centery += self.velocity_y
        self.checkcollision("vertical")

        self.rect.center = self.base_player_rect.center 
        
        self.vec_pos = (self.base_player_rect.centerx, self.base_player_rect.centery)
    
    def get_damage(self, amount):
        if ui.current_health > 0:
            ui.current_health -= amount
            self.health -= amount 
        if ui.current_health <= 0:
            ui.current_health = 0
            self.health = 0 

    def checkcollision(self, direction):
        for sprite in obstacles_group:
            if sprite.rect.colliderect(self.base_player_rect):
                if direction == "horizontal":
                    if self.velocity_x > 0:
                        self.base_player_rect.right = sprite.rect.left
                    if self.velocity_x < 0:
                        self.base_player_rect.left = sprite.rect.right

                if direction == "vertical":
                    if self.velocity_y < 0:
                        self.base_player_rect.top = sprite.rect.bottom
                    if self.velocity_y > 0:
                        self.base_player_rect.bottom = sprite.rect.top

    def isMoving(self):
        if self.footsteps_cooldown == 0 and self.moving:
            footsteps.play()
            self.footsteps_cooldown = 40

    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()
        self.isMoving()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.footsteps_cooldown > 0:
            self.footsteps_cooldown -= 1
   
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("bull.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, BULL_SIZE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.speed = bullet_speed
        self.angle = angle
        self.x_vel = math.cos(self.angle*(2*math.pi/360)) * self.speed
        self.y_vel = math.sin(self.angle*(2*math.pi/360)) * self.speed
        self.bullet_lifetime = BULLET_LIFETIME
        self.spawn_time = pygame.time.get_ticks()

    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

    def bullet_collision(self):
        hits = pygame.sprite.groupcollide(enemy_group, bullet_group, False, True, hitboxcollide)

        for h in hits:
            h.health -= 10

        if pygame.sprite.spritecollide(self, obstacles_group, False):
            self.kill()
        
    def update(self):
        self.bullet_movement()
        self.bullet_collision()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, position):
        super().__init__(enemy_group, all_sprites_group)
        self.alive = True
        self.position = pygame.math.Vector2(position) 
        self.direction_index = random.randint(0, 3)
        self.steps = random.randint(3, 6) * TILESIZE
        self.name = name

        enemy_info = monster_info[self.name]
        self.health = enemy_info["health"]
        self.roaming_speed = enemy_info["idlespeed"]
        self.hunting_speed = random.choice(enemy_info["atk_speed"])
        self.image_scale = enemy_info["image_scale"]
        self.image = enemy_info["image"].convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, self.image_scale)
        self.animation_speed = enemy_info["animspeed"]
        self.roam_animation_speed = enemy_info["roamanimspeed"]
        self.death_animation_speed = enemy_info["deathanimspeed"]
        self.notice_radius = enemy_info["atkradius"]
        self.attack_damage = enemy_info["atk_dmg"]
        self.moving = False
        self.footsteps_cooldown = 0

        self.current_index = 0

        self.image.set_colorkey((0,0,0))
        
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        self.hitbox_rect = enemy_info["hitbox_rect"]
        self.base_slime_rect = self.hitbox_rect.copy()
        self.base_slime_rect.center = self.rect.center
             
        self.velocity = pygame.math.Vector2()
        self.direction = pygame.math.Vector2()
        self.direction_list = [(1,1), (1,-1), (-1,1), (-1,-1)]

        self.collide = False

    def roam(self):
        self.direction.x, self.direction.y = self.direction_list[self.direction_index] 
        self.velocity = self.direction * self.roaming_speed
        self.position += self.velocity
            
        self.base_slime_rect.centerx = self.position.x
        self.check_collision("horizontal", "roam")

        self.base_slime_rect.centery = self.position.y
        self.check_collision("vertical", "roam")
            
        self.rect.center = self.base_slime_rect.center
        self.position = (self.base_slime_rect.centerx, self.base_slime_rect.centery)

        self.steps -= 1

        if self.steps == 0:
            self.get_new_direction_and_distance()

    def get_new_direction_and_distance(self):
        self.direction_index = random.randint(0, len(self.direction_list)-1)
        self.steps = random.randint(3, 6) * TILESIZE

    def hunt_player(self):  
        if self.velocity.x > 0:
            self.current_movement_sprite = 0
        else:
            self.current_movement_sprite = 1
        
        player_vector = pygame.math.Vector2(player.base_player_rect.center)
        enemy_vector = pygame.math.Vector2(self.base_slime_rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)

        if distance > 0:
            self.direction = (player_vector - enemy_vector).normalize()
        else:
            self.direction = pygame.math.Vector2()

        self.velocity = self.direction * self.hunting_speed
        self.position += self.velocity

        self.base_slime_rect.centerx = self.position.x
        self.check_collision("horizontal", "hunt")

        self.base_slime_rect.centery = self.position.y
        self.check_collision("vertical", "hunt")

        self.rect.center = self.base_slime_rect.center

        self.position = (self.base_slime_rect.centerx, self.base_slime_rect.centery)
        self.moving = True

    def health_bar(self, x, y):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = 100
        h = 5
        health_bar = HealthBar(x - 60 - GL.offset.x, y - 80 - GL.offset.y, width, h, 100, col)
        health_bar.hp = self.health
        health_bar.draw(screen)

    def check_collision(self, direction, move_state):
        for sprite in obstacles_group:
            if sprite.rect.colliderect(self.base_slime_rect):
                self.collide = True
                if direction == "horizontal":
                    if self.velocity.x > 0:
                        self.base_slime_rect.right = sprite.rect.left
                    if self.velocity.x < 0:
                        self.base_slime_rect.left = sprite.rect.right 
                if direction == "vertical":
                    if self.velocity.y < 0:
                        self.base_slime_rect.top = sprite.rect.bottom
                    if self.velocity.y > 0:
                        self.base_slime_rect.bottom = sprite.rect.top
                if move_state == "roam":
                    self.get_new_direction_and_distance()   

    def check_alive(self):
        if self.health <= 0:
            self.alive = False
            game_stats["enemies_killed_or_removed"] += 1
            game_stats["slime_death_count"] += 1

    def check_player_collision(self):
        if pygame.Rect.colliderect(self.base_slime_rect, player.base_player_rect):
            self.kill()
            slimeDeath.play()
            player.get_damage(self.attack_damage)
            game_stats["enemies_killed_or_removed"] += 1
        

    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()

    def isMoving(self):
        if self.footsteps_cooldown == 0 and self.moving:
            slimeSound.play()
            self.footsteps_cooldown = 50
    
    def update(self):
        self.health_bar(self.position[0], self.position[1])
        self.isMoving()
        if self.footsteps_cooldown > 0:
            self.footsteps_cooldown -= 1
        if self.alive:
            self.check_alive()
            if self.get_vector_distance(pygame.math.Vector2(player.base_player_rect.center), 
                                        pygame.math.Vector2(self.base_slime_rect.center)) < 100:
                self.check_player_collision()
                
            if self.get_vector_distance(pygame.math.Vector2(player.base_player_rect.center), 
                                        pygame.math.Vector2(self.base_slime_rect.center)) < self.notice_radius:    
                self.hunt_player()
            else:
                self.roam()    
        else:
            self.kill()
            slimeDeath.play()
        self.isMoving()
        if self.footsteps_cooldown > 0:
            self.footsteps_cooldown -= 1
            

class UI():
    def __init__(self):
        self.current_health = 100
        self.maximum_health = 100
        self.health_bar_length= 100
        self.health_ratio = self.maximum_health/self.health_bar_length
        self.current_colour = None
    
    def display_health_bar(self):
        pygame.draw.rect(screen, BLACK, (10,15, self.health_bar_length * 3, 20))

        if self.current_health >= 75:
            pygame.draw.rect(screen, GREEN, (10, 15, self.current_health*3, 20))
            self.current_colour = GREEN
        elif self.current_health >= 25:
            pygame.draw.rect(screen, YELLOW, (10, 15, self.current_health*3, 20))
            self.current_colour = YELLOW
        elif self.current_health >= 0:
            pygame.draw.rect(screen, RED, (10,15, self.current_health*3, 20))
            self.current_colour = RED
        
        pygame.draw.rect(screen, WHITE, (10, 15, self.health_bar_length *3, 20), 4)

    def display_health_text(self):
        health_surface = font.render(f"{player.health} / {self.maximum_health}", False, self.current_colour) 
        health_rect = health_surface.get_rect(center = (410, 25))
        screen.blit(health_surface, health_rect)
    
    def display_wave_text(self):
        wave_surface = font.render(f"Wave: {game_stats['current_wave']}", False, GREEN) 
        wave_rect = wave_surface.get_rect(center = (745, 28))
        screen.blit(wave_surface, wave_rect)

    def display_countdown(self, time):
        text_1 = font.render(f"Enemies spawning in {int(time/1000)} seconds!",True, RED)
        screen.blit(text_1, (400, 100))

    def display_enemy_count(self):
        text_1 = font.render(f"Enemies: {game_stats['number_of_enemies'][game_stats['current_wave'] - 1] - game_stats['enemies_killed_or_removed']}",True, GREEN)
        screen.blit(text_1, (855, 18))

    def update(self): 
        self.display_health_bar()
        self.display_health_text()
        self.display_wave_text()
        self.display_enemy_count()
    
class Camera(pygame.sprite.Group):
    def __init__(self): 
        super().__init__()
        self.offset = pygame.math.Vector2()
        self.floor_rect = background.get_rect(topleft = (0, 0))

    def custom_draw(self):
        self.offset.x = player.rect.centerx - WIDTH // 2
        self.offset.y = player.rect.centery - HEIGHT // 2

        # draw the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        screen.blit(background, floor_offset_pos)

        for sprite in all_sprites_group:
            offset_pos = sprite.rect.topleft - self.offset
            screen.blit(sprite.image, offset_pos)

class GameLevel(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = pygame.math.Vector2()
        self.floor_rect = background.get_rect(topleft = (0, 0))
        self.enemy_spawn_pos = [(1000, 400), (1000, 500), (1000, 600)]
        self.create_map()
    
    def spawn_enemies(self):
        self.number_of_enemies = game_stats["number_of_enemies"][game_stats["current_wave"]-1]
        enemy_spawned = 0
        while enemy_spawned < self.number_of_enemies:
            Enemy("slime", random.choice(self.enemy_spawn_pos))
            enemy_spawned += 1

    def create_map(self):
        layouts = {"boundary": self.import_csv_layout("data/csvfiles/Map_boundary.csv"),
                   "walls": self.import_csv_layout("data/csvfiles/Map_Walls.csv"),
                   "enemies": self.import_csv_layout("data/csvfiles/Map_enemies.csv"),
                   "health potions": self.import_csv_layout("data/csvfiles/Map_health potion.csv")
                  }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != "-1":
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == "boundary":
                            Tile((x,y), [obstacles_group], "boundary", col)
                        if style == "walls":
                            Tile((x,y), [all_sprites_group], "walls", col)  
                        if style == "enemies":
                            self.enemy_spawn_pos.append((x, y))
        self.spawn_enemies()

    def import_csv_layout(self, path):
        terrain_map = []
        with open(path) as level_map:
            layout = reader(level_map, delimiter=",")
            for row in layout:
                terrain_map.append(list(row))
            return terrain_map

    def custom_draw(self): 
        self.offset.x = player.rect.centerx - (WIDTH // 2) #REMEMBER TO BLIT THE PLAYER RECT AND NOT BASE RECT!!!!!!!!!!!
        self.offset.y = player.rect.centery - (HEIGHT // 2)

        
        floor_offset_pos = self.floor_rect.topleft - self.offset
        screen.blit(background, floor_offset_pos)

        for sprite in all_sprites_group: 
            offset_pos = sprite.rect.topleft - self.offset
            screen.blit(sprite.image, offset_pos)


class Tile(pygame.sprite.Sprite): 
    def __init__(self, pos, groups, type, unique_id):
        super().__init__(groups)
        if type == "boundary":
            self.image = boundary_block_img
        elif type == "walls":
            if unique_id == "19":
                self.image = top_wall_img
            if unique_id == "55":
                self.image = bottom_wall_img
            if unique_id == "20":
                self.image = left_wall_img
            if unique_id == "18":
                self.image = right_wall_img
            if unique_id == "27":
                self.image = topright_wall_img
            if unique_id == "29":
                self.image = topleft_wall_img
            if unique_id == "38":
                self.image = left_wall_connect_img
            if unique_id == "36":
                self.image = right_wall_connect_img
            if unique_id == "45":
                self.image = topright_black_wall_img
            if unique_id == "47":
                self.image = topleft_black_wall_img
        
        self.rect = self.image.get_rect(topleft = pos)

class HealthBar():
    def __init__(self, x, y, w, h, max_hp, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp
        self.color = color
    
    def draw(self, surface):
        ratio = self.hp/self.max_hp
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, GREEN, (self.x, self.y, self.w*ratio, self.h))


all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
obstacles_group = pygame.sprite.Group()

slime_image = pygame.image.load("enemy.png").convert_alpha()
slime_image = pygame.transform.rotozoom(slime_image,0,2)
slime_rect = slime_image.get_rect(center = (220,340))

camera = Camera()
player = Player((1000,900))

GL = GameLevel()

ui = UI()
start_time = 0
all_sprites_group.add(player)

def calculate_score():
    current_time = int((pygame.time.get_ticks() - start_time)) # resets score when player dies
    return current_time

def display_end_screen():
    screen.fill((40,40,40))
    screen.blit(slime_image, slime_rect)
    if beat_game:
        beat_game_surface = font.render("You beat the game! Thanks for playing!", True, WHITE)
        screen.blit(beat_game_surface, (300, 50))
    else:
        game_over_surface = title_font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_surface, (350, 50))
    text_surface = font.render("> Press 'P' to play again", True, WHITE)
    text_1 = font.render(f"You killed:", True, WHITE)
    text_2 = font.render(f"{game_stats['slime_death_count']} x", True, WHITE) 
    
    screen.blit(text_surface, (WIDTH / 2 - 70, HEIGHT * 7 / 8))
    screen.blit(text_1, (100, 150))
    screen.blit(text_2, (100, 250))
    score_text_1 = font.render(f"Your score:", False, WHITE)
    score_text_2 = score_font.render(f"{score:,}", False, WHITE)
    screen.blit(score_text_1, (550,150))
    screen.blit(score_text_2, (550,250))

def end_game():
    global game_active 
    game_active = False
    for enemy in enemy_group:
        enemy.kill()
    enemy_group.empty() 

while True: 
    current_time = pygame.time.get_ticks()
    if player.health <= 0:
        end_game()

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if not game_active and keys[pygame.K_p]:
            player.health, ui.current_health = 100, 100
            game_active = True
            game_stats["current_wave"] = 1
            start_time = pygame.time.get_ticks()            
            
            game_stats["slime_death_count"] = 0
            
            GL.spawn_enemies()    

    if game_active:
        screen.blit(plain_bg, (0,0))
        GL.custom_draw()
        all_sprites_group.update()
        ui.update()

        if game_stats["enemies_killed_or_removed"] == game_stats["number_of_enemies"][game_stats["current_wave"] - 1]: # level over  
            display_countdown_time = True 
            ready_to_spawn = True 
            level_over_time = pygame.time.get_ticks()
            game_stats["enemies_killed_or_removed"] = 0 
            game_stats["current_wave"] += 1        
            if game_stats["current_wave"] == len(game_stats["number_of_enemies"]) + 1: # beat game
                beat_game = True
                end_game()
            else:
                beat_game = False

        if current_time - level_over_time > game_stats["wave_cooldown"] and ready_to_spawn and not beat_game:
            GL.spawn_enemies()
            ready_to_spawn = False
        if current_time - level_over_time < game_stats["wave_cooldown"] and display_countdown_time and not game_stats["current_wave"] == 1:
            ui.display_countdown(game_stats["wave_cooldown"] - (current_time - level_over_time))
            if current_time - level_over_time > game_stats["wave_cooldown"]:
                display_countdown_time = False
                                                                
        score = calculate_score()
        pygame.display.set_caption(f"{clock.get_fps()}")
    else:
        end_game()
        display_end_screen()

    pygame.display.update()
    clock.tick(fps)