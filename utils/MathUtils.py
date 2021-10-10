import math

import numpy as np


class Line:

    def __init__(self, a, b, c):
        assert isinstance(a, (int, float)) and isinstance(b, (int, float)) and isinstance(c, (int, float)), \
            'Invalid argument/s! Expected numbers.'
        self.a = a
        self.b = b
        self.c = c

    @classmethod
    def fromList(cls, line: list):
        assert len(line) == 3, 'Invalid argument! Expected python list with length of 3.'
        return Line(line[0], line[1], line[2])

    @classmethod
    def fromPoints(cls, x1, y1, x2, y2):
        a, b = y2 - y1, x1 - x2
        c = -(a * x1 + b * y1)
        return Line(a, b, c)

    @classmethod
    def isPointAbove(cls, x1, y1, x2, y2, x, y):
        v1 = np.array([x2 - x1, y2 - y1])  # Vector 1
        v2 = np.array([x2 - x, y2 - y])  # Vector 2
        return np.cross(v1, v2) > 0

    def asList(self):
        return [self.a, self.b, self.c]

    def asTuple(self):
        return self.a, self.b, self.c

    def distFromLine(self, x, y):
        return math.fabs(self.a * x + self.b * y + self.c) / math.sqrt(self.a * self.a + self.b * self.b)


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))


def slope(x1, y1, x2, y2):
    return (float(y2) - y1) / (x2 - x1)
