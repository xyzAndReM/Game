import pygame
import random
import math
import os
purple = (255,0,255)
red = (255,0,0)
blue = (0,0,255)
pygame.mixer.pre_init(44100, -16, 2, 512) # setup mixer to avoid sound lag
pygame.init()
def cos(x,y):
    return x/math.sqrt(x**2 + y**2)
def sin(x,y):
    return y/math.sqrt(x**2 + y**2)
def aim(x0,y0,xf,yf):
    X = (xf - x0)
    Y = abs(yf - y0)
    vel = [10*cos(X,Y),10*sin(X,Y)]
    return vel
def dot(a,b):
    """Produto escalar entre os vetores a e b"""
    return sum(p*q for p,q in zip(a, b))
def scalar(s,a):
    """Produto de um vetor a pelo escalar s"""
    c = []
    for i in a:
        c.append(s*i)
    return c
def add(a,b):
    """Soma entre dois vetores a e b"""
    c = []
    for i in range(len(b)):
        c.append(a[i] + b[i])
    return c
def sub(a,b):
    """Subtração entre dois vetores a e b"""
    c = []
    for i in range(len(b)):
        c.append(a[i] - b[i])
    return c
_sound_library = {}
def play_sound(path):
  global _sound_library
  sound = _sound_library.get(path)
  if sound == None:
    canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    sound = pygame.mixer.Sound(canonicalized_path)
    _sound_library[path] = sound
  sound.play()
def color_power(p1,p2):
        if (p1.colour == red and p2.colour == blue) or (p2.colour == red and p1.colour == blue):
            p1.colour = purple
            p2.colour = purple
        elif (p1.colour == purple or p2.colour == purple ):
            if (p1.colour == purple and p2.colour == purple):
                    p1.death = True
                    p2.death = True
            else:
                p1.colour = purple
                p2.colour = purple
def collide(p1, p2):
    """ Tests whether two particles overlap
        If they do, make them bounce
        i.e. update their angle, speed and position 

        Formula from https://en.wikipedia.org/wiki/Elastic_collision"""
    dv = sub(p1.vel,p2.vel)
    dx = [p1.x - p2.x, p1.y - p2.y]
    dist = dx[0]**2 + dx[1]**2
    if dist < (p1.size + p2.size)**2:
        play_sound('collision.wav')
        color_power(p1,p2)
        s = (2*p2.mass)*dot(dv,dx)/(dot(dx,dx)*(p2.mass+p1.mass))
        k = scalar(s,dx)
        p1.vel = sub(p1.vel,k)
        k = scalar(p1.mass/p2.mass,k)
        p2.vel = add(p2.vel,k)
        tangent = math.atan2(dx[1],dx[0])
        angle = 0.5 * math.pi + tangent
        p1.x += 2*math.sin(angle)
        p1.y -= 2*math.cos(angle)
        p2.x -= 2*math.sin(angle)
        p2.y += 2*math.cos(angle)
def get_rank(n):
    """Atribui rank apartir do numero de pops"""
    k = int(n/3)
    if k > 4:
        k = 4
    elif k < 0:
        k = 0
    return k

class Particle():
    """ A circular object with a velocity, size and mass """
    def __init__(self,x,y,size):
        self.x = x #Coordenada x
        self.y = y #Coordenada y
        self.size = size #Tamanho da particula
        self.colour = (0, 0, 255) #Cor da particula
        self.thickness = 0
        self.vel = [0,0] #Velocidade da particula em coordenadas cartesianas
        self.mass = 1 #Massa da partícula
        self.protect = 180 #Segundos até destruição (180/FPS)
        self.death = False #Indica se a bolha irá morrer, isto ocorre caso duas bolhas roxas colidam entre si

    def move(self):
        self.x += self.vel[0]#Movimento na coordenada x
        self.y -= self.vel[1]#Movimento na coordenada y

class Environment:
    def __init__(self, width, height):
        self.width = width #Largura da tela
        self.height = height #Altura da tela
        self.particles = [] #Lista das particulas
        self.colour = (255,255,255) #Cor do background
        self.points = 0 #Pontos acumulados
        self.pops = 0 #Numero de bolhas estoradas atual
        self.rank = 0 #Ranking, decidido pela função get_rank
        self.messages = ['','Cacthy!', 'Ballistick!', 'Awesome!!!','Sensational!!!'] #Messagens indicadoras do ranking
    def addParticles(self, n=1, **kargs):
        """ Add n particles with properties given by keyword arguments """
        for i in range(n):
            size = kargs.get('size', random.randint(10, 20))
            mass = kargs.get('mass', size*0.12)
            x = kargs.get('x', random.uniform(size, self.width-size))
            y = kargs.get('y', random.uniform(size, self.height-size))
            p = Particle(x, y, size)
            p.vel = kargs.get('vel', [random.uniform(0.5,1),random.uniform(0.5,1)])
            p.colour = kargs.get('colour', (255, 0, 0))
            self.particles.append(p)
        if(n == 1):
            return p
    def update(self):
        """  Moves particles and tests for collisions with the walls and each other """
        for i, particle in enumerate(self.particles):
            if particle.protect > 0 and particle.death == True:
                particle.protect -=1
                if particle.protect == 0 and particle.death == True:
                    self.particles.remove(particle)
                    play_sound('plof.wav')
                    self.pops +=1
                    self.rank = get_rank(self.pops)
                    self.points += (self.rank + 1)*100 
            
            particle.move()
            self.bounce(particle)
            for particle2 in self.particles[i+1:]:
                collide(particle, particle2)
    def bounce(self,particle):
        """ Tests whether a particle has hit the boundary of the environment """
        if particle.x > self.width - particle.size:
            play_sound('bounce.wav')
            particle.x = 2*(self.width - particle.size) - particle.x
            particle.vel[0] = -particle.vel[0]
        elif particle.x< particle.size:
            play_sound('bounce.wav')
            particle.x = 2*particle.size - particle.x
            particle.vel[0]= - particle.vel[0]
        if particle.y > self.height + particle.size - 150:
            if(particle.colour != blue):
                self.particles.remove(particle)
            if particle.y > self.height:
                self.particles.remove(particle)
            #particle.y = 2*(self.height - particle.size) - particle.y
            #particle.vel[1] = -particle.vel[1]
        elif particle.y < particle.size:
            play_sound('bounce.wav')
            particle.y = 2*particle.size - particle.y
            particle.vel[1] = -particle.vel[1]
        