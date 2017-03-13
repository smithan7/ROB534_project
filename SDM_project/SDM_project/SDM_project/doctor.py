import pygame
import numpy as np
from treeNode import TreeNode
import time

d_edge           = 51      #edge of square surrounding robot (in pixels)
d_transparency   = 0      #0 is totally transp., 255 totally opaque

class Doctor(pygame.sprite.Sprite):

    transitions = np.ones((6,4))
    state = np.full( (6,4), -float("inf") )
    rewards = np.zeros((6,4))
    q_prop = np.zeros((6,4))
    locations = np.array([ [3,5], [3,9], [14,2],[14,5],[14,8],[14,11] ])

    for i in range(0,6):
        transitions[i][0] = -1
        transitions[i][1] = -1
        state[i][0] = 100
        state[i][1] = 100

    """description of class"""
    def __init__(self, image,im_scale_x,im_scale_y, arg,world,patients,vomit):
        self.id = arg[0]
        self.x = arg[1]
        self.y = arg[2]
        
        #GUI stuff
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        #Sprites must have an image and a rectangle
        self.image          = image
        self.image_original = self.image    #unchanging copy, for rotations
        self.rect           = image.get_rect()
        self.rect_original  = self.rect     #unchanging copy, for rotations
        self.rect.center = (self.x*im_scale_x-im_scale_x/2, self.y*im_scale_y-im_scale_y/2) # set starting position
        self.im_scale_x = im_scale_x
        self.im_scale_y = im_scale_y
        
        self.TreeNode = TreeNode(self.x, self.y, 0, self.state, self.transitions, self.locations, 0, 0, -1,-1)

        self.world  = world
        self.patients = patients
        self.performing_action = False
        self.action = 0
        self.patient_num = 0
        self.vomit = vomit

        
        
    def move(self,x,y):
        self.rect.center = (x*self.im_scale_x-self.im_scale_x/2,y*self.im_scale_y-self.im_scale_y/2)
        self.x = x
        self.y = y
        
    def updateAction(self,action,patient_num):
        self.action = action
        self.patient_num = patient_num
        
        self.performing_action = True
        if action ==0:
           print("YOU DID NOTHING.")
        elif action ==1:
            self.changeIV(self.patient_num)
        elif action == 2:
            self.feedPatient(self.patient_num)
        elif action ==3:
            self.cleanPatient(self.patient_num)
        elif action ==4:
            self.cleanVomit(self.patient_num)
        elif action ==5:
            self.checkSymptoms(self.patient_num)
            
    def continueAction(self):
        if self.action ==0:
           print("YOU DID NOTHING.")
           self.performing_action = False
        elif self.action ==1:
            self.changeIV(self.patient_num)
        elif self.action == 2:
            self.feedPatient(self.patient_num)
        elif self.action ==3:
            self.cleanPatient(self.patient_num)
        elif self.action ==4:
            self.cleanVomit(self.patient_num)
        elif self.action ==5:
            self.checkSymptoms(self.patient_num)
        
    def changeIV(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('YOU MADE IT')
            self.patients[(patient_num)].ivLevel = 100
            self.performing_action = False
        
        
    def feedPatient(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('YOU MADE IT')
            self.patients[(patient_num)].hunger = 100
            self.performing_action = False
       
        
    def cleanPatient(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('YOU MADE IT')
            self.performing_action = False
  
    def cleanVomit(self,v_pos):
        vom = -1
        for v in self.vomit:
            if v.id == v_pos:
                vom = v
        if vom == -1:
            print("Patient ",v_pos, " has not vomitted.")
            self.performing_action = False
            return
        [path, path_length] = self.world.aStar([self, vom, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('YOU MADE IT')
            self.performing_action = False
            self.vomit.remove(vom)
            self.patients[v_pos].dirty= False
            

        
    def checkSymptoms(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('YOU MADE IT')
            self.performing_action = False


    def searchTreeNode( self, args):
        search_time = args[0]
        method = args[1]
        method_param = args[2]
        current_time = args[3]

        start_time = time.clock()
        if method == 'Epsilon Greedy':
            while time.clock() - start_time < search_time:
                #print("Progress: ", float(i)/iters)
                self.TreeNode.epsilonGreedySearch([method_param, current_time])
        elif method == 'UCT':
            while time.clock() - start_time < search_time:
                #print("Progress: ", float(i)/iters)
                self.TreeNode.uctSearch( [current_time, current_time] )
        elif method == 'Greedy':
            while time.clock() - start_time < search_time:
                #print("Progress: ", float(i)/iters)
                self.TreeNode.greedySearch( current_time )
        else:
            while time.clock() - start_time < search_time:
                print("no search method given, default to UCT")
                #print("Progress: ", float(i)/iters)
                self.TreeNode.uctSearch( [current_time, current_time] )
        print(" Time to search: ", time.clock() - start_time)

