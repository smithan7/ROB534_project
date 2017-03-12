import random

p_edge           = 51     #edge of square surrounding robot (in pixels)
p_transparency   = 0      #0 is totally transp., 255 totally opaque

class Patient(object):
    """description of class""" 
    def __init__(self, arg):
        self.id = arg[0]
        self.x = arg[1]
        self.y = arg[2]
        self.n_tasks = 3
        self.rewards = [0]*4
        self.ivLevel = random.randint(50,100)
        self.hunger = random.randint(50,100)
        self.vomit = False
        self.vomitTime = 0
        self.dirty = False
        
    def iterate(self, arg):
        time_step = arg
        self.ivLevel -= 1
        self.hunger -= 1
        if self.hunger > 50:
           if random.random() < 0.01 and self.vomit == False:
               print("Patient " ,self.id, " vomitted")
               self.vomit = True
               self.vomit_time = time_step
             #  self.dirty = True
               self.hunger -= 30
           else:
               self.vomit = False
   
               
    def updateRewards( self, arg):
        dt = arg
        self.rewards[0] = self.getIVRewardAtTime( dt )
        self.rewards[1] = self.getHungerRewardAtTime( dt )
        self.rewards[2] = self.getVomitReward()
        self.rewards[3] = self.getCleanReward()
             
    def completeTask( self, arg ):
        t_index = arg
        if t_index == 0:
            self.ivLevel = 100
        elif t_index == 1:
            self.hunger = 100
        elif t_index == 2:
            self.vomit = False
        elif t_index  == 3:
            self.dirty = False
           
    def getIVRewardAtTime( self, arg ):
        dt = arg
        if self.ivLevel-dt > 50:
            return 0.0
        else:
            return 50 - (self.ivLevel - dt)

    def getHungerRewardAtTime( self, arg ):
        dt = arg
        if self.hunger - dt > 50:
            return 0.0
        else:
            return 50 - (self.hunger - dt)        

    def getVomitReward( self ):
        if self.vomit == False:
            return 0.0
        else:
            return 50

    def getCleanReward( self ):
        if self.vomit == False:
            return 0.0
        else:
            return 50
        
    def checkStatus(self):
        if self.ivLevel > 0:
            return 0.0
        else:
            return -1.0
