'''
Created on Nov 25, 2013

@author: lwan1@utk.edu
'''

class CrushRuleStep():
    '''
    class for crush rule step
    '''

    def __init__(self):
        self.op = 0
        self.arg1 = 0
        self.arg2 = 0

    def set_rule_step(self, op, arg1, arg2):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2


class CrushRuleMask():
    '''
    class for crush rule mask
    '''

    def __init__(self):
        self.rule_set = 0
        self.type = 0
        self.min_size = 0
        self.max_size = 0

    def set_rule_mask(self, rule_set, type, min_size, max_size):
        self.rule_set = rule_set
        self.type = type
        self.min_size = min_size
        self.max_size = max_size


class CrushRule():
    '''
    class for crush rule
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.len = 0
        self.rule_mask = CrushRuleMask()
        self.rule_steps = []

    def make_rule(self, len, rule_set, type, min_size, max_size):
        self.len = len
        self.rule_mask.set_rule_mask(rule_set, type, min_size, max_size)

    def add_rule_step(self, rule_step):
        if len(self.rule_steps) < self.len:
            self.rule_steps.append(rule_step)
            return 0
        else:
            return -1
