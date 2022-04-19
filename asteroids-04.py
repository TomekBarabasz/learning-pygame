import pygame
from pygame.gfxdraw import aacircle,filled_circle,line,filled_polygon
import argparse, random, math, json
from datetime import datetime
import numpy as np
from vector import Vector2
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Missile:
    pos : Vector2
    speed : Vector2
    t0 : datetime

@dataclass
class Asteroid:
    pos : Vector2
    speed : Vector2
    size : int

class Ship:
    def __init__(self, config, init_x, init_y, wrap):
        self.config = config
        self.pos = Vector2(init_x,init_y)
        self.speed = Vector2(0,0)
        self.angle = 0
        self.is_accel = False
        self.wrap = wrap

    def move_(self, events):
        self.pos,self.speed = self.wrap(self.pos, self.speed)
        rad = math.radians(self.angle+90)
        dir = Vector2(math.cos(rad), math.sin(rad))
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.angle += event.rel[0] * self.config.rotation_speed
                if self.angle > 360: self.angle -= 360
                elif self.angle < 0: self.angle += 360
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.is_accel = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_accel = False
        if self.is_accel:
            self.speed += dir*self.config.acceleration

    def draw(self, screen, events):
        self.move_(events)
        Size = self.config.size
        Points = [(-Size,-Size),(0,2*Size),(Size,-Size)]
        ToDraw = rotMove(self.angle, self.pos, Points)
        filled_polygon(screen, ToDraw, self.config.color)

        if self.is_accel:
            Points = [(-Size,-Size),(Size,-Size),(0,-2*Size)]
            ToDraw = rotMove(self.angle, self.pos, Points)
            filled_polygon(screen, ToDraw, (255,0,0))
    
    def fire(self,events):
        fire = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    fire = True
                    break
        if fire:
            rad = math.radians(self.angle+90)
            dir = Vector2(math.cos(rad), math.sin(rad))
            mpos = self.pos + dir*2*self.config.size
            mspeed = dir*self.config.missile_initial_speed
            return [Missile(mpos,mspeed,datetime.utcnow())]
        else:
            return []
    
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
    if type(dt) is Vector2:
        dt = (dt.x,dt.y)
    return np.array(Points)+dt

def rotMove(angle,dt,Points):
    rad = math.radians(angle)
    c = math.cos(rad)
    s = math.sin(rad)
    ROT = np.array([c,-s, s, c]).reshape(2,2)
    return move(dt,ROT.dot(np.array(Points).T).T)

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
    with Args.config.open() as jsonFile:
        data = json.load(jsonFile)
    return objectify(data)

def makeWrap(width,height):
    def wrap(pos,speed):
        npos = pos + speed
        if npos.x < 0: npos.x = width
        elif npos.x > width: npos.x=0
        if npos.y < 0: npos.y = height
        elif npos.y > height: npos.y=0
        return npos,speed
    return wrap

def makeBounce(width,height):
    def bounce(pos,speed):
        npos = pos + speed
        if npos.x < 0 or npos.x > width: speed.x = -speed.x
        if npos.y < 0 or npos.y > height: speed.y = -speed.y
        return npos,speed
    return bounce

def drawMissiles(Config,screen, Missiles, wrap):
    tm = datetime.utcnow()
    ValidMissiles = []
    for m in Missiles:
        if (tm-m.t0).total_seconds() < Config.lifetime:
            pos,speed = wrap(m.pos, m.speed)
            filled_circle(screen, round(pos.x),round(pos.y), Config.size, Config.color)
            ValidMissiles.append( Missile(pos, speed, m.t0) )
    return ValidMissiles

def drawAsteroids(screen, Asteroids, t0, wrap):
    pass

def main(Args):
    screen_size = width,height = tuple(map(int, Args.display.split(',')))
    Config = readConfig(Args.config)
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    if Args.fullscreen:
        pygame.display.toggle_fullscreen()
    else:
        pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    background=0,0,0
    wrap = makeWrap(width,height)
    bounce = makeBounce(width,height)
    ship = Ship(Config.ship, width//2, height//2, wrap)
    Missiles = []
    Asteroids = []
    t0 = datetime.utcnow()
    while True:
        t0 = datetime.utcnow()
        events = pygame.event.get()
        if got_quit_event(events):
            break
        screen.fill(background)
        ship.draw(screen,events)
        Missiles.extend(ship.fire(events))
        Missiles = drawMissiles(Config.missile, screen, Missiles, bounce)
        Asteroids = drawAsteroids(screen,Asteroids,t0,wrap)
        pygame.display.flip()
        t1 = datetime.utcnow()
    
    pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="gra asteroids")
    parser.add_argument("config", type=Path, help='game config file')
    parser.add_argument("-test", action='store_true', help='execute unittests')
    parser.add_argument("-display","-d",type=str, default="1280,1024", help="screen size width,height")
    parser.add_argument("-fullscreen","-f",action='store_true', help="run in fullscreen mode")
    Args = parser.parse_args()
    if Args.test:
        unittest.main(argv=[__file__])
    else:
        main(Args)
