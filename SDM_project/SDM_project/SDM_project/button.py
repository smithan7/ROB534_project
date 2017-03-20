class Button(object):
    """description of class"""

    x = -1
    y = -1
    r = -1

    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def clicked(self, click):
        if math.sqrt( pow(self.x -click[0],2) + pow(self.y - click[1],2) ) < self.r:
            return True

        return False