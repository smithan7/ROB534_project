
from patient import Patient
from PatientSprite import PatientSprite
from robot import Robot
from doctor import Doctor
from world import World
from vomit import Vomit

import random, time
import numpy as np
import matplotlib.pyplot as plt

import os, pygame
from pomdp import POMDP
from pygame.locals import *

#POMDP set-up
filename_env =  'SDM.pomdp'
filename_policy = 'out.policy'
pomdp = POMDP(filename_env, filename_policy, np.array([[0.5],[0.5]]))

### GUI setup
fps                 = 10        #at most  this many frames per second
back_image          = 'GUI Images/Map1.bmp'   #background image
r_image          = 'GUI Images/pr2.bmp'  #robot image
d_image          = 'GUI Images/dr.bmp'  #doctor image
p_image          = 'GUI Images/patient.bmp'  #patient image
v_image         = 'GUI Images/vomit.bmp' #vomit image 

display_cols        = 800
display_rows        = 610
wall_thickness      = 5         #thickness in pixels
wall_color          = 'black'
color_of_nothing    = 'white'
sim_version         = 'EBOLA ROBOT SIMULATOR EXTREME!!!   '
r_transparency      = 0


main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(name):
    imgs_path = os.path.join(main_dir, name)
    temp_image = pygame.image.load(imgs_path).convert_alpha()  #need this if using ppalpha
    return change_alpha_for_alpha(temp_image, r_transparency) 
    
def change_alpha_for_white(surface,new_alpha):
    size = surface.get_size()
    if size[0]>800 or size[1]>600:
        print('change_alpha_for_white-> size = ', size, ' IMAGE TOO LARGE!')
        return surface
    for y in range(size[1]):
        for x in range(size[0]):
            r,g,b,a = surface.get_at((x,y))
            if r==255 and g==255 and b==255:
                surface.set_at((x,y),(r,g,b,new_alpha))
    return surface

''' Changes alpha for surfaces with per-pixel alpha; only for small surfaces!
    Sets alpha for pixels with alpha == 0 to new_alpha. It is needed b/c
    transform.smoothscale pads image with alpha=0. '''
    
def change_alpha_for_alpha(surface,new_alpha):
    size = surface.get_size()
    for y in range(size[1]):
        for x in range(size[0]):
            r,g,b,a = surface.get_at((x,y))
            if a<200:
                surface.set_at((x,y),(r,g,b,new_alpha))
    return surface

screen = pygame.display.set_mode((display_cols, display_rows))
pygame.init()           #also calls display.init()   
caption = ( 'Time: ' )

background = load_image(back_image)
r_sprite = load_image(r_image)
p_sprite = load_image(p_image)
d_sprite = load_image(d_image)
v_sprite = load_image(v_image)


im_scale_x = (display_cols)/16 #scale world position to image position
im_scale_y = (display_rows)/12

### setup

numPatients = 6
numDoctors = 1
numRobots = 1

world = World([16, 12])

patients = []
patientSprites = []
patients.append(Patient([0, 3, 5]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[0, 3, 5]))
patients.append(Patient([1, 3, 9]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[1,3,9]))
patients.append(Patient([2, 14, 2]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[2,14,2]))
patients.append(Patient([3, 14, 5]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[3,14,5]))
patients.append(Patient([4, 14, 8]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[4,14,8]))
patients.append(Patient([5, 14, 11]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[5,14,11]))

v_spots = []
vSprites = []

doctors = []
for d in range(0, numDoctors):
    doctor = Doctor(d_sprite,im_scale_x,im_scale_y,[d, 2, 2],world,patients,v_spots)
    doctors.append(doctor)

robots = []
for r in range(0, numRobots):
    robot = Robot(r_sprite,im_scale_x,im_scale_y,[r,1,1, 1],world,patients,v_spots)
    robots.append(robot)

#GUI sprites
robotSprite = pygame.sprite.Group(robots[0])
doctorSprite = pygame.sprite.Group(doctors[0])

pSprites = []
for p in patientSprites:
    patientSprite = pygame.sprite.Group(p)
    pSprites.append(patientSprite)

## do things
pygame.display.set_caption(sim_version + caption+ str(0))
robotSprite.update()
doctorSprite.update()
for p in pSprites:
    p.update()
screen.blit(background, (0, 0))  #redraws the entire bkgrnd.
robotSprite.draw(screen)
doctorSprite.draw(screen)
for p in pSprites:
    p.draw(screen)
pygame.display.flip()

# solve TSP between tasks using MCTS
searchIters = 1000
searchMethod = 'UCT' #'UCT', 'Epsilon Greedy', 'Greedy'
searchParam = 0.5 # epsilon for e-greedy

#t_time = 0
#n_samples = 100
#for n in range(0,n_samples):
    # sampled_tasks = robots[0].Tree.sampleTreeEpsilonGreedy([epsilon, task_list, time]) # epsilon, if random(0->1) greater than epsilon choose randomly, else greedy
    #sampled_tasks = robots[0].Tree.sampleTreeUCB([sampled_tasks, t_time, 1, -1]) # uses UCB to sample tree, accounts for unsampled nodes then value, seems smarter ;)


## do things
maxTime = 100
for it_time in range(0, maxTime):
    for d in doctors:
        if not d.performing_action:
            for patient in patients:
                print('Patient[', patient.id,'] IV Level, hunger, vomit, dirty: ', patient.ivLevel,patient.hunger, patient.vomit, patient.dirty)
            action_h = int(input('Choose an action: [0: do nothing, 1: change IV, 2: feed patient, 3: clean patient, 4: clean vomit, 5: check symptoms] '))
            if action_h != 0 :
                patient_num = int(input('Which patient?: '))
            else:
                patient_num = 0
            d.updateAction(action_h,patient_num)
        else:
            d.continueAction()
    
    
    pygame.display.set_caption(sim_version + caption+ str(it_time))
    
    # check robots possible actions
    for robot in robots:
        if not robot.performing_action:
            robot.updatePatients(patients)
            robot.searchTree( [searchIters, searchMethod, searchParam, it_time ])
            path = []
            path = robot.Tree.exploitTree( path )
            print("[patients, tasks]: ", path )
            robot.executeAction( path[-2] )
            robot.createNewTree( it_time )
        else:
            robot.continueAction()

    #calculate human rationality
    obs = 0 #will be range of rationaility 
    pomdp.update_belief(0,obs)
    rational = pomdp.belief[1]
    
    

    # iterate the patient and environment
    for patient in patients:
        patient.iterate(it_time)
    if patient.vomit == True:
            nbr = random.choice([[0,1],[0,-1],[1,0],[-1,0]])
            nbr = [patient.id,nbr[0]+patient.x,nbr[1]+patient.y]
            v_spots.append(Vomit(v_sprite,im_scale_x,im_scale_y,nbr))

    #Update sprites
    vSprites = []
    for v in v_spots:
        vomitSprite = pygame.sprite.Group(v)
        vSprites.append(vomitSprite)
      
    robotSprite.update()
    doctorSprite.update()
    for p in pSprites:
        p.update()
    for v in vSprites:
        v.update()
    screen.blit(background, (0, 0))  #redraws the entire bkgrnd.
    robotSprite.draw(screen)
    doctorSprite.draw(screen)
    for p in pSprites:
        p.draw(screen)
    for v in vSprites:
        v.draw(screen)

        
    time.sleep(.1)
        
    pygame.display.flip()   #all changes are drawn at once (double buffer)
    
## exit pygame ##
pygame.quit()               #also calls display.quit()
            
        




