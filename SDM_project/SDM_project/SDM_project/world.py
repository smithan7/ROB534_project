import math
from State import State
import numpy as np

class World(object):
    """description of class"""
    def __init__(self, arg):
        self.width = arg[0]
        self.height = arg[1]

        self.map = np.zeros([self.width, self.height])
        self.obstacle = 1
        self.free = 0


    def aStar(self, arg):
        start = State([arg[0].x, arg[0].y]) # state
        goal = State([arg[1].x, arg[1].y]) # state
        epsilon = arg[2]

        start.g = 0
        start.f = epsilon * self.heuristic( [start, goal] )
        print("start: ", start.x, ", ", start.y)
        print("goal: ", goal.x, ", ", goal.y)

        o_set = []
        c_set = []
        o_set.append( start )


        while len(o_set) > 0:
            c = self.getMindex(o_set)
            current = o_set[c]
            o_set.remove(current)
            c_set.append( current )

            if abs(current.x - goal.x) +  abs(current.y - goal.y) < 1:
                path = []
                length = 0
                path.append(current)
                while abs(current.x - start.x) +  abs(current.y - start.y) > 0.1:
                    prev = current.cameFrom
                    path.append( prev )
                    length += self.heuristic([prev, current])
                    current = prev

                path.reverse()
                return [path, length]

            nbrs = self.getNbrs( current )
            

            for nbr in nbrs:
                if self.map[nbr.x, nbr.y] == self.free and not self.inList([c_set, nbr]):
                    if not self.inList([o_set, nbr]):
                        nbr.g = current.g + 1
                        nbr.f = nbr.g + epsilon * self.heuristic([nbr, goal])
                        nbr.cameFrom = current
                        o_set.append( nbr )
                    elif nbr.g > current.g + 1:
                        nbr.g = current.g + 1
                        nbr.f = nbr.g + epsilon * self.heuristic([nbr, goal])
                        nbr.cameFrom = current
        
        return [-1, float("inf")]

    def inList(self, arg):
        list = arg[0]
        item = arg[1]

        for s in list:
            if s.x == item.x and s.y == item.y:
                return True

        return False

    def getNbrs(self, arg):
        c = State([arg.x, arg.y])
        nbrs = []
        
        nx = [-1,-1,-1, 0,0, 1,1,1]
        ny = [-1, 0, 1,-1,1,-1,0,1]

        for x,y in zip(nx, ny):
            n = State([c.x+x, c.y+y])
            if n.x > -1 and n.x < self.width and n.y > -1 and n.y < self.height and self.map[n.x, n.y] == self.free:
                nbrs.append( n )

        return nbrs

            
    def getMindex(self, arg):
        set = arg
        min = float("inf")
        mindex = -1
        for i, s in enumerate(set):
            if s.f < min:
                min = s.f
                mindex = i

        return mindex

    def heuristic(self, arg):
        return math.sqrt(math.pow(arg[0].x - arg[1].x,2) + pow(arg[0].y - arg[1].y,2))