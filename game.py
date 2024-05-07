import pygame, sys, random
from pygame.locals import *

SCALE = 4
WINDOW_SIZE = (128 * SCALE, 128 * SCALE)
DISPLAY_SIZE = (128, 128)
GRAVITY = 0.5

# -- Classes
class Timer(object):
    def __init__(self, ticks, autostart, loop):
        self.ticks = ticks
        self.curr_tick = 0
        self.enabled = False
        self.loop = loop
        self.active = autostart

    def update(self):
        if self.active:
            self.curr_tick += 1
            if self.curr_tick >= self.ticks:
                self.enabled = True
                self.curr_tick = 0
                self.active = False
                if self.loop:
                    self.active = True
            else:
                self.enabled = False

class Coin(object):
    def __init__(self):
        self.rect = pygame.Rect((0, 0, 8, 8))
        self.action = 'spin'
        self.frame = 0
        self.animation_frames = {}
        self.animation_db = {}
        self.load_animations_db()
        self.generate_pos()
        #SFX
        self.pickup_sfx = pygame.mixer.Sound('assets/sfx/sounds/pickup.ogg')

    def render(self, display):
        self.frame += 1
        if self.frame >= len(self.animation_db[self.action]):
            self.frame = 0
        img_id = self.animation_db[self.action][self.frame]
        img = self.animation_frames[img_id]
        display.blit(img, self.rect)
        
    def load_animation(self, path, duration):
       animation_name = path.split('/')[-1]
       animation_frame_data = []
       n = 0
       for frame in duration:
           animation_frame_id = animation_name + '_' + str(n)
           img_location = path + '/' + animation_frame_id + '.png'
           animation_image = pygame.image.load(img_location).convert()
           animation_image.set_colorkey((255, 0, 255))
           self.animation_frames[animation_frame_id] = animation_image.copy()
           for i in range(frame):
               animation_frame_data.append(animation_frame_id)
           n += 1
       return animation_frame_data

    def load_animations_db(self):
        self.animation_db['spin'] = self.load_animation('assets/graphics/coin/spin', [6, 6, 6, 6])

    def generate_pos(self, play_sound = False):
        if play_sound:
            self.pickup_sfx.play()
        y_list = [4, 7, 10, 13]
        y_selected = y_list[random.randrange(len(y_list))]
        self.rect.y = 8 * y_selected

        if y_selected == 7 or y_selected == 13:
            if random.randrange(2) == 0:
                self.rect.x = 8 * random.randint(1, 4)
            else:
                self.rect.x = 8 * random.randint(11, 14)
        else:
            self.rect.x = 8 * random.randint(4, 11)

class BaseEnemy(object):
    def __init__(self, x, y, angry):
        self.type = 'Base'
        self.rect = pygame.Rect(x, y, 8, 8)
        self.life = 3 if not angry else 5
        self.dead = False
        self.flip = False
        self.action = 'walk' if not angry else 'angry_walk'
        self.frame = 0
        self.animation_frames = {}
        self.animation_db = {}
        self.load_animations_db()
        self.disabled_timer = Timer(5, False, False)
        self.dead_timer = Timer(8, False, False)
        self.angry = angry

        rnd = random.randint(-1, 1)
        if rnd == 0:
            rnd += (1 if random.randint(0, 1) == 0 else -1)
        self.velocity = [1 * rnd,0]

        self.hurt_sfx = [pygame.mixer.Sound('assets/sfx/sounds/hurt_1.ogg'), pygame.mixer.Sound('assets/sfx/sounds/hurt_2.ogg')]

    def render(self, display):
        self.frame += 1
        if self.frame >= len(self.animation_db[self.action]):
            self.frame = 0
        img_id = self.animation_db[self.action][self.frame]
        
        img = self.animation_frames[img_id]
        if self.disabled_timer.active:
            if self.disabled_timer.curr_tick % 2 == 0 and self.disabled_timer.curr_tick > 0:
                display.blit(pygame.transform.flip(img, self.flip, False), self.rect)
        else:
            display.blit(pygame.transform.flip(img, self.flip, False), self.rect)

    def update(self, tiles):
        if not 'dead' in self.action:
            self.flip = self.velocity[0] < 0
            self.velocity[1] += GRAVITY
            if self.velocity[1] > 3:
                self.velocity[1] = 3

            self.rect, collisions = self.move(self.rect, self.velocity, tiles)
            if collisions['top'] and self.velocity[1] < 0:
                self.velocity[1] = 0
            if collisions['bottom']:
                if self.velocity[0] != 0:
                    if not self.angry:
                        self.action, self.frame = self.change_action(self.action, self.frame, 'walk')
                    else:
                        self.action, self.frame = self.change_action(self.action, self.frame, 'angry_walk')

            if collisions['left'] or collisions['right']:
                self.velocity[0] = -self.velocity[0]
                        
            self.disabled_timer.update()
        self.dead_timer.update()

        if self.dead_timer.enabled:
            self.dead = True
        if self.dead_timer.active:
            if not self.angry:
                self.action = 'dead'
            else:
                self.action = 'angry_dead'
    
    def hurt(self):
        if not 'dead' in self.action:
            self.hurt_sfx[random.randrange(2)].play()
        self.life -= 1
        if self.life <= 0:
            self.dead_timer.active = True
        else:
            self.disabled_timer.active = True

    def load_animation(self, path, duration):
        animation_name = path.split('/')[-1]
        animation_frame_data = []
        n = 0
        for frame in duration:
            animation_frame_id = animation_name + '_' + str(n)
            img_location = path + '/' + animation_frame_id + '.png'
            animation_image = pygame.image.load(img_location).convert()
            animation_image.set_colorkey((255, 0, 255))
            self.animation_frames[animation_frame_id] = animation_image.copy()
            for i in range(frame):
                animation_frame_data.append(animation_frame_id)
            n += 1
        return animation_frame_data

    def load_animations_db(self):
        pass
    
    def change_action(self, curr_action, frame, new_action):
        if curr_action != new_action:
            curr_action = new_action
            frame = 0
        return curr_action, frame

    def check_collision(self, rect, tiles):
        hit_list = []
        for tile in tiles:
            if rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list
    
    def move(self, rect, velocity, tiles):
        collision_types = {"top": False, "bottom": False, "right": False, "left": False}
        rect.x += velocity[0]
        hit_list = self.check_collision(rect, tiles)
        for tile in hit_list:
            if velocity[0] > 0:
                rect.right = tile.left
                collision_types['right'] = True
            elif velocity[0] < 0:
                rect.left = tile.right
                collision_types['left'] = True
        rect.y += velocity[1]
        hit_list = self.check_collision(rect, tiles)
        for tile in hit_list:
            if velocity[1] > 0:
                self.rect.bottom = tile.top
                collision_types['bottom'] = True
            elif velocity[1] < 0:
                rect.top = tile.bottom
                collision_types['top'] = True
        return rect, collision_types

class Zombie(BaseEnemy):
    def __init__(self, x, y, angry):
        super().__init__(x, y, angry)
        self.type = 'zombie'
        
    def load_animations_db(self):
        self.animation_db['walk'] = self.load_animation('assets/graphics/enemies/zombie/walk', [6, 6, 6])
        self.animation_db['dead'] = self.load_animation('assets/graphics/enemies/zombie/dead', [1])
        self.animation_db['angry_walk'] = self.load_animation('assets/graphics/enemies/zombie/angry_walk', [6, 6, 6])
        self.animation_db['angry_dead'] = self.load_animation('assets/graphics/enemies/zombie/angry_dead', [1])

class Cricket(BaseEnemy):
    def __init__(self, x, y, angry):
        super().__init__(x, y, angry)
        self.type = 'cricket'
        
    def load_animations_db(self):
        self.animation_db['walk'] = self.load_animation('assets/graphics/enemies/cricket/walk', [6, 6, 6])
        self.animation_db['dead'] = self.load_animation('assets/graphics/enemies/cricket/dead', [1])
        self.animation_db['angry_walk'] = self.load_animation('assets/graphics/enemies/cricket/angry_walk', [6, 6, 6])
        self.animation_db['angry_dead'] = self.load_animation('assets/graphics/enemies/cricket/angry_dead', [1])

class Ghost(BaseEnemy):
    def __init__(self, x, y, angry):
        super().__init__(x, y, angry)
        self.type = 'ghost'
        
    def load_animations_db(self):
        self.animation_db['walk'] = self.load_animation('assets/graphics/enemies/ghost/walk', [6, 6, 6])
        self.animation_db['dead'] = self.load_animation('assets/graphics/enemies/ghost/dead', [1])
        self.animation_db['angry_walk'] = self.load_animation('assets/graphics/enemies/ghost/angry_walk', [6, 6, 6])
        self.animation_db['angry_dead'] = self.load_animation('assets/graphics/enemies/ghost/angry_dead', [1])

class MudDemon(BaseEnemy):
    def __init__(self, x, y, angry):
        super().__init__(x, y, angry)
        self.type = 'mud_demon'
        
    def load_animations_db(self):
        self.animation_db['walk'] = self.load_animation('assets/graphics/enemies/mud_demon/walk', [6, 6, 6])
        self.animation_db['dead'] = self.load_animation('assets/graphics/enemies/mud_demon/dead', [1])
        self.animation_db['angry_walk'] = self.load_animation('assets/graphics/enemies/mud_demon/angry_walk', [6, 6, 6])
        self.animation_db['angry_dead'] = self.load_animation('assets/graphics/enemies/mud_demon/angry_dead', [1])

class SandDemon(BaseEnemy):
    def __init__(self, x, y, angry):
        super().__init__(x, y, angry)
        self.type = 'sand_demon'
        
    def load_animations_db(self):
        self.animation_db['walk'] = self.load_animation('assets/graphics/enemies/sand_demon/walk', [6, 6, 6])
        self.animation_db['dead'] = self.load_animation('assets/graphics/enemies/sand_demon/dead', [1])
        self.animation_db['angry_walk'] = self.load_animation('assets/graphics/enemies/sand_demon/angry_walk', [6, 6, 6])
        self.animation_db['angry_dead'] = self.load_animation('assets/graphics/enemies/sand_demon/angry_dead', [1])

class ScissorsDemon(BaseEnemy):
    def __init__(self, x, y, angry):
        super().__init__(x, y, angry)
        self.type = 'scissors_demon'
        
    def load_animations_db(self):
        self.animation_db['walk'] = self.load_animation('assets/graphics/enemies/scissors_demon/walk', [6, 6, 6])
        self.animation_db['dead'] = self.load_animation('assets/graphics/enemies/scissors_demon/dead', [1])
        self.animation_db['angry_walk'] = self.load_animation('assets/graphics/enemies/scissors_demon/angry_walk', [6, 6, 6])
        self.animation_db['angry_dead'] = self.load_animation('assets/graphics/enemies/scissors_demon/angry_dead', [1])

class Slug(BaseEnemy):
    def __init__(self, x, y, angry):
        super().__init__(x, y, angry)
        self.type = 'slug'
        
    def load_animations_db(self):
        self.animation_db['walk'] = self.load_animation('assets/graphics/enemies/slug/walk', [6, 6, 6])
        self.animation_db['dead'] = self.load_animation('assets/graphics/enemies/slug/dead', [1])
        self.animation_db['angry_walk'] = self.load_animation('assets/graphics/enemies/slug/angry_walk', [6, 6, 6])
        self.animation_db['angry_dead'] = self.load_animation('assets/graphics/enemies/slug/angry_dead', [1])

class Vampire(BaseEnemy):
    def __init__(self, x, y, angry):
        super().__init__(x, y, angry)
        self.type = 'vampire'
        
    def load_animations_db(self):
        self.animation_db['walk'] = self.load_animation('assets/graphics/enemies/vampire/walk', [6, 6, 6])
        self.animation_db['dead'] = self.load_animation('assets/graphics/enemies/vampire/dead', [1])
        self.animation_db['angry_walk'] = self.load_animation('assets/graphics/enemies/vampire/angry_walk', [6, 6, 6])
        self.animation_db['angry_dead'] = self.load_animation('assets/graphics/enemies/vampire/angry_dead', [1])

class EnemiesManager(object):
    def __init__(self):
        self.enemies = []
        self.spawn_timer = Timer(random.randint(60,80), True, True)

    def render(self, display):
        for enemy in self.enemies:
            if not enemy.dead:
                enemy.render(display)

    def update(self, tiles):
        self.spawn_timer.update()
        if self.spawn_timer.enabled:
            self.new_enemy()
            self.spawn_timer.ticks = random.randint(60, 120)

        for enemy in self.enemies:
            if enemy.rect.top >= 128:
                match enemy.type:
                    case 'zombie':
                        self.enemies.append(Zombie(8*8,-8,True))
                    case 'cricket':
                        self.enemies.append(Cricket(8*8,-8,True))
                    case 'ghost':
                        self.enemies.append(Ghost(8*8,-8,True))
                    case 'mud_demon':
                        self.enemies.append(MudDemon(8*8,-8,True))
                    case 'sand_demon':
                        self.enemies.append(SandDemon(8*8,-8,True))
                    case 'scissors_demon':
                        self.enemies.append(ScissorsDemon(8*8,-8,True))
                    case 'slug':
                        self.enemies.append(Slug(8*8,-8,True))
                    case 'vampire':
                        self.enemies.append(Vampire(8*8,-8,True))
                self.enemies.remove(enemy)
            else:
                if not enemy.dead: 
                    enemy.update(tiles)
                else:
                    self.enemies.remove(enemy)

    def new_enemy(self):
        match random.randint(0,7):
            case 0:
                self.enemies.append(Zombie(8*8,-8, False))
            case 1:
                self.enemies.append(Cricket(8*8,-8, False))
            case 2:
                self.enemies.append(Ghost(8*8,-8, False))
            case 3:
                self.enemies.append(MudDemon(8*8,-8, False))
            case 4:
                self.enemies.append(SandDemon(8*8,-8, False))
            case 5:
                self.enemies.append(ScissorsDemon(8*8,-8, False))
            case 6:
                self.enemies.append(Slug(8*8,-8, False))
            case 7:
                self.enemies.append(Vampire(8*8,-8, False))

class Shuriken(object):
    def __init__(self, x, y, direction):
        self.img = pygame.image.load('assets/graphics/weapons/shuriken.png')
        self.img.set_colorkey((255, 0, 0))
        self.rect = pygame.Rect(x, y, self.img.get_width(), self.img.get_height())
        self.vx = 5 * (-1 if direction else 1)
        self.dead = False
        #SFX
        self.crash_sfx = pygame.mixer.Sound('assets/sfx/sounds/crash.ogg')

    def update(self, tiles, enemies):
        self.rect.centerx += self.vx

        for tile in tiles:
            if self.rect.colliderect(tile):
                self.crash_sfx.play()
                self.dead = True

        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if not enemy.disabled_timer.active:
                  enemy.hurt()
                self.dead = True
        
    def render(self, display):
        display.blit(self.img, (self.rect.x, self.rect.y))

class ProjectilesManager(object):
    def __init__(self):
        self.projectiles = []

    def update(self, tiles, enemies):
        for projectile in self.projectiles:
            if not projectile.dead:
                projectile.update(tiles, enemies)
            else:
                self.projectiles.remove(projectile)

    def render(self, display):
        for projectile in self.projectiles:
            if not projectile.dead:
                projectile.render(display)
        
class Map(object):
    def __init__(self):
        self.tile_size = 8
        self.game_map = []
        self.tile_rects = []
        self.load_map('level')
        self.calculate_rects()
        self.img = pygame.image.load('assets/graphics/tiles/tile_1.png')
       
    def load_map(self, path):
        f = open(path + '.dat', 'r')
        data = f.read()
        f.close()
        data = data.split('\n')
        for row in data:
            self.game_map.append(list(row))

    def render(self, display):
        y = 0
        for row in self.game_map:
            x = 0
            for tile in row:
                if tile == '1':
                    display.blit(self.img, (x * self.tile_size, y * self.tile_size))
                x += 1
            y += 1
    
    def calculate_rects(self):
        y = 0
        for row in self.game_map:
            x = 0
            for tile in row:
                if tile != '0':
                    self.tile_rects.append(pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size))
                x += 1
            y += 1

class Player(object):
    def __init__(self):
        self.hspeed = 1
        self.jspeed = 6
        self.move_right = False
        self.move_left = False
        self.rect = pygame.Rect(DISPLAY_SIZE[0]//2, 0, 8, 8)
        self.rect.bottom = 8 * 12
        self.velocity = [0, 0]
        self.airtime = 0
        self.flip = False
        self.action = 'idle'
        self.frame = 0
        self.animation_frames = {}
        self.animation_db = {}
        self.load_animations_db()
        self.move_now = 0
        #SFX
        self.jump_sfx = pygame.mixer.Sound('assets/sfx/sounds/jump.ogg')
        self.throw_sfx = pygame.mixer.Sound('assets/sfx/sounds/throw.ogg')
        
    def update(self, tiles, enemies, coin):
        if self.rect.colliderect(coin.rect):
            coin.generate_pos(True)
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                pass
                #pygame.quit()
                #sys.exit()
                ##########
        if self.rect.top <= 0:
            self.rect.top = 0
        
        self.velocity[0] = 0

        if self.move_left:
            self.velocity[0] = -self.hspeed
            self.flip = True
        if self.move_right:
            self.velocity[0] = self.hspeed
            self.flip = False
        
        self.velocity[1] += GRAVITY
        if self.velocity[1] > 3:
            self.velocity[1] = 3

        self.rect, collisions = self.move(self.rect, self.velocity, tiles)

        if collisions['bottom']:
            self.airtime = 0
        else:
            self.airtime += 1

        if collisions['top'] and self.velocity[1] < 0:
            self.velocity[1] = 0


        if not collisions['bottom']:
            if self.velocity[1] > 0:
                self.action, self.frame = self.change_action(self.action, self.frame, 'fall')
            elif self.velocity[1] < 0:
                self.action, self.frame = self.change_action(self.action, self.frame, 'jump')
        else:
            if self.velocity[0] != 0:
                self.action, self.frame = self.change_action(self.action, self.frame, 'run')
            else:
                self.action, self.frame = self.change_action(self.action, self.frame, 'idle')
        
    def render(self, display):
        self.frame += 1
        if self.frame >= len(self.animation_db[self.action]):
            self.frame = 0
        img_id = self.animation_db[self.action][self.frame]
        img = self.animation_frames[img_id]
        display.blit(pygame.transform.flip(img, self.flip, False), self.rect)

    def shoot(self, projectiles):
        self.throw_sfx.play()
        projectiles.append(Shuriken(self.rect.centerx, self.rect.centery, self.flip))
        
    def load_animation(self, path, duration):
        animation_name = path.split('/')[-1]
        animation_frame_data = []
        n = 0
        for frame in duration:
            animation_frame_id = animation_name + '_' + str(n)
            img_location = path + '/' + animation_frame_id + '.png'
            animation_image = pygame.image.load(img_location).convert()
            animation_image.set_colorkey((255, 255, 255))
            self.animation_frames[animation_frame_id] = animation_image.copy()
            for i in range(frame):
                animation_frame_data.append(animation_frame_id)
            n += 1
        return animation_frame_data

    def load_animations_db(self):
        self.animation_db['idle'] = self.load_animation('assets/graphics/player/animations/idle', [30, 30])
        self.animation_db['run'] = self.load_animation('assets/graphics/player/animations/run', [8, 8, 8, 8])
        self.animation_db['jump'] = self.load_animation('assets/graphics/player/animations/jump', [1])
        self.animation_db['fall'] = self.load_animation('assets/graphics/player/animations/fall', [1])
    
    def change_action(self, curr_action, frame, new_action):
        if curr_action != new_action:
            curr_action = new_action
            frame = 0
        return curr_action, frame
    
    def check_collision(self, rect, tiles):
        hit_list = []
        for tile in tiles:
            if rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list
    
    def move(self, rect, velocity, tiles):
        collision_types = {"top": False, "bottom": False, "right": False, "left": False}
        rect.x += velocity[0]
        hit_list = self.check_collision(rect, tiles)
        for tile in hit_list:
            if velocity[0] > 0:
                rect.right = tile.left
                collision_types['right'] = True
            elif velocity[0] < 0:
                rect.left = tile.right
                collision_types['left'] = True
        rect.y += velocity[1]
        hit_list = self.check_collision(rect, tiles)
        for tile in hit_list:
            if velocity[1] > 0:
                self.rect.bottom = tile.top
                collision_types['bottom'] = True
            elif velocity[1] < 0:
                rect.top = tile.bottom
                collision_types['top'] = True
        return rect, collision_types
    
# -- Main
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface(DISPLAY_SIZE)
pygame.display.set_caption("Frog Training")

clock = pygame.time.Clock()

projectiles_manager = ProjectilesManager()
enemies_manager = EnemiesManager()
player = Player()
game_map = Map()
now = 0
coin = Coin()

while True:
    display.fill((24, 28, 41))

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_a:
                player.move_left = True
            if event.key == K_d:
                player.move_right = True
            if event.key == K_k:
                if player.airtime < 5:
                    player.velocity[1] = -player.jspeed
                    player.jump_sfx.play()
            if event.key == K_j:
                player.shoot(projectiles_manager.projectiles)
        if event.type == KEYUP:
            if event.key == K_a:
                player.move_left = False
            if event.key == K_d:
                player.move_right = False
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    # -- objs
    game_map.render(display)
    player.render(display)
    projectiles_manager.render(display)
    enemies_manager.render(display)
    coin.render(display)
    player.update(game_map.tile_rects, enemies_manager.enemies, coin)
    projectiles_manager.update(game_map.tile_rects, enemies_manager.enemies)
    now += 1
    if now > 1:
        now = 0
        enemies_manager.update(game_map.tile_rects)
    # -- objs
    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    
    pygame.display.update()
    clock.tick(60)
