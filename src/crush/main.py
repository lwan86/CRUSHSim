'''
Created on Jan 4, 2014

@author: lwan1@utk.edu
'''
from crush_bucket import *
from crush_hash import *
from crush_rule import *
from crush_map import *
from copy import deepcopy

def buckettype_to_number(buckettype):
    if buckettype == 'uniform':
        return 1
    elif buckettype == 'list':
        return 2
    elif buckettype == 'tree':
        return 3
    elif buckettype == 'straw':
        return 4
    else:
        return 0

def build_crush_map(num_osds, fn):
    layers = []
    f = open(fn, 'r')
    line_id = 0
    for line in f:
        layer = []
        tmp = line.split()
        layer.append(tmp[0])
        layer.append(tmp[1])
        layer.append(int(tmp[2]))
        layers.append(layer)
        print 'layer '+str(line_id+1)+': '+str(layer)
        line_id += 1
    print '*************************************************'
    crush = CrushMap()
    lower_items = []
    lower_weights = []
    for i in range(num_osds):
        lower_items.append(i)
        lower_weights.append(0x10000)
    type = 1
    root_id = 0
    for row in layers:
        layer_name = row[0]
        layer_buckettype = row[1]
        layer_size = row[2]
        buckettype_in_num = buckettype_to_number(layer_buckettype)
        if buckettype_in_num == 0:
            print 'unknown bucket type!'
        cur_items = []
        cur_weights = []
        lower_pos = 0
        i = 0
        while True:
            if lower_pos == len(lower_items):
                break
            items = [0]*num_osds
            weights = [0]*num_osds
            weight = 0
            for j in range(layer_size):
                if layer_size == 0:
                    break
                if lower_pos == len(lower_items):
                    break
                items[j] = lower_items[lower_pos]
                weights[j] = lower_weights[lower_pos]
                weight += weights[j]
                lower_pos += 1
            hash = CrushHash()
            if buckettype_in_num == 1:
                bucket = UniformCrushBucket()
                if j+1 and weights:
                    item_weight = weights[0]
                else:
                    item_weight = 0
                bucket.make_bucket(hash, type, j+1, items, item_weight)
            elif buckettype_in_num == 2:
                bucket = ListCrushBucket()
                bucket.make_bucket(hash, type, j+1, items, weights)
            elif buckettype_in_num == 3:
                bucket = TreeCrushBucket()
                bucket.make_bucket(hash, type, j+1, items, weights)
            elif buckettype_in_num == 4:
                bucket = StrawCrushBucket()
                bucket.make_bucket(hash, type, j+1, items, weights)
            bucket_id = crush.add_bucket(bucket, 0)
            root_id = bucket_id
            cur_items.append(bucket_id)
            cur_weights.append(weight)
            i += 1
        lower_items = deepcopy(cur_items)
        lower_weights = deepcopy(cur_weights)
        type += 1
    rule_set = 1
    rule = CrushRule()
    rule.make_rule(3, rule_set, 1, 2, 2)
    rule_step1 = CrushRuleStep()
    #print root_id
    rule_step1.set_rule_step(1, root_id, 0)
    rule_step2 = CrushRuleStep()
    rule_step2.set_rule_step(6, 0, 1)
    rule_step3 = CrushRuleStep()
    rule_step3.set_rule_step(4, 0, 0)
    rule.add_rule_step(rule_step1)
    rule.add_rule_step(rule_step2)
    rule.add_rule_step(rule_step3)
    crush.add_rule(rule, -1)
    crush.finalize()
    return crush

def print_crush_map(crush_map):
    for i in range(crush_map.max_buckets-1, -1, -1):
        #print i
        print 'bucket id: '+str(crush_map.crush_buckets[i].id)
        print 'bucket type: '+crush_map.crush_buckets[i].get_alg_name(crush_map.crush_buckets[i].alg)
        nnz_items = [j for j in crush_map.crush_buckets[i].items if j != 0]
        print 'items: '+str(nnz_items)
        print '********************************************************************************************************'

def main():
    '''
    build a CRUSH map with fixed number of osds
    '''
    num_osds = 100
    crush = build_crush_map(num_osds, 'layers.txt')
    print_crush_map(crush)
    print 'done!'

if __name__ == '__main__':
    main()