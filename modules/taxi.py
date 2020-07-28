from modules.node import Node
from modules.orders import Orders

class Taxi(object):
    '''Class representation of a Taxi'''
    __slots__ = ('taxi_id','online','offline','order','node','city_time')

    def __init__(self, taxi_id):
        self.taxi_id = taxi_id
        self.online = True
        self.onservice = False
        self.order = None
        self.node = None
        self.city_time = 0

    def get_taxi_id(self):
        return self.taxi_id

    def set_position(self, node):
        self.node = node

    def set_order_start(self, order):
        self.order = order

    def set_order_finish(self):
        self.order = None
        self.onservice = False

    def update_city_time(self):
        self.city_time += 1

    def set_city_time(self, city_time):
        self.city_time = city_time

    def set_offline(self):
        '''e.g. set taxi offline in the end of the shift'''
        assert self.onservice is False and self.online is True
        self.online = False
        self.node.num_idle_taxis -= 1
        self.node.num_offline_taxis += 1

    def set_offline_for_start_dispatch(self):
        assert self.onservice is False
        self.online = False

    def set_online(self):
        assert self.onservice is False
        self.online = True
        self.node.num_idle_taxis += 1
        self.node.num_offline_taxis -= 1

    def set_online_for_finish_dispatch(self):
        self.online = True
        assert self.onservice is False


    def take_order(self, order):
        """take order, taxi show up at destination when order is finished"""
        assert self.online == True
        self.set_order_start(order)
        self.onservice = True
        self.node.num_idle_taxis -= 1
    
    def status_control_eachtime(self, city):

        assert self.city_time == city.city_time
        if self.onservice is True:
            assert self.online is True
            order_end_time = self.order.get_assigned_time() + self.order.get_duration()
            if self.city_time == order_end_time:
                self.set_position(self.order.get_end_position())
                self.set_order_finish()
                self.node.add_taxi(self._taxi_id, self)
                city.n_taxis += 1
            elif self.city_time < order_end_time:
                pass
            else:
                raise ValueError('Taxi: status_control_eachtime(): order end time less than city time')