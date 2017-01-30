
from ivBag import IvBag

class Patient(object):
    """description of class"""
    def __init__(self, arg):
        self.id = arg
        self.iv = IvBag([100.0, 100.0, 1.5, 0.5])
        
    def iterate(self):
        self.iv.drip()


    def checkStatus(self):
        if self.iv.level > 0:
            return 0.0
        else:
            return -1.0