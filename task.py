class Task(object):
    """description of class"""
    def __init__(self, arg):
        self.x = arg[0]
        self.y = arg[1]
        self.reward = arg[2]
        self.index = arg[3]

        self.pMine = []
        self.pMyTime = []
        self.pParent = []
        self.pDepth = []

        self.pTaken = []
        self.pTakenTime = []

    def getReward(self, arg):
        # eventually this will take in time and solve for the reward at the time it will be solved
        return self.Reward

    def getPenalty(self, arg):
        # eventually this will take in time and give the cumulative penalty for the the task not being completed from t_0 to now
        return self.Reward
