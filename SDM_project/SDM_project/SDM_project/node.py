import numpy as np
import random
import math
from operator import attrgetter
from task import Task

class Node(object):
    """description of class"""
    def __init__(self, arg):
        self.x = arg[0]
        self.y = arg[1]
        self.searchDepth = arg[2]
        self.tasks = arg[3]
        # value is the cumulative value along the path, we break this into three parts
        ### valueAbove: value from the root to my parent, not really used as we search down
        self.valueAbove = arg[4]
        ### value: value for specifically for me from parent, w/o my children
        self.valueMine = arg[5]
        ### valueBelow: value of my children through the end of my branch
        self.valueBelow = 0
        ### value of all 3 to get expected value of all actions in branch!
        self.value = 0
        self.updateValue()



        self.taskIndex = arg[6]

        self.nPulls = 0 # how many times have i been searched
        self.children = [] # my kids!
        self.maxSearchDepth = 10 # how deep do I search the tree
        self.maxRollOutIters = 10 # how deep is my rollout horizon
        

    def updateValue( self ):
        self.value = self.valueMine + self.valueBelow

    def exploitTree(self, arg):
        path = arg
        if len( self.children ) > 0:
            # get best child and continue search
            goldenChild = max(self.children, key=attrgetter('value') )
            path = goldenChild.exploitTree( path )
        
        path.append( [self.x, self.y] )
        return path

    def findChildren(self):
        # takes in tasklist and creates a new child for each task - tasks represent possible actions 
        #print("nTasks: ", len(self.tasks) )
        for task in self.tasks:
            #print("in task loop")
            tempTasks = list(self.tasks)
            tempTasks.remove(task)
            d = math.sqrt( pow(task.x - self.x,2) + pow(task.y - self.y,2) )
            newChild = Node([task.x, task.y, self.searchDepth+1, tempTasks, self.valueAbove + self.value, task.reward - d, task.index])
            # rollout child to get value of child
            newChild.valueBelow = newChild.greedyRollout()
            newChild.updateValue()
            # add to children
            self.children.append( newChild )

    def greedyRollout(self):
        # simple policy used to evalaute an action by greedily selecting remaining actions through a horizon, selecting actions with highest value (reward - cost)
        tempTasks = list(self.tasks)
        rolloutValue = 0
        curX = self.x
        curY = self.y
        rollOutIters = 0
        while len(tempTasks) > 0 and rollOutIters < self.maxRollOutIters:
            rollOutIters = rollOutIters + 1
            maxValue = -float('inf')
            maxTask = tempTasks[0]
            for task in tempTasks:
                tV = task.reward - math.sqrt( pow(curX - task.x,2) + pow(curY - task.y,2) )
                if tV > maxValue:
                    maxValue = tV
                    maxTask = task
            rolloutValue = rolloutValue + maxValue
            curX = maxTask.x
            curY = maxTask.y
            tempTasks.remove( maxTask )

        #print("rollout value: ", rolloutValue)
        return rolloutValue


    def epsilonGreedySearch(self, arg):
        tempValueBelow = -float("inf")
        if len(self.children) > 0:
            # if I have children to search
            # with p(epsilon) choose the best child for expansion, else randomly select a child to expand
            epsilon = arg
            if random.random() < epsilon:
                # get best child and continue search
                goldencChild = max(self.children, key=attrgetter('value') )
                #print("nChildren: ", len(self.children) )
                tempValueBelow = goldencChild.epsilonGreedySearch(epsilon)
            else:
                # get random child and continue search
                gc = random.randint(0, len(self.children)-1 );
                #print("nChildren: ", len(self.children), "; gc = :", gc )
                tempValueBelow = self.children[gc].epsilonGreedySearch(epsilon)
        else:
            if self.searchDepth < self.maxSearchDepth:
                # don't have children, make some if I'm not past max depth
                self.findChildren()
                if len(self.children) > 0:
                    #print("nChildren: ", len(self.children) )
                    tempValueBelow = max(child.value for child in self.children)
                else:
                    tempValueBelow = 0
        # update my valueBelow if a child has better value than is currently known
        if tempValueBelow > self.valueBelow:
            self.valueBelow = tempValueBelow
            self.updateValue()

        return self.value
    
    def uctSearch(self):
        # use UCT (upper confidence bound for trees) to select child to search
        tempValueBelow = -float("inf")
        if self.searchDepth < self.maxSearchDepth:
            if len(self.children) > 0:
                # if I have children to search
                self.nPulls = self.nPulls + 1;
                mv = max(child.value for child in self.children)
                um = -1;
                goldenChild = self.children[0]
                for child in self.children:
                    u = 0
                    if child.nPulls > 0: # child has been pulled, use UCB
                        val = child.value / mv
                        iter = 1.4142*math.sqrt(math.log(child.nPulls)/self.nPulls)
                        u = val + iter;
                        if u > um:
                            goldenChild = child
                            um = u
                    else: # child has NOT been pulled, pull child
                        goldenChild = child
                        break

                tempValueBelow = goldenChild.uctSearch()
            else:
                # don't have children, make some!
                self.findChildren()
                if len(self.children) > 0:
                    tempValueBelow = max(child.value for child in self.children)
                else:
                    tempValueBelow = 0

            # update my value if a child has better value
            if tempValueBelow > self.valueBelow:
                self.valueBelow = tempValueBelow
                self.updateValue()

        return self.value
        
    
    def greedySearch(self, arg):
        # select best child to search
        if self.searchDepth < self.maxSearchDepth:
            tempValueBelow = -float("inf")
            if len( self.children ) > 0:
                    # get best child and continue search
                    gc = children.index( max(child.value for child in self.children) )
                    tempValueBelow = self.children[gc].greedySearch()
            else:
                # don't have children, make some!
                self.findChildren()
                tempValueBelow = max(child.value for child in self.children)

            # update my value if a child has better value
            if tempValueBelow > self.valueBelow:
                self.valueBelow = tempValueBelow
                self.updateValue()

        return self.value


    def updateTasks(self, args):
        # update tasks robot knows about
        self.tasks = args

    def appendTasks(self, args):
        # add a new task
        self.tasks.append( args )






