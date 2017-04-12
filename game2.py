import pygame
from pygame.locals import *
from sys import exit
import time,math
import pyganim
import cc
from random import randrange


def create_asteroid():
    picture = pygame.image.load('sphere.png').convert_alpha()
    picture = pygame.transform.scale(picture, (25, 25))
    return {
        'surface': picture,
        'position': [randrange(892), -64],
        'speed': [-2 + randrange(4), 2 + randrange(2)]
    }


def move_asteroids():
    for asteroid in asteroids:
        asteroid['position'][1] += asteroid['speed'][1]
        asteroid['position'][0] += asteroid['speed'][0]


def remove_used_asteroids():
    for asteroid in asteroids:
        if asteroid['position'][1] > 560:
            asteroids.remove(asteroid)


def move_bubble():
    for bubble in bubbles:
        bubble['position'][1] += bubble['speed'][1]
        bubble['position'][0] += bubble['speed'][0]


def remove_used_bubbles():
    for bubble in bubbles:
        if bubble['position'][1] < 0 or bubble['position'][1] > 600 :
            bubbles.remove(bubble)


def bounce_lateral():
    for bubble in bubbles:
        if bubble['position'][0] <= 10 or bubble['position'][0] >= 935 :
            bubble['speed'][0] = -bubble['speed'][0]
    for asteroid in asteroids:
        if asteroid['position'][0] <= 10 or asteroid['position'][0] >= 935:
            asteroid['speed'][0] = -asteroid['speed'][0]


def get_rect(obj):
    return Rect(obj['position'][0],
                obj['position'][1],
                obj['surface'].get_width() - 1,
                obj['surface'].get_height() - 1)


def ship_collided():
    bubble_pop = False
    ship_rect = get_rect(ship)
    
    for asteroid in asteroids:
        asteroid_body = get_rect(asteroid)
        if ship_rect.colliderect(asteroid_body):
            return True
        for bubble in bubbles:
            bubbles_rect = get_rect(bubble)
            if bubbles and bubbles_rect.colliderect(asteroid_body):
            	bubbles.remove(bubble)
            	asteroids.remove(asteroid)
            	if not explosion_played:
            		bubble_pop = True
            		pop_sound.play()
            		ship['position'][0] += ship['speed']['x']
            		ship['position'][1] += ship['speed']['y']
            		screen.blit(ship['surface'], ship['position'])
    return False

def rot_center(image, angle):
    """rotate a Surface, maintaining position."""

    loc = image.get_rect().center  #rot_image is not defined 
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite


def bubble_bullet(ship):
    picture = pygame.image.load('sphere.png').convert_alpha()
    picture = pygame.transform.scale(picture, (25, 25))
    a = (ship['angle']+90)*2*math.pi/360 
    print(a)
    x = math.cos(a)
    y = math.sin(a)
    return {
        'surface': picture,
        'position': [ship['position'][0] , ship['position'][1]],
        'speed': [13*x, -13*y]}


class spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error, message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit, message
    # Load a specific image from a specific rectangle

    def image_at(self, rectangle, colorkey=None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA, 32).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list

    def images_at(self, rects, colorkey=None):
        "Loads multiple images, supply a list of coordinates"
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images

    def load_strip(self, rect, image_count, colorkey=None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


pygame.init()
pygame.font.init()
pygame.mixer.pre_init(44100, 32, 2, 4096)
font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 72)
collided = False
teta = 0
explosion_sound = pygame.mixer.Sound('boom.wav')
pop_sound = pygame.mixer.Sound('pop3.wav')
explosion_played = False
screen = pygame.display.set_mode((956, 560), 0, 32)

background_filename = 'space.jpg'
background = pygame.image.load(background_filename).convert()

ship_filename = 'arrow2.png'

ss = spritesheet('bm.png')
bm = ss.image_at((0, 42, 40, 42), colorkey=(255, 255, 255)).convert_alpha()

bmw = []
# Load two images into an array, their transparent bit is (255, 255, 255)
bmw = ss.images_at(((0, 84, 40, 42), (35, 84, 40, 42), (70,
                                                        84, 40, 42), (105, 84, 40, 42)), colorkey=(255, 255, 255))
hit = ss.images_at(((100, 210, 39, 42), (105, 210, 39, 42),
                    (140, 210, 39, 42), (175, 210, 39, 42)), colorkey=(255, 255, 255))

ship = {
    'angle': 0,
    'omega': 0,
    'surface': pygame.image.load(ship_filename).convert_alpha(),
    'position': [randrange(956), randrange(560)],
    'speed': {
        'x': 0,
        'y': 0
    }
}

exploded_ship = {
    'surface': pygame.image.load('ship_exploded.png').convert_alpha(),
    'position': [],
    'speed': {
        'x': 0,
        'y': 0
    },
    'rect': Rect(0, 0, 48, 48)
}


pygame.display.set_caption('Bubble Shock')

clock = pygame.time.Clock()

ticks_to_asteroid = 45
asteroids = []
bubbles = []
ship_illusion =  ship['surface']
collision_animation_counter = 0
while True:

    if not ticks_to_asteroid:
        ticks_to_asteroid = 45
        asteroids.append(create_asteroid())
    else:
        ticks_to_asteroid -= 1

    ship['speed'] = {
        'x': 0,
        'y': 0
    }

    ship['omega'] = 0

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    pressed_keys = pygame.key.get_pressed()

    if pressed_keys[K_UP]:
        ship['speed']['y'] = -4
    elif pressed_keys[K_DOWN]:
        ship['speed']['y'] = 4

    if pressed_keys[K_LEFT]:
        ship['speed']['x'] = -4
    elif pressed_keys[K_RIGHT]:
        ship['speed']['x'] = 4

    if pressed_keys[K_q] and len(bubbles) < 1:
        bubbles.append(bubble_bullet(ship))

    if pressed_keys[K_a]:
        ship['omega'] += 3
    elif pressed_keys[K_d]:
        ship['omega'] -= 3

    screen.blit(background, (0, 0))

    if not collided:
        collided = ship_collided()
        ship['position'][0] += ship['speed']['x']
        ship['position'][1] += ship['speed']['y']
        ship['angle'] += ship['omega']
        #ship['angle'] = ship['angle'] % 2*math.pi

        ship['surface'] = rot_center(ship_illusion, ship['angle'])#pygame.transform.rotate(ship_illusion, ship['angle'])
        #print(ship['angle'])
        screen.blit(ship['surface'], ship['position'])
    else:
        if not explosion_played:
            explosion_played = True
            explosion_sound.play()
            #ship['position'][0] += ship['speed']['x']
            #ship['position'][1] += ship['speed']['y']
            #screen.blit(ship['surface'], ship['position'])
        elif collision_animation_counter == 3:
            text = game_font.render('Game Over', 1, (255, 0, 0))
            screen.blit(text, (335, 250))

        else:
            exploded_ship['rect'].x = collision_animation_counter * 48
            exploded_ship['position'] = ship['position']
            screen.blit(exploded_ship['surface'], exploded_ship[
                        'position'], exploded_ship['rect'])
            collision_animation_counter += 1

    move_asteroids()

    for asteroid in asteroids:
        screen.blit(asteroid['surface'], asteroid['position'])

    move_bubble()

    for bubble in bubbles:
        screen.blit(bubble['surface'], bubble['position'])
    pygame.display.update()
    time_passed = clock.tick(60)

    remove_used_asteroids()
    bounce_lateral()

    remove_used_bubbles()
