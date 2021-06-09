import pygame

pygame.init()

_screen_width = 800
_screen_height = int(800 * 0.8)

screen = pygame.display.set_mode((_screen_width, _screen_height))
pygame.display.set_caption("Scrolling Shooter")

# Load images
start_img = pygame.image.load("Assets/img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("Assets/img/exit_btn.png").convert_alpha()

# Colors
_bg = (144, 201, 120)


# button class
class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


# Creating the buttons
start_btn = Button(_screen_width // 2 - 130, _screen_height // 2 - 150, start_img, 1)
exit_btn = Button(_screen_width // 2 - 110, _screen_height // 2 + 50, exit_img, 1)


def Menu():
    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False

        screen.fill(_bg)
        if start_btn.draw(screen):
            return True
        if exit_btn.draw(screen):
            return False
        pygame.display.update()

