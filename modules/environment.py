import h3.api.numpy_int as h3
import pandas as pd
import numpy as np
from scipy import stats
import os, sys
import random
sys.path.append(os.path.abspath('../data'))
from modules.node import Node
from modules.order import Order
from modules.taxi import Taxi


class CitySim:
    '''
    This class represents the area where taxis have to be dispatched
    and the size of the hexagons.
    
    :param: geoJson - a nested list of coordinates e.g.
                    geoJson = {'type':      'Polygon',
                               'coordinates': [[[40.742239, -74.008574],
                                                [40.731461, -73.982515],
                                                [40.770477, -73.950370], 
                                                [40.782619, -73.980991]]]}
    
    :param: resolution - specifies the edge size of each hexagon. Default 
                         is 9 with edge length ~ 173 meter
    '''
    __slots__ = ['geoJson', 'resolution', 'polyline', 'hexagons', 'nodes'
                , 'city_time', 'lookup_table', 'orders', 'max_timesteps', 'days'
                , 'num_taxis', 'taxis', 'valid_nodes']

    def __init__(self, geoJson, resolution=9):
        self.geoJson = geoJson
        self.resolution = resolution
        self.polyline = self.geoJson['coordinates'][0]
        self.polyline.append(self.polyline[0])
        self.hexagons = list(h3.polyfill(geoJson, resolution))
        self.lookup_table = pd.read_pickle(os.path.abspath('data/lookup_table.pkl'))
        self.valid_nodes = list(self.lookup_table.index.levels[0])#[50:60]
        self.nodes = [Node(node_id) for node_id in self.valid_nodes]#[50:60]
        self.city_time = 0
        self.orders = np.load(os.path.abspath('data/prep_data.npy'))
        self.max_timesteps = 143
        self.days = 2
        #self.num_taxis = 5
        self.taxis = None #[Taxi(_id) for _id in range(self.num_taxis)]
        self.set_node_neighbors()

    def set_node_neighbors(self):
        '''
        initial mapping of the grid
        '''
        for node in self.nodes:
            nb_ids = node.get_layers_neighbors(1)[1]
            nbs = [node for node in self.nodes if node.node_id in nb_ids]
            node.set_neighbors(nbs)

    def generate_orders(self, location):
        '''
        This function generates the available orders per timestep.
        '''
        time, lookup_table, orders = self.city_time, self.lookup_table, self.orders
        population = np.zeros((1,6))
        try:
            mean, sd, _min, _max = lookup_table.loc[(location, time), :]
            population = orders[(orders[:,0] == location) & (orders[:,2] == time)]
        except:
            'KeyError:'
        if np.sum(population) == 0:
            #print(population, "No orders here at {}".format(time))
            return population
        else:
            amount_of_samples = np.random.poisson(mean)
            if amount_of_samples > len(population):
                amount_of_samples = len(population) #limit amount_of_samples to the length of all available orders at this timestep
            indices = np.random.choice(population.shape[0], int(amount_of_samples), replace=False)
            return population[indices]

    def get_observation(self):
        '''
        Generates orders for all nodes
        TODO:   create this as class variable, acces it later to get the actual number 
                number of orders (which is known later when action space it set for 
                each individual node)
        '''
        observation = []
        for node in self.nodes:
            orders = self.generate_orders(node.node_id)#Order(self.city_time, node.get_node_id(), self.lookup_table, self.orders)
            node.set_orders(orders)
            node.set_taxis(self.taxis)
            n_taxis = len(node.taxis)
            obs = [node.node_id, self.city_time, n_taxis, len(orders)]
            observation.append(obs)
            # print(obs)
        return observation

    def get_action_space(self, direct_dispatch=True):
        for node in self.nodes:
            node.actionspace = node.get_available_orders()
            if direct_dispatch == True:
                node.random_dispatcher()
            #print(node.node_id, actions)

    def initialize_taxis(self, num_taxis):
        self.taxis = [Taxi(_id) for _id in range(num_taxis)]
        node_ids = self.valid_nodes#[node.node_id for node in self.nodes]
        for taxi in self.taxis:
            taxi.set_position(random.choice(node_ids))
            #print(taxi.node)

    def random_dispatch(self):
        return

    def update_time(self):
        '''Updates city_time in the environment'''
        self.city_time += 1

    def step(self):
        '''
        Everything what should happen per timestep is declared here.
        '''
        
        self.get_observation()
        self.update_time()
        self.get_action_space()
        #return next_state, reward, done, info

    def reset(self):
        assert self.city_time == 0, "the reset method is exclusive for the first interval"
        #self.initialize_taxis()
        #for taxi in self.taxis
        self.get_observation()
        self.get_action_space()

        