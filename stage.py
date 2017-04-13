

import pygame
import pygame.mixer
from pygame.locals import *
from sys import exit
import time
import math
from player import Player
import random
from random import randrange



pygame.mixer.pre_init(44100, 32, 2, 4096)
explosion_played = False
explosion_sound = pygame.mixer.Sound('boom.wav')
pop_sound = pygame.mixer.Sound('pop3.wav')


def get_rect(obj):
    return Rect(obj['position'][0],
                obj['position'][1],
                obj['surface'].get_width() - 1,
                obj['surface'].get_height() - 1)

class Stage:

    asteroids = []
    bubbles = []

    def create_asteroid(self):
        picture = pygame.image.load('sphere.png').convert_alpha()
        picture = pygame.transform.scale(picture, (25, 25))
        asteroid = {
            'surface': picture,
            'position': [randrange(892), -64],
            'speed': [-0.1 + random.uniform(0.1,0.2), 0.2 + random.uniform(0.1,0.2)]
        }
        self.asteroids.append(asteroid)
    def move_asteroids(self,dt):
        for asteroid in self.asteroids:
            asteroid['position'][1] += asteroid['speed'][1]*dt
            asteroid['position'][0] += asteroid['speed'][0]*dt
    def remove_used_asteroids(self):
        for asteroid in self.asteroids:
            if asteroid['position'][1] > 560:
                self.asteroids.remove(asteroid)
    def move_bubble(self,dt):
        for bubble in self.bubbles:
            bubble['position'][1] += bubble['speed'][1]*dt
            bubble['position'][0] += bubble['speed'][0]*dt
    def remove_used_bubbles(self):
        for bubble in self.bubbles:
            if bubble['position'][1] < 0 or bubble['position'][1] > 600:
                Stage.bubbles.remove(bubble)
    def bounce_lateral(self):
        for bubble in self.bubbles:
            if bubble['position'][0] <= 10 or bubble['position'][0] >= 935:
                bubble['speed'][0] = -bubble['speed'][0]
        for asteroid in self.asteroids:
            if asteroid['position'][0] <= 10 or asteroid['position'][0] >= 935:
                asteroid['speed'][0] = -asteroid['speed'][0]
    def ship_collided(self,Player):
        bubble_pop = False
        ship_rect = get_rect(Player.ship)
        for asteroid in self.asteroids:
            asteroid_body = get_rect(asteroid)
            if ship_rect.colliderect(asteroid_body):
                return True
            for bubble in self.bubbles:
                bubbles_rect = get_rect(bubble)
                if self.bubbles and bubbles_rect.colliderect(asteroid_body):
                    self.bubbles.remove(bubble)
                    self.asteroids.remove(asteroid)
                    if not explosion_played:
                        bubble_pop = True
                        pop_sound.play()
                        Player.ship['position'][0] += Player.ship['speed']['x']
                        Player.ship['position'][1] += Player.ship['speed']['y']
                        screen.blit(Player.ship['surface'],
                                    Player.ship['position'])
        return False