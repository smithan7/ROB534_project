
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
numDoctors = 1
numRobots = 1

world = World([16, 12])

patients = []
patientSprites = []
if  True:
    patients.append(Patient(0, 3, 5, random.randint(20,100), random.randint(20,100)))
    patients.append(Patient(1, 3, 9, random.randint(20,100), random.randint(20,100)))
    patients.append(Patient(2, 14, 2, random.randint(20,100), random.randint(20,100)))
    patients.append(Patient(3, 14, 5, random.randint(20,100), random.randint(20,100)))
    patients.append(Patient(4, 14, 8, random.randint(20,100), random.randint(20,100)))
    patients.append(Patient(5, 14, 11, random.randint(20,100), random.randint(20,100)))
else:
    patients.append(Patient(0, 3, 5, 100, 10))
    patients.append(Patient(1, 3, 9, 10, 10))
    patients.append(Patient(2, 14, 2, 100, 100))
    patients.append(Patient(3, 14, 5, 100, 100))
    patients.append(Patient(4, 14, 8, 100, 100))
    patients.append(Patient(5, 14, 11, 100, 100))

patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[0, 3, 5]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[1,3,9]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[2,14,2]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[3,14,5]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[4,14,8]))
patientSprites.append( PatientSprite(p_sprite,im_scale_x,im_scale_y,[5,14,11]))

v_spots = []
vSprites = []

doctors = []
for d in range(0, numDoctors):
    doctor = Doctor(d_sprite, im_scale_x, im_scale_y, d, 2, 2, len(patients), 4, world, patients, v_spots)
    doctors.append(doctor)

robots = []
for r in range(0, numRobots):
    robot = Robot(r_sprite, im_scale_x, im_scale_y, r, 1, 1, len(patients), 4, world, patients, v_spots)
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
searchMethod = 'UCT' #'UCT', 'Greedy' --- not updated to work 'Epsilon Greedy'
include_rationality = True
searchParam = 0.5 # epsilon for e-greedy

doctors_robot_search_depth = 1
doctors_rollout_depth = 0
doctors_robot_rollout_iters = 0
doctors_robot_search_time = 0.01
doctors_robot_search_iters = 20

doctor_search_depth = 2
doctor_rollout_depth = 2
doctor_rollout_iters = 1
doctor_search_time = 0.2
doctor_search_iters = 400

robot_search_depth = 3
robot_rollout_depth = 2
robot_rollout_iters = 1
robot_search_time = 1.0
robot_search_iters = float("inf")

obs = 0
rational = 0.5

## do things
maxTime = 100
for it_time in range(0, maxTime):
    pygame.event.get()
    for doctor in doctors:
        if not doctor.performing_action:

            for patient in patients:
                print('Patient[', patient.id,'] IV Level, hunger, vomit, dirty: ', patient.ivLevel,patient.hunger, patient.vomit, patient.dirty)

            # build doctor's tree
            doctor.TreeNode.updatePatients( doctor.state, patients )
            doctor.searchTreeNode( doctor_search_time, doctor_search_iters, searchMethod, searchParam, it_time, doctor_search_depth, doctor_rollout_depth, doctor_rollout_iters)
            path = []
            path = doctor.TreeNode.exploitTree( path )
            #print("doctor's path[patients, tasks]: ", path )            
            robots[0].TreeNode.q_prior = doctor.TreeNode.sampleTree(robots[0].TreeNode.q_prob )

            action_h = int(input('Choose an action: [0: do nothing, 1: change IV, 2: feed patient, 3: clean patient, 4: clean vomit, 5: check symptoms] '))
            if action_h != 0 :
                patient_num = int(input('Which patient?: '))
            else:
                patient_num = -1
            doctor.updateAction(action_h,patient_num)

            if include_rationality:
                obs = doctor.TreeNode.getRationality(patient_num, action_h)
                rational = rational + 0.1*(obs-rational)
                #print("rationality: ", rational)
                #pomdp.update_belief(0,obs)
                #rational = pomdp.belief[1]

            doctor.createNewTree( it_time )
        else:
            doctor.continueAction()

    pygame.display.set_caption(sim_version + caption+ str(it_time))
    
    # check robots possible actions
    for robot in robots:
        if not robot.performing_action:
            robot.TreeNode.updatePatients( robot.state, patients )
            robot.update_Q( rational )
            #print("q_prior: ", robot.TreeNode.q_prior)
            #print("q_prob: ", robot.TreeNode.q_prob)

            robot.searchTreeNode( robot_search_time, robot_search_iters, searchMethod, searchParam, it_time, robot_search_depth, robot_rollout_depth, robot_rollout_iters)
            path = []
            path = robot.TreeNode.exploitTree( path )
            robot.createNewTree( it_time )
            #print("robot's path[patients, tasks]: ", path )
            robot.executeAction( path[-2] )
            robot.createNewTree( it_time )
        else:
            robot.continueAction()
    
    

    # iterate the patient and environment
    for patient in patients:
        patient.iterate(it_time)
        if patient.vomit == True and patient.dirty == False:
                nbr = random.choice([[0,1],[0,-1],[1,0],[-1,0]])
                nbr = [patient.id,nbr[0]+patient.x,nbr[1]+patient.y]
                v_spots.append(Vomit(v_sprite,im_scale_x,im_scale_y,nbr))
                patient.dirty = True
                
  
    #Update sprites
    vSprites = []
    for v in v_spots:
        vomitSprite = pygame.sprite.Group(v)
        vSprites.append(vomitSprite)
      
    robotSprite.update()
    doctors[0].rect
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
    # draw the window onto the screen
    
## exit pygame ##
pygame.quit()               #also calls display.quit()
            
        




