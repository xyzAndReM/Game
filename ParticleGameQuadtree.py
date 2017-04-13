import pygame, random, math, sys

#Colors   R    G   B
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
FUCHSIA = (255, 0, 255)
GRAY = (128, 128, 128)
LIME = (0, 128, 0)
MAROON = (128, 0, 0)
NAVYBLUE = (0, 0, 128)
OLIVE = (128, 128, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
SILVER = (192, 192, 192)
TEAL = (0, 128, 128)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
CYAN = (0, 255, 255)

pygame.init()#pygame init method
BGCOLOR = BLUE
(DISPLAYWIDTH, DISPLAYHEIGHT) = (800, 500)
DISPLAYSURF = pygame.display.set_mode((DISPLAYWIDTH, DISPLAYHEIGHT))#create pygame display surface with width and height
FPS = 30
FPSCLOCK = pygame.time.Clock()#create fps clock to limit game speed to 30FPS
pygame.display.set_caption("A Great Game!")

mass_of_air = 0.2
elasticity = 0.75
gravity = (math.pi, 0.5)#vector quantity of gravity with (direction, magnitude)
number_of_particles = 500#number of particles in game
displayTree = False#boolean to display quadtree boxes behind particles

def addVectors((angle1, length1), (angle2, length2)):
    '''Adds two vectors of (direction, magnitude) and returns vector'''
    x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y  = math.cos(angle1) * length1 + math.cos(angle2) * length2
    
    angle = 0.5 * math.pi - math.atan2(y, x)
    length  = math.hypot(x, y)

    return (angle, length)

def rect_quad_split(rect):
    '''Splits rect object into four smaller rect objects'''
    w=rect.width/2.0
    h=rect.height/2.0
    rl=[]
    rl.append(pygame.Rect(rect.left, rect.top, w, h))
    rl.append(pygame.Rect(rect.left+w, rect.top, w, h))
    rl.append(pygame.Rect(rect.left, rect.top+h, w, h))
    rl.append(pygame.Rect(rect.left+w, rect.top+h, w, h))
    return rl

def findParticle(particles, x, y):
    '''Checks if x and y coordinates are inside particle in particles list'''
    for p in particles:
        if math.hypot(p.x-x, p.y-y) <= p.radius:
            return p
    return None

def collide(p1, p2):
    '''Tests if two particles collide and changes their speed and direction'''
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    
    dist = math.hypot(dx, dy)
    if dist < p1.radius + p2.radius:
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        total_mass = p1.mass + p2.mass
        (p1.angle, p1.speed) = addVectors((p1.angle, p1.speed*(p1.mass-p2.mass)/total_mass), (angle, 2*p2.speed*p2.mass/total_mass))
        (p2.angle, p2.speed) = addVectors((p2.angle, p2.speed*(p2.mass-p1.mass)/total_mass), (angle+math.pi, 2*p1.speed*p1.mass/total_mass))
        p1.speed *= elasticity
        p2.speed *= elasticity

        overlap = 0.5*(p1.radius + p2.radius - dist+1)
        p1.x += math.sin(angle)*overlap
        p1.y -= math.cos(angle)*overlap
        p2.x -= math.sin(angle)*overlap
        p2.y += math.cos(angle)*overlap

class Particle():
    def __init__(self, (x, y), radius, mass=1):
        '''A particle at coordinates (x,y) represented by a circle with mass'''
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (0, 0, 255)
        self.thickness = 0
        self.speed = 0#magnitude of velocity vector
        self.angle = 0#direction of velocity vector
        self.mass = mass
        self.drag = (self.mass/(self.mass + mass_of_air)) ** self.radius
        self.set_rect()#sets particle rect for collision testing with quadtree boxes

    def get_rect(self):
        '''Returns particle rect object'''
        return self.rect

    def set_rect(self):
        '''Sets particle rect object at current coordinates with side length 2*radius'''
        self.rect = pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)

    def display(self):
        '''Draws particle onto DISPLAYSURF'''
        pygame.draw.circle(DISPLAYSURF, self.color, (int(self.x), int(self.y)), self.radius, self.thickness)

    def move(self):
        '''Adds gravity and particle movement vectors and then moves particle'''
        (self.angle, self.speed) = addVectors((self.angle, self.speed), gravity)
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed
        self.speed *= self.drag

    def bounce(self):
        '''Tests for wall collisions and changes particle velocity accordingly'''
        if self.x > DISPLAYWIDTH - self.radius:
            self.x = 2*(DISPLAYWIDTH - self.radius) - self.x
            self.angle = - self.angle
            self.speed *= elasticity

        elif self.x < self.radius:
            self.x = 2*self.radius - self.x
            self.angle = - self.angle
            self.speed *= elasticity

        if self.y > DISPLAYHEIGHT - self.radius:
            self.y = 2*(DISPLAYHEIGHT - self.radius) - self.y
            self.angle = math.pi - self.angle
            self.speed *= elasticity

        elif self.y < self.radius:
            self.y = 2*self.radius - self.y
            self.angle = math.pi - self.angle
            self.speed *= elasticity

class Quadtree(object):
    def __init__(self, level, rect, particles=[], color = (0,0,0)):
        '''Quadtree box at with a current level, rect, list of particles, and color(if displayed)
        level: set to zero for "trunk" of quadtree
        rect: should be entire display for "trunk" of quadtree
        particles: list of all particles for collision testing'''
        self.maxlevel = 4#max number of subdivisions
        self.level = level#current level of subdivision
        self.maxparticles = 3#max number of particles without subdivision
        self.rect = rect#pygame rect object
        self.particles = particles#list of particles
        self.color = color#color of box if displayed
        self.branches = []#empty list that is filled with four branches if subdivided

    def get_rect(self):
        '''Returns quadtree rect object'''
        return self.rect

    def subdivide(self):
        '''Subdivides quadtree into four branches'''
        for rect in rect_quad_split(self.rect):
            branch = Quadtree(self.level+1, rect, [], (self.color[0]+30,self.color[1],self.color[2]))
            self.branches.append(branch)

    def add_particle(self, particle):
        '''Adds a particle to the list of particles inside quadtree box'''
        self.particles.append(particle)

    def subdivide_particles(self):
        '''Subdivides list of particles in current box to four branch boxes'''
        for particle in self.particles:
            for branch in self.branches:
                if branch.get_rect().colliderect(particle.get_rect()):
                    branch.add_particle(particle)

    def render(self, display):
        '''Displays quadtree box on the display surface given'''
        pygame.draw.rect(display, self.color, self.rect)

    def test_collisions(self):
        '''Tests for collisions between all particles in the particle list'''
        for i, particle in enumerate(self.particles):
            for particle2 in self.particles[i+1:]:
                collide(particle, particle2)
            
    def update(self, display):
        '''Updates the quadtree and begins recursive process of subdividing or collision testing'''
        if len(self.particles) > self.maxparticles and self.level <= self.maxlevel:
            self.subdivide()
            self.subdivide_particles()
            for branch in self.branches:
                branch.update(display)
        else:
            self.test_collisions()
            if displayTree:
                self.render(display)

        
my_particles = []

for n in range(number_of_particles):#creates particles and adds them to my_particles
    radius = random.randint(5, 10)#each particle has random radius, density, and coordinates
    density = random.randint(1, 20)
    x = random.randint(radius, DISPLAYWIDTH-radius)
    y = random.randint(radius, DISPLAYHEIGHT-radius)

    particle = Particle((x, y), radius, density*radius**2)#instance of particle class
    particle.color = (255, 0, 200-density*10)#changes particle color
    particle.speed = random.random()#gives particle random velocity (direction, magnitude)
    particle.angle = random.uniform(0, math.pi*2)

    my_particles.append(particle)#adds particle to list

selected_particle = None
while True:#game loop
    for event in pygame.event.get():#event loop checking for mouse click and exit
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle = findParticle(my_particles, mouseX, mouseY)
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_particle = None

    if selected_particle:#if mouse click on particle, particle follows mouse 
        (mouseX, mouseY) = pygame.mouse.get_pos()
        dx = mouseX - selected_particle.x
        dy = mouseY - selected_particle.y
        selected_particle.angle = 0.5*math.pi + math.atan2(dy, dx)
        selected_particle.speed = math.hypot(dx, dy) * 0.1

    DISPLAYSURF.fill(BGCOLOR)#fill background with BGCOLOR

    tree = Quadtree(0, pygame.Rect(0,0,DISPLAYWIDTH,DISPLAYHEIGHT), my_particles)#creates trunk of quadtree
    tree.update(DISPLAYSURF)#updates trunk and begins recursive process for collision testing

    for particle in my_particles:#display, move, bounce, and set_rect for particles
        particle.display()
        particle.move()
        particle.bounce()
        particle.set_rect()
        
    FPSCLOCK.tick(FPS)#limit game speed with FPS clock
    pygame.display.update()#update display for user
