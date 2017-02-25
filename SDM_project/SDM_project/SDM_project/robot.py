from node import Node


class Robot(object):
    """description of class"""
    def __init__(self, arg):
        self.id = arg[0]
        self.battery = arg[1]
        self.x = arg[2]
        self.y = arg[3]
        self.tasks = []

        self.Tree = Node([self.x, self.y, 0, self.tasks, 0, 0, -1])

    def searchTree( self, args):
        tasks = args[0]
        iters = args[1]
        method = args[2]
        method_param = args[3]
        
        self.Tree.updateTasks(tasks)
            
        if method == 'Epsilon Greedy':
            for i in range(0,iters):
                #print("Progress: ", float(i)/iters)
                self.Tree.epsilonGreedySearch(method_param)
        elif method == 'UCT':
            for i in range(0,iters):
                #print("Progress: ", float(i)/iters)
                self.Tree.uctSearch()
        elif method == 'Greedy':
            for i in range(0,iters):
                #print("Progress: ", float(i)/iters)
                self.Tree.greedySearch()
        else:
            for i in range(0,iters):
                print("no search method given, default to UCT")
                #print("Progress: ", float(i)/iters)
                self.Tree.uctSearch()

        path = []
        path = self.Tree.exploitTree( path )
        return path

    