import numpy as np
import random
import math
from operator import attrgetter

class TreeNode(object):
    """description of class"""

    
    def __init__(self, x, y, searchDepth, state, transitions, locations, current_time, simulation_time, patientIndex, taskIndex):
        self.x = x
        self.y = y
        self.searchDepth = searchDepth
        self.state = state
        self.transitions = transitions
        self.locations = locations
        self.rewards = np.zeros((6,4))

        self.reward = 0
        self.nSamples = -1 # for sampling the tree
        self.current_time = current_time
        self.simulation_time = simulation_time

        self.patientIndex = patientIndex
        self.taskIndex = taskIndex
        self.priorValue = 0


        ## for UCT
        self.nPulls = 0 # how many times have i been searched

        self.children = [] # my kids!
        self.maxSearchDepth = 5 # how deep do I search the tree
        self.maxRollOutIters = 2 # how deep is my rollout horizon
        
    def generateQ( self, args):
        # this will be used to get the probability of an action being completed at a certain time.
       # The general idea is to use the max value of each node's children (recursive by back prop) to determine the probability of each node being selected at that time, this is stored to a list as:
       #        [task id, prob of selection, time of task completion]
       # this is then used to determine the probability that a task will be completed by a certain time, which is passed on to other agents.
       path = args[0]

    def updateRewards_WRT_Q( self, args ):
        # this is used to take Q and update the rewards. The idea is that if P(task 0 is complete at time = 10) and I arrive there at time 10 then when I plan I should assume a reward of 0.7*reward_0
        # This should cause me to stay away from areas I am unlikely to get to before another agent and should cause the paths to converge.
        path = args[0]

    def updatePatients( self, states, patients ):
        for i in range(0,6):
            states[i][0] = patients[i].ivLevel
            states[i][1] = patients[i].hunger
            states[i][2] = patients[i].vomit_time
            states[i][3] = patients[i].dirty_time

    def iteratePatients( self, dt ):
        self.state += self.transitions*dt

    def backTrackPatients( self, dt ):
        self.state -= self.transitions*dt

    def updateRewards( self ):
        for i in range(0,6):
            if self.state[i][0] < 20:
                self.rewards[i][0] = 50# - self.transitions[i][0]
            if self.state[i][1] < 20:
                self.rewards[i][1] = 50# - self.transitions[i][0]
            if self.state[i][2] > 0:
                self.rewards[i][2] = 50
            if self.state[i][3] > 0:
                self.rewards[i][3] = 50
    
    def completeTask( self, p, t ):
        self.priorValue = self.state[p][t]
        if t == 0 or t == 1:
            self.state[p][t] = 100
        elif t == 2 or t == 3:
            self.state[p][t] = -float("inf")

    def undoTask( self, p, t ):
        self.state[p][t] = self.priorValue

    
    def sampleTreeEpsilonGreedy( self, args ):
        # this needs to eplore the tree with some level of greedyness ( to select better paths more frequently or even the optimal path or completely random path as desired ) and 
        # return for each iteration of search the value of the path, the expected time of completing each task.
        # this information will be used to calculate the probability of tasks being completed at certain times by each agent
        epsilon = args[0] # how greedy am I?
        task_index_list = args[1] # list of actions: each action will have the task id (global / universal name) and time of completion.
        sample_value = 0
        if len( self.children ) > 0:
            if random.random() < epsilon:
                # get best child and continue search
                goldencChild = max(self.children, key=attrgetter('reward') )
                #print("nChildren: ", len(self.children) )
                [task_index_list, sample_value] = goldencChild.sampleTree([epsilon, task_index_list])
            else:
                # get random child and continue to sample
                gc = random.randint(0, len(self.children)-1 );
                [task_index_list, sample_value] = self.children[gc].sampleTree([epsilon, task_index_list])
        else:
            sample_reward = self.reward

        task_index_list.append( self.taskIndex )
        
        return [task_index_list, sample_reward]

    def sampleTree( self, q ):
        
        maxR = max([child.reward for child in self.children])
        if maxR > 0:
            for child in self.children:
                q[child.patientIndex][child.taskIndex] = child.reward / maxR
        else:
            for child in self.children:
                q[child.patientIndex][child.taskIndex] = 1/24

        return q


    def getRationality( self, p, ta ):
        t = ta-1
        
        maxR = max([child.reward for child in self.children])
        if maxR <= 0:
            if t== -1:
                return 1
            else:
                return 1/24

        for child in self.children:
            if child.taskIndex == t and child.patientIndex == p:
                obs = reward[p][t] / maxR
                return obs

        return 1/24


    def sampleTreeUCB( self, args ):
        # this needs to eplore the tree with some level of greedyness ( to select better paths more frequently or even the optimal path or completely random path as desired ) and 
        # return for each iteration of search the value of the path, the expected time of completing each task.
        # this information will be used to calculate the probability of tasks being completed at certain times by each agent
        self.nSamples = self.nSamples + 1

        task_list = args[0] # list of actions: each action will have the task id (global / universal name) and time of completion.
        time = args[1]
        myProb = args[2]
        myDepth = args[3]+1
        sample_value = 0
        if len(self.children) > 0:
            # get total value
            sv = sum(child.value for child in self.children)
            # get each childs relative value
            for child in self.children:
                 if child.nSamples == -1:
                     # only add to task list if it hasn't been campled before
                     rv = child.value / sv
                     task_list[ child.taskIndex ].pMine.append( myProb * rv )
                     task_list[ child.taskIndex ].pMyTime.append( time + 5 )
                     task_list[ child.taskIndex ].pParent.append( self.taskIndex )
                     task_list[ child.taskIndex ].pDepth.append( myDepth + 1 )
                     child.nSamples = 0
                     
            
            # if I have children to samples
            mv = max(child.value for child in self.children)
            um = -1
            goldenChild = self.children[0]
            for child in self.children:
                u = 0
                if child.nSamples > 0: # child has been pulled, use UCB
                    val = child.value / mv
                    iter = 1.4142*math.sqrt(math.log(child.nSamples)/self.nSamples)
                    u = val + iter
                    if u > um:
                        goldenChild = child
                        um = u
                else: # child has NOT been pulled, pull child
                    goldenChild = child
                    break

            task_list = goldenChild.sampleTreeUCB([task_list, time + 5, myProb * goldenChild.value/sv, myDepth ])
        
        return task_list

    def exploitTree(self, arg):
        path = arg
        if len( self.children ) > 0:
            # get best child and continue search
            goldenChild = max(self.children, key=attrgetter('reward') )
            path = goldenChild.exploitTree( path )
        
        path.append( [self.patientIndex, self.taskIndex] )
        return path

    def findChildren(self, arg):
        current_time = arg[0]
        simulation_time = arg[1]
        # takes in tasklist and creates a new child for each task - tasks represent possible actions 
        for p in range(0,6):
            d = math.sqrt( pow(self.locations[p][0] - self.x,2) + pow(self.locations[p][1] - self.y,2) )
            sim_time = simulation_time + d - current_time
            self.iteratePatients( sim_time )
            self.updateRewards()
            
            for t in range(0,4):
                # only accept children with some reward
                if self.rewards[p][t] > 0:
                    self.completeTask(p,t) # complete childs task
                    newChild = TreeNode(self.locations[p][0], self.locations[p][1], self.searchDepth+1, self.state, self.transitions, self.locations , current_time, sim_time, p, t) # create child
                    newChild.reward = newChild.greedyRollout( current_time, sim_time, 0, self.locations[p][0], self.locations[p][1] ) # rollout child to get value of child
                    self.children.append( newChild ) # add to children
                    self.undoTask(p, t)
            self.iteratePatients( -sim_time ) # undo state transitions of patients

        self.children.append(TreeNode(self.x, self.y, self.searchDepth+1, self.state, self.transitions, self.locations , current_time, sim_time+5, self.patientIndex, self.taskIndex) ) # always have the option not to move
        
    def greedyRollout(self, current_time, sim_time, rollOutIters, curX, curY):
        # simple policy used to evalaute an action by greedily selecting remaining actions through a horizon, selecting actions with highest value (reward - cost)
        self.updateRewards()
        cumReward = np.sum( self.rewards )

        if rollOutIters > self.maxRollOutIters:
            return 24*50 - cumReward

        if cumReward > 0:
            maxReward = 1
            maxPatient = -1
            maxTask = -1
            
            for p in range(0,6):
                dist = math.sqrt( pow(curX - self.locations[p][0],2) + pow(curY - self.locations[p][1],2) )
                dt = sim_time + dist - current_time
                self.iteratePatients(dt)
                self.updateRewards()
                for t in range(0, 4):
                    tr = self.rewards[p][t]
                    if tr > maxReward:
                        maxValue = tr
                        maxPatient = p
                        maxTask = t
                self.iteratePatients(-dt)

            if maxPatient != -1 and maxTask != -1:
                dist = math.sqrt( pow(curX - self.locations[maxPatient][0],2) + pow(curY - self.locations[maxPatient][1],2) )
                dt = sim_time + dist - current_time
                self.iteratePatients(dt)
                self.completeTask( maxPatient, maxTask)
                rollOutReward = self.greedyRollout( current_time, sim_time+dist, rollOutIters+1, self.locations[maxPatient][0], self.locations[maxPatient][1])
                self.undoTask( maxPatient, maxTask)
                self.iteratePatients( -dt )
        else:
            self.iteratePatients(5)
            rollOutReward = self.greedyRollout( current_time, sim_time+5, rollOutIters+1, self.x, self.y)
            self.iteratePatients( -5 )

        return rollOutReward
    
    def uctSearch(self, arg):
        current_time = arg[0]
        sim_time = arg[1]
        # use UCT (upper confidence bound for trees) to select child to search
        tempValueBelow = -float("inf")
        if self.searchDepth < self.maxSearchDepth:
            if len(self.children) > 0:
                # if I have children to search
                self.nPulls = self.nPulls + 1
                mr = max(child.reward for child in self.children)
                if mr == 0:
                    return 0
                ur = -1
                goldenChild = self.children[0]
                for child in self.children:
                    u = 0
                    if child.nPulls > 0: # child has been pulled, use UCB
                        val = child.reward / mr
                        iter = 1.4142*math.sqrt(math.log(child.nPulls)/self.nPulls)
                        u = val + iter
                        if u > ur:
                            goldenChild = child
                            ur = u
                    else: # child has NOT been pulled, pull child
                        goldenChild = child
                        break
                dist = math.sqrt( pow(self.x - goldenChild.x,2) + pow(self.y - goldenChild.y,2) )
                tempRewardBelow = goldenChild.uctSearch( [current_time, sim_time + dist]  )
            else:
                # don't have children, make some!
                self.findChildren( [current_time, sim_time] )
                if len(self.children) > 0:
                    tempRewardBelow = max(child.reward for child in self.children)
                else:
                    tempRewardBelow = 0

            # update my value if a child has better value
            if tempRewardBelow > self.reward:
                self.reward = tempRewardBelow

        return self.reward
        
    
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




