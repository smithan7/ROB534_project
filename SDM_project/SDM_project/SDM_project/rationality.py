from fuzzy_bin import fuzzy_bin
import numpy as np

class rationality(object):
    """description of class"""

    bins = []


    def __init__(self):

        self.bins.append( fuzzy_bin( (0,0), (0,1), (0.5,0) ) )
        self.bins.append( fuzzy_bin( (0,0), (0.5,1), (1,0) ) )
        self.bins.append( fuzzy_bin( (0,0), (1,0.5), (1,0) ) )


    def weight_values( self, values, rat ):

        v_max = np.amax( values )
        # ensure there is something to do!
        if v_max == 0:
            return values

        v_min = np.amin( values )
        v_mean = np.mean( values )
        v_sum = np.sum ( values )
        w = [0.0]*len( self.bins )
        r_sum = np.zeros((6,4))

        for b, bin in enumerate(self.bins):
                w[b] = bin.getWeight( rat )

        for p, patient in enumerate(values):
            for t, task in enumerate( patient ):        
                r_rand = w[0]*1 / 24
                r_weighted = w[1]*( float(task)/ float(v_sum) )
                if task == v_max:
                    r_opt = w[2]
                else:
                    r_opt = 0
            
                r_sum[p][t] = r_rand + r_weighted + r_opt

        return r_sum