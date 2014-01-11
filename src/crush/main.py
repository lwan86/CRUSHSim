'''
Created on Jan 4, 2014

@author: lwan1@utk.edu
'''
from crush_bucket import *
from crush_hash import *
from crush_rule import *
from crush_map import *
from copy import deepcopy
import random

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

def build_crush_map(num_osds, layers):
    '''
    build a CRUSH map with fixed number of osds and pre-configured storage hierarchy as input
    '''
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
            items = [None]*num_osds
            weights = [0]*num_osds
            weight = 0
            for j in range(layer_size):
                if layer_size == 0:
                    break
                items[j] = lower_items[lower_pos]
                weights[j] = lower_weights[lower_pos]
                weight += weights[j]
                lower_pos += 1
                if lower_pos == len(lower_items):
                    break
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
        if crush_map.crush_buckets[i] == None:
            continue
        print 'bucket id: '+str(crush_map.crush_buckets[i].id)
        print 'bucket type: '+crush_map.crush_buckets[i].get_alg_name(crush_map.crush_buckets[i].alg)
        items = [j for j in crush_map.crush_buckets[i].items if j != None]
        print 'items: '+str(items)
        print '********************************************************************************************************'

def adjust_weights(crush_map, weights, bucket_down_ratio, dev_down_ratio):
    '''
    adjust the device weight based on the bucket and device down ratio
    '''
    if dev_down_ratio > 0:
        w = weights
        bucket_ids = []
        for i in range(crush_map.max_buckets):
            b_id = -1-i
            if crush_map.crush_buckets[i]:
                bucket_ids.append(b_id)
        buckets_above_devices = []
        for i in range(len(bucket_ids)):
            b_id = bucket_ids[i]
            if crush_map.crush_buckets[-1-b_id].size == 0:
                continue
            first_child = crush_map.crush_buckets[-1-b_id].items[0]
            if first_child >= 0:
                buckets_above_devices.append(b_id)
        #permute bucket list
        for i in range(len(buckets_above_devices)):
            j = random.randint(0, pow(2, 31))%(len(buckets_above_devices)-1)
            buckets_above_devices[i], buckets_above_devices[j] = buckets_above_devices[j], buckets_above_devices[i]
        num_buckets_to_visit = int(bucket_down_ratio*len(buckets_above_devices))
        for i in range(num_buckets_to_visit):
            id = buckets_above_devices[i]
            size = crush_map.crush_buckets[-1-id].size
            items = []
            for j in range(size):
                items.append(crush_map.crush_buckets[-1-id].items[j])
            #permute item list
            for k in range(size):
                l = random.randint(0, pow(2, 31))%(size-1)
                items[k], items[l] = items[l], items[k]
            local_devices_to_visit = int(dev_down_ratio*size)
            for m in range(local_devices_to_visit):
                item = crush_map.crush_buckets[-1-id].items[m]
                w[item] = 0
        return w

def test_crush(crush_map, min_x, max_x, num_replicas, dev_weights, bucket_down_ratio, dev_down_ratio, num_batches):
    #print dev_weights
    min_rule_id = 0
    max_rule_id = crush_map.max_rules-1
    weights = []
    for i in range(crush_map.max_devices):
        if i in dev_weights:
            weights.append(dev_weights[i])
        elif crush_map.item_exists(i):
            weights.append(0x10000)
        else:
            weights.append(0)
    new_weights = adjust_weights(crush_map, weights, bucket_down_ratio, dev_down_ratio)
    num_devices_active = 0
    for i in range(len(new_weights)):
        if new_weights[i] > 0:
            num_devices_active += 1
    print 'number of active devices: '+str(num_devices_active)
    print 'device weight: '+str(new_weights)
    for r in range(min_rule_id, max_rule_id+1):
        print 'rule id: '+str(r)
        print 'x: '+str(min_x)+'..'+str(max_x)
        print 'number of replicas: '+str(num_replicas)
        per = [0]*crush_map.max_devices
        sizes = {}
        for i in range(num_replicas+1):
            sizes[i] = 0
        num_objects = (max_x-min_x)+1
        batch_per = {}
        objects_per_batch = num_objects/num_batches
        batch_min = min_x
        batch_max = min_x+objects_per_batch-1
        total_weight = 0
        for i in range(crush_map.max_devices):
            total_weight += new_weights[i]
        if total_weight == 0:
            continue
        expected_objects = float(num_replicas*num_objects)
        proportional_weights = [float(0)]*crush_map.max_devices
        for i in range(crush_map.max_devices):
            proportional_weights[i] = float(new_weights[i])/total_weight
        num_objects_expected = [float(0)]*crush_map.max_devices
        for i in range(crush_map.max_devices):
            num_objects_expected[i] = proportional_weights[i]*expected_objects
        for cur_batch in range(num_batches):
            if cur_batch == num_batches-1:
                batch_max = max_x
                objects_per_batch = (batch_max-batch_min+1)
            batch_expected_objects = num_replicas*objects_per_batch
            batch_num_objects_expected = [float(0)]*crush_map.max_devices
            for i in range(crush_map.max_devices):
                batch_num_objects_expected[i] = proportional_weights[i]*batch_expected_objects
            temporary_per = [0]*crush_map.max_devices
            for x in range(batch_min, batch_max+1):
                result = [None]*num_replicas
                [res_len, res] = crush_map.get_mapping_using_rule(r, x, new_weights, len(new_weights), result, num_replicas)
                has_item_none = False
                for i in range(res_len):
                    if res[i] != None:
                        per[res[i]] += 1
                        temporary_per[res[i]] += 1
                    else:
                        has_item_none = True
                batch_per[cur_batch] = temporary_per
                sizes[res_len] += 1
                if has_item_none:
                    print 'bad mapping rule!'
                batch_min = batch_max+1
                batch_max = batch_min+objects_per_batch-1
        print 'times each device has been chosen: '+str(per)

def main():
    #num_osds = 100
    layers = []
    f1 = open('layers.txt', 'r')
    line_id = 0
    for line in f1:
        layer = []
        tmp = line.split()
        layer.append(tmp[0])
        layer.append(tmp[1])
        layer.append(int(tmp[2]))
        layers.append(layer)
        print 'layer '+str(line_id+1)+': '+str(layer)
        line_id += 1
    f1.close()
    print '*************************************************'
    args = {}
    f2 = open('args.txt', 'r')
    for line in f2:
        tmp = line.split()
        args[tmp[0]] = float(tmp[1]) if '.' in tmp[1] else int(tmp[1])
    f2.close()
    crush = build_crush_map(args['num_osds'], layers)
    print_crush_map(crush)
    dev_weights = {}
    f3 = open('dev_weight.txt', 'r')
    for line in f3:
        tmp = line.split()
        w = int(float(tmp[1])*0x10000)
        if w < 0:
            w = 0
        if w > 0x10000:
            w = 0x10000
        dev_weights[int(tmp[0])] = w
    f3.close()
    #min_x = 0
    #max_x = 1023
    #num_replicas = 3
    #bucket_down_ratio = 0.5
    #dev_down_ratio = 0.1
    #num_batches = 10
    #print dev_weights
    test_crush(crush, args['min_x'], args['max_x'], args['num_replicas'], dev_weights, args['bucket_down_ratio'], args['dev_down_ratio'], args['num_batches'])
    print 'done!'

if __name__ == '__main__':
    main()