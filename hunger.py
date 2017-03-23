import pygame, sys, random, math
from pygame.locals import *
from button import Button

class Hunger(object):
    """description of class"""
    def __init__(self, x, y, r, level, full, dripMean, dripVar):
        self.x = x
        self.y = y
        self.r = r
        self.button = button(x+10,y-10,15)
        self.level = level
        self.full = full
        self.dripMean = dripMean
        self.dripVar = dripVar

    def iterate(self, dt):
        self.level -= dt * random.normalvariate(self.dripMean, self.dripVar)

    def checkReward(self, dt):
        test = self.level - dt * random.normalvariate(self.dripMean, self.dripVar)
        if test < 0:
            reward = -100
        else:
            reward = 0

    def complete(self):
        self.level = self.full

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 255), ( round(self.x), round(self.y) ), self.r, 0)