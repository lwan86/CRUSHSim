'''
Created on Nov 27, 2013

@author: lwan1@utk.edu
'''

class CrushMap():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.crush_buckets = []
        self.crush_rules = []

        self.max_buckets = 0
        self.max_rules = 0
        self.max_devices = 0

        self.num_local_tries = 2
        self.num_local_fallback_tries = 5
        self.num_total_tries = 19
        self.leaf_descend_once = 0
        self.tries = []

    def add_rule(self, crush_rule, rule_id):
        if rule_id < 0:
            self.crush_rules.append(crush_rule)
            self.max_rules += 1
            return self.max_rules-1
        elif rule_id < self.max_rules:
            self.crush_rules[rule_id] = crush_rule
            return rule_id
        else:
            return -1

    def get_next_bucket_id(self):
        for pos in range(0, self.max_buckets):
            if not self.crush_buckets or self.crush_buckets[pos] == 0:
                break
        return -1-pos

    def add_bucket(self, crush_bucket, bucket_id):
        if bucket_id == 0:
            bucket_id = self.get_next_bucket_id()
        pos = -1-bucket_id
        while pos >= self.max_buckets:
            old_size = self.max_buckets
            if self.max_buckets:
                self.max_buckets *= 2
            else:
                self.max_buckets = 8
            for i in range(old_size, self.max_buckets):
                self.crush_buckets.append(0)
        crush_bucket.id = bucket_id
        self.crush_buckets[pos] = crush_bucket
        return bucket_id

    def remove_bucket(self, crush_bucket):
        pos = -1-crush_bucket.id
        self.crush_buckets[pos] = 0

    def find_rule(self, rule_set, type, size):
        for i in range(self.max_rules):
            if (self.crush_rules[i] and self.crush_rules[i].rule_mask.rule_set == rule_set and
                self.crush_rules[i].rule_mask.type == type and self.crush_rules[i].rule_mask.min_size <= size
                and self.crush_rules[i].rule_mask.max_size >= size):
                return i
        return -1

    def finalize(self):
        self.max_devices = 0
        for i in range(self.max_buckets):
            if self.crush_buckets[i] == 0:
                continue
            for j in range(self.crush_buckets[i].size):
                if self.crush_buckets[i].items[j] >= self.max_devices:
                    self.max_devices = self.crush_buckets[i].items[j]+1

    def reweight_bucket(self, crush_bucket):
        if crush_bucket.alg == 1:
            sum = 0
            n = 0
            leaves = 0
            for i in range(crush_bucket.size):
                id = crush_bucket.items[i]
                if id < 0:
                    self.reweight_bucket(self.crush_buckets[-1-id])
                    sum += self.crush_buckets[-1-id].weight
                    n += 1
                else:
                    leaves += 1
            if n > leaves:
                crush_bucket.item_weight = sum/n
            crush_bucket.weight = crush_bucket.item_weight*crush_bucket.size
        elif crush_bucket.alg == 2:
            crush_bucket.weight = 0
            for i in range(crush_bucket.size):
                id = crush_bucket.items[i]
                if id < 0:
                    self.reweight_bucket(self.crush_buckets[-1-id])
                    crush_bucket.item_weights[i] = self.crush_buckets[-1-id].weight
                crush_bucket.weight += crush_bucket.item_weights[i]
        elif crush_bucket.alg == 3:
            crush_bucket.weight = 0
            for i in range(crush_bucket.size):
                id = crush_bucket.items[i]
                node_id = crush_bucket.get_node_index(i)
                if id < 0:
                    self.reweight_bucket(self.crush_buckets[-1-id])
                    crush_bucket.node_weights[node_id] = self.crush_buckets[-1-id].weight
                crush_bucket.weight += crush_bucket.node_weights[node_id]
        elif crush_bucket.alg == 4:
            crush_bucket.weight = 0
            for i in range(crush_bucket.size):
                id = crush_bucket.items[i]
                if id < 0:
                    self.reweight_bucket(self.crush_buckets[-1-id])
                    crush_bucket.item_weights[i] = self.crush_buckets[-1-id].weight
                crush_bucket.weight += crush_bucket.item_weights[i]

    def choose_first_n_items(self, crush_bucket, weight, x, num_replicas, type):
        '''
        still working on this
        '''
