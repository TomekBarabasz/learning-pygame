class Vector2:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    @staticmethod
    def fromPolar(length,angle):
        deg = 2*math.pi*angle/180
        x = length * math.sin(deg)
        y = length * math.cos(deg)
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
        return math.sqrt( self.lengthSq() )
    def unity(self):
        ool = 1.0/self.length()
        return Vector2(x*ool,y*ool)
    def __str__(self):
        return f'({self.x},{self.y})'
        