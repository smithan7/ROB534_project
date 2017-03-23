import numpy as np
import random
import math
from operator import attrgetter
from rationality import rationality

class TreeNode(object):
    """description of class"""

    discount = 0.95
    num_patients = 6
    num_tasks = 4
    
    def __init__(self, x, y, searchDepth, state, transitions, locations, current_time, simulation_time, patientIndex, taskIndex, reward):
        self.x = x
        self.y = y
        self.searchDepth = searchDepth
        self.state = state
        self.transitions = transitions
        self.locations = locations
        self.rewards = np.zeros((self.num_patients,self.num_tasks))
        self.q_prob = np.zeros((self.num_patients,self.num_tasks))
        self.q_prior = np.zeros((self.num_patients,self.num_tasks))

        self.reward = reward
        self.reward_below = 0
        self.cum_reward = reward
        self.nSamples = -1 # for sampling the tree
        self.current_time = current_time
        self.simulation_time = simulation_time

        self.patientIndex = patientIndex
        self.taskIndex = taskIndex
        
        ## for UCT
        self.nPulls = 0 # how many times have i been searched

        self.children = [] # my kids!

    def update_Q_WRT_rationality( self, rat ):
        # this is used to take Q and update the rewards. The idea is that if P(task 0 is complete at time = 10) and I arrive there at time 10 then when I plan I should assume a reward of 0.7*reward_0
        # This should cause me to stay away from areas I am unlikely to get to before another agent and should cause the paths to converge.
        r = rationality()
        self.q_prob = r.weight_values(self.q_prior, rat )



    def updatePatients( self, states, patients ):
        for i in range(0,self.num_patients):
            states[i][0] = patients[i].ivLevel
            states[i][1] = patients[i].hunger
            states[i][2] = patients[i].vomit_time
            states[i][3] = patients[i].dirty_time

    def iteratePatients( self, dt ):
        self.state += self.transitions*dt

    def updateRewards( self ):
        for i in range(0,self.num_patients):
            if self.state[i][0] < 20:
                self.rewards[i][0] = 50 * (1-self.q_prob[i][0]) # - self.transitions[i][0]
            elif self.state[i][0] < 30:
                self.rewards[i][0] = 40 * (1-self.q_prob[i][0]) # - self.transitions[i][0]
            elif self.state[i][0] < 40:
                self.rewards[i][0] = 30 * (1-self.q_prob[i][0]) # - self.transitions[i][0]
            if self.state[i][1] < 20:
                self.rewards[i][1] = 40 * (1-self.q_prob[i][1]) # - self.transitions[i][0]
            elif self.state[i][1] < 30:
                self.rewards[i][1] = 30 * (1-self.q_prob[i][1]) # - self.transitions[i][0]
            elif self.state[i][1] < 40:
                self.rewards[i][1] = 20 * (1-self.q_prob[i][1]) # - self.transitions[i][0]
            if self.state[i][2] > 0:
                self.rewards[i][2] = 30 * (1-self.q_prob[i][2]) 
            if self.state[i][3] > 0:
                self.rewards[i][3] = 30 * (1-self.q_prob[i][3]) 
    
    def updatePatientRewards(self, p):
            if self.state[p][0] < 20:
                self.rewards[p][0] = 50 * (1-self.q_prob[p][0]) # - self.transitions[i][0]
            elif self.state[p][0] < 30:
                self.rewards[p][0] = 40 * (1-self.q_prob[p][0]) # - self.transitions[i][0]
            elif self.state[p][0] < 40:
                self.rewards[p][0] = 10 * (1-self.q_prob[p][0]) # - self.transitions[i][0]
            if self.state[p][1] < 20:
                self.rewards[p][1] = 40 * (1-self.q_prob[p][1]) # - self.transitions[i][0]
            elif self.state[p][1] < 30:
                self.rewards[p][1] = 30 * (1-self.q_prob[p][1]) # - self.transitions[i][0]
            elif self.state[p][1] < 40:
                self.rewards[p][1] = 10 * (1-self.q_prob[p][1]) # - self.transitions[i][0]
            if self.state[p][2] > 0:
                self.rewards[p][2] = 30 * (1-self.q_prob[p][2]) 
            if self.state[p][3] > 0:
                self.rewards[p][3] = 30 * (1-self.q_prob[p][3]) 


    def completeTask( self, p, t ):
        priorState = self.state[p][t]
        priorReward = self.rewards[p][t]
        if t == 0 or t == 1:
            self.state[p][t] = 100
            self.rewards[p][t] = 0
        elif t == 2 or t == 3:
            self.state[p][t] = -float("inf")
            self.rewards[p][t] = 0
        return [priorState, priorReward]

    def undoTask( self, p, t, priorState, priorReward ):
        self.state[p][t] = priorState
        self.rewards[p][t] = priorReward

    
    def sampleTreeEpsilonGreedy( self, epsilon, task_index_list ):
        # this needs to eplore the tree with some level of greedyness ( to select better paths more frequently or even the optimal path or completely random path as desired ) and 
        # return for each iteration of search the value of the path, the expected time of completing each task.
        # this information will be used to calculate the probability of tasks being completed at certain times by each agent
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
        minR = min([child.cum_reward for child in self.children])
        maxR = max([child.cum_reward for child in self.children])
        if maxR-minR > 0:
            for child in self.children:
                q[child.patientIndex][child.taskIndex] = (child.cum_reward - minR) / (maxR-minR)
        else:
            for child in self.children:
                q[child.patientIndex][child.taskIndex] = 1/24
        return q

    def remap_tasks( self, task ):
        if task == -1:
            return 0
        elif task==0:
            return 1
        elif task==1:
            return 2
        elif task==2:
            return 4
        elif task==3:
            return 3

    def getRationality( self, patient, task ):

        if task == 0:
            maxR = max([child.cum_reward for child in self.children])
            if maxR <= 1:
                return 1
            else:
                return 0
        elif task == 1:
           t = 0
        
        elif task == 2:
            t = 1
        elif task == 3:
            t = 4
        elif task == 4:
            t = 3
        

        #t = self.remap_tasks( task )
        p = patient
        
        maxR = max([child.cum_reward for child in self.children])
        minR = min([child.cum_reward for child in self.children])

        if minR == maxR: # only 1 option or options are equivalent
            for child in self.children:
                if child.taskIndex == t and child.patientIndex == p:
                    obs = 1
                    return obs

        if maxR <= 1:
            return 1/24

        for child in self.children:
            if child.taskIndex == t and child.patientIndex == p:
                obs = (child.cum_reward-minR) / (maxR-minR)
                return obs

        return 1/24


    def sampleTreeUCB( self, task_list, time, myProb, myDepth ):
        # this needs to eplore the tree with some level of greedyness ( to select better paths more frequently or even the optimal path or completely random path as desired ) and 
        # return for each iteration of search the value of the path, the expected time of completing each task.
        # this information will be used to calculate the probability of tasks being completed at certain times by each agent
        self.nSamples = self.nSamples + 1
        myDepth += 1
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

    def exploitTree(self, path):
        if len( self.children ) > 0:
            # get best child and continue search
            goldenChild = max(self.children, key=attrgetter('cum_reward') )
            path = goldenChild.exploitTree( path )
        
        path.append( [self.patientIndex, self.taskIndex] )
        return path

    def findChildren(self, current_time, simulation_time, maxRolloutIters ):
        # takes in tasklist and creates a new child for each task - tasks represent possible actions 
        for p in range(0,self.num_patients):
            d = math.sqrt( pow(self.locations[p][0] - self.x,2) + pow(self.locations[p][1] - self.y,2) )
            sim_time = simulation_time + d - current_time
            self.iteratePatients( sim_time )
            self.updatePatientRewards( p )
            
            for t in range(0,self.num_tasks):
                # only accept children with some reward
                if self.rewards[p][t] > 0:
                    child_reward = self.rewards[p][t] * pow( self.discount, sim_time )
                    [priorState, priorReward] = self.completeTask(p,t) # complete childs task 
                    newChild = TreeNode(self.locations[p][0], self.locations[p][1], self.searchDepth+1, self.state, self.transitions, self.locations , current_time, sim_time, p, t, child_reward ) # create child
                    newChild.reward_below = newChild.greedyRollout( current_time, sim_time, 0, self.locations[p][0], self.locations[p][1], maxRolloutIters ) # rollout child to get value of child
                    newChild.cum_reward = newChild.reward + newChild.reward_below
                    self.children.append( newChild ) # add to children
                    self.undoTask(p, t, priorState, priorReward)
            self.iteratePatients( -sim_time ) # undo state transitions of patients

        ## add option to stay put if nothing else
        if len( self.children ) == 0:
            self.iteratePatients( 5 )
            self.updateRewards()
            lazyChild = TreeNode(self.x, self.y, self.searchDepth+1, self.state, self.transitions, self.locations , current_time, simulation_time+5, self.patientIndex, self.taskIndex, 0)
            lazyChild.reward_below = lazyChild.greedyRollout( current_time, simulation_time+5, 0, self.x, self.y, maxRolloutIters )
            lazyChild.cum_reward = lazyChild.reward_below
            self.children.append( lazyChild ) # always have the option not to move
            self.iteratePatients( -5 )
        
    def greedyRollout(self, current_time, sim_time, rollOutIters, curX, curY, maxRolloutIters):
        # simple policy used to evalaute an action by greedily selecting remaining actions through a horizon, selecting actions with highest value (reward - cost)
        
        if rollOutIters >= maxRolloutIters:
            return 0

        self.updateRewards()
        cumReward = np.sum( self.rewards )

        if cumReward > 0:
            maxReward = 1
            maxPatient = -1
            maxTask = -1
            
            for p in range(0,self.num_patients):
                dist = math.sqrt( pow(curX - self.locations[p][0],2) + pow(curY - self.locations[p][1],2) )
                dt = sim_time + dist - current_time
                self.iteratePatients(dt)
                self.updatePatientRewards(p)
                for t in range(0, self.num_tasks):
                    curReward = self.rewards[p][t]*pow(self.discount, dt)
                    if  curReward > maxReward:
                        maxReward = curReward
                        maxPatient = p
                        maxTask = t
                self.iteratePatients(-dt)

            if maxPatient != -1 and maxTask != -1:
                dist = math.sqrt( pow(curX - self.locations[maxPatient][0],2) + pow(curY - self.locations[maxPatient][1],2) )
                dt = sim_time + dist - current_time
                rollOutReward = 0
                self.iteratePatients(dt)
                [priorState, priorReward] = self.completeTask(maxPatient, maxTask)
                rollOutReward = maxReward + self.greedyRollout( current_time, sim_time+dist, rollOutIters+1, self.locations[maxPatient][0], self.locations[maxPatient][1], maxRolloutIters)*pow(self.discount, sim_time)
                self.undoTask( maxPatient, maxTask, priorState, priorReward)
                self.iteratePatients( -dt )
        else:
            self.iteratePatients(5)
            rollOutReward = self.greedyRollout( current_time, sim_time+5, rollOutIters+1, self.x, self.y, maxRolloutIters)*pow(self.discount, sim_time)
            self.iteratePatients( -5 )

        return rollOutReward
    
    def uctSearch(self, current_time, sim_time, maxSearchDepth, maxRollOutIters):
        # use UCT (upper confidence bound for trees) to select child to search
        self.nPulls += 1
        tempValueBelow = -float("inf")
        if self.searchDepth < maxSearchDepth:
            if len(self.children) > 0:
                # if I have children to search
                maxR = max(child.cum_reward for child in self.children)
                minR = min(child.cum_reward for child in self.children)
                
                if maxR == 0:
                    return 0
                bestR = -1
                goldenChild = self.children[0]
                for child in self.children:
                    curR = 0
                    if child.nPulls > 0: # child has been pulled, use UCB
                        val = (child.cum_reward-maxR) / (maxR-minR) # actual value
                        iter = min(1, 1.4142*math.sqrt(math.log(self.nPulls)/child.nPulls) ) # number of trys reward
                        
                        curR = val + iter
                        if curR > bestR:
                            goldenChild = child
                            bestR = curR
                    else: # child has NOT been pulled, pull child
                        goldenChild = child
                        break
                dist = math.sqrt( pow(self.x - goldenChild.x,2) + pow(self.y - goldenChild.y,2) )
                dt = sim_time + dist - current_time
                self.iteratePatients(dt)
                [priorState, priorReward] = self.completeTask(goldenChild.patientIndex, goldenChild.taskIndex)
                tempRewardBelow = goldenChild.uctSearch(current_time, sim_time + dist, maxSearchDepth, maxRollOutIters )
                self.undoTask( goldenChild.patientIndex, goldenChild.taskIndex, priorState, priorReward)
                self.iteratePatients( -dt )
                
            else:
                # don't have children, make some!
                self.findChildren( current_time, sim_time, maxRollOutIters )
                if len(self.children) > 0:
                    tempRewardBelow = max(child.cum_reward for child in self.children)
                else:
                    tempRewardBelow = 0

            # update my value if a child has better value
            if tempRewardBelow > self.reward_below:
                self.reward_below = tempRewardBelow

            self.cum_reward = self.reward + self.reward_below
        
        return self.cum_reward
    
    def greedySearch(self, maxSearchDepth, current_time, sim_time, maxRollOutIters ):
        # select best child to search
        if self.searchDepth < maxSearchDepth:
            tempRewardBelow = -float("inf")
            
            self.iteratePatients(5)
            self.findChildren( current_time, sim_time, maxRollOutIters )
            goldenChild = max(self.children, key=attrgetter('cum_reward') )
            [priorState, priorReward] = self.completeTask(goldenChild.patientIndex, goldenChild.taskIndex)
            self.reward_below = goldenChild.greedySearch( maxSearchDepth, current_time, sim_time+5, maxRollOutIters  )
            self.undoTask( goldenChild.patientIndex, goldenChild.taskIndex, priorState, priorReward)
            self.iteratePatients( -5 )
            self.cum_reward = self.reward +self.reward_below
            return self.cum_reward

        else:
            return 0
    
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




