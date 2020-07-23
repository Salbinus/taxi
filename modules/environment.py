import h3.api.numpy_int as h3
from node import Node

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
    __slots__ = ['geoJson', 'resolution', 'polyline', 'hexagons', 'nodes', 'city_time']

    def __init__(self, geoJson, resolution=9):
        self.geoJson = geoJson
        self.resolution = resolution
        self.polyline = self.geoJson['coordinates'][0]
        self.polyline.append(self.polyline[0])
        self.hexagons = list(h3.polyfill(geoJson, resolution))
        self.nodes = [Node(node_id) for node_id in self.hexagons]
        self.city_time = 0
        #self.fleet_size = None
        #self.taxis = {}

