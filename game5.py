import pygame
import PyParticles
import PyAnimation
import time
import os
from sys import exit
from pygame.locals import *
import pygame.gfxdraw
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
def null_bubble(p):
	p.points = 0
	p.shockwave = False
	p.message = ''
	p.sound = 'plof.wav'
	p.life = 0
	p.damage = 0

pygame.mixer.pre_init(44100, -16, 2, 512) # setup mixer to avoid sound lag
pygame.init()
pygame.display.set_caption('Bubble Shock')
(width, height) = (600, 700)
x0 = width/2
y0 = height
FPS = 60



screen = pygame.display.set_mode((width, height))
env = PyParticles.Environment(width, height)

#Load de musicas#
pygame.mixer.music.load('main.mp3')
#-----------------------------------

#Ticks-----------------------
ticks_to_particles = 240 #Se refere ao intervalo de tempo necessário para surgirem novas particulas, t = ticks_to_particles/fps
ticks_to_bullet = 0 #Se refere ao intervalo de tempo necessário para carregar a arma de bolha novamente
ticks_to_bonus = 240
ticks_to_bomb = 240
rankup_ticks = 0
ticks_pop = 0
ticks_gameover = 0
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

###############Looping principal###############################################################
while running:

    dt = clock.tick(FPS)
    #####################Queda dos meteoros####################
    if not ticks_to_particles:
        ticks_to_particles = 240
        env.addParticles(2,y = 0, damage = 1)
    else:
        ticks_to_particles -= 1
    ###########################################################

    ######################Queda dos bônus######################
    if not ticks_to_bonus:
        bonus = env.addParticles(0,y = 0, colour = (0,200,0), life = 1, message = '+1 HP', label = 'HP', sound = 'life.wav')
        ticks_to_bonus = 720
    else:
        ticks_to_bonus -= 1
    ############################################################
        
    ######################Queda das bombas######################
    if not ticks_to_bomb:
        bomb = env.addParticles(0,y = 0, colour = (60,50,50),message = 'KABOOM !',label = 'TNT', sound = 'destroyed.wav')
        ticks_to_bomb = 1200
    else:
        ticks_to_bomb -= 1
    ############################################################    

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
                ticks_to_bullet = 180 
    ###################################################################
    env.update()
    screen.fill(env.colour)
    text = GAME_HP_font.render("HP: {0}".format(env.hp), 1, (0, 255, 0))
    screen.blit(text, (width - 90, 10))

    ###########################################GAMEOVER##########################################
    if (not env.hp): 
    	for p in env.particles:
    		null_bubble(p)
    		env.BubblePoP(p)
  
    	pygame.mixer.music.pause()
    	if(ticks_gameover >= 120):
    		if(ticks_gameover == 120):
    			play_sound('clear.wav')
    		display_text('Game Set',32,(153,0,0),'sensational.ttf',width/2, (height-200)/2)
    	if(ticks_gameover >= 360):
    		running = False
    	ticks_gameover += 1
    ##################################################################################################	
    	
    
    ########################Mira Laser###############################
    [xl,yl] = pygame.mouse.get_pos()
    PyAnimation.draw_laser(screen,x0,y0,xl,yl,width,height,15)
    PyAnimation.draw_lifebar(screen,475,height - 25,(255,105,180),0.75,env.hp)
    ########################MIra Laser - END########################
    
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, height-60),5) # Desenho das bordas
    
    
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
    score_height = score.get_height()
     #Mostra o score
    if(env.rank > UP or rankup_animation):
    	#print(env.rank)
    	#print(rankup_ticks)
    	if( not rankup_animation ):
    		print('oi')
    		rankup_animation = True
    	elif(rankup_animation):
	    	rankup_ticks += 1
	    	P = int(14*rankup_ticks)
	    	#print('P = ' + str(P))
	    	PyAnimation.draw_rects(screen,width,P,(height-200)/2,80,30,(255,140,0))
	    	if(P >= width/2 and P <= 6*width/2 ):
	    		rankup = rank_font.render(env.messages[env.rank],1,(255,140,0))
	    		rankup_width = rankup.get_width()
	    		rankup_height = rankup.get_height()
	    		screen.blit(rankup,  ( (width - rankup_width)/2,(height-200-rankup_height)/2 ))
	    	elif(P > 6*width/2):
	    		#print('oi')
	    		rankup_animation = False
	    		rankup_ticks = 0



    	
    	#playsound
    UP = env.rank
    rank = game_font.render(str(env.rank + 1) + 'x' ,1,(100,100,100))
    rank_width = rank.get_width()
    rank_height = rank.get_height()
    screen.blit(score, ( (width - score_width)/2,height-60))
    screen.blit(rank,  ( (width - rank_width)/2,height-90))



    pygame.display.flip()

#####################SCORE SCREEN####################################



f = open('highscore.txt', 'w')
f.write(str(env.points))  # python will convert \n to os.linesep
f.close()


    
