
from patient import Patient
from robot import Robot
from doctor import Doctor
from world import World
from task import Task

import random
import numpy as np
import matplotlib.pyplot as plt
### setup

numPatients = 1
numDoctors = 1
numRobots = 2
numTasks = 5

world = World([10, 10])

patients = []
for p in range(0, numPatients):
    patient = Patient([p, 5, 5])
    patients.append(patient)

doctors = []
for d in range(0, numDoctors):
    doctor = Doctor([d, 2, 2])
    doctors.append(doctor)

robots = []
for r in range(0, numRobots):
    robot = Robot([r,1,1, 1])
    robots.append(robot)

tasks = []
for t in range(0, numTasks):
    task = Task([random.random()*10, random.random()*10, random.random()*100, t])
    tasks.append( task )
plt.plot([task.x for task in tasks], [task.y for task in tasks], 'ro')

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
time = 0
n_samples = 100
for n in range(0,n_samples):
    # sampled_tasks = robots[0].Tree.sampleTreeEpsilonGreedy([epsilon, task_list, time]) # epsilon, if random(0->1) greater than epsilon choose randomly, else greedy
    sampled_tasks = robots[0].Tree.sampleTreeUCB([sampled_tasks, time, 1, -1]) # uses UCB to sample tree, accounts for unsampled nodes then value, seems smarter ;)

for task in sampled_tasks:
    task
    s = sum(task.pMine)
    task.index

## do things
maxTime = 0
for time in range(0, maxTime):
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
        print('Patient[', patient.id,'] status: ', patient.checkStatus() )