import math
from utils.vector import Vector2
import numpy as np

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
