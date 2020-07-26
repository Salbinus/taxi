import os, sys
sys.path.append(os.path.abspath('../modules'))
from modules.environment import CitySim

geoJson = {'type': 'Polygon',
 'coordinates': [[[40.742239, -74.008574],
                  [40.731461, -73.982515],
                  [40.770477, -73.950370], 
                  [40.782619, -73.980991]
                 ]]}

city = CitySim(geoJson)

while city.city_time <= 143:
    city.generate_orders()
    city.update_time()