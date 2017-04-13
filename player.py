import pygame
from pygame.locals import *
from sys import exit
import time
import math
import random
from random import randrange
class Player:
    ship = {
        'angle': 0,
        'omega': 0,
        'surface': pygame.image.load('ship.png'),
        'position': [randrange(956), randrange(560)],
        'speed': {
            'x': 0,
            'y': 0
        }
    }
    exploded_ship = {
        'surface': pygame.image.load('ship_exploded.png'),
        'position': [],
        'speed': {
            'x': 0,
            'y': 0
        },
        'rect': Rect(0, 0, 48, 48)
    }
    def bubble_bullet(self):
        picture = pygame.image.load('sphere.png').convert_alpha()
        picture = pygame.transform.scale(picture, (25, 25))
        a = (self.ship['angle'] + 90) * 2 * math.pi / 360
        print(a)
        x = math.cos(a)
        y = math.sin(a)
        return {
            'surface': picture,
            'position': [self.ship['position'][0], self.ship['position'][1]],
            'speed': [1* x, -1 * y]}