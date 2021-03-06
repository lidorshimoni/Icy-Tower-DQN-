import random

import pygame

pygame.init()

from Constants import GRAVITY, SCREEN_WIDTH, SCREEN_HEIGHT, MAX_VEL_X, ACCELERATION, COMBO_JUMP_MULTIPLIER, \
    MIN_COMBO_VEL
from Utils import load_image, resource_path

from copy import deepcopy


class Player:
    width = 30
    height = 50

    vel_x = 0
    vel_y = 0
    max_falling_speed = 20

    acceleration = ACCELERATION
    max_vel_x = MAX_VEL_X

    color = (255, 0, 0)
    speed = 5

    def __init__(self):

        self.x = random.randint(1, 120) * 5
        self.y = 500
        self.score = -10  # negate floor platform -10
        self.combo_score = 0
        self.prev_pos = [(self.x, self.y),(self.x, self.y),(self.x, self.y),(self.x, self.y)]

        self.spritesheet_image = load_image(resource_path('spritesheet.png'))
        self.spritesheet = []

        # Idle
        self.cropped = pygame.Surface((33, 57), pygame.SRCALPHA, 32)
        self.cropped.blit(self.spritesheet_image, (0, 0), (0, 0, 33, 57))
        self.cropped2 = pygame.Surface((33, 57), pygame.SRCALPHA, 32)
        self.cropped2.blit(self.spritesheet_image, (0, 0), (37, 0, 33, 57))
        self.cropped3 = pygame.Surface((33, 57), pygame.SRCALPHA, 32)
        self.cropped3.blit(self.spritesheet_image, (0, 0), (75, 0, 33, 57))
        self.spritesheet.append(self.cropped)
        self.spritesheet.append(self.cropped2)
        self.spritesheet.append(self.cropped3)

        # Going right
        self.cropped4 = pygame.Surface((33, 57), pygame.SRCALPHA, 32)
        self.cropped4.blit(self.spritesheet_image, (0, 0), (0, 56, 33, 57))
        self.cropped5 = pygame.Surface((33, 57), pygame.SRCALPHA, 32)
        self.cropped5.blit(self.spritesheet_image, (0, 0), (37, 56, 33, 57))
        self.cropped6 = pygame.Surface((33, 57), pygame.SRCALPHA, 32)
        self.cropped6.blit(self.spritesheet_image, (0, 0), (75, 56, 33, 57))
        self.spritesheet.append(self.cropped4)
        self.spritesheet.append(self.cropped5)
        self.spritesheet.append(self.cropped6)

        # Going left
        self.spritesheet.append(pygame.transform.flip(self.cropped4, True, False))
        self.spritesheet.append(pygame.transform.flip(self.cropped5, True, False))
        self.spritesheet.append(pygame.transform.flip(self.cropped6, True, False))

        # Jumping
        self.cropped7 = pygame.Surface((33, 57), pygame.SRCALPHA, 32)
        self.cropped7.blit(self.spritesheet_image, (0, 0), (75, 112, 33, 57))
        self.spritesheet.append(self.cropped7)
        self.spritesheet.append(self.cropped7)
        self.spritesheet.append(self.cropped7)

        self.combo_count = 0
        self.combo_start_value = 0

        self.sprite_index_x = 0
        self.sprite_index_y = 0
        self.frame_counter = 0
        self.frame_delay = 9

        self.is_on_platform = True

    def draw(self, game_display, camera):
        game_display.blit(self.spritesheet[self.sprite_index_y * 3 + self.sprite_index_x], (self.x, self.y - camera.y))

        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.sprite_index_x += 1
            if self.sprite_index_x > 2:
                self.sprite_index_x = 0
            self.frame_counter = 0

    def update(self):
        if (
                self.vel_x <= MIN_COMBO_VEL and self.vel_x > 0 or self.vel_x > -MIN_COMBO_VEL and self.vel_x < 0) and self.combo_count > 0:
            self.end_combo()
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY
        if self.vel_y > self.max_falling_speed:
            self.vel_y = self.max_falling_speed
        if self.x <= 0:
            self.x = 0
        if self.x + self.width >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        self.prev_pos.append((self.x, self.y))
        if len(self.prev_pos)>=4:
            self.prev_pos.pop(0)



    def combo(self):
        if self.x == 0 or self.x + self.width >= SCREEN_WIDTH:
            self.vel_x *= -1
            if (self.vel_y < 0):
                self.vel_y *= COMBO_JUMP_MULTIPLIER
            # self.start_combo()

    # def combo(self):
    # 	if self.x == 0:
    # 		self.vel_x *= -1
    # 	# if self.vel_y < 0:
    # 	# 	if self.vel_x < 0:
    # 	# 		self.vel_y -= 10
    # 	# 		self.vel_x *= -2.5
    # 	if self.x + self.width >= SCREEN_WIDTH:
    # 		self.vel_x *= -1
    # # if self.vel_y < 0:
    # # 	if self.vel_x > 0:
    # # 		self.vel_y -= 10
    # # 		self.vel_x *= -2.5

    def on_platform(self, platform):
        # return platform.rect.top <= self.y + self.height
        return platform.rect.collidepoint((self.x, self.y + self.height)) or \
               platform.rect.collidepoint((self.x + self.width, self.y + self.height))

    def on_any_platform(self, platform_controller, floor):
        for p in platform_controller.platform_set:
            if self.on_platform(p):
                self.is_on_platform = True
                return True
        if self.on_platform(floor):
            self.is_on_platform = True
            return True
        self.is_on_platform = False
        return False

    def collide_platform(self, platform, index, platforms=None):
        for i in range(0, int(self.vel_y)):
            if pygame.Rect(self.x, self.y - i, self.width, self.height).colliderect(platform.rect):
                if platform.rect.collidepoint((self.x, self.y + self.height - i)) or \
                        platform.rect.collidepoint(
                            (self.x + self.width, self.y + self.height - i)):  # do not change! no on_platform here
                    self.y = platform.y - self.height
                    if not platform.collect_score(self):
                        self.score += 10
                        if self.score < index * 10:
                            self.score = index * 10

                        if platforms != None:
                            for plat in platforms[0:index]:
                                plat.collect_score(self)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def fallen_off_screen(self, camera):
        if self.y - camera.y + self.height >= SCREEN_HEIGHT:
            return True
        return False

    def start_combo(self):
        if self.combo_count == 0:
            self.combo_start_value = self.score
        self.combo_count += 1
        # print("starting combo")

    def end_combo(self):
        if self.combo_count >= 2:
            self.combo_score += ((self.score - self.combo_start_value) / 10) ** 2
        # print(self.combo_count, " - endcombo = ", self.combo_score)

        self.combo_start_value = 0
        self.combo_count = 0
