from node import Node
import pygame


r_edge           = 51      #edge of square surrounding robot (in pixels)
r_transparency   = 0      #0 is totally transp., 255 totally opaque


class Robot(pygame.sprite.Sprite):
    """description of class"""
    def __init__(self, image,im_scale_x,im_scale_y, arg,world,patients,vomit):
        self.id = arg[0]
        self.battery = arg[1]
        self.x = arg[2]
        self.y = arg[3]
        self.tasks = []

        self.Tree = Node([self.x, self.y, 0, self.tasks, 0, 0, -1])
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
        self.patients = patients
        self.performing_action = False
        self.action = 0
        self.patient_num = 0
        self.vomit = vomit

    def searchTree( self, args):
        tasks = args[0]
        iters = args[1]
        method = args[2]
        method_param = args[3]
        
        self.Tree.updateTasks(tasks)
            
        if method == 'Epsilon Greedy':
            for i in range(0,iters):
                #print("Progress: ", float(i)/iters)
                self.Tree.epsilonGreedySearch(method_param)
        elif method == 'UCT':
            for i in range(0,iters):
                #print("Progress: ", float(i)/iters)
                self.Tree.uctSearch()
        elif method == 'Greedy':
            for i in range(0,iters):
                #print("Progress: ", float(i)/iters)
                self.Tree.greedySearch()
        else:
            for i in range(0,iters):
                print("no search method given, default to UCT")
                #print("Progress: ", float(i)/iters)
                self.Tree.uctSearch()

        path = []
        path = self.Tree.exploitTree( path )
        return path

    def move(self,x,y):
        self.rect.center = (x*self.im_scale_x-self.im_scale_x/2,y*self.im_scale_y-self.im_scale_y/2)
        self.x = x
        self.y = y
        
    def updateAction(self,action,patient_num):
        self.action = action
        self.patient_num = patient_num-1
        
        self.performing_action = True
        if action ==0:
           print "YOU DID NOTHING."
        elif action ==1:
            self.changeIV(self.patient_num)
        elif action == 2:
            self.feedPatient(self.patient_num)
        elif action ==3:
            self.cleanPatient(self.patient_num)
        elif action ==4:
            self.cleanVomit(self.patient_num+1)
        elif action ==5:
            self.checkSymptoms(self.patient_num)
            
    def continueAction(self):
        if self.action ==0:
           print "YOU DID NOTHING."
           self.performing_action = False
        elif self.action ==1:
            self.changeIV(self.patient_num)
        elif self.action == 2:
            self.feedPatient(self.patient_num)
        elif self.action ==3:
            self.cleanPatient(self.patient_num)
        elif self.action ==4:
            self.cleanVomit(self.patient_num+1)
        elif self.action ==5:
            self.checkSymptoms(self.patient_num)
        
    def changeIV(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print 'YOU MADE IT'
            patient.iv.refill()
            self.performing_action = False
        
        
    def feedPatient(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print 'YOU MADE IT'
            self.performing_action = False
       
        
    def cleanPatient(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print 'YOU MADE IT'
            self.performing_action = False
  
    def cleanVomit(self,v_pos):
        vom = -1
        for v in self.vomit:
            if v.id == v_pos:
                vom = v
        if vom == -1:
            print "Patient ",v_pos, " has not vomitted."
            self.performing_action = False
            return
        [path, path_length] = self.world.aStar([self, vom, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print 'YOU MADE IT'
            self.performing_action = False
            self.vomit.remove(vom)
            self.patients[v_pos-1].dirty= False
            

        
    def checkSymptoms(self,patient_num):
        patient = self.patients[(patient_num)]
        [path, path_length] = self.world.aStar([self, patient, 5])
        if path_length > 0:
            move = path.pop(0)
            self.move(move.x,move.y)
        else:
            print 'YOU MADE IT'
            self.performing_action = False

    
