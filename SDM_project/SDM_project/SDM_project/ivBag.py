import random

class IvBag(object):
    """description of class"""
    def __init__(self, arg):
        self.level = arg[0]
        self.full = arg[1]
        self.dripMean = arg[2]
        self.dripVar = arg[3]

    def drip(self):
        self.level -= random.normalvariate(self.dripMean, self.dripVar)

    def refill(self):
        self.level = self.full

    def checkLevel(self):
        return self.level

