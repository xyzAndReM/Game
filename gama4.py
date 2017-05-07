import pygame
import PyParticles
import PyAnimation
import time
import os
from sys import exit
from pygame.locals import *
import pygame.gfxdraw

pygame.mixer.pre_init(44100, -16, 2, 512) # setup mixer to avoid sound lag
pygame.init()
pygame.display.set_caption('Bubble Shock')
(width, height) = (600, 800)
x0 = width/2
y0 = height
FPS = 60
_sound_library = {}
def play_sound(path):
  global _sound_library
  sound = _sound_library.get(path)
  if sound == None:
    canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    sound = pygame.mixer.Sound(canonicalized_path)
    _sound_library[path] = sound
  sound.play()
class Arena(PyParticles.Environment):
    pass


screen = pygame.display.set_mode((width, height))
env = Arena(width, height)

#env.addParticles(5,y = 0)

#Ticks-----------------------
ticks_to_particles = 240 #Se refere ao intervalo de tempo necessário para surgirem novas particulas, t = ticks_to_particles/fps
ticks_to_bullet = 0 #Se refere ao intervalo de tempo necessário para carregar a arma de bolha novamente
#-----------------------------
#Sound and Font:
pygame.font.init()
font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 16) #Fonte do jogo (SUJEITO A MUDANÇAS)
#-----------------------------------------------------------
bullet = None #Objeto do projétil
selected_particle = None #Ignorar
running = True
clock = pygame.time.Clock()

while running:

    dt = clock.tick(FPS)
    #####################Queda dos meteoros####################
    if not ticks_to_particles:
        ticks_to_particles = 240
        env.addParticles(5,y = 0)
    else:
        ticks_to_particles -= 1
    ###################Queda dos meteorso-END##################

    ######################Disparos###########################
    if not ticks_to_bullet:
                if(not bullet or (bullet.x !=x0 or bullet.y !=y0)):
                    bullet = env.addParticles(x = x0,y = y0,size = 15, mass =1.5, colour = (0,0,255),vel = [0,0])
                ticks_to_bullet = 180
    else:
        ticks_to_bullet -=1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if (bullet.x ==x0 and bullet.y ==y0):
                play_sound('launch.wav')
                [xf,yf] = pygame.mouse.get_pos()
                bullet.vel = PyParticles.aim(x0,y0,xf,yf)
                ticks_to_bullet = 180 #Quando ticks_to_bullet assumir 0 novamente a bala é restaurada
    ###########################DIsparos-End############################
    env.update() #movimento das particulas entre outras coisas que precisam ser atualizadas
    screen.fill(env.colour)
    ########################Mira Laser###############################
    [xl,yl] = pygame.mouse.get_pos()
    PyAnimation.draw_laser(screen,x0,y0,xl,yl,width,height,15)
    ########################MIra Laser - END########################
    
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, height-120),5) # Desenho das bordas
    
    
    for p in env.particles:
        #pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), p.size, p.thickness)
        pygame.gfxdraw.filled_circle(screen, int(p.x), int(p.y), p.size, p.colour)  # draw filled circle
        pygame.gfxdraw.aacircle(screen, int(p.x), int(p.y), p.size, p.colour)  # draw border
        label = game_font.render(str(int(p.protect/FPS)), 1, (0,0,0)) #Segundos de destruição nas bolhas
        score = game_font.render(str(int(env.points)),1,(100,100,100)) #Mostra o score
        rank = game_font.render(env.messages[env.rank],1,(100,100,100)) #Mostra o ranking

        screen.blit(label, (p.x-4, p.y-4))
        screen.blit(score, (width/2 - 5,height-60))
        screen.blit(rank, (width/2 - 15,height-90))
    for s in env.scores:
        ticks = 120 - s.endurance
        if(ticks <= 60):
            PyAnimation.draw_clock(screen,s.x,s.y,10+(ticks/3),12,10-(ticks/6),s.colour)
        s.endurance -=1
        plus = game_font.render('+' + str(int(s.score)),1,(0,0,0))
        screen.blit(plus,(s.x,s.y-10))
        if   s.endurance < 1:
            env.scores.remove(s)

    pygame.display.flip()



    