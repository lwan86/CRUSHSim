'''
Created on Nov 27, 2013

@author: lwan1@utk.edu
'''
from copy import deepcopy

class CrushMap():
    '''
    class for crush map
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
        self.tries = [0]*(self.num_total_tries+1)

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
        pos = 0
        flag = False
        for pos in range(self.max_buckets):
            if not self.crush_buckets or self.crush_buckets[pos] == None:
                flag = True
                break
        if flag:
            return -1-pos
        else:
            return -1-(pos+1)

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
                self.crush_buckets.append(None)
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

    def item_exists(self, id):
        found = False
        for i in range(self.max_buckets):
            b = self.crush_buckets[i]
            if b == None:
                continue
            for j in range(b.size):
                if b.items[j] == id:
                    found = True
        return found

    def finalize(self):
        '''
        can only be called after the crush map has been built
        '''
        self.max_devices = 0
        for i in range(self.max_buckets):
            if self.crush_buckets[i] == None:
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

    def item_is_out(self, weight, weight_max, item, x):
        if item >= weight_max:
            return 1
        if weight[item] >= 0x10000:
            return 0
        if weight[item] == 0:
            return 1
        if (self.crush_buckets[0].hash.hash_32_2(x, item) & 0xffff) < weight[item]:
            return 0
        return 1

    def choose_first_n_items(self, crush_bucket, weight, weight_max, x, num_replicas, type, out, outpos, tries, recurse_tries, local_tries, local_fallback_tries, recurse_to_leaf, out2):
        out3 = out
        out4 = out2
        #print '1st out3: '+str(out3)
        #print '1st out4: '+str(out4)
        #if out3 == None and outpos >= 0:
        #    print 'stop!'
        for rep in range(outpos, num_replicas):
            ftotal = 0
            skip_rep = 0
            while True:
                retry_descent = 0
                input_bucket = crush_bucket
                flocal = 0
                while True:
                    collide = 0
                    retry_bucket = 0
                    r = rep
                    r += ftotal
                    if input_bucket.size == 0:
                        reject = 1
                    else:
                        if local_fallback_tries > 0 and flocal >= (input_bucket.size >> 1) and flocal > local_fallback_tries:
                            item = input_bucket.choose_item_by_rand_perm(x, r)
                        else:
                            item = input_bucket.choose_item(x, r)
                        #print 'item: '+str(item)
                        if item >= self.max_devices:
                            skip_rep = 1
                            break
                        if item < 0:
                            item_type = self.crush_buckets[-1-item].type
                        else:
                            item_type = 0
                        if item_type != type:
                            if item >= 0 or -1-item >= self.max_buckets:
                                skip_rep = 1
                                break
                            input_bucket = self.crush_buckets[-1-item]
                            retry_bucket = 1
                            continue
                        for i in range(outpos):
                            #print '2nd out3: '+str(out3)
                            #print 'item: '+str(item)
                            if out3[i] == item:
                                collide = 1
                                break
                        reject = 0
                        if not collide and recurse_to_leaf:
                            if item < 0:
                                #if outpos > 0:
                                #    print 'stop!'
                                #print '2nd out4: '+str(out4)
                                res = self.choose_first_n_items(self.crush_buckets[-1-item], weight, weight_max, x, outpos+1, 0, out4, outpos, recurse_tries, 0, local_tries, local_fallback_tries, 0, None)
                                if res[0] <= outpos:
                                    #print '3rd out4: '+str(out4)
                                    out4 = res[1]
                                    #print '4th out4: '+str(out4)
                                    reject = 1
                            else:
                                #print '6th out4: '+str(out4)
                                out4[outpos] = item
                                #print '7th out4: '+str(out4)
                        if not reject:
                            if item_type == 0:
                                reject = self.item_is_out(weight, weight_max, item, x)
                            else:
                                reject = 0
                    if reject or collide:
                        ftotal += 1
                        flocal += 1
                        if collide and flocal <= local_tries:
                            retry_bucket = 1
                        elif local_fallback_tries > 0 and flocal <= input_bucket.size+local_fallback_tries:
                            retry_bucket = 1
                        elif ftotal <= tries:
                            retry_descent = 1
                        else:
                            skip_rep = 1
                    if not retry_bucket:
                        break
                if not retry_descent:
                    break
            if skip_rep:
                continue
            #print '3rd out3: '+str(out3)
            #print 'item: '+str(item)
            out3[outpos] = item
            #print '4th out3: '+str(out3)
            outpos += 1
            if self.tries and ftotal <= self.num_total_tries:
                self.tries[ftotal] += 1
        return [outpos, out3, out4]

    def get_mapping_using_rule(self, rule_id, x, weight, weight_max, result, result_max):
        total_tries = self.num_total_tries
        local_tries = self.num_local_tries
        local_fallback_tries = self.num_local_fallback_tries
        leaf_tries = 0
        w = [None]*result_max
        o = [None]*result_max
        c = [None]*result_max
        res = result
        if rule_id >= self.max_rules:
            print 'bad rule id!'
            return 0
        result_len = 0
        for step in range(self.crush_rules[rule_id].len):
            first_n = 0
            # CRUSH_RULE_TAKE
            if self.crush_rules[rule_id].rule_steps[step].op == 1:
                w[0] = self.crush_rules[rule_id].rule_steps[step].arg1
                w_size = 1
            # CRUSH_RULE_SET_CHOOSE_TRIES
            elif self.crush_rules[rule_id].rule_steps[step].op == 8:
                if self.crush_rules[rule_id].rule_steps[step].arg1 > 0:
                    total_tries = self.crush_rules[rule_id].rule_steps[step].arg1
            # CRUSH_RULE_SET_CHOOSELEAF_TRIES
            elif self.crush_rules[rule_id].rule_steps[step].op == 9:
                if self.crush_rules[rule_id].rule_steps[step].arg1 > 0:
                    leaf_tries = self.crush_rules[rule_id].rule_steps[step].arg1
            # CRUSH_RULE_SET_CHOOSE_LOCAL_TRIES
            elif self.crush_rules[rule_id].rule_steps[step].op == 10:
                if self.crush_rules[rule_id].rule_steps[step].arg1 > 0:
                    local_tries = self.crush_rules[rule_id].rule_steps[step].arg1
            # CRUSH_RULE_SET_CHOOSE_LOCAL_FALLBACK_TRIES
            elif self.crush_rules[rule_id].rule_steps[step].op == 11:
                if self.crush_rules[rule_id].rule_steps[step].arg1 > 0:
                    local_fallback_tries = self.crush_rules[rule_id].rule_steps[step].arg1
            # CRUSH_RULE_CHOOSE_FIRSTN or CRUSH_RULE_CHOOSELEAF_FIRSTN
            elif self.crush_rules[rule_id].rule_steps[step].op == 2 or self.crush_rules[rule_id].rule_steps[step].op == 6:
                first_n = 1
                if w_size == 0:
                    continue
                recurse_to_leaf = self.crush_rules[rule_id].rule_steps[step].op == 6
                o_size = 0
                for i in range(w_size):
                    num_replicas = self.crush_rules[rule_id].rule_steps[step].arg1
                    if num_replicas <= 0:
                        num_replicas += result_max
                        if num_replicas <= 0:
                            continue
                    j = 0
                    if first_n:
                        if leaf_tries:
                            recurse_tries = leaf_tries
                        elif self.leaf_descend_once:
                            recurse_tries = 1
                        else:
                            recurse_tries = total_tries
                        #print 'o: '+str(o)
                        #print 'o_size: '+str(o_size)
                        #print 'o[o_size:len(o)]: '+str(o[o_size:len(o)])
                        ret = self.choose_first_n_items(self.crush_buckets[-1-w[i]], weight, weight_max, x, num_replicas, self.crush_rules[rule_id].rule_steps[step].arg2, o[o_size:len(o)], j, total_tries, recurse_tries, local_tries, local_fallback_tries, recurse_to_leaf, c[o_size:len(c)])
                        o[o_size:len(o)] = ret[1]
                        c[o_size:len(c)] = ret[2]
                        o_size += ret[0]
                if recurse_to_leaf:
                    o = deepcopy(c)
                tmp = deepcopy(o)
                o = deepcopy(w)
                w = deepcopy(tmp)
                w_size = o_size
            # CRUSH_RULE_EMIT
            elif self.crush_rules[rule_id].rule_steps[step].op == 4:
                for i in range(w_size):
                    if result_len < result_max:
                        res[result_len] = w[i]
                        result_len += 1
                w_size = 0
            else:
                print 'unknown op!'
        return [result_len, res]