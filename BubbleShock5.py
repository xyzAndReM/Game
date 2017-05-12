import pygame
import PyParticles1
import PyAnimation
import time
import os
from sys import exit
from pygame.locals import *
import pygame.gfxdraw
import random
import math
_sound_library = {}
def play_sound(path):
  global _sound_library
  sound = _sound_library.get(path)
  if sound == None:
    canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    sound = pygame.mixer.Sound(canonicalized_path)
    _sound_library[path] = sound
  sound.play()

_font_library = {}
def use_font(path,size):
	global _font_library
	font = _font_library.get(path)
	if font == None:
		canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
		font = pygame.font.Font(canonicalized_path,size)
		_font_library[path] = font
	return font

def display_text(message,size,color,font,x,y):
	fonte = use_font(font,size)
	text = fonte.render(message,1,color)
	text_width = text.get_width()
	text_height = text.get_height()
	screen.blit(text, ( x-(text_width)/2, y-(text_height)/2 ))

pygame.mixer.pre_init(44100, -16, 2, 512) # setup mixer to avoid sound lag
pygame.init()
pygame.display.set_caption('Bubble Shock')
(width, height) = (600, 700)
x0 = width/2
y0 = height
FPS = 120



screen = pygame.display.set_mode((width, height))
env = PyParticles1.Environment(width, height)
scenery = pygame.image.load(os.path.join("scenery1.jpg"))
scenery_theta = 0

#Load de musicas#
pygame.mixer.music.load('main1.mp3')
#-----------------------------------

#Ticks-----------------------
ticks_to_particles = 240 #Se refere ao intervalo de tempo necessário para surgirem novas particulas, t = ticks_to_particles/fps
ticks_to_bullet = 0 #Se refere ao intervalo de tempo necessário para carregar a arma de bolha novamente
ticks_to_bonus = 240
ticks_to_bomb = 240
rankup_ticks = 0
ticks_pop = 0
ticks_gameover = 0
ticks_to_freeze = 0
ticks_to_laser = 0
ticks_to_scenery = 2
#-----------------------------

#Font:
pygame.font.init()
font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 16) #Fonte do jogo (SUJEITO A MUDANÇAS)
label_font = pygame.font.SysFont(font_name, 14)
rank_font = pygame.font.Font('sensational.ttf', 32)   #'GoodDog.otf'
GAME_HP_font = pygame.font.SysFont(font_name, 32)
menu_font = pygame.font.Font('GoodDOG.otf',32)
#-----------------------------------------------------------

#Variaveis globais:
bullet = None #Objeto do projétil
selected_particle = None #Ignorar
running = True
UP = 0
rankup_animation = False
MENU = True
flag = False
clock = pygame.time.Clock()
loading = False
#--------------------------------------------------------------------------

############################MENU####################################################
while MENU:
	dt = clock.tick(FPS)
	screen.fill(env.colour)
	display_text('Start',32,(0,0,0),'GoodDog.otf',width/2, (height)/2)
	for event in pygame.event.get():
	        if event.type == pygame.QUIT:
	            MENU = False
	            running = False
	        elif event.type == pygame.MOUSEBUTTONUP:
	                [xf,yf] = pygame.mouse.get_pos()
	                if( (xf-width/2)**2 + (yf-height/2)**2 < 100**2):
	                	flag = True
	                	play_sound('plof.wav')
	if(flag):
		if(ticks_pop <= 120):
			PyAnimation.draw_clock(screen,int(width/2),int(height/2),50+(ticks_pop/6),12,50-(ticks_pop/12),(0, 7, 61))
			ticks_pop += 1
		else:
			MENU = False
			ticks_pop = 0
	else:
		pygame.gfxdraw.aacircle(screen, int(width/2), int(height/2), 100, (0, 7, 61))
	pygame.display.flip()       
##############################################################################################
pygame.time.wait(500)
############Música##############
pygame.mixer.music.play(-1,0.0)
################################
time = 0
###############Looping principal###############################################################
while running:
    dt = clock.tick(FPS)
    time +=1
    #####################Queda dos meteoros####################
    if not ticks_to_particles:
        ticks_to_particles = 180
        env.addParticles(2,y = 0, damage = 1, V = 1 + time/(FPS*100))
    else:
        ticks_to_particles -= 1
    ###########################################################

    ######################Queda dos bônus######################
    if not ticks_to_bonus:
        bonus = env.addParticles(1,y = 20, colour = (0,200,0), life = 1, message = '+1 HP', label = 'HP', sound = 'life.wav')
        ticks_to_bonus = 720
    else:
        ticks_to_bonus -= 1
    ############################################################
        
    ######################Queda das bombas######################
    if not ticks_to_bomb:
        bomb = env.addParticles(1,y = 25, colour = (60,50,50),message = 'KABOOM !',label = 'TNT', sound = 'destroyed.wav')
        ticks_to_bomb = FPS*4
    else:
        ticks_to_bomb -= 1
    ############################################################    

    ######################Disparos###########################
    if not ticks_to_bullet:
        if(not bullet or  not loading):
            bullet = env.addParticles(x = x0,y = y0,size = 15, mass =1.5, colour = (0,0,255),vel = [0,0], life = 0, damage = 0, message = '',label = '')
            loading = True
    else:
        ticks_to_bullet -=3*(not env.freeze)
        print(env.freeze)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if (bullet.x ==x0 and bullet.y ==y0):
                play_sound('launch.wav')
                [xf,yf] = pygame.mouse.get_pos()
                bullet.vel = PyParticles1.aim(x0,y0,xf,yf)
                ticks_to_bullet = 2*FPS
                loading = False 
    ###################################################################

    #########################Freeze####################################
    if ticks_to_freeze == 8*FPS:
    	env.addParticles(2,y = 50, colour = (165, 242, 243),message = 'Chilly !',label = 'F', sound = 'ice.wav', freeze = 1)
    	ticks_to_freeze = 0
    else:
    	ticks_to_freeze += 1


    ###################################################################

    env.update()
    screen.fill(env.colour)
    scenery_x = 200*math.cos(scenery_theta)
    scenery_y = 200*math.sin(scenery_theta)
    screen.blit(scenery, (-0 - scenery_x, -0 - scenery_y))
    text = GAME_HP_font.render("HP: {0}".format(env.hp), 1, (0, 255, 0))
    screen.blit(text, (width - 90, 10))

    
    ###########################################GAMEOVER##########################################
    if ( env.hp <= 0): 
    	for p in env.particles:
    		p.null() #Se o jogo acaba todas as bolhas perdem suas caracteristicas
    		env.BubblePoP(p) #Todas as bolhas são estouradas
  
    	pygame.mixer.music.pause()
    	if(ticks_gameover >= 120):
    		if(ticks_gameover == 120):
    			play_sound('clear.wav')
    		display_text('Game Set',64,(153,0,0),'sensational.ttf',width/2, (height-200)/2)
    	if(ticks_gameover >= 360):
    		running = False
    	ticks_gameover += 1
    ##################################################################################################	
    	
    
    ########################Graficos###############################
    [xl,yl] = pygame.mouse.get_pos()
    if(env.freeze > 0):
    	bullet_bar_color = (165, 242, 243)
    else:
    	bullet_bar_color = (0,0,255)
    PyAnimation.draw_laser(screen,x0,y0,xl,yl,width,height,15) #O laser da mira
    PyAnimation.draw_lifebar(screen,475,height - 25,(255,105,180),0.75,env.hp,env.max_hp) #Desenha os corações no canto da tela
    PyAnimation.draw_bullet_bar(screen,10 ,height - 35,int(2*FPS-(ticks_to_bullet)),240,30,bullet_bar_color) #Desenha a barra de carregamento da bala
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, height-60),5) # Desenho das bordas
    display_text(str(int(env.points)),12,(255,215,0),'Ultra.ttf',width/2,height-40) #MOstra do score
    
    ###############################################################
    
    ###########################EVENTOS DAS PARTICULAS##################################################
    for p in env.particles:
        pygame.gfxdraw.filled_circle(screen, int(p.x), int(p.y), p.size, p.colour)  # Aqui estou desenhando todos os circulos de cada particula
        pygame.gfxdraw.aacircle(screen, int(p.x), int(p.y), p.size, p.colour) 
        if(p.damage):
        	pygame.gfxdraw.filled_circle(screen, int(p.x), int(p.y), int(p.size/2), (255,0,0))
        if(p.colour == (255,0,255)):  
        	label = label_font.render(str(int(p.protect/FPS)), 1, (0,0,0)) #Segundos de destruição nas bolhas roxas
        else:
        	label = label_font.render(p.label, 1, (0,0,0))
        label_width = label.get_width()
        label_height = label.get_height()
        screen.blit(label, (p.x-label_width/2, p.y-label_height/2))
    ####################################################################################################

    #########################EVENTOS DOS FANTASMAS (quando uma particula morre ela gera um fantasma que guarda a posição de onde esta morreu)######## 
    for g in env.grave:
        ticks_pop = 120 - g.endurance
        if(ticks_pop <= 60):
            PyAnimation.draw_clock(screen,g.x,g.y,10+(ticks_pop/3),12,10-(ticks_pop/6),g.colour)
        g.endurance -=1
        display_text(g.message,12 + (env.rank-1)*4,g.colour,'Ultra.ttf',g.x,g.y)
        if   g.endurance < 1:
            env.grave.remove(g)
    ########################EVENTOS DAS ONDAS DE CHOQUE##################################################
    for s in env.shockwaves:
    	ticks_pop = 120 - s.endurance
    	s.size = 2*ticks_pop
    	if(ticks_pop <= 120):
    		pygame.gfxdraw.circle(screen,int(s.x),int(s.y),s.size,s.colour)
    		s.endurance -=1
    	if   s.endurance < 0:
    		env.shockwaves.remove(s)
    ######################################################################################################

    ##########################ANIMAÇÃO DO RANKUP##########################################################
    if(env.rank > UP or rankup_animation):
    	if(not ticks_to_laser):
    		play_sound('iha.wav')
    		play_sound('laser.wav')
    		ticks_to_laser = 300
    	if( not rankup_animation ):
    		print('oi')
    		rankup_animation = True
    	elif(rankup_animation):
	    	rankup_ticks += 1
	    	P = int(17*rankup_ticks)
	    	#print('P = ' + str(P))
	    	if(ticks_to_laser):
	    		PyAnimation.draw_rects(screen,width,P,(height-100)/2,80,30,(255,140,0))
	    	if(P >= width/2 and P <= 6*width/2 ):
	    		message = env.messages[env.rank]
	    	elif(P > 6*width/2):
	    		#print('oi')
	    		rankup_animation = False
	    		rankup_ticks = 0
    if(ticks_to_laser):
    	ticks_to_laser -= 1
    display_text(env.messages[env.rank],48,(66, 33, 0),'Bombing.ttf',width/2,(height-100)/2)
    UP = env.rank
    rank = game_font.render(str(env.rank + 1) + 'x' ,1,(100,100,100))
    rank_width = rank.get_width()
    rank_height = rank.get_height()
    screen.blit(rank,  ( (width - rank_width)/2,height-90))
    ########################################################################################################


    pygame.display.flip()

#####################SCORE SCREEN####################################
Score_Screen = True
f = open('highscore.txt', 'r+')
hs = int(f.read())
if(env.points > hs):
	g = open('highscore.txt.tmp', 'w')
	g.write(str(env.points))
	f.close()
	g.close()
	os.remove('highscore.txt')
	os.renames('highscore.txt.tmp', 'highscore.txt')
	hs = env.points
	play_sound('yeshs.wav')
while(Score_Screen):
	screen.fill(env.colour)
	display_text('Your Score: ',48,(255,215,0),'GoodDog.otf',width/2, height/4)
	display_text(str(env.points),64,(0,0,0),'Ultra.ttf',width/2,height/4 + 40)
	display_text('High Score: ',48,(255,215,0),'GoodDog.otf',width/2, 3*height/4 )
	display_text(str(hs),64,(0,0,0),'Ultra.ttf',width/2,3*height/4 + 40)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			Score_Screen = False
		elif event.type == pygame.MOUSEBUTTONUP:
			pass
	pygame.display.flip()


    
