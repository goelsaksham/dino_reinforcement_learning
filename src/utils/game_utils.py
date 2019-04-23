import pygame
from pygame import RLEACCEL


def load_image(sprites_path, x_size=-1, y_size=-1, color_key=None):
    sprites_image = pygame.image.load(sprites_path)
    sprites_image = sprites_image.convert()
    if color_key is not None:
        if color_key is -1:
            color_key = sprites_image.get_at((0, 0))
        sprites_image.set_colorkey(color_key, RLEACCEL)

    if x_size != -1 or y_size != -1:
        sprites_image = pygame.transform.scale(sprites_image, (x_size, y_size))

    return sprites_image, sprites_image.get_rect()


def load_sprite_sheet(sprites_path, nx, ny,
                      x_scale=-1, y_scale=-1, color_key=None):
    sprites_sheet = pygame.image.load(sprites_path)
    sprites_sheet = sprites_sheet.convert()

    sheet_rectangle = sprites_sheet.get_rect()

    sprites = []

    x_size = sheet_rectangle.width / nx
    y_size = sheet_rectangle.height / ny

    for i in range(0, ny):
        for j in range(0, nx):
            rect = pygame.Rect((j * x_size, i * y_size, x_size, y_size))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sprites_sheet, (0, 0), rect)
            if color_key is not None:
                if color_key is -1:
                    color_key = image.get_at((0, 0))
                image.set_colorkey(color_key, RLEACCEL)
            if x_scale != -1 or y_scale != -1:
                image = pygame.transform.scale(image, (x_scale, y_scale))
            sprites.append(image)

    sprite_rect = sprites[0].get_rect()
    return sprites, sprite_rect


def display_game_over_message(screen, width, height, return_button_image, game_over_image):
    return_button_rect = return_button_image.get_rect()
    return_button_rect.centerx = width / 2
    return_button_rect.top = height * 0.52

    gameover_rect = game_over_image.get_rect()
    gameover_rect.centerx = width / 2
    gameover_rect.centery = height * 0.35

    screen.blit(return_button_image, return_button_rect)
    screen.blit(game_over_image, gameover_rect)


def extract_digits(number):
    if number > -1:
        digits = []
        i = 0
        while number / 10 != 0:
            digits.append(number % 10)
            number = int(number / 10)

        digits.append(number % 10)
        for i in range(len(digits), 5):
            digits.append(0)
        digits.reverse()
        return digits
