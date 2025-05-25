import os 
import random
import math 
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

BG_COLOR = (183, 234, 245)
WIDTH, HEIGHT = 1000, 768

FPS = 60
PLAYER_VEL = 5

SCORE_FONT = pygame.font.SysFont("arial", 30)
SCORE = 0

FONT = pygame.font.SysFont("arial", 60)

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def show_message(screen, message, color=(255, 255, 255)):
    lines = message.split('\n')
    line_height = FONT.get_height()
    total_height = line_height * len(lines)
    
    for i, line in enumerate(lines):
        text = FONT.render(line, True, color)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - total_height // 2 + i * line_height))
        screen.blit(text, text_rect)

    pygame.display.update()


def load_sprite_sheets(dir1, dir2, width, height, direction = False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width,height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale_by(surface, 4))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)

        else:
            all_sprites[image.replace(".png","")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "sprites", "world_tileset.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale_by(surface, 6)

def get_finish(size):
    path = join("assets", "sprites", "world_tileset.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(112, 80, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale_by(surface, 6)

def get_coin(size):
    path = join("assets", "sprites", "coin.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale_by(surface, 4)

def spawn_coins():
    return [
        Coin(208, HEIGHT - 176, 16),
        Coin(496, HEIGHT - 176, 16),
        Coin(880, HEIGHT - 560, 16),
        Coin(976, HEIGHT - 272, 16),
        Coin(1360, HEIGHT - 176, 16),
    ]

def draw(window, player, objects, coins, offset_x):
    window.fill(BG_COLOR)
    
    for obj in objects:
        obj.draw(window, offset_x)
    
    for coin in coins:
        coin.draw(window, offset_x)

    player.draw(window, offset_x)

    score_text = SCORE_FONT.render(f"Score: {SCORE}", True, (0, 0, 0))
    window.blit(score_text, (10, 10))

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            print(obj)
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
        
            collided_objects.append(obj)
    
    return collided_objects

def check_enemy_collision(player, enemies):
    for enemy in enemies:
        if pygame.sprite.collide_mask(player, enemy):
            return True
    return False

#move player -> check if it collides with oject -> move player in opposite direction 
def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None 
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 3)
    collide_right = collide(player, objects, PLAYER_VEL * 3)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in  to_check:
        if to_check and obj == "slime":
            player.hit()

#--------Player------------

class Player(pygame.sprite.Sprite):
    COLOR =  (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("sprites", "knight", 32, 19, True)
    ANIMATION_DELAY = 6

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
    
    def jump(self):
        self.y_vel = -self.GRAVITY * 9
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    
    def move(self,dx,dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self,vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self,vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def loop(self,fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.fall_count = 0
        print(self.y_vel)
        self.y_vel *= -1
        print(self.y_vel)

    def hit():
        print("hit")

    def update_sprite(self):
        sprite_sheet = "knight_idle"
        
        if self.x_vel !=0:
            sprite_sheet = "knight_run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)


    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

#--------Object------------

class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width,height),pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image,(self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        block = get_block(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Finish(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        finish = get_finish(size)
        
        
        self.image.blit(finish,(0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Coin(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        coin = get_coin(size)
        self.image = coin
        self.mask = pygame.mask.from_surface(self.image)

class Slime(Object):
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "slime")
        self.slime = load_sprite_sheets("sprites", "slimes", 24, 15)
        self.image = self.slime["slime_purple"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_name = "slime_purple"
        self.animation_count = 0

    def loop(self):

        sprites = self.slime["slime_purple"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


#--------main------------

def main(window):
    global SCORE
    clock = pygame.time.Clock()

    player = Player(100,400,50,50)
    
    block_size = 96
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) 
             for i in range(-WIDTH // block_size, WIDTH * 3 // block_size)]
    
    wall_l = [Block(-(block_size * 3), i * block_size, block_size) 
            for i in range(0, HEIGHT // block_size)]
    
    wall_r = [Block(WIDTH * 2, i * block_size, block_size) 
            for i in range(0, HEIGHT // block_size)]

    coins = spawn_coins()

    enemies = [Slime(block_size * 3, HEIGHT - block_size - 60, 24, 15),
               Slime(block_size * 5, HEIGHT - block_size * 4 - 60, 24, 15),
               Slime(block_size * 11, HEIGHT - block_size * 2 - 60, 24, 15)]

    finish = Finish(1600, HEIGHT - block_size * 2, block_size)

    collide_objects = [*floor, *wall_l, *wall_r
                       , Block(0, HEIGHT - block_size * 2, block_size)
                       , Block(block_size * 3, HEIGHT - block_size * 4, block_size)
                       , Block(block_size * 4, HEIGHT - block_size * 4, block_size)
                       , Block(block_size * 5, HEIGHT - block_size * 4, block_size)
                       , Block(block_size * 8, HEIGHT - block_size * 5, block_size)
                       , Block(block_size * 9, HEIGHT - block_size * 5, block_size)
                       , Block(block_size * 9, HEIGHT - block_size * 2, block_size)
                       , Block(block_size * 10, HEIGHT - block_size * 2, block_size)
                       , Block(block_size * 11, HEIGHT - block_size * 2, block_size)
                       , Block(block_size * 12, HEIGHT - block_size * 4, block_size)]
   
    objects = [*collide_objects, *enemies, finish]

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        
        player.loop(FPS)
        for enemy in enemies:
            enemy.loop()
        
        handle_move(player, collide_objects)

        for coin in coins[:]:
            if pygame.sprite.collide_mask(player, coin):
                coins.remove(coin)
                SCORE += 1
        
        if check_enemy_collision(player, enemies):
            pygame.time.delay(300)
            window.fill((0, 0, 0))  
            show_message(window, "You Died", (255, 0, 0))

            SCORE = 0
            coins = spawn_coins()

            pygame.display.update()
            pygame.time.delay(1000)
            player = Player(100, 400, 50, 50)
            offset_x = 0
            continue

        if pygame.sprite.collide_mask(player, finish):
            pygame.time.delay(300)
            window.fill((0, 0, 0))  
            show_message(window, f"You Won \n Score: {SCORE}", (0, 255, 0))
            SCORE = 0
            coins = spawn_coins()

            pygame.display.update()
            pygame.time.delay(2000)
            player = Player(100, 400, 50, 50)
            offset_x = 0
            continue
        
        draw(window, player, objects, coins, offset_x)
        pygame.display.flip()

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
    