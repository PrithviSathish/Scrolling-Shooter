import pygame
import random
import os
import csv

# from Player import Soldier

pygame.init()

_screen_width = 800
_screen_height = int(800 * 0.8)

screen = pygame.display.set_mode((_screen_width, _screen_height))
pygame.display.set_caption("Scrolling Shooter")

# Set Frame Rate
clock = pygame.time.Clock()
FPS = 60

# Game Variables
level = 1
_gravity = 0.75
_scroll_tresh = 200
_rows = 16
_cols = 150
screen_scroll = 0
bg_scroll = 0
_tile_size = _screen_height // _rows
_tile_types = 21

# Load images
_pine1_img = pygame.image.load('Assets/img/background/pine1.png').convert_alpha()
_pine2_img = pygame.image.load('Assets/img/background/pine2.png').convert_alpha()
_mountain_img = pygame.image.load('Assets/img/background/mountain.png').convert_alpha()
_sky_img = pygame.image.load('Assets/img/background/sky_cloud.png').convert_alpha()

# Load tiles
img_list = []
for x in range(_tile_types):
    img = pygame.transform.scale(pygame.image.load(f'Assets/img/tile/{x}.png'), (_tile_size, _tile_size))
    img_list.append(img)

_bullet_img = pygame.image.load('Assets/img/icons/bullet.png').convert_alpha()
_grenade_img = pygame.image.load('Assets/img/icons/grenade.png').convert_alpha()
_health_box_img = pygame.image.load('Assets/img/icons/health_box.png').convert_alpha()
_ammo_box_img = pygame.image.load('Assets/img/icons/ammo_box.png').convert_alpha()
_grenade_box_img = pygame.image.load('Assets/img/icons/grenade_box.png').convert_alpha()

item_boxes = {
    'Health': _health_box_img,
    'Ammo': _ammo_box_img,
    'Grenade': _grenade_box_img
}

# Setting Colors
_bg = (144, 201, 120)
_red = (255, 0, 0)
_green = (0, 255, 0)
_white = (255, 255, 255)
_black = (0, 0, 0)

# Font
font = pygame.font.SysFont('Futura', 30)

# Keyboard actions
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


class Soldier(pygame.sprite.Sprite):

    def __init__(self, char_type, x, y, scale, speed, ammo, grenades=0, *groups):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        # Character animation
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # Load all the images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for char in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir("Assets/img/" + self.char_type + "/" + char))
            for i in range(num_of_frames):
                img = pygame.image.load(
                    "Assets/img/" + self.char_type + "/" + char + "/" + str(i) + ".png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)

            self.animation_list.append(temp_list)

            # Setting up the player sprite
            self.image = self.animation_list[self.action][self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.speed = speed
            self.direction = 1
            self.in_air = True
            self.jump = False
            self.start_ammo = ammo
            self.ammo = ammo
            self.vel_y = 0
            self.shoot_cooldown = 0
            self.grenades = grenades
            self.health = 100
            self.max_health = self.health
            self.flip = False
            # Ai specific variables
            self.move_counter = 0
            self.idling = False
            self.idling_counter = 0
            self.vision = pygame.Rect(0, 0, 150, 20)

    def update(self):
        self.update_animation()
        self.check_alive()
        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, move_left, move_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # Assign them to the speed
        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        elif move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Apply gravity
        self.vel_y += _gravity
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # Check ground collision
        for tile in world.obstacle_list:
            # X collision
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0

                # If AI has hit the wall, turn around
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0

            # Y collision
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if player is jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top

                # Else check if player is falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Check if reached screen edge
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > _screen_width:
                dx = 0

        # Update the player rect
        self.rect.x += dx
        self.rect.y += dy

        # Update scroll based on player position
        if self.char_type == "player":
            if (self.rect.right > _screen_width - _scroll_tresh and bg_scroll < (world.level_length * _tile_size) - _screen_width)\
                 or (self.rect.left < _scroll_tresh and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 7:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50

            elif self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()

            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > _tile_size:
                        self.direction *= -1
                        self.move_counter *= -1

                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # Enemy scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # Updating animation
        _animation_cooldown = 100
        # Update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # Checks if enough time has passed
        if pygame.time.get_ticks() - self.update_time > _animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # Check if the new animation is different from the previous one
        if new_action != self.action:
            self.action = new_action
            # Update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World:
    def __init__(self):
        self.obstacle_list = []
        self.level_length = 0

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * _tile_size
                    img_rect.y = y * _tile_size
                    tile_data = (img, img_rect)

                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)

                    if tile >= 9 and tile <= 10:
                        # Water
                        water = Water(img, x * _tile_size, y * _tile_size)
                        water_group.add(water)

                    elif tile >= 11 and tile <= 14:
                        # Decorations
                        decoration = Decoration(img, x * _tile_size, y * _tile_size)
                        decoration_group.add(decoration)

                    elif tile == 15:
                        # Player
                        player = Soldier('player', x * _tile_size, y * _tile_size, 1.6, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)

                    elif tile == 16:
                        # Enemy
                        enemy = Soldier('enemy', x * _tile_size, y * _tile_size, 1.6, 3, 20)
                        enemy_group.add(enemy)

                    elif tile == 17:
                        # Ammo
                        item_box = ItemBox('Ammo', x * _tile_size, y * _tile_size)
                        item_box_group.add(item_box)

                    elif tile == 18:
                        # Grenade
                        item_box = ItemBox('Grenade', x * _tile_size, y * _tile_size)
                        item_box_group.add(item_box)

                    elif tile == 19:
                        # Health
                        item_box = ItemBox('Health', x * _tile_size, y * _tile_size)
                        item_box_group.add(item_box)

                    elif tile == 20:
                        # Exit
                        exit = Exit(img, x * _tile_size, y * _tile_size)
                        exit_group.add(exit)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + _tile_size // 2, y + (_tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + _tile_size // 2, y + (_tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + _tile_size // 2, y + (_tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + _tile_size // 2, y + (_tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        # Check if the player picks up the box
        if pygame.sprite.collide_rect(self, player):
            # Check what box
            if self.item_type == "Health":
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammo":
                player.ammo += 15
            elif self.item_type == "Grenade":
                player.grenades += 2

            # Delete the box
            self.kill()


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # Update with new health
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, _black, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, _red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, _green, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = _bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # Move the bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # Check if bullet reaches the end of the screen
        if self.rect.right < 0 or self.rect.left > _screen_width:
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 20
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 10
        self.image = _grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += _gravity
        dx = self.direction * self.speed
        dy = self.vel_y

        for tile in world.obstacle_list:
            # Check if grenade hits the walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed

            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # Check if thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top

                # Else check if player is falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # Update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # Explosion timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 1.5)
            explosion_group.add(explosion)

            # Explosion damage
            if abs(self.rect.centerx - player.rect.centerx) < _tile_size * 2 and \
                    abs(self.rect.centery - player.rect.centery) < _tile_size * 2:
                player.health -= 25

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < _tile_size * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < _tile_size * 2:
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for n in range(1, 6):
            img = pygame.image.load("Assets/img/explosion/exp" + str(n) + ".png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        _explosion_speed = 4
        self.counter += 1

        if self.counter >= _explosion_speed:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(_bg)
    width = _sky_img.get_width()
    for x in range(5):
        screen.blit(_sky_img, ((x * width) - bg_scroll * 0.4, 0))
        screen.blit(_mountain_img, ((x * width) - bg_scroll * 0.5, _screen_height - _mountain_img.get_height() - 300))
        screen.blit(_pine1_img, ((x * width) - bg_scroll * 0.6, _screen_height - _pine1_img.get_height() - 150))
        screen.blit(_pine2_img, ((x * width) - bg_scroll * 0.7, _screen_height - _pine2_img.get_height()))
    # pygame.draw.line(screen, _red, (0, 300), (_screen_width, 300))


# Bullet groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Create empty tile list
world_data = []
for row in range(_rows):
    r = [-1] * _cols
    world_data.append(r)

# Load in level data and create the world
with open("Assets/CSV/level" + str(level) + "_data.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

# print(world_data)

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    clock.tick(FPS)
    draw_bg()
    world.draw()

    # Show player health
    health_bar.draw(player.health)

    # Show the number of bullets
    draw_text('AMMO: ', font, _white, 10, 35)
    for x in range(player.ammo):
        screen.blit(_bullet_img, (90 + (x * 10), 40))

    # Show the number of grenades
    draw_text('GRENADES: ', font, _white, 10, 60)
    for y in range(player.grenades):
        screen.blit(_grenade_img, (135 + (y * 15), 63))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Keyboard pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True

            if event.key == pygame.K_d:
                moving_right = True

            if event.key == pygame.K_w:
                player.jump = True

            if event.key == pygame.K_SPACE:
                shoot = True

            if event.key == pygame.K_g:
                grenade = True

            if event.key == pygame.K_ESCAPE:
                run = False

        # Keyboard released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False

            if event.key == pygame.K_d:
                moving_right = False

            if event.key == pygame.K_SPACE:
                shoot = False

            if event.key == pygame.K_g:
                grenade = False
                grenade_thrown = False

    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    # Update and draw groups
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()
    decoration_group.update()
    water_group.update()
    exit_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_box_group.draw(screen)
    decoration_group.draw(screen)
    water_group.draw(screen)
    exit_group.draw(screen)

    # Update player moving animation
    if player.alive:
        if shoot:
            player.shoot()
        elif grenade and not grenade_thrown and player.grenades > 0:
            grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top,
                              player.direction)
            grenade_group.add(grenade)
            player.grenades -= 1
            grenade_thrown = True
        if player.in_air:
            player.update_action(2)  # 2:Jump
        elif moving_left or moving_right:
            player.update_action(1)  # 1:Run
        else:
            player.update_action(0)  # 0:Idle
        screen_scroll = player.move(moving_left, moving_right)

        bg_scroll -= screen_scroll

    pygame.display.update()

pygame.quit()
