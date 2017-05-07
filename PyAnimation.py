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
	if(angle != math.pi/2):
		r = (width-x0-size)/(15*abs(math.cos(angle)))
	else:
		r = 100
	n = r*math.cos(angle)
	m = r*math.sin(angle)
	while(yn >= 0 and yn <= height):#and xn >= 0 and xn <= width-size):
		if(xn == width-size or xn == size):
			n = -n
		yn -= m
		xn += n
		pygame.gfxdraw.filled_circle(screen, int(xn), int(yn), 1, (0,0,0))

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
	#draw_clock(screen,300,400,30+(tick%20),12,20,(0,0,0))
	draw_laser(screen,300,400,400,500,width,height)
	pygame.display.flip()"""