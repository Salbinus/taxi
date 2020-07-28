import h3.api.numpy_int as h3
import pandas as pd
import numpy as np
import os, sys
sys.path.append(os.path.abspath('../data'))
from modules.node import Node
from modules.orders import Orders

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
                , 'taxis']

    def __init__(self, geoJson, resolution=9):
        self.geoJson = geoJson
        self.resolution = resolution
        self.polyline = self.geoJson['coordinates'][0]
        self.polyline.append(self.polyline[0])
        self.hexagons = list(h3.polyfill(geoJson, resolution))
        self.nodes = [Node(node_id) for node_id in self.hexagons]
        self.city_time = 0
        self.orders = np.load(os.path.abspath('data/prep_data.npy'))
        self.lookup_table = pd.read_pickle(os.path.abspath('data/lookup_table.pkl'))

        self.max_timesteps = 143
        self.days = 2

        self.taxis = {}

    def generate_orders(self):
        '''Generates orders per timestep per node'''
        for node in self.nodes:
            orders = Orders(self.city_time, node.get_node_id(), self.lookup_table, self.orders)
            node.set_orders(orders)
            print(node.get_orders())
    
    def initialize_taxis(self):
        pass


    def update_time(self):
        '''Updates city_time in the environment'''
        self.city_time += 1

    def step(self):
        '''
        Everything what should happen per timestep is declared here. Initially, the 
        nested for loops are placed here but will be replaced later.
        '''
        for day in range(self.days):
            for time in range(self.max_timesteps):
                self.generate_orders()
                self.update_time()