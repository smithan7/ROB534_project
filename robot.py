from node import Node
from treeNode import TreeNode
import math
import pygame
import time
import numpy as np

r_edge           = 51      #edge of square surrounding robot (in pixels)
r_transparency   = 0      #0 is totally transp., 255 totally opaque


class Robot(pygame.sprite.Sprite):
    
    """description of class"""
    def __init__(self, image,im_scale_x,im_scale_y, id, x, y, num_patients, num_tasks,world,patients,vomit ):
        self.id = id
        self.x = x
        self.y = y
        self.patients = patients

        self.transitions = np.ones((num_patients, num_tasks))
        self.state = np.full( (num_patients, num_tasks), -float("inf") )
        self.rewards = np.zeros((num_patients, num_tasks))
        self.locations = np.array([ [3,5], [3,9], [14,2],[14,5],[14,8],[14,11] ])

        for i in range(0,num_patients):
            self.transitions[i][0] = -1
            self.transitions[i][1] = -1
            self.state[i][0] = 100 # hunger and iv level's default to full
            self.state[i][1] = 100

        self.TreeNode = TreeNode(self.x, self.y, 0, self.state, self.transitions, self.locations, 0, 0, -1,-1, 0)
        #self.Tree = Node([self.x, self.y, 0, self.patients, 0, 0, 0, 0, -1, -1])

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
        
              
        self.world  = world
        self.performing_action = False
        self.action = 0
        self.patient_num = 0
        self.vomit = vomit

    def createNewTree( self, arg ):
        self.TreeNode = TreeNode(self.x, self.y, 0, self.state, self.transitions, self.locations, 0, 0, -1,-1, 0)

    def updatePatients( self, patients ):
        self.patients = deepcopy( patients )

    def update_Q( self, rationality ):
        self.TreeNode.update_Q_WRT_rationality( rationality )

    def searchTreeNode( self, search_time, search_iters, method, method_param, current_time, search_depth, rollout_depth, rollout_iters):

        start_time = time.clock()
        search_iters = 0
        if method == 'Epsilon Greedy':
            while time.clock() - start_time < search_time:
                #print("Progress: ", float(i)/iters)
                search_iters += 1
                self.TreeNode.epsilonGreedySearch(method_param, current_time)
        elif method == 'UCT':
            while time.clock() - start_time < search_time:
                #print("Progress: ", float(i)/iters)
                search_iters += 1
                self.TreeNode.uctSearch(current_time, current_time, search_depth, rollout_depth)
        elif method == 'Greedy':
                self.TreeNode.greedySearch( search_depth, current_time, current_time, rollout_depth )
        else:
            while time.clock() - start_time < search_time:
                print("no search method given, default to UCT")
                #print("Progress: ", float(i)/iters)
                search_iters += 1
                self.TreeNode.uctSearch(current_time, current_time, search_depth, rollout_depth )
        print("Robot time to search[", search_iters, "]: ", time.clock() - start_time)

    def move(self,x,y):
        self.rect.center = (x*self.im_scale_x-self.im_scale_x/2,y*self.im_scale_y-self.im_scale_y/2)
        self.x = x
        self.y = y
    
    def executeAction( self, args ):
        patient = args[0]
        task = args[1]
        if task == -1:
            print("Robot did nothing")
            self.updateAction(0,-1)
        elif task==0:
            print("Robot changing patient ", patient, "'s IV")
            self.updateAction(1,patient)
        elif task==1:
            print("Robot feeding patient ", patient )
            self.updateAction(2,patient)
        elif task==2:
            print("Robot cleaning up vomit near patient ", patient )
            self.updateAction(4,patient)
        elif task==3:
            print("Robot cleaning up patient ", patient)
            self.updateAction(3,patient)
    
    def updateAction(self,action,patient_num):
        self.action = action
        self.patient_num = patient_num
        
        self.performing_action = True
        if action ==0:
           print("Robot does nothing.")
           self.performing_action = False
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
           print("Robot does nothing.")
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
            print('Robot filled IV')
            self.patients[patient_num].ivLevel = 100
            self.performing_action = False
        
        
    def feedPatient(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('Robot fed patient')
            self.patients[(patient_num)].hunger = 100
            self.performing_action = False
       
        
    def cleanPatient(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('Robot cleaned patient')
            self.performing_action = False
            patient.dirty_time = -float("inf")
            self.dirty = False

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
            print('Robot cleaned vomit')
            self.performing_action = False
            self.vomit.remove(vom)
            self.patients[v_pos].dirty= False
            self.patients[v_pos].vomit_time = -float("inf")
            
    def checkSymptoms(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('Robot checked symptoms')
            self.performing_action = False

    
