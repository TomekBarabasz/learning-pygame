import pygame
from pygame.gfxdraw import aacircle,filled_circle,line,filled_polygon
import math,argparse
from datetime import datetime

def got_quit_event(events):
    for event in events:
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.unicode == 'q':
                return True
    return False

def drawShip(screen,events,x,y):
    S=15
    filled_polygon(screen, [(x-S,y),(x,y-3*S),(x+S,y)], (72,54,107))

def main(Args):
    screen_size = width,height = tuple(map(int, Args.display.split(',')))
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    background = 0,0,0
    x,y = width//2,height//2
    while True:
        t0 = datetime.utcnow()
        events = pygame.event.get()
        if got_quit_event(events):
            break
        screen.fill(background)
        drawShip(screen,events,x,y)
        pygame.display.flip()
        delta_time = (datetime.utcnow() - t0).total_seconds()
    
    pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="gra asteroids")
    parser.add_argument("-display","-d",type=str, default="1280,1024", help="screen size width,height")
    Args = parser.parse_args()
    main(Args)
