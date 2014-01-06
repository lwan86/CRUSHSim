'''
Created on Nov 19, 2013

@author: lwan1@utk.edu
'''

class CrushBucket():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.id = 0
        self.type = 0
        self.alg = 0
        self.hash = None
        self.weight = 0
        self.size = 0
        self.items = []

        self.perm_x = 0
        self.perm_n = 0
        self.perm = []

    def get_alg_name(self, alg):
        if alg == 1:
            return 'uniform'
        elif alg == 2:
            return 'list'
        elif alg == 3:
            return 'tree'
        elif alg == 4:
            return 'straw'
        else:
            return 'unknown'

    def choose_item_by_rand_perm(self, x, r):
        pr = r % self.size
        if self.perm_x != x or self.perm_n == 0:
            self.perm_x = x
            if pr == 0:
                s = self.hash.hash_32_3(x, self.id, 0) % self.size
                self.perm[0] = s
                self.perm_n = 0xffff
                return self.items[s]
            for i in range(self.size):
                self.perm[i] = i
            self.perm_n = 0
        elif self.perm_n == 0xffff:
            for i in range(1, self.size):
                self.perm[i] = i
            self.perm[self.perm[0]] = 0
            self.perm_n = 1
        while self.perm_n <= pr:
            p = self.perm_n
            if p < self.size-1:
                i = self.hash.hash_32_3(x, self.id, p) % (self.size-p)
                if i:
                    t = self.perm[p+i]
                    self.perm[p+i] = self.perm[p]
                    self.perm[p] = t
            self.perm_n += 1
        s = self.perm[pr]
        return self.items[s]


class UniformCrushBucket(CrushBucket):
    '''
    classdocs
    '''

    def __init__(self):
        self.item_weight = 0
        CrushBucket.__init__(self)

    def get_item_weight(self):
        return self.item_weight

    def make_bucket(self, hash, type, size, items, item_weight):
        self.alg = 1
        self.hash = hash
        self.type = type
        self.size = size
        self.weight = size*item_weight
        self.item_weight = item_weight
        self.items = items

    def add_bucket_item(self, item, weight):
        self.items.append(item)
        self.weight += weight
        self.size += 1

    def remove_bucket_item(self, item):
        if item in self.items:
            self.items.remove(item)
        else:
            return -1
        self.size -= 1
        self.weight -= self.item_weight
        return 0

    def adjust_item_weight(self, item, item_weight):
        diff = (item_weight-self.item_weight)*self.size
        self.item_weight = item_weight
        self.weight = self.item_weight*self.size
        return diff

    def choose_item(self, x, r):
        return self.choose_item_by_rand_perm(x, r)


class ListCrushBucket(CrushBucket):
    '''
    classdocs
    '''

    def __init__(self):
        self.item_weights = []
        self.sum_weights = []
        CrushBucket.__init__(self)

    def get_item_weight(self, pos):
        return self.item_weights[pos]

    def make_bucket(self, hash, type, size, items, item_weights):
        self.alg = 2
        self.hash = hash
        self.type = type
        self.size = size
        self.items = items
        self.item_weights = item_weights

        w = 0
        for i in range(size):
            w += item_weights[i]
            self.sum_weights[i] = w

        self.weight = w

    def add_bucket_item(self, item, weight):
        self.items.append(item)
        self.item_weights.append(weight)
        if self.size > 0:
            self.sum_weights.append(self.sum_weights[self.size-1]+weight)
        else:
            self.sum_weights.append(weight)
        self.weight += weight
        self.size += 1

    def remove_bucket_item(self, item):
        if item in self.items:
            item_id = self.items.index(item)
            item_weight = self.item_weights[item_id]
            for i in range(item_id+1, self.size):
                self.sum_weights[i] -= item_weight
            self.sum_weights.pop(item_id)

            self.items.remove(item)
            self.item_weights.remove(item_weight)
        else:
            return -1
        self.weight -= item_weight
        self.size -= 1
        return 0

    def adjust_item_weight(self, item, item_weight):
        if item in self.items:
            new_item_weight = item_weight
            item_id = self.items.index(item)
            current_item_weight = self.item_weights[item_id]
            diff = new_item_weight-current_item_weight
            self.item_weights[item_id] = new_item_weight
            self.weight += diff
            for i in range(item_id, self.size):
                self.sum_weights[i] += diff
            return diff
        else:
            return -1

    def choose_item(self, x, r):
        for i in range(self.size-1, -1, -1):
            w = self.hash.hash_32_4(x, self.items[i], r, self.id)
            w &= 0xffff
            w *= self.sum_weights[i]
            w = w >> 16
            if w < self.item_weights[i]:
                return self.items[i]
        print('bad list sums for bucket '+str(self.id))
        return self.items[0]


class TreeCrushBucket(CrushBucket):
    '''
    classdocs
    '''

    def __init__(self):
        self.num_nodes = 0
        self.node_weights = []
        CrushBucket.__init__(self)

    def get_node_index(self, pos):
        return ((pos+1) << 1)-1

    def get_item_weight(self, pos):
        return self.node_weights[self.get_node_index(pos)]

    def get_tree_depth(self, size):
        depth = 1
        t = size-1
        while t:
            t = t >> 1
            depth += 1
        return depth

    def get_node_height(self, n):
        h = 0
        while (n & 1) == 0:
            h += 1
            n = n >> 1
        return h

    def is_right_child(self, n, h):
        return n & (1 << (h+1))

    def get_parent_node(self, n):
        h = self.get_node_height(n)
        if self.is_right_child(n, h):
            return n-(1 << h)
        else:
            return n+(1 << h)

    def get_left_child(self, n):
        h = self.get_node_height(n)
        return n-(1 << (h-1))

    def get_right_child(self, n):
        h = self.get_node_height(n)
        return n+(1 << (h-1))

    def is_leaf(self, n):
        return n & 1

    def make_bucket(self, hash, type, size, items, item_weights):
        self.alg = 3
        self.hash = hash
        self.type = type
        self.size = size

        depth = self.get_tree_depth(size)
        self.num_nodes = 1 << depth
        self.items = items
        self.node_weights = [0]*self.num_nodes

        for i in range(size):
            node_id = self.get_node_index(i)
            self.node_weights[node_id] = item_weights[i]
            self.weight += item_weights[i]
            for j in range(1, depth):
                node_id = self.get_parent_node(node_id)
                self.node_weights[node_id] += item_weights[i]

    def add_bucket_item(self, item, weight):
        new_size = self.size+1
        new_depth = self.get_tree_depth(new_size)
        self.num_nodes = 1 << new_depth
        new_node_id = self.get_node_index(new_size-1)
        self.node_weights[new_node_id] = weight

        for j in range(1, new_depth):
            new_node_id = self.get_parent_node(new_node_id)
            self.node_weights[new_node_id] += weight

        self.weight += weight
        self.size += 1

    def remove_bucket_item(self, item):
        if item in self.items:
            depth = self.get_tree_depth(self.size)
            item_id = self.items.index(item)
            node_id = self.get_node_index(item_id)
            node_weight = self.node_weights[node_id]
            self.node_weights[node_id] = 0
            for i in range(1, depth):
                node_id = self.get_parent_node(node_id)
                self.node_weights[node_id] -= node_weight
            self.weight -= node_weight
            new_size = self.size
            while new_size > 0:
                tmp_node_id = self.get_node_index(new_size-1)
                if self.node_weights[tmp_node_id]:
                    break
                new_size -= 1
            if new_size != self.size:
                for j in range(new_size, self.size):
                    self.items.pop()
                old_depth = self.get_tree_depth(self.size)
                new_depth = self.get_tree_depth(new_size)
                if new_depth != old_depth:
                    old_num_nodes = self.num_nodes
                    new_num_nodes = 1 << new_depth
                    for k in range(new_num_nodes, old_num_nodes):
                        self.node_weights.pop()
                    self.num_nodes = new_num_nodes
                self.size = new_size
            return 0
        else:
            return -1

    def adjust_item_weight(self, item, item_weight):
        if item in self.items:
            item_id = self.items.index(item)
            node_id = self.get_node_index(item_id)
            diff = item_weight - self.node_weights[node_id]
            self.node_weights[node_id] = item_weight
            self.weight += diff
            depth = self.get_tree_depth(self.size)
            for i in range(1, depth):
                node_id = self.get_parent_node(node_id)
                self.node_weights[node_id] += diff
            return diff
        else:
            return -1

    def choose_item(self, x, r):
        n = self.num_nodes >> 1
        while not self.is_leaf(n):
            w = self.node_weights[n]
            t = self.hash.hash_32_4(x, n, r, self.id)*w
            t = t >> 32
            l = self.get_left_child(n)
            if t < self.node_weights[l]:
                n = l
            else:
                n = self.get_right_child(n)
        return self.items[n >> 1]


class StrawCrushBucket(CrushBucket):
    '''
    classdocs
    '''

    def __init__(self):
        self.item_weights = []
        self.straws = []
        CrushBucket.__init__(self)

    def get_item_weight(self, pos):
        return self.item_weights[pos]

    def set_staw_value(self, size, item_weights):
        sorted_weights_idx = []
        if size:
            sorted_weights_idx[0] = 0
        for i in range(1, size):
            for j in range(i):
                if item_weights[i] < item_weights[sorted_weights_idx[j]]:
                    for k in range(i, j, -1):
                        sorted_weights_idx[k] = sorted_weights_idx[k-1]
                    sorted_weights_idx[j] = i
                    break
            if j == i:
                sorted_weights_idx[i] = i

        left_weights_num = size
        straw = 1.0
        weight_below = 0.0
        last_weight = 0.0

        i = 0
        while i < size:
            if item_weights[sorted_weights_idx[i]] == 0:
                self.straws[sorted_weights_idx[i]] = 0
                i += 1
                continue
            self.straws[sorted_weights_idx[i]] = straw*0x10000

            i += 1
            if i == size:
                break

            if item_weights[sorted_weights_idx[i]] == item_weights[sorted_weights_idx[i-1]]:
                continue

            weight_below += (float(item_weights[sorted_weights_idx[i-1]])-last_weight)*left_weights_num
            for j in range(i, size):
                if item_weights[sorted_weights_idx[j]] == item_weights[sorted_weights_idx[i]]:
                    left_weights_num -= 1
                else:
                    break
            weight_next = float(left_weights_num*(item_weights[sorted_weights_idx[i]]-item_weights[sorted_weights_idx[i-1]]))
            prob_below = weight_below/(weight_below+weight_next)
            straw *= pow(1.0/prob_below, 1.0/float(left_weights_num))
            last_weight = item_weights[sorted_weights_idx[i-1]]

    def make_bucket(self, hash, type, size, items, item_weights):
        self.alg = 4
        self.hash = hash
        self.type = type
        self.size = size
        self.items = items
        self.item_weights = item_weights

        for i in range(size):
            self.weight += item_weights[i]

        self.set_staw_value(size, item_weights)

    def add_bucket_item(self, item, weight):
        self.items.append(item)
        self.item_weights.append(weight)
        self.weight += weight
        self.size += 1

        self.set_staw_value(self.size, self.item_weights)

    def remove_bucket_item(self, item):
        if item in self.items:
            item_id = self.items.index(item)
            item_weight = self.item_weights[item_id]
            self.size -= 1
            self.weight -= item_weight
            self.items.remove(item)
            self.item_weights.remove(item_weight)
            self.set_staw_value(self.size, self.item_weights)
            return 0
        else:
            return -1

    def adjust_item_weight(self, item, item_weight):
        if item in self.items:
            item_id = self.items.index(item)
            diff = item_weight-self.item_weights[item_id]
            self.item_weights[item_id] = item_weight
            self.weight += diff
            self.set_staw_value(self.size, self.item_weights)
            return 0
        else:
            return -1

    def choose_item(self, x, r):
        high = 0
        high_draw = 0
        for i in range(self.size):
            draw = self.hash.hash_32_3(x, self.items[i], r)
            draw &= 0xffff
            draw *= self.straws[i]
            if i == 0 or draw > high_draw:
                high = i
                high_draw = draw
        return self.items[high]