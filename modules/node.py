import h3.api.numpy_int as h3
import numpy as np

class PoissonDistribution:

    def __init__(self, lam):
        self._lambda = lam

    def sample(self, seed=0):
        np.random.seed(seed)
        return np.random.poisson(self._lambda, 1)[0]

class GaussianDistribution:

    def __init__(self, args):
        mu, sigma = args
        self.mu = mu        # mean
        self.sigma = sigma  # standard deviation

    def sample(self, seed=0):
        np.random.seed(seed)
        return np.random.normal(self.mu, self.sigma, 1)[0]


class Node(object):
    __slots__ = ('node_id','valid_nodes','neighbors','orders','taxis','num_idle_taxis'
                ,'num_offline_taxis','order_generator','layers_neighbors')
    
    def __init__(self, node_id):
        self.node_id = node_id
        self.neighbors = list(h3.hex_ring(self.node_id))
        self.orders = None
        self.num_orders = 0
        self.taxis = {}
        self.num_idle_taxis = 0
        self.num_offline_taxis = 0
        self.order_generator = None
        self.layers_neighbors = None
        self.neighbors = list(get_layers_neighbors(1)[1])
#        self.taxis = {}

    def get_node_id(self):
        return self.node_id

    def clean_node(self):
        self.orders = None
        self.num_orders = 0
        self.taxis = {}
        self.num_idle_taxis = 0
        self.num_offline_taxis = 0

    def get_layers_neighbors(self, l_max):
        '''
        The use of H3 index system instead of plain python implementation makes it more
        readable as well as (probably) faster. 
        
        layers_neighbors[0] == node_id
        layers_neighbors[1] == directly surrounding nodes
        layers_neighbors[n] == the ring around the surrounding grids
        '''
        self.layers_neighbors = h3.k_ring_distances(self.node_id, l_max)
        return self.layers_neighbors

    def get_num_idle_taxis(self):
        return self.num_idle_taxis

    def get_num_idle_taxis_loop(self):
        temp_idle_taxi = 0
        for key, taxi in self.taxis.iteritems():
            if taxi.onservice is False and taxi.online is True:
                temp_idle_taxi += 1
        return temp_idle_taxi

    def get_num_off_taxis_loop(self):
        temp_idle_taxi = 0
        for key, taxi in self.taxis.iteritems():
            if taxi.onservice is False and taxi.online is False:
                temp_idle_taxi += 1
        return temp_idle_taxi
        
    def order_distribution(self, distribution, dis_paras):
        if distribution == 'Poisson':
            self.order_generator = PoissonDistribution(dis_paras)
        elif distribution == 'Gaussian':
            self.order_generator = GaussianDistribution(dis_paras)
        else:
            pass

    def generate_order_real(self, l_max, order_time_dist, order_price_dist, city_time, nodes, seed):
        """
        Generate new orders at each time step
        """
        num_order_t = self.order_generator.sample(seed)
        self.num_orders += num_order_t
        for ii in np.arange(num_order_t):
            if l_max == 1:
                duration = 1
            else:
                duration = np.random.choice(np.arange(1, l_max+1), p=order_time_dist)
            price_mean, price_std = order_price_dist[duration-1]
            price = np.random.normal(price_mean, price_std, 1)[0]
            price = price if price > 0 else price_mean

            current_node_id = self.get_node_index()
            destination_node = []
            for jj in np.arange(duration):
                for kk in self.layers_neighbors[jj]:
                    if nodes[kk] is not None:
                        destination_node.append(kk)
            self.orders.append(Order(nodes[current_node_id],
                                     nodes[np.random.choice(destination_node, 1)[0]],
                                     city_time,
                                     duration,
                                     price, 1))
        return

    def add_order_real(self, city_time, destination_node, duration, price):
        current_node_id = self.get_node_index()
        self.orders.append(Order(self,
                                 destination_node,
                                 city_time,
                                 duration,
                                 price, 0))
        self.num_orders += 1        

    def remove_idle_taxi_random(self):
        """Randomly remove one idle driver from current grid"""
        removed_taxi_id = "NA"
        for key,  in self.taxis.iteritems():
            if taxi.onservice is False and taxi.online is True:
                self.remove_taxi(key)
                removed_taxi_id = key
            if removed_taxi_id != "NA":
                break
        assert removed_taxi_id != "NA"
        return removed_taxi_id

    def remove_taxi(self, taxi_id):
        removed_taxi = self.taxis.pop(taxi_id, None)
        self.num_idle_taxis -= 1
        if removed_taxi is None:
            raise ValueError('Nodes.remove_driver: Remove a driver that is not in this node')
        return removed_taxi

    def set_idle_taxi_offline_random(self):
        """Randomly set one idle driver offline"""
        removed_taxi_id = "NA"
        for key, item in self.drivers.iteritems():
            if item.onservice is False and item.online is True:
                item.set_offline()
                removed_taxi_id = key
            if removed_taxi_id != "NA":
                break
        assert removed_taxi_id != "NA"
        return removed_taxi_id
    
    def set_offline_taxi_online(self):

        online_taxi_id = "NA"
        for key, taxi in self.taxis.iteritems():
            if taxi.onservice is False and taxi.online is False:
                taxi.set_online()
                online_taxi_id = key
            if online_taxi_id != "NA":
                break
        assert online_taxi_id != "NA"
        return online_taxi_id    

    def get_taxi_random(self):
        """Randomly get one driver"""
        assert self.idle_taxi_num > 0
        get_taxi_id = 0
        for key in self.taxis.iterkeys():
            get_taxi_id = key
            break
        return self.taxis[get_taxi_id]

    def add_taxi(self, taxi_id, taxi):
        self.taxis[taxi_id] = taxi
        self.num_idle_taxis += 1

    def remove_unfinished_order(self, city_time):
        un_finished_order_index = []
        for idx, o in enumerate(self.orders):
            # order un served
            if o.get_wait_time() + o.get_begin_time() < city_time:
                un_finished_order_index.append(idx)

            # order completed
            if o.get_assigned_time() + o.get_duration() == city_time and o.get_assigned_time() != -1:
                un_finished_order_index.append(idx)

        if len(un_finished_order_index) != 0:
            # remove unfinished orders
            self.orders = [i for j, i in enumerate(self.orders) if j not in un_finished_order_index]
            self.num_orders = len(self.orders)        

    def simple_order_assign(self, city_time, city):
        reward = 0
        num_assigned_order = min(self.num_orders, self.num_idle_taxis)
        served_order_index = []
        for idx in np.arange(num_assigned_order):
            order_to_serve = self.orders[idx]
            order_to_serve.set_assigned_time(city_time)
            self.num_orders -= 1
            reward += order_to_serve.get_price()
            served_order_index.append(idx)
            for key, assigned_driver in self.drivers.iteritems():
                if assigned_driver.onservice is False and assigned_driver.online is True:
                    assigned_driver.take_order(order_to_serve)
                    removed_driver = self.drivers.pop(assigned_driver.get_driver_id(), None)
                    assert removed_driver is not None
                    city.n_drivers -= 1
                    break

        all_order_num = len(self.orders)
        finished_order_num = len(served_order_index)

        # remove served orders
        self.orders = [i for j, i in enumerate(self.orders) if j not in served_order_index]
        assert self.num_orders == len(self.orders)

    def simple_order_assign_real(self, city_time, city):

        reward = 0
        num_assigned_order = min(self.num_orders, self.idle_driver_num)
        served_order_index = []
        for idx in np.arange(num_assigned_order):
            order_to_serve = self.orders[idx]
            order_to_serve.set_assigned_time(city_time)
            self.num_orders -= 1
            reward += order_to_serve.get_price()
            served_order_index.append(idx)
            for key, assigned_driver in self.drivers.iteritems():
                if assigned_driver.onservice is False and assigned_driver.online is True:
                    if order_to_serve.get_end_position() is not None:
                        assigned_driver.take_order(order_to_serve)
                        removed_driver = self.drivers.pop(assigned_driver.get_driver_id(), None)
                        assert removed_driver is not None
                    else:
                        assigned_driver.set_offline()  # order destination is not in target region
                    city.n_drivers -= 1
                    break

        all_order_num = len(self.orders)
        finished_order_num = len(served_order_index)

        # remove served orders
        self.orders = [i for j, i in enumerate(self.orders) if j not in served_order_index]
        assert self.num_orders == len(self.orders)

        return reward, all_order_num, finished_order_num

    def simple_order_assign_broadcast_update(self, city, neighbor_node_reward):

        assert self.idle_driver_num == 0
        reward = 0
        num_finished_orders = 0
        for neighbor_node in self.neighbors:
            if neighbor_node is not None and neighbor_node.idle_driver_num > 0:
                num_assigned_order = min(self.num_orders, neighbor_node.idle_driver_num)
                rr = self.utility_assign_orders_neighbor(city, neighbor_node, num_assigned_order)
                reward += rr
                neighbor_node_reward[neighbor_node.get_node_index()] += rr
                num_finished_orders += num_assigned_order
            if self.num_orders == 0:
                break

        assert self.num_orders == len(self.orders)
        return reward, num_finished_orders

    def utility_assign_orders_neighbor(self, city, neighbor_node, num_assigned_order):

        served_order_index = []
        reward = 0
        curr_city_time = city.city_time
        for idx in np.arange(num_assigned_order):
            order_to_serve = self.orders[idx]
            order_to_serve.set_assigned_time(curr_city_time)
            self.num_orders -= 1
            reward += order_to_serve.get_price()
            served_order_index.append(idx)
            for key, assigned_driver in neighbor_node.drivers.iteritems():
                if assigned_driver.onservice is False and assigned_driver.online is True:
                    if order_to_serve.get_end_position() is not None:
                        assigned_driver.take_order(order_to_serve)
                        removed_driver = neighbor_node.drivers.pop(assigned_driver.get_driver_id(), None)
                        assert removed_driver is not None
                    else:
                        assigned_driver.set_offline()
                    city.n_drivers -= 1
                    break

        # remove served orders
        self.orders = [i for j, i in enumerate(self.orders) if j not in served_order_index]
        assert self.num_orders == len(self.orders)
        return reward

    def set_neighbors(self, valid_nodes):
        '''
        Probably useless...
        '''
        nbs = [-100 if nb not in valid_nodes else nb for nb in self.neighbors]
        self.neighbors = nbs