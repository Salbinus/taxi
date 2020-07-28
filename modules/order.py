import pandas as pd
import numpy as np
from scipy import stats

class Order(object):
    __slots__ = ('_begin_p', '_end_p', '_begin_t',
                 '_t', '_p', '_waiting_time', '_assigned_time')

    def __init__(self, begin_position, end_position, begin_time, duration, price, wait_time):
        self._begin_p = begin_position  # node
        self._end_p = end_position      # node
        self._begin_t = begin_time
        # self._end_t = end_time
        self._t = duration              # the duration of order.
        self._p = price
        self._waiting_time = wait_time  # a order can last for "wait_time" to be taken
        self._assigned_time = -1

    def get_begin_position(self):
        return self._begin_p

    def get_begin_position_id(self):
        return self._begin_p.get_node_index()

    def get_end_position(self):
        return self._end_p

    def get_begin_time(self):
        return self._begin_t

    def set_assigned_time(self, city_time):
        self._assigned_time = city_time

    def get_assigned_time(self):
        return self._assigned_time

    # def get_end_time(self):
    #     return self._end_t

    def get_duration(self):
        return self._t

    def get_price(self):
        return self._p

    def get_wait_time(self):
        return self._waiting_time
    




    def get_orders(self):
        time, location, lookup_table, orders =self.time, self.location, self.lookup_table, self.orders
        mean,sd,_min,_max = lookup_table.loc[(location, time), :]
        population = orders[(orders[:,0] == location) & (orders[:,2] == time)]
        amount_of_samples = round(stats.truncnorm.rvs(_min, _max, loc=mean, scale=sd, size=1)[0])
        indices = np.random.choice(population.shape[0], amount_of_samples, replace=False)
        return population[indices]