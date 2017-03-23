import pygame


p_edge           = 51     #edge of square surrounding robot (in pixels)
p_transparency   = 0      #0 is totally transp., 255 totally opaque

class PatientSprite(pygame.sprite.Sprite):
    """description of class""" 
    def __init__(self,image,im_scale_x,im_scale_y, arg):

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