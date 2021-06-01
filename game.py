import pygame
import os

pygame.init()

_screen_width = 800
_screen_height = int(800 * 0.8)

screen = pygame.display.set_mode((_screen_width, _screen_height))
pygame.display.set_caption("Scrolling Shooter")

# Set Frame Rate
clock = pygame.time.Clock()
FPS = 60

# Load images
_bullet_img = pygame.image.load('Assets/img/icons/bullet.png').convert_alpha()

# Game Variables
_gravity = 0.75

# Setting Colors
_bg = (144, 201, 120)
_red = (255, 0, 0)

# Keyboard actions
moving_left = False
moving_right = False
shoot = False


class Soldier(pygame.sprite.Sprite):

    def __init__(self, char_type, x, y, scale, speed, ammo, *groups):
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
            num_of_frames = len(os.listdir(f"Assets/img/{self.char_type}/{char}"))
            for i in range(num_of_frames):
                img = pygame.image.load(f"Assets/img/{self.char_type}/{char}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)

            self.animation_list.append(temp_list)

            # Setting up the player sprite
            self.image = self.animation_list[self.action][self.frame_index]
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            self.speed = speed
            self.direction = 1
            self.in_air = True
            self.jump = False
            self.start_ammo = ammo
            self.ammo = ammo
            self.vel_y = 0
            self.shoot_cooldown = 0
            self.health = 100
            self.max_health = self.health
            self.flip = False

    def update(self):
        self.update_animation()
        self.check_alive()
        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, move_left, move_right):
        # reset movement variables
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
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # Update the player rect
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(player.rect.centerx + (0.6 * player.rect.size[0] * player.direction), player.rect.centery,
                            player.direction)
            bullet_group.add(bullet)
            self.ammo -= 1

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
        self.rect.x += (self.direction * self.speed)
        # Check if bullet reaches the end of the screen
        if self.rect.right < 0 or self.rect.left > _screen_width:
            self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 20
                self.kill()


# Bullet groups
bullet_group = pygame.sprite.Group()


def draw_bg():
    screen.fill(_bg)
    pygame.draw.line(screen, _red, (0, 300), (_screen_width, 300))


player = Soldier('player', 200, 200, 2, 5, 20)
enemy = Soldier('enemy', 400, 200, 2, 5, 20)

run = True
while run:
    clock.tick(FPS)
    draw_bg()
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

    player.update()
    enemy.update()
    player.draw()
    enemy.draw()

    # Update and draw groups
    bullet_group.update()
    bullet_group.draw(screen)

    # Update player moving animation
    if player.alive:
        if shoot:
            player.shoot()
        if player.in_air:
            player.update_action(2)  # 2:Jump
        elif moving_left or moving_right:
            player.update_action(1)  # 1:Run
        else:
            player.update_action(0)  # 0:Idle
        player.move(moving_left, moving_right)

    pygame.display.update()

pygame.quit()
