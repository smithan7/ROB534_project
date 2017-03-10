from node import Node
import math
import pygame
from copy import deepcopy


r_edge           = 51      #edge of square surrounding robot (in pixels)
r_transparency   = 0      #0 is totally transp., 255 totally opaque


class Robot(pygame.sprite.Sprite):
    """description of class"""
    def __init__(self, image,im_scale_x,im_scale_y, arg,world,patients,vomit ):
        self.id = arg[0]
        self.battery = arg[1]
        self.x = arg[2]
        self.y = arg[3]
        self.patients = patients

        self.Tree = Node([self.x, self.y, 0, self.patients, 0, 0, 0, 0, -1, -1])
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
        self.Tree = Node([self.x, self.y, 0, self.patients, 0, 0, arg, arg, -1, -1])

    def updatePatients( self, arg ):
        self.patients = deepcopy( arg )

    def searchTree( self, args):
        iters = args[0]
        method = args[1]
        method_param = args[2]
        current_time = args[3]

        self.Tree.updatePatients(self.patients)
            
        if method == 'Epsilon Greedy':
            for i in range(0,iters):
                #print("Progress: ", float(i)/iters)
                self.Tree.epsilonGreedySearch([method_param, current_time])
        elif method == 'UCT':
            for i in range(0,iters):
                #print("Progress: ", float(i)/iters)
                self.Tree.uctSearch( [current_time, current_time] )
        elif method == 'Greedy':
            for i in range(0,iters):
                #print("Progress: ", float(i)/iters)
                self.Tree.greedySearch( current_time )
        else:
            for i in range(0,iters):
                print("no search method given, default to UCT")
                #print("Progress: ", float(i)/iters)
                self.Tree.uctSearch( [current_time, current_time] )

    def move(self,x,y):
        self.rect.center = (x*self.im_scale_x-self.im_scale_x/2,y*self.im_scale_y-self.im_scale_y/2)
        self.x = x
        self.y = y
    
    def executeAction( self, arg ):
        p = arg[0]
        t = arg[1]

        if t == -1:
            print("Robot did nothing")
            self.updateAction(0,-1)
        elif t==0:
            print("Robot changing patient ", p, "'s IV")
            self.updateAction(1,p)
        elif t==1:
            print("Robot feeding patient ", p )
            self.updateAction(2,p)
        elif t==2:
            print("Robot cleaning up vomit near patient ", p )
            self.updateAction(4,p)
        elif t==3:
            print("Robot cleaning up patient ", p)
            self.updateAction(3,p)
    
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
            patient.ivLevel = 100
            self.performing_action = False
        
        
    def feedPatient(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('Robot fed patient')
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
            
    def checkSymptoms(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print('Robot checked symptoms')
            self.performing_action = False

    
