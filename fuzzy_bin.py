class fuzzy_bin(object):
    """description of class"""


    def __init__(self, start, middle, end):
        self.s = start
        self.m = middle
        self.e = end

    def getWeight( self, x ):
        if x < self.s[0] or x > self.e[0]:
            return 0
        if x > self.s[0] and x < self.m[0]:
            slope = (self.m[1] - self.s[1])/(self.m[0] - self.s[0]);
            intercept = self.m[1] - slope*self.m[0];
            return slope*x+intercept;
        else:
            if x > self.m[0] and x < self.e[0]:
                slope = (self.e[1] - self.m[1])/(self.e[0] - self.m[0])
                intercept = self.e[1] - slope*self.e[0]
                return slope*x+intercept
            else:
                if x == self.m[0]:
                    return self.m[1];
                else:
                    return 0