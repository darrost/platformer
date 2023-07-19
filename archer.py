import pygame
import os
import random
import csv

pygame.init()

clock = pygame.time.Clock()
screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Project")

gravity = 0.5
scroll_threshold = screen_width * 0.40
rows = 16
cols = 150
tile_size = screen_height // rows
tile_type = 15
screen_scroll = 0
background_scroll = 0

moving_left = False
moving_right = False
fire_projectile = False

hills1_img = pygame.image.load("img/Background/My project (1).png").convert_alpha()


img_list = []
for x in range(tile_type):
    img = pygame.image.load(f"img/Tile/{x}.png")
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)


player_projectile_img = pygame.image.load("assets/Player/projectiles/projectile.png").convert_alpha()
enemy_projectile_img = pygame.image.load("assets/Player/projectiles/enemy_projectile.png").convert_alpha()
enemy_projectile_img = pygame.transform.scale(enemy_projectile_img, (20, 40))



background = (101, 101, 101)
black = (1, 1, 1)
red = (255, 0, 0)
green = (0, 255, 0)

font = pygame.font.SysFont("Futura", 30)

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y ))

def draw_background():
    screen.fill(background)
    screen.blit(hills1_img, (0, 0))



def reset():
    enemy_group.empty()
    water_group.empty()
    decoration_group.empty()
    finish_group.empty()

    data = []
    for row in range(rows):
        r = [-1] * cols
        data.append(r)
    return data

class Unit(pygame.sprite.Sprite):
    def __init__(self, unit_type, x, y, scale, move_speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.unit_type = unit_type
        self.direction = 1
        self.velocity_y = 0
        self.idle_counter = 0
        self.movement_counter = 0
        self.hp = 100
        self.max_hp = self.hp
        self.fire_projectile_cd = 0
        self.jump = False
        self.is_in_air = True
        self.flip = False
        self.idle = False
        self.move_speed = move_speed
        self.los = pygame.Rect(0, 0, 500, 20)
        self.animation = []
        self.frame_i = 0
        self.state = 0
        self.update_time = pygame.time.get_ticks()

        animation_types = ["idle", "jump", "run", "death"]
        for animation_type in animation_types:
            temp_list = []
            frame_num = len(os.listdir(f"assets/{self.unit_type}/{animation_type}"))
            for i in range(frame_num):
                img = pygame.image.load(f"assets/{self.unit_type}/{animation_type}/My project ({i}).png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()) / scale, int(img.get_height()) / scale))
                temp_list.append(img)
            self.animation.append(temp_list)

        self.image = self.animation[self.state][self.frame_i]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        self.update_animation()
        self.status()
        if self.fire_projectile_cd > 0:
            self.fire_projectile_cd -= 1


    def movement(self, moving_left, moving_right):
        screen_scroll = 0
        x_cord = 0
        y_cord = 0

        if moving_left:
            x_cord = -self.move_speed
            self.flip = True
            self.direction = -1
        if moving_right:
            x_cord = self.move_speed
            self.flip = False
            self.direction = 1

        if self.jump == True and self.is_in_air == False:
            self.velocity_y = -15
            self.jump = False
            self.is_in_air = True

        self.velocity_y += gravity
        if self.velocity_y > 15:
            self.velocity_y = 15
        y_cord += self.velocity_y
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + x_cord, self.rect.y, self.width, self.height):
                x_cord = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + y_cord, self.width, self.height):
                if self.velocity_y < 0:
                    self.velocity_y = 0
                    y_cord = tile[1].bottom - self.rect.top
                elif self.velocity_y >= 0:
                    self.velocity_y = 0
                    self.is_in_air = False
                    y_cord = tile[1].top - self.rect.bottom

        if self.unit_type == "Player":
            if self.rect.bottom > screen_height:
                self.hp -= self.max_hp

        if self.unit_type == "Player":
            if self.rect.left + x_cord < 0 or self.rect.right + x_cord > screen_width:
                x_cord = 0

        self.rect.x += x_cord
        self.rect.y += y_cord

        if self.unit_type == "Player":
            if (self.rect.right > screen_width - scroll_threshold and background_scroll < (world.level_length * tile_size) - screen_width)\
                    or (self.rect.left < scroll_threshold and background_scroll > abs(x_cord)):
                self.rect.x -= x_cord
                screen_scroll = -x_cord
        return screen_scroll





    def update_animation(self):
        animation_cooldown = 120
        self.image = self.animation[self.state][self.frame_i]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_i += 1
        if self.frame_i >= len(self.animation[self.state]):
            if self.state == 3:
                self.frame_i = len(self.animation[self.state]) - 1
            else:
                self.frame_i = 0

    def update_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.frame_i = 0
            self.update_time = pygame.time.get_ticks()

    def fire_projectile(self):
        if self.fire_projectile_cd == 0:
            self.fire_projectile_cd = 50
            if self.unit_type == 'Player':
                projectile = Projectile(self.rect.centerx + (0.9 * self.rect.size[0] * self.direction),
                                        self.rect.centery, self.direction, True)
            else:
                projectile = Projectile(self.rect.centerx + (0.65 * self.rect.size[0] * self.direction),
                                        self.rect.centery, self.direction, False)
            projectile_group.add(projectile)

    def status(self):
        if self.hp <= 0:
            self.hp = 0
            self.move_speed = 0
            self.alive = False
            self.update_state(3)

    def ai(self):
        if self.alive and player.alive:
            if self.idle == False and random.randint(1, 200) == 69:
                self.idle = True
                self.update_state(0)
                self.idle_counter = 60
            if self.los.colliderect(player.rect):
                self.update_state(0)
                self.fire_projectile()
            else:
                if self.idle == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.movement(ai_moving_left, ai_moving_right)
                    self.update_state(2)
                    self.movement_counter += 1
                    self.los.center = (self.rect.centerx + 250 * self.direction, self.rect.centery)
                    if self.movement_counter > tile_size:
                        self.direction *= -1
                        self.movement_counter *= -1
                else:
                    self.idle_counter -= 1
                    if self.idle_counter <= 0:
                        self.idle = False


        self.rect.x += screen_scroll







    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Health():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp

        total_sum = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * total_sum, 20))

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    tile_data = (img, img_rect)
                    if 0 <= tile <= 1:
                        self.obstacle_list.append(tile_data)
                    elif 2 <= tile <= 3:
                        water = Water(img, x * tile_size, y * tile_size)
                        water_group.add(water)
                    elif 4 <= tile <= 10:
                        decoration = Decor(img, x*tile_size, y*tile_size)
                        decoration_group.add(decoration)
                    elif tile == 11:
                        player = Unit('Player', x*tile_size, y*tile_size, 2.5, 8)
                        hp_bar = Health(10, 10, player.hp, player.hp)
                    elif tile == 12:
                        enemy = Unit("Enemy", x*tile_size, y*tile_size, 2, 3)
                        enemy_group.add(enemy)
                    elif tile == 13:
                        finish = Finish(img, x * tile_size, y * tile_size)
                        finish_group.add(finish)

        return player, hp_bar



    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decor(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Finish(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, is_player):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        if is_player:
            self.image = player_projectile_img
        else:
            self.image = enemy_projectile_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, projectile_group, False):
            if player.alive:
                player.hp -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, projectile_group, False):
                if enemy.alive:
                    enemy.hp -= 40
                    self.kill()



enemy_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
finish_group = pygame.sprite.Group()





world_data = []
for row in range(rows):
    r = [-1] * cols
    world_data.append(r)
with open(f"level1.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, hp_bar = world.process_data(world_data)


run = True
while run:

    clock.tick(60)
    draw_background()
    world.draw()
    draw_text(f"HP: {player.hp}", font, black, 10, 35)
    hp_bar.draw(player.hp)

    player.update()
    player.draw()
    for enemy in enemy_group:
        enemy.ai()
        enemy.draw()
        enemy.update()

    projectile_group.update()
    projectile_group.draw(screen)

    decoration_group.update()
    decoration_group.draw(screen)

    water_group.update()
    water_group.draw(screen)

    finish_group.update()
    finish_group.draw(screen)

    if player.alive:
        if fire_projectile:
            player.fire_projectile()
        if player.is_in_air:
            player.update_state(1)
        elif moving_left or moving_right:
            player.update_state(2)
        else:
            player.update_state(0)
        screen_scroll = player.movement(moving_left, moving_right)
        background_scroll -= screen_scroll
    else:
        screen_scroll = 0
        background_scroll = 0
        world_data = reset()
        with open(f"level1.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)
        world = World()
        player, hp_bar = world.process_data(world_data)



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_k:
                fire_projectile = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True

            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_k:
                fire_projectile = False

    pygame.display.update()

pygame.quit()
