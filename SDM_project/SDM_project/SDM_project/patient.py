from ivBag import IvBag
import pygame
import random

p_edge           = 51     #edge of square surrounding robot (in pixels)
p_transparency   = 0      #0 is totally transp., 255 totally opaque

class Patient(pygame.sprite.Sprite):
    """description of class""" 
    def __init__(self,image,im_scale_x,im_scale_y, arg):
        self.id = arg[0]
        self.x = arg[1]
        self.y = arg[2]
        self.iv = IvBag([100.0, 100.0, 1.5, 0.5])
        
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
        self.hunger = 100
        self.vomit = False
        self.dirty = False
        

        
        
        
    def move(self,x,y):
        self.rect = self.rect.move(x*self.im_scale_x-self.im_scale_x/2,y*self.im_scale_y-self.im_scale_y/2)
        self.x = self.rect.center[0]/self.im_scale_x-self.im_scale_x/2
        self.y = self.rect.center[1]/self.im_scale_y-self.im_scale_y/2
        
    def iterate(self):
        self.iv.drip()
        self.hunger -= 1
        if self.hunger > 50:
           v = random.random()
           if v < .1 and self.dirty == False:
               print "Patient " ,self.id, " vomitted"
               self.vomit = True
               self.dirty = True
               self.hunger -= 30
           else:
               self.vomit = False
        
               
               
            

    def checkStatus(self):
        if self.iv.level > 0:
            return 0.0
        else:
            return -1.0
