
import math, sys, pygame, random
from math import *
from pygame import *

class Node(object):
    def __init__(self, point, parent):
        super(Node, self).__init__()
        self.point = point
        self.parent = parent
        self.cost=0

#15*20
level1 = ["xxxxxxxxxxxxxxxxxxxx",
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
          "x......xx.xxx......x",
          "x......xx.xxx.xxxxxx",
          "xxxxxx.xx.xxx......x",
          "x......xx..........x",
          "x......xxxxxx......x",
          "x......xxxxxx...xxxx",
          "x......xxxxxx.....xx",
          "xxxxxxxxxxxxxxxxxxxx"]

XDIM = 800
YDIM = 600
windowSize = [XDIM, YDIM]
delta = 20.0
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
rectObs1 =[]


def dist(p1,p2):    #distance between two points
    return sqrt((p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1]))

def point_circle_collision(p1, p2, radius):
    distance = dist(p1,p2)
    if (distance <= radius):
        return True
    return False

def step_from_to(p1,p2):
    if dist(p1,p2) < delta:
        return p2
    else:
        theta = atan2(p2[1]-p1[1],p2[0]-p1[0])
        return p1[0] + delta*cos(theta), p1[1] + delta*sin(theta)

def point_in_polygon(p, vertices):
    # If the point is a vertex, it's in the polygon
    if tuple(p) in (tuple(i) for i in vertices):
        return True

    xs = [i[0] for i in vertices]
    ys = [i[1] for i in vertices]
    # if the point is outside of the polygon's bounding
    # box, it's not in the polygon
    if ((p[0] > max(*xs) or p[0] < min(*xs)) or (p[1] > max(*ys) or p[1] < min(*ys))):
        return False

    p1 = vertices[-1] # Start with first and last vertices
    count = 0
    for p2 in vertices:
        # Check if point is between lines y=p1[1] and y=p2[1]
        if p[1] <= max(p1[1], p2[1]) and p[1] >= min(p1[1], p2[1]):
            # Get the intersection with the line that passes
            # through p1 and p2
            x_inters = float(p2[0]-p1[0])*float(p[1]-p1[1])/float(p2[1]-p1[1])+p1[0]

            # If p[0] is less than or equal to x_inters,
            # we have an intersection
            if p[0] <= x_inters:
                count += 1
        p1 = p2

    # If the intersections are even, the point is outside of
    # the polygon.
    return count % 2 != 0

def collides(p):    #check if point collides with the obstacle
    for vertices in rectObs:
        if (point_in_polygon(tuple(sum(x) for x in zip(p,(0,-5))),vertices) or point_in_polygon(tuple(sum(x) for x in zip(p,(0,5))),vertices) \
         or point_in_polygon(tuple(sum(x) for x in zip(p,(5,0))),vertices) or point_in_polygon(tuple(sum(x) for x in zip(p,(5,0))),vertices)) == True:
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
    print(lines,columns)
    for yi in range(lines):
        for xi in range(columns):
            if level[yi][xi] == 'x': # wall
                if yi==0 or xi==0:
                    vertices=[]
                    vertices.append((length * xi, height * yi))
                    vertices.append((length * (xi+1), height * yi))
                    vertices.append((length * (xi+1), height * (yi+1)))
                    vertices.append((length * xi, height * (yi+1)))
                    rectObs.append(vertices)
                else:
                    vertices=[]
                    vertices.append((length * xi - 10, height * yi - 6))
                    vertices.append((length * xi, height * yi - 12))
                    vertices.append((length * (xi+1), height * yi - 12))
                    vertices.append((length * (xi+1), height * (yi+1)))
                    vertices.append((length * xi, height * (yi+1)))
                    vertices.append((length * xi - 10, height * (yi+1) - 6 ))
                    rectObs.append(vertices)
                vertices=[]
                vertices.append((length * xi, height * yi))
                vertices.append((length * (xi+1), height * yi))
                vertices.append((length * (xi+1), height * (yi+1)))
                vertices.append((length * xi, height * (yi+1)))
                rectObs1.append(vertices)


    for rect in rectObs:
        pygame.draw.polygon(screen, black, rect)


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
            currNode = goalNode.parent
            pygame.display.set_caption('Goal Reached')
            #print ("Goal Reached")

            
            while currNode.parent != None:
                pygame.draw.line(screen,red,currNode.point,currNode.parent.point)
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
                    if(count%20==0):
                        rand = goalPoint.point
                    else:
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
    






