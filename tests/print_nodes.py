import os, sys
sys.path.append(os.path.abspath('../modules'))
from modules.environment import CitySim
import time

geoJson = {'type': 'Polygon',
 'coordinates': [[[40.742239, -74.008574],
                  [40.731461, -73.982515],
                  [40.770477, -73.950370], 
                  [40.782619, -73.980991]
                 ]]}

start_time = time.time()

env = CitySim(geoJson)
env.initialize_taxis(200)
env.reset()
#action = 
#env.step()

print("Simulation took ", time.time() - start_time, "to run")