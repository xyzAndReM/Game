import pygame
import math
from pygame.locals import *
import pygame.gfxdraw
def draw_clock(screen,x0,y0,size,n,r,color):
	"""Função responsavel por desenhar os efeitos de explosao"""
	for i in range(n+1):
		angle = i*2*math.pi/n
		x1 = int(x0 +  (size+5)*math.cos(angle))
		y1 = int(y0 +  (size+5)*math.sin(angle))
		x2 =int(x1 +  r*math.cos(angle))
		y2 =int(y1 +  r*math.sin(angle))
		pygame.gfxdraw.line(screen,x1,y1,x2,y2,color)
def draw_laser(screen,x0,y0,x1,y1,width,height,size):
	"""Função responsável por desenhar a mira laser"""
	DX = (x1 - x0)
	DY = -(y1 - y0)
	angle = math.atan2(DY,DX)
	xn = x0
	yn = y0
	flag = 1
	if(angle != math.pi/2 and angle != -math.pi/2):
		r = (width-x0-size)/(15*abs(math.cos(angle)))
	else:
		r = 50
	n = r*math.cos(angle)
	m = r*math.sin(angle)
	while(yn >= 0 and yn <= height):#and xn >= 0 and xn <= width-size):
		if(xn == width-size or xn == size):
			n = -n
		yn -= m
		xn += n
		pygame.gfxdraw.filled_circle(screen, int(xn), int(yn), 1, (0,0,0))
def draw_heart(screen,x0,y0,color,r,full):
	H = []
	for i in range(1001):
		t = 2*i*math.pi/1000
		H.append( (r*(16*math.sin(t)**3) + x0, -(r*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))) + y0))
	pygame.gfxdraw.aapolygon(screen,H,color)
	if(full):
		pygame.gfxdraw.filled_polygon(screen,H,color)
def draw_lifebar(screen,x0,y0,color,r,HP):
	for i in range(3):
		if(HP > i):
			full = True
		else:
			full = False
		draw_heart(screen,x0+50*i,y0,color,r,full)
def draw_rects(screen,width,x0,y0,l,h,color):
	x1 = x0-l
	y1 = y0-h/2
	#ygame.pydraw.rectangle(screen,( (x1,y1),(y1,y2) ), color  )
	pygame.draw.rect(screen, color,  [(x1,y1),(l,h)], 0)
	x1 = width-x0
	y1 = y0-h/2
	pygame.draw.rect(screen, color,  [(x1,y1),(l,h)], 0)
def draw_bullet_bar(screen,x0,y0,l,L,h,color):
	pygame.draw.rect(screen, color,  [(x0,y0),(L,h)], 3)
	pygame.draw.rect(screen, color,  [(x0,y0),(l,h)], 0)

"""bgcolor = (255,255,255)
pygame.init()
pygame.display.set_caption('Bubble Shock')
(width, height) = (600, 800)
running = True
screen = pygame.display.set_mode((width, height))
tick = 0
while running:
	pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, height-120),5)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	screen.fill(bgcolor)
	tick +=1
	pygame.gfxdraw.filled_circle(screen, 300, 400, 1, (0,0,0))  # draw filled circle
	pygame.gfxdraw.aacircle(screen, 300, 400, 30, (0,0,0)) 
	pygame.gfxdraw.rectangle(screen,( (305,10),(20,20) ), (0,0,0)  )
	draw_rects(screen,600,100,500,40,20,(0,0,0))
	#draw_clock(screen,300,400,30+(tick%20),12,20,(0,0,0))
	#draw_laser(screen,300,400,400,500,width,height)
	pygame.display.flip()"""