import pandas as pd
import numpy as np
import os , sys
sys.path.append(os.path.abspath('../data'))
from modules.orders import Orders

time, location = 88, 617733151092637695
lookup_table = pd.read_pickle(os.path.abspath('data/lookup_table.pkl'))
orders = np.load(os.path.abspath('data/prep_data.npy'))
o = Orders(time, location, lookup_table, orders)
sample = o.get_orders()

if isinstance(sample, np.ndarray):
    print('Sampled succesfully from real orders')
else:
    print('unable to sample new orders')
