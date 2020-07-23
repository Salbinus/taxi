import os, sys
sys.path.append(os.path.abspath('../modules'))
from modules.environment import CitySim

geoJson = {'type': 'Polygon',
 'coordinates': [[[40.742239, -74.008574],
                  [40.731461, -73.982515],
                  [40.770477, -73.950370], 
                  [40.782619, -73.980991]
                 ]]}
m = CitySim(geoJson)

ids = []
for node in m.nodes:
    print(node.node_id)