import pygame
from pygame.gfxdraw import line,filled_polygon
import argparse, math
from pathlib import Path
from datetime import datetime
from utils.vector import Vector2
from utils.pygame_utils import *

class Car:
    def __init__(self,attributes,pos,orientation):
        self.steering_angle = 0
        self.attributes = attributes
        self.wheel_base = attributes.length - attributes.front_wheel_mount_point + attributes.rear_wheel_mount_point
        self.pos = pos
        self.orientation = math.radians(orientation)
        w2,l = attributes.width/2,attributes.length
        self.geometry = [(-w2,l),(0,int(l*1.1)), (w2,l),(w2,0),(-w2,0)]
        self.color = attributes.color

    def move(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if self.steering_angle > -self.attributes.max_steering_angle:   
                self.steering_angle -= self.attributes.steering_speed * dt
        elif keys[pygame.K_RIGHT]:
            if self.steering_angle < self.attributes.max_steering_angle:   
                self.steering_angle += self.attributes.steering_speed * dt
        
        if keys[pygame.K_LEFTBRACKET]:
            self.orientation -= dt
        elif keys[pygame.K_RIGHTBRACKET]:
            self.orientation += dt
        
        if keys[pygame.K_UP]:
            speed = 1.0
        elif keys[pygame.K_DOWN]:
            speed = -1.0
        else:
            speed = 0
        
        if speed != 0:
            speed *= self.attributes.move_speed * dt
            c = math.cos(self.orientation)
            s = math.sin(self.orientation)
            self.pos += Vector2(-speed*s,speed*c)
            rad_s = math.radians(self.steering_angle)
            self.orientation += speed * math.tan(rad_s) / self.wheel_base

    def draw(self, screen):
        pts = rotMove_radians(self.orientation, self.pos, self.geometry)
        filled_polygon(screen, pts, self.color)

def displayDebugInfo(screen,font,car):
    text = [f'steering angle {car.steering_angle:.1f}',
            f'orientation {car.orientation:.1f}']
    displayText(screen,font,(255,255,255),(0,0,0),text,(0,100))

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
    pos = Vector2(*Config.starting_pos.pos) + Vector2(width/2,height/2)
    car = Car(Config.car,pos,Config.starting_pos.orientation)
    font = pygame.font.SysFont("Arial", 20)
    t0 = t1 = datetime.now()
    while True:
        events = pygame.event.get()
        if got_quit_event(events):
            break
        screen.fill(background)
        car.move((t1-t0).total_seconds())
        car.draw(screen)
        displayDebugInfo(screen,font,car)
        pygame.display.flip()
        t0 = t1
        t1 = datetime.now()
    pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="gra asteroids")
    parser.add_argument("config", type=Path, help='game config file')
    parser.add_argument("-display","-d",type=str, default="1280,1024", help="screen size width,height")
    parser.add_argument("-fullscreen","-f",action='store_true', help="run in fullscreen mode")
    Args = parser.parse_args()
    main(Args)