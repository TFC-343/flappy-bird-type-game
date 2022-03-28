#! /usr/bin/env python3.9

"""
flappy bird in python
"""

__author__ = "TFC343"

import math
import random
import sys

import pygame
import pygame.gfxdraw
from pygame.locals import *

pygame.init()
pygame.font.init()


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, x, y):
        self.x += x
        self.y += y

    def get_tuple(self):
        return self.x, self.y


class Bird:
    def __init__(self):
        self.real = Pos(250, SCREEN_HEIGHT//2)
        self.radius = 40
        self.speed = 0
        self.distance = 0
        self.score = 0

        self.image = pygame.image.load("bird.png")
        self.image = pygame.transform.scale(self.image, (int(38 * 2.5), int(30 * 2.5)))
        self.rect = self.image.get_rect()
        self.rect.center = self.real.get_tuple()
        self.left = self.real.x - 40
        self.right = self.real.x + 44
        self.top = self.real.y - 20
        self.bottom = self.real.y + 30

    def jump(self):
        self.speed = -12

    def update(self):
        self.speed += 0.5

        self.real.move(0, self.speed)
        self.top += self.speed
        self.bottom += self.speed
        self.rect.center = self.real.get_tuple()

    def get_hitbox(self):
        top = self.top
        left = self.left
        bottom = self.bottom
        return pygame.Rect(left + abs(self.speed), top + abs(self.speed), self.right-left, bottom-top)

    def draw(self, surface):
        surface.blit(pygame.transform.rotate(self.image, -self.speed * 2 - 5), self.rect)
        # pygame.draw.circle(surface, 'red', self.real.get_tuple(), self.radius, 2)
        # pygame.draw.rect(surface, 'red', self.rect, 2)
        if SHOW_HITBOXES:
            pygame.draw.rect(surface, 'red', self.get_hitbox(), 2)


class Pipe:
    def __init__(self):
        self.middle = Pos(SCREEN_WIDTH + 30, random.randint(200, SCREEN_HEIGHT - 200))
        self.rect1 = pygame.Rect(SCREEN_WIDTH, 0, 56, self.middle.y - 100)
        self.rect2 = pygame.Rect(SCREEN_WIDTH, self.middle.y + 100, 56, SCREEN_HEIGHT)
        self.scored = False
        self.pipe_image_top = pygame.image.load("pipe2.png")
        self.pipe_image_top = pygame.transform.scale(self.pipe_image_top, (11 * 8, 50 * 8))

        self.pipe_image_bottom = pygame.image.load("pipe7.png")
        self.pipe_image_bottom = pygame.transform.scale(self.pipe_image_bottom, (11 * 8, 50 * 8))

        self.rect3 = pygame.Rect(self.middle.x - self.pipe_image_top.get_width()//2, self.middle.y-100 - 4 * 8, self.pipe_image_top.get_width(), 4 * 8)
        self.rect4 = pygame.Rect(self.middle.x - self.pipe_image_bottom.get_width() // 2, self.middle.y + 100,
                                 self.pipe_image_bottom.get_width(), 4 * 8)

    def get_rects(self):
        return self.rect1, self.rect2, self.rect3, self.rect4

    def update(self):
        for rect in self.get_rects():
            rect.move_ip(-7, 0)
        self.middle.move(-7, 0)

    def draw(self, surface):
        # pygame.draw.rect(surface, PIPE_GREEN, self.top)
        # pygame.draw.rect(surface, PIPE_GREEN, self.bottom)
        surface.blit(self.pipe_image_top, self.pipe_image_top.get_rect(centerx=self.middle.x, top=self.middle.y + 100))
        surface.blit(self.pipe_image_bottom, self.pipe_image_top.get_rect(centerx=self.middle.x, bottom=self.middle.y - 100))


class Cloud:
    def __init__(self, left=0, top=True):
        self.pos = Pos(0, 0)
        self.image = pygame.image.load("cloud3.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width()*5, self.image.get_height()*5))
        if top:
            self.image = pygame.transform.flip(self.image, False, True)
        self.rect = self.image.get_rect(center=(left, 0 if top else SCREEN_HEIGHT - BAR_SIZE))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Constants

SKY_BLUE = pygame.Color(135, 206, 235)
BIRD_YELLOW = pygame.Color(255, 211, 0)
PIPE_GREEN = pygame.Color(3, 172, 19)
WHITE = pygame.Color(255, 255, 255)

FPS = 60

SCREEN_WIDTH, SCREEN_HEIGHT = 1270, 720

BAR_SIZE = 17


SHOW_HITBOXES = False


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("The Adventures Of The Honourable Sir Robert Duckius The Third")
    screen.fill(SKY_BLUE)
    pygame.display.set_icon(pygame.image.load("bird_icon.png"))
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()

    bird = Bird()
    pipes = []
    clouds = [Cloud(i) for i in range(0, SCREEN_WIDTH, 120)] + [Cloud(i, False) for i in range(0, SCREEN_WIDTH, 120)]

    distance = 0  # frames since last pipe spawn

    font = pygame.font.SysFont("forte", 60)

    paused = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                if event.key == K_SPACE:
                    if paused:
                        paused = False
                        bird = Bird()
                        pipes = [Pipe()]
                        distance = 0
                    bird.jump()

        # update
        if not paused:
            distance += 1
            bird.update()
            for pipe in pipes:
                pipe.update()
        if distance > 100:
            distance = 0
            pipes.append(Pipe())

        collided = False
        if bird.real.y - bird.radius < -bird.radius//2:
            collided = True
        if bird.real.y + bird.radius > SCREEN_HEIGHT + bird.radius//2:
            collided = True
        for pipe in pipes:
            if bird.real.x > pipe.rect1.centerx and not pipe.scored:
                pipe.scored = True
                bird.score += 1
            if bird.get_hitbox().collidelistall(pipe.get_rects()):
                collided = True
        if collided:
            pygame.display.update()
            paused = True

        # draw
        screen.fill(SKY_BLUE)

        bird.draw(screen)
        for pipe in pipes:
            pipe.draw(screen)
            if SHOW_HITBOXES:
                for rect in pipe.get_rects():
                    pygame.draw.rect(screen, 'red', rect, 2)
        for cloud in clouds:
            cloud.draw(screen)

        score = font.render(f"{bird.score}", True, (0, 0, 0))
        screen.blit(score, score.get_rect(center=(SCREEN_WIDTH//2, 75)))

        if paused:
            play_text = font.render(f"press space to play", True, (0, 0, 0))
            screen.blit(play_text, play_text.get_rect(center=(SCREEN_WIDTH//2, 500)))

        # cloud bar
        pygame.draw.rect(screen, WHITE, (0, SCREEN_HEIGHT - BAR_SIZE, SCREEN_WIDTH, BAR_SIZE))

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
        print("closing")
