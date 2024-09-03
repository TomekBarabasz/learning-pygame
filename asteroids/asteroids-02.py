import pygame
from pygame.gfxdraw import aacircle,filled_circle,line,filled_polygon
import argparse
import random
import math
from datetime import datetime
import numpy as np

def got_quit_event(events):
    for event in events:
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.unicode == 'q':
                return True
    return False
  
def rotate(angle, Points):
    rad = math.radians(angle)
    c = math.cos(rad)
    s = math.sin(rad)
    ROT = np.array([c,-s, s, c]).reshape(2,2)
    return ROT.dot(np.array(Points).T).T

def move(dt,Points):
    return np.array(Points)+dt

def rotMove(angle,dt,Points):
    rad = math.radians(angle)
    c = math.cos(rad)
    s = math.sin(rad)
    ROT = np.array([c,-s, s, c]).reshape(2,2)
    return move(dt,ROT.dot(np.array(Points).T).T)

def drawShip(screen,events,state,wrap):
    S=15
    ACCEL = 0.01
    ROT_SPEED = 1
    FIRE_SPEED = 5
    x,y,angle,vx,vy,is_accel = state
    x,y = wrap(x+vx,y+vy)
    rad = math.radians(angle+90)
    dirx = math.cos(rad)
    diry = math.sin(rad)
    fire = False
    for event in events:
        if event.type == pygame.MOUSEMOTION:
            angle += event.rel[0] * ROT_SPEED
            if angle > 360: angle -= 360
            elif angle < 0: angle += 360
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                fire = True
            elif event.button == 1:
                is_accel = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_accel = False
    
    Points = [(-S,-S),(0,2*S),(S,-S)]
    ToDraw = rotMove(angle, (x,y), Points)
    filled_polygon(screen, ToDraw, (72,54,107))

    if is_accel:
        vx += ACCEL*dirx
        vy += ACCEL*diry
        Points = [(-S,-S),(S,-S),(0,-2*S)]
        ToDraw = rotMove(angle, (x,y),Points)
        filled_polygon(screen, ToDraw, (255,0,0))

    missiles = [(x+dirx*2*S,y+diry*2*S,dirx*FIRE_SPEED,diry*FIRE_SPEED,datetime.utcnow())] if fire else []
    return (x,y,angle,vx,vy,is_accel),missiles

def drawMissiles(screen, Missiles, wrap):
    SIZE = 2
    VALID_TIME = 1
    tm = datetime.utcnow()
    color = (196,121,23)
    #Missiles = filter(lambda m: (tm-m[4]).total_seconds()<VALID_TIME, Missiles)
    ValidMissiles = []
    for m in Missiles:
        x,y,vx,vy,t0 = m
        if (tm-t0).total_seconds() < VALID_TIME:
            x,y = wrap(x+vx,y+vy)
            filled_circle(screen, round(x),round(y), SIZE, color)
            ValidMissiles.append( (x,y,vx,vy,t0))
    return ValidMissiles

def makeWrap(width,height):
    def wrap(x,y):
        if x < 0: x = width
        elif x > width: x=0
        if y < 0: y = height
        elif y > height: y=0
        return x,y
    return wrap

def main(Args):
    screen_size = width,height = tuple(map(int, Args.display.split(',')))
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    if Args.fullscreen:
        pygame.display.toggle_fullscreen()
    else:
        pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    background=0,0,0
    state = width//2,height//2, 0, 0, 0, False
    Missiles = []
    wrap = makeWrap(width,height)
    while True:
        t0 = datetime.utcnow()
        events = pygame.event.get()
        if got_quit_event(events):
            break
        screen.fill(background)
        state,missiles = drawShip(screen,events,state,wrap)
        Missiles.extend(missiles)
        Missiles = drawMissiles(screen, Missiles, wrap)
        pygame.display.flip()
        t1 = datetime.utcnow()
    
    pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="gra asteroids")
    parser.add_argument("-test", action='store_true', help='execute unittests')
    parser.add_argument("-display","-d",type=str, default="1280,1024", help="screen size width,height")
    parser.add_argument("-fullscreen","-f",action='store_true', help="run in fullscreen mode")
    Args = parser.parse_args()
    if Args.test:
        unittest.main(argv=[__file__])
    else:
        main(Args)


