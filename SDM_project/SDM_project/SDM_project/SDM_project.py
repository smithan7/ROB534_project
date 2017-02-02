
from patient import Patient
from robot import Robot
from doctor import Doctor
from world import World

### setup

numPatients = 1
numDoctors = 1
numRobots = 1

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

## do things

maxTime = 100
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