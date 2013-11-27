'''
Created on Nov 25, 2013

@author: lwan1@utk.edu
'''

class CrushRuleStep():
    '''
    classdocs
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
    classdocs
    '''

    def __init__(self):
        self.ruleset = 0
        self.type = 0
        self.min_size = 0
        self.max_size = 0

    def set_rule_mask(self, ruleset, type, min_size, max_size):
        self.ruleset = ruleset
        self.type = type
        self.min_size = min_size
        self.max_size = max_size


class CrushRule():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.len = 0
        self.rule_mask = CrushRuleMask()
        self.rule_steps = []

    def make_rule(self, len, ruleset, type, min_size, max_size):
        self.len = len
        self.rule_mask.set_rule_mask(ruleset, type, min_size, max_size)

    def add_rule_step(self, rule_step):
        if len(self.rule_steps) < self.len:
            self.rule_steps.append(rule_step)
            return 0
        else:
            return -1
