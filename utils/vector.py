from math import sin,cos,pi,sqrt
from numpy import dot

class Vector2:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    @staticmethod
    def fromPolar(length,angle):
        deg = 2*pi*angle/180
        x = length * sin(deg)
        y = length * cos(deg)
        return Vector2(x,y)
    def __add__(self, other):
        return Vector2(self.x+other.x, self.y+other.y)
    def __sub__(self, other):
        return Vector2(self.x-other.x, self.y-other.y)
    def __mul__(self, s):
        return Vector2(self.x*s, self.y*s)
    def lengthSq(self):
        return self.x*self.x + self.y*self.y
    def length(self):
        return sqrt( self.lengthSq() )
    def distSq(self,other):
        dx = self.x-other.x
        dy = self.y-other.y
        return dx*dx+dy*dy
    def dist(self,other):
        return sqrt( self.distSq() )
    def unity(self):
        ool = 1.0/self.length()
        return Vector2(self.x*ool,self.y*ool)
    def __str__(self):
        return f'({self.x},{self.y})'
    def dot(self, matrix):
        return Vector2(*dot(matrix,[self.x, self.y]))

