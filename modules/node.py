import h3.api.numpy_int as h3

class Node(object):
    __slots__ = ('node_id', 'valid_nodes', 'neighbors', 'orders', 'taxis')
    
    def __init__(self, node_id):
        self.node_id = node_id
        self.neighbors = list(h3.hex_ring(self.node_id))
        self.orders = None

#        self.taxis = {}
#        self.valid_nodes = None #valid_nodes

    def get_node_id(self):
        return self.node_id

    def clean(self):
        del self.orders
        #self.taxis = {}
        #self.idle_drivers = 0
    
    def set_neighbors(self, valid_nodes):
        '''
        Should be in the city class to avoid copying the list of valid nodes? `\~°.°~/`
        '''
        nbs = [-100 if nb not in valid_nodes else nb for nb in self.neighbors]
        self.neighbors = nbs

    def set_orders(self, orders):
        self.orders = orders
    
    def get_orders(self):
        return self.orders