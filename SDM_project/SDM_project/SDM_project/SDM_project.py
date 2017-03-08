
from patient import Patient
from robot import Robot
from doctor import Doctor
from world import World
from task import Task
from vomit import Vomit

import random, time
import numpy as np
import matplotlib.pyplot as plt

import os, pygame
from pygame.locals import *

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
        print 'change_alpha_for_white-> size = ', size, ' IMAGE TOO LARGE!'
        return surface
    for y in xrange(size[1]):
	for x in xrange(size[0]):
	    r,g,b,a = surface.get_at((x,y))
	    if r==255 and g==255 and b==255:
                surface.set_at((x,y),(r,g,b,new_alpha))
    return surface

''' Changes alpha for surfaces with per-pixel alpha; only for small surfaces!
    Sets alpha for pixels with alpha == 0 to new_alpha. It is needed b/c
    transform.smoothscale pads image with alpha=0. '''
    
def change_alpha_for_alpha(surface,new_alpha):
    size = surface.get_size()
    for y in xrange(size[1]):
	for x in xrange(size[0]):
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
numRobots = 2
numTasks = 5

world = World([16, 12])

patients = []
#for p in range(0, numPatients):
#    patient = Patient([p, 5, 5])
#    patients.append(patient)
patient1 = Patient(p_sprite,im_scale_x,im_scale_y,[1, 3, 5])
patients.append(patient1)

patient2 = Patient(p_sprite,im_scale_x,im_scale_y,[2, 3, 9])
patients.append(patient2)

patient3 = Patient(p_sprite,im_scale_x,im_scale_y,[3, 14, 2])
patients.append(patient3)

patient4 = Patient(p_sprite,im_scale_x,im_scale_y,[4, 14, 5])
patients.append(patient4)

patient5 = Patient(p_sprite,im_scale_x,im_scale_y,[5, 14, 8])
patients.append(patient5)

patient6 = Patient(p_sprite,im_scale_x,im_scale_y,[6, 14, 11])
patients.append(patient6)

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

tasks = []
for t in range(0, numTasks):
    task = Task([random.random()*10, random.random()*10, random.random()*100, t])
    tasks.append( task )
plt.plot([task.x for task in tasks], [task.y for task in tasks], 'ro')


#GUI sprites
robotSprite = pygame.sprite.Group(robots[0])
doctorSprite = pygame.sprite.Group(doctors[0])

pSprites = []
for p in patients:
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
print("nTasks: ", len(tasks) )
searchIters = 1000
searchMethod = 'UCT' #'UCT', 'Epsilon Greedy', 'Greedy'
searchParam = 0.5 # epsilon for e-greedy

path = robots[0].searchTree( [tasks, searchIters, searchMethod, searchParam])
print("robots[0].path: ", path )
plt.plot( [p[0] for p in path], [p[1] for p in path], 'b' )
plt.show(block=False)

sampled_tasks = list( tasks )
t_time = 0
n_samples = 100
for n in range(0,n_samples):
    # sampled_tasks = robots[0].Tree.sampleTreeEpsilonGreedy([epsilon, task_list, time]) # epsilon, if random(0->1) greater than epsilon choose randomly, else greedy
    sampled_tasks = robots[0].Tree.sampleTreeUCB([sampled_tasks, t_time, 1, -1]) # uses UCB to sample tree, accounts for unsampled nodes then value, seems smarter ;)

for task in sampled_tasks:
    task
    s = sum(task.pMine)
    task.index

## do things
maxTime = 100
for it_time in range(0, maxTime):
    for d in doctors:
        if not d.performing_action:
            action_h = int(raw_input('Choose an action: [0: do nothing, 1: change IV, 2: feed patient, 3: clean patient, 4: clean vomit, 5: check symptoms] '))
            if action_h != 0 :
                patient_num = int(raw_input('Which patient?: '))
            else:
                patient_num = 0
            d.updateAction(action_h,patient_num)
        else:
            d.continueAction()
    
    
    pygame.display.set_caption(sim_version + caption+ str(it_time))
    
    # check robots possible actions
    for robot in robots:
        for patient in patients:
            [path, path_length] = world.aStar([robot, patient, 5])
            if patient.iv.checkLevel() < path_length:
                patient.iv.refill()

    # iterate the patient and environment
    for patient in patients:
        patient.iterate()
        print('Patient[', patient.id,'] IV Level: ', patient.iv.level)
        print('                 hunger: ',patient.hunger)
        print('Patient[', patient.id,'] status: ', patient.checkStatus() )
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
            
        




