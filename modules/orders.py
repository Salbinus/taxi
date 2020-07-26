import pandas as pd
import numpy as np
from scipy import stats

class Orders:
    #__slots__ = ()
    def __init__(self, time, location, lookup_table, orders):
        self.time = time
        self.location = location
        self.lookup_table = lookup_table
        self.orders = orders
    
    def get_orders(self):
        time, location, lookup_table, orders =self.time, self.location, self.lookup_table, self.orders
        mean,sd,_min,_max = lookup_table.loc[(location, time), :]
        population = orders[(orders[:,0] == location) & (orders[:,2] == time)]
        amount_of_samples = round(stats.truncnorm.rvs(_min, _max, loc=mean, scale=sd, size=1)[0])
        indices = np.random.choice(population.shape[0], amount_of_samples, replace=False)
        return population[indices]

