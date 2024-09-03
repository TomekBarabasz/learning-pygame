import pygame
from pygame.gfxdraw import aacircle,filled_circle,line,filled_polygon
import argparse, random, math, json
from datetime import datetime
import numpy as np
from utils.vector import Vector2
from dataclasses import dataclass
from pathlib import Path
from utils.pygame_utils import *
from utils.math_utils import *

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
        self.ToDraw = []
        self.hitPoints = 0
    
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
        self.ToDraw = rotMove(self.angle, self.pos, Points)
        filled_polygon(screen, self.ToDraw, self.config.color)

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
            return [Missile(mpos,mspeed,datetime.now())]
        else:
            return []
    
    def getBoundingPolygon(self):
        return self.ToDraw
    
    def collideWith(self, asteroid, pt):
        self.hitPoints += asteroid.size

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

def drawMissiles(Config, screen, Missiles, wrap):
    tm = datetime.now()
    ValidMissiles = []
    for m in Missiles:
        if (tm-m.t0).total_seconds() < Config.lifetime:
            pos,speed = wrap(m.pos, m.speed)
            filled_circle(screen, round(pos.x),round(pos.y), Config.size, Config.color)
            ValidMissiles.append( Missile(pos, speed, m.t0) )
    return ValidMissiles

def drawAsteroids(Config, screen, Asteroids, tstart, wrap, screen_size):
    for a in Asteroids:
        a.pos,a.speed = wrap(a.pos,a.speed)
        idx = a.size - 1
        aacircle(screen, int(round(a.pos.x)), int(round(a.pos.y)), Config.size[idx], Config.color[idx])
    totWeight = sum( [a.size for a in Asteroids])
    delta_time = (datetime.now() - tstart).total_seconds()
    newWeight = delta_time * Config.weight_inc - totWeight
    weight = Config.weights[-1]
    if newWeight > weight:
        width,height = screen_size
        size = Config.size[-1]
        angle = random.uniform(0,359)
        speed = Vector2.fromPolar(Config.speed[-1], angle)
        if angle < 90:
            pos = Vector2(-size,height+size)
        elif angle < 180:
            pos = Vector2(width+size,height+size)
        elif angle < 270:
            pos = Vector2(width+size,-size)
        else:
            pos = Vector2(-size,-size)
        Asteroids.append( Asteroid(pos,speed,weight) )
    return Asteroids

def asteroidHit(Config, asteroid,missile):
    if asteroid.size == 1:
        return []
    elif asteroid.size == 2:
        dir = missile.speed.unity()
        pdir = Vector2(-dir.y,dir.x)
        size = Config.asteroid.size[0]
        speed = Config.asteroid.speed[0]
        a1 = Asteroid(asteroid.pos + pdir*size, pdir*speed, 1)
        a2 = Asteroid(asteroid.pos - pdir*size, pdir*-speed, 1)
        return [a1,a2]
    elif asteroid.size == 3:
        size = Config.asteroid.size[1]
        speed = Config.asteroid.speed[1]
        dir = missile.speed.unity()
        dist = 1.1547005383792515*size
        a1 = Asteroid(asteroid.pos + dir*size, dir*speed, 2)
        rot = makeRotMatrix(120)
        dir = dir.dot(rot)
        a2 = Asteroid(asteroid.pos + dir*size, dir*speed, 2)
        dir = dir.dot(rot)
        a3 = Asteroid(asteroid.pos + dir*size, dir*speed, 2)
        return [a1,a2,a3]

def collide(Config, Asteroids, Missiles, ship):
    #ship vs Asteroids
    if not Asteroids:
        return Asteroids,Missiles
    
    ship_pts = ship.getBoundingPolygon()
    Sizes = Config.asteroid.size
    for a in Asteroids:
        r = Sizes[a.size-1]
        r_sq = r*r
        for p in ship_pts:
            d_sq = (p[0]-a.pos.x)**2 + (p[1]-a.pos.y)**2
            if d_sq <= r_sq:
                ship.collideWith(a,p)
                break
    
    #Missiles vs Asteroids
    if not Missiles:
        return Asteroids,Missiles
    
    AliveMissiles = []
    AliveAsteroids = []
    for m in Missiles:
        hit = False
        AliveAsteroids = []
        for a in Asteroids:
            r = Sizes[a.size-1]
            r_sq = r*r
            d_sq = m.pos.distSq(a.pos)
            if d_sq <= r_sq:
                hit = True
                AliveAsteroids += asteroidHit(Config,a,m)
                break
            else:
                AliveAsteroids.append(a)

        if not hit:
            AliveMissiles.append(m)
        Asteroids = AliveAsteroids

    return AliveAsteroids,AliveMissiles

def displayText(screen,font,color,background,Text,pos):
    left,top = pos
    for line in Text:
        size = font.size(line)
        ren = font.render(line, 0, color, background)
        screen.blit(ren, (left,top))
        top += int( round(size[1] * 1.2) )
    return (left,top)

def displayPoints(ship,screen,font,pos):
    return displayText(screen,font,(255,255,255),(0,0,0),[f'hit {ship.hitPoints} times'],pos)

def displayTimeStats(time_measurements,screen,font,pos):
    return pos

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
    tstart= datetime.now()
    font = pygame.font.SysFont("Arial", 20)
    time_measurements = [0,0,0,0,0,0]
    while True:
        time_measurements[0] = datetime.now()
        events = pygame.event.get()
        if got_quit_event(events):
            break
        screen.fill(background)
        time_measurements[1] = datetime.now()
        ship.draw(screen,events)
        Missiles.extend(ship.fire(events))
        time_measurements[2] = datetime.now()
        Missiles = drawMissiles(Config.missile, screen, Missiles, bounce)
        time_measurements[3] = datetime.now()
        Asteroids = drawAsteroids(Config.asteroid, screen, Asteroids, tstart, wrap, screen_size)
        time_measurements[4] = datetime.now()
        Asteroids,Missiles = collide(Config, Asteroids, Missiles, ship)
        time_measurements[5] = datetime.now()
        tpos = displayPoints(ship,screen,font,(10,10))
        displayTimeStats(time_measurements,screen,font,tpos)
        pygame.display.flip()
        
    
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
