
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
numTasks = 20;

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
    task = Task([random.random()*10, random.random()*10, 100, t])
    tasks.append( task )
plt.plot([task.x for task in tasks], [task.y for task in tasks], 'ro')

# solve TSP between tasks using MCTS
print("nTasks: ", len(tasks) )
searchIters = 1000
searchMethod = 'UCT' #'UCT', 'Epsilon Greedy', 'Greedy'
searchParam = 0.5

path = robots[0].searchTree( [tasks, searchIters, searchMethod, searchParam])

print("robots[0].path: ", path )
plt.plot( [p[0] for p in path], [p[1] for p in path], 'b' )
plt.show(block=False)

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