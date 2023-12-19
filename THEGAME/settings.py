import pygame

#game setup
WIDTH = 1280
HEIGHT = 720
fps = 60
TILESIZE = 32

#Player Settings
PLAYER_START_X = 900
PLAYER_START_Y = 700
player_size = 0.35
PLAYER_SPEED = 8

#Bullet Setting
shoot_cooldown = 10
BULL_SIZE = 0.5
bullet_speed = 50
BULLET_LIFETIME = 750
GUN_OFFSET_X = 45
GUN_OFFSET_Y = 0

#Enemy Setting
ENEMY_SPEED = 4
monster_info = {"slime":{"health":100, "atk_dmg":20, "idlespeed":2, "atk_speed": [4, 4, 7, 7, 7], "image": pygame.image.load("enemy.png"), "image_scale":1.5, "hitbox_rect": pygame.Rect(0, 0, 75, 100), "animspeed":0.2, "roamanimspeed": 0.05, "deathanimspeed": 0.12, "atkradius": 500}}

# colours
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
BLACK = (0,0,0)
WHITE = (255,255,255)

#Game Stats

game_stats = {
    "enemies_killed_or_removed": 0, "slime_death_count": 0, "coins": 0, "health_potion_heal": 20, "current_wave": 1, "number_of_enemies": [3, 4,5], "wave_cooldown": 6000
}