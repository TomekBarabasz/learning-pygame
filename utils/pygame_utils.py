import pygame,json,math
from utils.vector import Vector2
import numpy as np

def got_quit_event(events):
    for event in events:
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.unicode == 'q':
                return True
    return False

def readConfig(filename):
    class Config:
        pass
    def objectify(dict_):
        cfg = Config()
        for k,v in dict_.items():
            if type(v) is dict:
                setattr(cfg,k,objectify(v))
            else:
                setattr(cfg,k,v)    
        return cfg
    with open(filename) as jsonFile:
        data = json.load(jsonFile)
    return objectify(data)

def makeRotMatrix(angle):
    rad = math.radians(angle)
    c = math.cos(rad)
    s = math.sin(rad)
    return np.array([c,-s, s, c]).reshape(2,2)

def rotate(angle, Points):
    ROT = makeRotMatrix(angle)
    return ROT.dot(np.array(Points).T).T

def move(dt,Points):
    if type(dt) is Vector2:
        dt = (dt.x,dt.y)
    return np.array(Points)+dt

def rotMove_radians(rad,dt,Points):
    c = math.cos(rad)
    s = math.sin(rad)
    ROT = np.array([c,-s, s, c]).reshape(2,2)
    return move(dt,ROT.dot(np.array(Points).T).T)

def rotMove(angle,dt,Points):
    rad = math.radians(angle)
    return rotMove_radians(rad,dt,Points)

def displayText(screen,font,color,background,Text,pos):
    left,top = pos
    for line in Text:
        size = font.size(line)
        ren = font.render(line, 0, color, background)
        screen.blit(ren, (left,top))
        top += int( round(size[1] * 1.2) )
    return (left,top)
