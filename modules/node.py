import h3.api.numpy_int as h3

class Node(object):
    __slots__ = ('node_id', 'valid_nodes', 'neighbors', 'orders', 'taxis')
    
    def __init__(self, node_id):
        self.node_id = node_id
        self.valid_nodes = None #valid_nodes
        self.neighbors = list(h3.hex_ring(self.node_id))
        self.orders = []
        self.taxis = {}
        #self.idle_drivers = 0
        
    def clean(self):
        self.orders = []
        self.taxis = {}
        self.idle_drivers = 0
    
    def set_neighbors(self, valid_nodes):
        '''
        Should be in the city class to avoid copying the list of valid nodes? `\~°.°~/`
        '''
        nbs = [-100 if nb not in hexagons else nb for nb in nbs]
        neighborhoods.append(nbs)

    def set_orders(self):
        orders = Orders()
        for order in orders:
            self.order.append(order)
    
    def status_control(self):
        pass