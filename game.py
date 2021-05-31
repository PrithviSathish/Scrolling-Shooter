import pygame

pygame.init()

screen_width = 800
screen_height = int(800 * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Scrolling Shooter")

# Set Frame Rate
clock = pygame.time.Clock()
FPS = 60

# Setting Colors
BG = (144, 201, 120)

# Keyboard actions
moving_left = False
moving_right = False


class Soldier(pygame.sprite.Sprite):

    def __init__(self, char_type, x, y, scale, speed, *groups):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type

        # Character animation
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        temp_list = []
        for i in range(5):
            img = pygame.image.load(f"Assets/img/{self.char_type}/Idle/{i}.png")
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)

        self.animation_list.append(temp_list)
        temp_list = []

        for i in range(6):
            img = pygame.image.load(f"Assets/img/{self.char_type}/Run/{i}.png")
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)

        self.animation_list.append(temp_list)

        # Setting up the player sprite
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.direction = 1
        self.flip = False

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

        # Update the player rect
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        # Updating animation
        animation_cooldown = 100
        # Update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # Checks if enough time has passed
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # Check if the new animation is different from the previous one
        if new_action != self.action:
            self.action = new_action
            # Update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


def draw_bg():
    screen.fill(BG)


player = Soldier('player', 200, 200, 2, 5)

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

            if event.key == pygame.K_ESCAPE:
                run = False

        # Keyboard released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False

            if event.key == pygame.K_d:
                moving_right = False

    player.update_animation()
    player.draw()

    # Update player moving animation
    if moving_left or moving_right:
        player.update_action(1)  # 1:Run
    else:
        player.update_action(0)  # 0:Idle
    player.move(moving_left, moving_right)

    pygame.display.update()

pygame.quit()
