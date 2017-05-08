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
#Music----------------------
pygame.mixer.music.load('main.mp3')
pygame.mixer.music.play(-1,0.0)

#Ticks-----------------------
ticks_to_particles = 240 #Se refere ao intervalo de tempo necessário para surgirem novas particulas, t = ticks_to_particles/fps
ticks_to_bullet = 0 #Se refere ao intervalo de tempo necessário para carregar a arma de bolha novamente
ticks_to_bonus = 240
ticks_to_bomb = 240
#-----------------------------
#Font:
pygame.font.init()
font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 16) #Fonte do jogo (SUJEITO A MUDANÇAS)
label_font = pygame.font.SysFont(font_name, 14)
rank_font = pygame.font.Font('sensational.ttf', 32)   #'GoodDog.otf'
GAME_HP_font = pygame.font.SysFont(font_name, 32)
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
        env.addParticles(2,y = 0, damage = 1)
    else:
        ticks_to_particles -= 1
    ###################Queda dos meteorso-END##################

    ######################Queda dos bônus######################
    if not ticks_to_bonus:
        bonus = env.addParticles(3,y = 0, colour = (0,200,0), life = 1, message = '+1 HP', label = 'HP', sound = 'life.wav')
        ticks_to_bonus = 720
    else:
        ticks_to_bonus -= 1
    ####################Queda dos bônus-END####################
        
    ######################Queda das bombas######################
    if not ticks_to_bomb:
        bomb = env.addParticles(3,y = 0, colour = (60,50,50),message = 'KABOOM !',label = 'TNT', sound = 'destroyed.wav')
        ticks_to_bomb = 1200
    else:
        ticks_to_bomb -= 1
    ####################Queda das bombas####################    

    ######################Disparos###########################
    if not ticks_to_bullet:
        if(not bullet or (bullet.x !=x0 or bullet.y !=y0)):
            bullet = env.addParticles(x = x0,y = y0,size = 15, mass =1.5, colour = (0,0,255),vel = [0,0], life = 0, damage = 0, message = '',label = '')
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
    env.update()
    screen.fill(env.colour)
    text = GAME_HP_font.render("HP: {0}".format(env.hp), 1, (0, 255, 0))
    screen.blit(text, (width - 90, 10))
    if (not env.hp): #movimento das particulas entre outras coisas que precisam ser atualizadas
        GAME_OVER_font = pygame.font.SysFont(font_name, 72)
        text = GAME_OVER_font.render("GAME OVER", 1, (255, 0, 00))
        screen.blit(text, (width/2 - 155, height/2 - 105))
        print("GAME OVER")
        running = False
    """else:
        GAME_HP_font = pygame.font.SysFont(font_name, 32)
        text = GAME_HP_font.render("HP: {0}".format(hp), 1, (50, 255, 0))
        screen.blit(text, (width - 100, 10))"""
    ########################Mira Laser###############################
    [xl,yl] = pygame.mouse.get_pos()
    PyAnimation.draw_laser(screen,x0,y0,xl,yl,width,height,15)
    PyAnimation.draw_lifebar(screen,475,775,(255,105,180),0.75,env.hp)
    ########################MIra Laser - END########################
    
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, height-120),5) # Desenho das bordas
    UP = 0
    for p in env.particles:
        #pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), p.size, p.thickness)
        pygame.gfxdraw.filled_circle(screen, int(p.x), int(p.y), p.size, p.colour)  # draw filled circle
        pygame.gfxdraw.aacircle(screen, int(p.x), int(p.y), p.size, p.colour)
        if(p.colour == (255,0,255)):  # draw border
        	label = label_font.render(str(int(p.protect/FPS)), 1, (0,0,0)) #Segundos de destruição nas bolhas
        else:
        	label = label_font.render(p.label, 1, (0,0,0))
        label_width = label.get_width()
        label_height = label.get_height()
        screen.blit(label, (p.x-label_width/2, p.y-label_height/2)) 
    for g in env.grave:
        ticks_pop = 120 - g.endurance
        if(ticks_pop <= 60):
            PyAnimation.draw_clock(screen,g.x,g.y,10+(ticks_pop/3),12,10-(ticks_pop/6),g.colour)
        g.endurance -=1
        plus = game_font.render(g.message,1,g.colour)
        screen.blit(plus,(g.x-5,g.y-10))
        if   g.endurance < 1:
            env.grave.remove(g)
    for s in env.shockwaves:
    	ticks_pop = 120 - s.endurance
    	s.size = 2*ticks_pop
    	if(ticks_pop <= 120):
    		pygame.gfxdraw.circle(screen,int(s.x),int(s.y),s.size,s.colour)
    		s.endurance -=1
    	if   s.endurance < 0:
    		env.shockwaves.remove(s)

    score = game_font.render(str(int(env.points)),1,(100,100,100))
    score_width = score.get_width()
    score_height = score.get_height() #Mostra o score
    if(env.rank > UP):
    	rankup = rank_font.render(env.messages[env.rank],1,(255,140,0))
    	rankup_width = rankup.get_width()
    	rankup_height = rankup.get_height()
    	screen.blit(rankup,  ( (width - rankup_width)/2,(height-200-rankup_height)/2 ))
    	#playsound
    rank = game_font.render(str(env.rank + 1) + 'x' ,1,(100,100,100))
    rank_width = rank.get_width()
    rank_height = rank.get_height()
    screen.blit(score, ( (width - score_width)/2,height-60))
    screen.blit(rank,  ( (width - rank_width)/2,height-90))



    pygame.display.flip()



    
