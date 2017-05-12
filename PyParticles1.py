import pygame
import random
import math
import os
purple = (255,0,255)
red = (255,0,0)
blue = (0,0,255)
green = (0, 200, 0)
gray = (60, 50, 50)
ice = (165, 242, 243)
FPS = 60
pygame.mixer.pre_init(44100, -16, 2, 512) # setup mixer to avoid sound lag
pygame.init()
font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 12)

def aim(x0,y0,xf,yf):
    """função que determina o vetor velocidade da bolha projétil"""
    DX = (xf - x0)
    DY = -(yf - y0)
    angle = math.atan2(DY,DX)
    vel = [10*math.cos(angle),10*math.sin(angle)]
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

def get_rank(n):
    """Atribui rank apartir do numero de pops"""
    k = int(n/20)
    if k > 4:
        k = 4
    elif k < 0:
        k = 0
    return k
class Ghost():
    """Após uma bolha ser removida um elemento da classe PLus é adicionada a uma lista no environment (chamada scores). esta lista será utilizada
    para criar efeitos de explosao e registrar os pontos obtidos na tela """
    def __init__(self,x,y,message,colour):
        self.x = x
        self.y = y
        self.endurance = 120
        self.colour = colour
        self.message = message
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
        self.damage = 0# Dano causado caso a bolha atinja o piso da tela
        self.life = 0# HP fornecida ao ser estourada
        self.shockwave = False #Marca se todas as bolhas devem explodir
        self.points = 0 #Pontos fornecidos quando a bolha explodir
        self.message = 'Ouch!'
        self.label = 'DMG'
        self.sound = 'plof.wav'
        self.freeze = 0
    def purple_rain(self):
        self.colour = purple
        self.points = 100
        self.damage = 0
        self.freeze = 0
    def chill(self):
        self.colour = ice
        self.label = 'F'
        self.sound = 'ice.wav'
        self.freeze = 1
        self.message = 'Icy!'
    def move(self):
        self.x += self.vel[0]#Movimento na coordenada x
        self.y -= self.vel[1]#Movimento na coordenada y
    def null(self):
        self.points = 0
        self.shockwave = False
        self.message = ''
        self.sound = 'plof.wav'
        self.life = 0
        self.damage = 0
class Shockwave():
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.endurance = 120
        self.colour = purple
        self.size = 0

class Environment:
    def __init__(self, width, height):
        self.width = width #Largura da tela
        self.height = height #Altura da tela
        self.particles = [] #Lista das particulas
        self.grave = []
        self.shockwaves = []
        self.colour = (255,255,255) #Cor do background
        self.points = 0 #Pontos acumulados
        self.pops = 0 #Numero de bolhas estoradas atual
        self.rank = 0 #Ranking, decidido pela função get_rank
        self.messages = ['','Cacthy!', 'Ballistick!', 'Awesome!!!','Sensational!!!'] #Messagens indicadoras do ranking
        self.hp = 3
        self.max_hp = 3
        self.freeze = 0
    def addParticles(self, n=1, **kwargs):
        """ Add n particles with properties given by keyword arguments """
        for i in range(n):
            size = kwargs.get('size', random.randint(10, 20))
            mass = kwargs.get('mass', size*0.12)
            x = kwargs.get('x', random.uniform(size, self.width-size))
            y = kwargs.get('y', random.uniform(size, self.height-size))
            p = Particle(x, y, size)
            V = kwargs.get('V', 1)
            p.vel = kwargs.get('vel', [V*random.uniform(0.3,0.8),V*random.uniform(0.5,1)])
            p.colour = kwargs.get('colour', (255, 0, 0))
            p.life = kwargs.get('life',0)
            p.damage = kwargs.get('damage',0)
            p.message =kwargs.get('message','-1 HP')
            p.label = kwargs.get('label','')
            p.sound = kwargs.get('sound','plof.wav')
            p.freeze = kwargs.get('freeze',0)
            self.particles.append(p)
        if(n == 1):
            return p
    def BubblePoP(self,particle):
        """Sets the action of bubble pop, such as sound, removing the bubble and adding the event for animation in <scores> queue.
        The variable worth determines if the bubble pop is worth points, blue bubbles popping on the ceiling are not worthy for
        example."""
        if(type(particle) is Particle and particle in self.particles):
            play_sound(particle.sound)
            colour = particle.colour
            x = particle.x
            y = particle.y

            self.pops += (particle.points > 0) - particle.damage*10 #Guardando o numero de bolas estouradas para determinar o rank, se dano eh tomado o ranking eh diminuido

            self.rank = get_rank(self.pops) #função que retorna o ranking

            self.points += (self.rank + 1)*particle.points #acumulação de pontos que depende do atual ranking
            
            if(particle.points):
                particle.message = '+' + str(int((self.rank + 1)*particle.points)) + ' pts' #alterando a pontuação fornecida por cada particula
            
            self.grave.append(Ghost(x,y,particle.message,colour)) #criando o fantasma que guarda a posição da morte das particulas, importante para as animações de morte

            if(self.hp < self.max_hp): #Recuperando vida
                self.hp += particle.life

            self.hp -= particle.damage #Recebendo dano

            self.freeze += 2*particle.freeze*FPS #Congelando a barra de carregamento

            if(self.freeze > 0 and particle.damage): #Ao receber dano congelado, o coração quebra e não pode ser mais recuperado( ANTES SOFRIA AGORA SOU FRIA)
                self.max_hp -= 1

            self.particles.remove(particle) #Remover a particula
            if(particle.colour == gray): #Se a particula é cinza criar uma onde de choque
                self.shockwaves.append(Shockwave(x,y))

    def color_power(self,p1,p2):
   # """função responsável pelas mudanças de cor na colisão entre bolhas"""
   ##################################COLISAO ENTRE AZUL E VERMELHO############################################
        if (p1.colour == red and p2.colour == blue) or (p2.colour == red and p1.colour == blue):
            p1.purple_rain()
            p2.purple_rain()
            return True #Aplicar colisao
    ###########################################################################################################
    ##################################COLISAO ENTRE AZUL E VERDE###############################################
        elif (p1.colour == green and p2.colour == blue) or (p1.colour == blue and p2.colour == green):
            if(p1.colour == green):
                self.BubblePoP(p1)
            elif(p2.colour == green):
                self.BubblePoP(p2)
            return False #Nao aplicar colisao
    ###########################################################################################################
    ##################################COLISAO ENTRE AZUL E CINZA###############################################
        elif (p1.colour == gray and p2.colour == blue) or (p1.colour == blue and p2.colour == gray):
            if(p1.colour == gray):
                self.BubblePoP(p1)
            elif(p2.colour == gray):
                self.BubblePoP(p2)
            return False #Nao aplicar colisao
    ############################################################################################################
    ###################################COLISAO ENTRE ROXOS######################################################
        elif (p1.colour == purple or p2.colour == purple ):
            if (p1.colour == purple and p2.colour == purple):
                p1.death = True
                p2.death = True
            elif(p1.colour == red or p2.colour == red ):
                p1.purple_rain()
                p2.purple_rain()
            elif(p1.colour == ice or p2.colour == ice):
                p1.purple_rain()
                p2.purple_rain()
            return True #Aplicar colisao
    #############################################################################################################
    ##################################COLISAO ENTRE GELO E AZUL##################################################
        elif(p1.colour == ice and p2.colour == blue) or (p2.colour == ice and p1.colour == blue):
            if(p1.colour == ice):
                p1.damage = 0
                self.BubblePoP(p1)
            elif(p2.colour == ice):
                p2.damage = 0
                self.BubblePoP(p2)
            return False #Aplicar colisao
    ###############################################################################################################
    ##################################COLISAO ENTRE GELO E VERMELHO################################################
        elif(p1.colour == ice and p2.colour == red) or (p2.colour == ice and p1.colour == red):
            if(p1.colour == red):
                p1.chill()
            elif(p2.colour == red):
                p2.chill()
            return False
        return True
    def collide(self,p1, p2):
        """ Tests whether two particles overlap
            If they do, make them bounce
            i.e. update their angle, speed and position 

            Formula from https://en.wikipedia.org/wiki/Elastic_collision"""
        dv = sub(p1.vel,p2.vel)
        dx = [p1.x - p2.x, p1.y - p2.y]
        dist = dx[0]**2 + dx[1]**2
        if dist < (p1.size + p2.size)**2:
            play_sound('collision.wav')
            impact = self.color_power(p1,p2)
            if(impact):
                divisor = dot(dx,dx)
                if(not divisor):
                    s = 1
                else:
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
    def shockwave_collide(self,p1,p2):
        dx = [p1.x - p2.x, p1.y - p2.y]
        dist = dx[0]**2 + dx[1]**2
        if dist < (p1.size + p2.size)**2:
            if(p1.colour == red or p1.colour == ice):
                p1.purple_rain()
            if(  p1.colour != blue):
                self.BubblePoP(p1)


    def update(self):
        """  Moves particles and tests for collisions with the walls and each other """
        if(self.freeze > 0):
            self.freeze -=1 
        for i, particle in enumerate(self.particles):
            if (particle.protect > 0 and particle.death == True):
                particle.protect -=1
                if (particle.protect == 0 and particle.death == True):
                    self.BubblePoP(particle)
            for shock in self.shockwaves:
                if(particle):
                    self.shockwave_collide(particle,shock)

            particle.move()
            self.bounce(particle)
            for particle2 in self.particles[i+1:]:
                self.collide(particle, particle2)
            
    def bounce(self,particle):
        """ Tests whether a particle has hit the boundary of the environment AND sets the path for actions involving crossing the vertical borders """
        if particle.x > self.width - particle.size:
            """Particle hit the right boundary"""
            play_sound('bounce.wav')
            particle.x = 2*(self.width - particle.size) - particle.x
            particle.vel[0] = -particle.vel[0]
        elif particle.x< particle.size:
            """Particle hit the left boundary"""
            play_sound('bounce.wav')
            particle.x = 2*particle.size - particle.x
            particle.vel[0]= - particle.vel[0]
        if particle.y > self.height -60 -particle.size:
            """Particle hit the bottom boundary"""
            if (particle.colour == purple or particle.colour == red or particle.colour == ice):
                self.BubblePoP(particle)
                if (particle.colour == red or particle.colour == ice):
                    play_sound('hit.wav')
            elif(particle.colour != blue):
                particle.y = 2*(self.height - 60 - particle.size) -particle.y
                particle.vel[1] = -particle.vel[1]

        elif particle.y < particle.size:
            """Particle hit the top boundary"""
            if(particle.colour == blue):
                self.BubblePoP(particle)
            else:
                play_sound('bounce.wav')
                particle.y = 2*particle.size - particle.y
                particle.vel[1] = -particle.vel[1]
