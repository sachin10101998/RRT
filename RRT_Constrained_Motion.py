import math, sys, pygame, random
from math import *
from pygame import *

class Node(object):
    def __init__(self, point, parent):
        super(Node, self).__init__()
        self.point = point
        self.parent = parent
        self.cost=0

#20*15
level1 = ["xxx.xxxxxxxxxxxxxxxx",
          "xs.....x............",
          "xxxx.........xx....x",
          "x......x....x.x....x",
          "x......x......x....x",
          "x......x......x....x",
          "x...xxxxxxxx..x....x",
          "x......x...........x",
          "x.............xxxxxx",
          "xxxxxx.x...........x",
          "x......x.xxx.......x",
          "x......x...........x",
          "x..........xxx..xxxx",
          "x..........x......nx",
          "xxxxxxxxxxxxxxxxxxxx"]

level2 = ["xxx.xxxxxxxxxxxxxxxx",
          "x......xxxxxx.......",
          "x......xxxxxx......x",
          "x......xxxxxx.x....x",
          "x......xxxxxx.x....x",
          "x......xxxxxx.x....x",
          "x..................x",
          "x......xxxxxx......x",
          "x......xxxxxx.xxxxxx",
          "xxxxxx.xxxxxx......x",
          "x......xxxxxx......x",
          "x......xxxxxx......x",
          "x......xxxxxx...xxxx",
          "x......xxxxxx.....xx",
          "xxxxxxxxxxxxxxxxxxxx"]

XDIM = 800
YDIM = 600
windowSize = [XDIM, YDIM]
delta = 10.0
GAME_LEVEL = 1
GOAL_RADIUS = 10
MIN_DISTANCE_TO_ADD = 1.0
NUMNODES = 5000
pygame.init()
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode(windowSize)
screenrect = screen.get_rect()
white = 255, 255, 255
black = 0, 0, 0
red = 255, 0, 0
blue = 0, 0, 255
green = 0, 255, 0
cyan = 0,105,180

count = 0
rectObs = []


def dist(p1,p2):    #distance between two points
    return sqrt((p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1]))

def point_circle_collision(p1, p2, radius):
    distance = dist(p1,p2)
    if (distance <= radius):
        return True
    return False

def step_from_to(p1,p2):
    if dist(p1,p2) < delta:
        if(p1[0]==p2[0]):
            return (p1[0],p2[1])
        else:
            return (p2[0],p1[1])
    else:
        theta = atan2(p2[1]-p1[1],p2[0]-p1[0])
        if (theta>2.35):
            theta=3.14
        elif(theta>.785):
            theta=1.57
        elif(theta>-.785):
            theta=-0
        elif(theta>-2.35):
            theta=-1.57
        else:
            theta=-3.14
        return p1[0] + delta*cos(theta), p1[1] + delta*sin(theta)
        
def collides(p):    #check if point collides with the obstacle
    for rect in rectObs:
        if rect.collidepoint(p) == True:
            return True
    return False

def get_random_clear():
    while True:
        p = random.random()*XDIM, random.random()*YDIM
        noCollision = collides(p)
        if noCollision == False:
            return p

def init_obstacles(level):  
    global rectObs
    rectObs = []

    lines = len(level)
    columns = len(level[0])

    length = screenrect.width / columns
    height = screenrect.height / lines

    for yi in range(lines):
        for xi in range(columns):
            if level[yi][xi] == 'x': # wall
                rectObs.append(pygame.Rect((length * xi, height * yi),(length,height)))

    for rect in rectObs:
        pygame.draw.rect(screen, black, rect)

def reset():
    global count
    screen.fill(white)
    init_obstacles(level1)
    count = 0

def main():
    global count
    
    initPoseSet = False
    initialPoint = Node(None, None)
    goalPoseSet = False
    goalPoint = Node(None, None)
    currentState = 'init'

    nodes = []
    reset()

    while True:
        if currentState == 'init':
            #print('goal point not yet set')
            pygame.display.set_caption('Select Starting Point and then Goal Point')
            fpsClock.tick(10)
        elif currentState == 'goalFound':
            currNode = goalNode
            pygame.display.set_caption('Goal Reached')
            while currNode.parent != None:
                pygame.draw.line(screen,red,currNode.point,currNode.parent.point,2)
                currNode = currNode.parent
            optimizePhase = True
        elif currentState == 'optimize':
            fpsClock.tick(0.5)
            pass
        elif currentState == 'buildTree':
            count = count+1
            pygame.display.set_caption('Performing RRT')
            if count < NUMNODES:
                foundNext = False
                while foundNext == False:
                    rand = get_random_clear()
                    parentNode = nodes[0]
                    for p in nodes:
                        if dist(p.point,rand) <= dist(parentNode.point,rand):
                            newPoint = step_from_to(p.point,rand)
                            if collides(newPoint) == False:
                                parentNode = p
                                foundNext = True

                newnode = step_from_to(parentNode.point,rand)
                newnode1 = Node(newnode, parentNode)
                newnode1.cost=parentNode.cost+delta
                nodes.append(newnode1)
                pygame.draw.line(screen,cyan,parentNode.point,newnode)

                if point_circle_collision(newnode, goalPoint.point, GOAL_RADIUS):
                    currentState = 'goalFound'
                    goalNode = nodes[len(nodes)-1]
                    print('goalFound','cost = ',goalNode.cost)
            else:
                print("Ran out of nodes... :(")
                return;

        #handle events
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                sys.exit("Exiting")
            if e.type == MOUSEBUTTONDOWN:
                #print('mouse down')
                if currentState == 'init':
                    if initPoseSet == False:
                        nodes = []
                        if collides(e.pos) == False:
                            print('initiale point set: '+str(e.pos))
                            initialPoint = Node(e.pos, None)
                            nodes.append(initialPoint) # Start in the center
                            initPoseSet = True
                            pygame.draw.circle(screen, red, initialPoint.point, GOAL_RADIUS)
                    elif goalPoseSet == False:
                        print('goal point set: '+str(e.pos))
                        if collides(e.pos) == False:
                            goalPoint = Node(e.pos,None)
                            goalPoseSet = True
                            pygame.draw.circle(screen, blue, goalPoint.point, GOAL_RADIUS)
                            currentState = 'buildTree'
                else:
                    currentState = 'init'
                    initPoseSet = False
                    goalPoseSet = False
                    reset()

        pygame.display.update()
        fpsClock.tick(10000)



if __name__ == '__main__':
    main()
    






