
from patient import Patient
from robot import Robot
from doctor import Doctor


### setup

numPatients = 2
numDoctors = 1
numRobots = 1

patients = []
for p in range(0, numPatients):
    patient = Patient(p)
    patients.append(patient)

doctors = []
for d in range(0, numDoctors):
    doctor = Doctor([d, 1])
    doctors.append(doctor)

robots = []
for r in range(0, numRobots):
    robot = Robot([r,1, 100])
    robots.append(robot)

## do things

maxTime = 100
for time in range(0, maxTime):
    # check robots possible actions
    for robot in robots:
        for patient in patients:
            if patient.iv.checkLevel() < 5:
                patient.iv.refill()

    # iterate the patient and environment
    for patient in patients:
        patient.iterate()
        print('Patient[', patient.id,'] IV Level: ', patient.iv.level)
        print('Patient[', patient.id,'] status: ', patient.checkStatus() )
