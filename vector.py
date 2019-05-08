import math
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def fromAngle(angle, magnitude):
        return Vector(magnitude*math.cos(angle),magnitude*math.sin(angle))

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return self.x*other.x + self.y*other.y

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return '(%g, %g)' % (self.x, self.y)

    def angle(self):
        return math.atan(self.y/self.x)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def distance(v1, v2):
        return math.sqrt((v1.x-v2.x)**2 + (v1.y-v2.y)**2)