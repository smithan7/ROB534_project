class State(object):
    """description of class"""
    def __init__(self, arg):
        self.x = arg[0]
        self.y = arg[1]
        self.g = float("inf")
        self.f = float("inf")

