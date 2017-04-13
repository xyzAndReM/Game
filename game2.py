import pygame
from pygame.locals import *
from sys import exit
import time
import math
import random
# import pyganim
# import cc
from random import randrange


def get_rect(obj):
    return Rect(obj['position'][0],
                obj['position'][1],
                obj['surface'].get_width() - 1,
                obj['surface'].get_height() - 1)

#-------------------------------------------------------------------------
#---------------------------------Classe do jogador-----------------------
#-------------------------------------------------------------------------


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
            'speed': [0.5 * x, -0.5 * y]}

    def move_ship(self):
        self.ship['position'][0] += self.ship['speed']['x'] * dt
        self.ship['position'][1] += self.ship['speed']['y'] * dt
        self.ship['angle'] += self.ship['omega'] * dt
        self.ship['surface'] = rot_center(ship_illusion, self.ship['angle'])
        screen.blit(self.ship['surface'], self.ship['position'])
    def no_inertia(self):
        self.ship['speed'] = {
        'x': 0,
        'y': 0
    }
        self.ship['omega'] = 0

#-------------------------------------------------------------------------
#---------------------------------Classe do estagio-----------------------
#-------------------------------------------------------------------------


class Stage:

    asteroids = []
    bubbles = []

    def create_asteroid(self):  # Cria um asteroide guardado dentro de um vetor
        picture = pygame.image.load('sphere.png').convert_alpha()
        picture = pygame.transform.scale(picture, (25, 25))
        asteroid = {
            'surface': picture,
            'position': [randrange(892), -64],
            'speed': [-0.5 + random.uniform(0.5, 1), 0.3 + random.uniform(0.2, 0.4)]
        }
        self.asteroids.append(asteroid)

    def move_asteroids(self, dt):  # Responsavel pela mudanca de coordenadas dos asteroides
        for asteroid in self.asteroids:
            asteroid['position'][1] += asteroid['speed'][1] * dt
            asteroid['position'][0] += asteroid['speed'][0] * dt
            screen.blit(asteroid['surface'], asteroid['position'])

    def remove_used_asteroids(self):  # Remocao dos asteroides da tela
        for asteroid in self.asteroids:
            if asteroid['position'][1] > 560:
                self.asteroids.remove(asteroid)

    def move_bubble(self, dt):  # Move o tiro da nave
        for bubble in self.bubbles:
            bubble['position'][1] += bubble['speed'][1] * dt
            bubble['position'][0] += bubble['speed'][0] * dt
            screen.blit(bubble['surface'], bubble['position'])

    def remove_used_bubbles(self):  # Remove a bala da tela
        for bubble in self.bubbles:
            if bubble['position'][1] < 0 or bubble['position'][1] > 600:
                Stage.bubbles.remove(bubble)

    def bounce_lateral(self):  # Reflexao da bala na lateral da tela
        for bubble in self.bubbles:
            if bubble['position'][0] <= 10 or bubble['position'][0] >= 935:
                bubble['speed'][0] = -bubble['speed'][0]
        for asteroid in self.asteroids:
            if asteroid['position'][0] <= 10 or asteroid['position'][0] >= 935:
                asteroid['speed'][0] = -asteroid['speed'][0]

    # Colisao da nave com os asteroides, e da bala com os asteroides
    def ship_collided(self, Player):
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


def rot_center(image, angle):
    """rotate a Surface, maintaining position."""

    loc = image.get_rect().center  # rot_image is not defined
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite


#------------------Main-------------------------
pygame.init()
Player = Player()
Stage = Stage()
pygame.font.init()
pygame.mixer.pre_init(44100, 32, 2, 4096)
font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 72)

#----------------Variaveis globais--------------
collided = False
teta = 0
explosion_played = False
ship_illusion = Player.ship['surface']
ticks_to_asteroid = 45
collision_animation_counter = 0
FPS = 45
ship_speed = 0.3
ship_omega = 0.3
#----------------Efeitos sonoros----------------
explosion_sound = pygame.mixer.Sound('boom.wav')
pop_sound = pygame.mixer.Sound('pop3.wav')
#-------------------Imagens----------------------
background_filename = 'space.jpg'
ship_filename = 'arrow2.png'
#------------------------------------------------
screen = pygame.display.set_mode((956, 560), 0, 32)
background = pygame.image.load(background_filename).convert()
pygame.display.set_caption('Bubble Shock')
clock = pygame.time.Clock()

while True:
    dt = clock.tick(FPS)
    Player.no_inertia()
    if not ticks_to_asteroid:
        ticks_to_asteroid = 45
        Stage.create_asteroid()
    else:
        ticks_to_asteroid -= 1

    

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    pressed_keys = pygame.key.get_pressed()

    if pressed_keys[K_UP]:
        Player.ship['speed']['y'] = -ship_speed
    elif pressed_keys[K_DOWN]:
        Player.ship['speed']['y'] = ship_speed

    if pressed_keys[K_LEFT]:
        Player.ship['speed']['x'] = -ship_speed
    elif pressed_keys[K_RIGHT]:
        Player.ship['speed']['x'] = ship_speed

    if pressed_keys[K_q] and len(Stage.bubbles) < 1:
        Stage.bubbles.append(Player.bubble_bullet())

    if pressed_keys[K_a]:
        Player.ship['omega'] += ship_omega
    elif pressed_keys[K_d]:
        Player.ship['omega'] -= ship_omega

    screen.blit(background, (0, 0))

    if not collided:
        collided = Stage.ship_collided(Player)
        Player.move_ship()
    else:
        if not explosion_played:
            explosion_played = True
            explosion_sound.play()
        elif collision_animation_counter == 3:
            text = game_font.render('Game Over', 1, (255, 0, 0))
            screen.blit(text, (335, 250))

        else:
            Player.exploded_ship['rect'].x = collision_animation_counter * 48
            Player.exploded_ship['position'] = Player.ship['position']
            screen.blit(Player.exploded_ship['surface'], Player.exploded_ship[
                        'position'], Player.exploded_ship['rect'])
            collision_animation_counter += 1

    Stage.move_asteroids(dt)
    Stage.move_bubble(dt)
    pygame.display.update()
    Stage.remove_used_asteroids()
    Stage.bounce_lateral()
    Stage.remove_used_bubbles()
