'''
Created on Dec 3, 2013

@author: lwan1_000
'''

class CrushHash():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.hash_seed = 1315423911

    def hash_32_mix(self, a, b, c):
        a = a-b
        a = a-c
        a = pow(a, c >> 13)
        b = b-c
        b = b-a
        b = pow(b, a << 8)
        c = c-a
        c = c-b
        c = pow(c, b >> 13)
        a = a-b
        a = a-c
        a = pow(a, c >> 12)
        b = b-c
        b = b-a
        b = pow(b, a << 16)
        c = c-a
        c = c-b
        c = pow(c, b >> 5)
        a = a-b
        a = a-c
        a = pow(a, c >> 3)
        b = b-c
        b = b-a
        b = pow(b, a << 10)
        c = c-a
        c = c-b
        c = pow(c, b >> 15)
        return [a, b, c]

    def hash_32_1(self, a):
        hash = pow(self.hash_seed, a)
        b = a
        x = 231232
        y = 1232
        [b, x, hash] = self.hash_32_mix(b, x, hash)
        [y, a, hash] = self.hash_32_mix(y, a, hash)
        return hash

    def hash_32_2(self, a, b):
        hash = pow(pow(self.hash_seed, a), b)
        x = 231232
        y = 1232
        [a, b, hash] = self.hash_32_mix(a, b, hash)
        [x, a, hash] = self.hash_32_mix(x, a, hash)
        [b, y, hash] = self.hash_32_mix(b, y, hash)
        return hash

    def hash_32_3(self, a, b, c):
        hash = pow(pow(pow(self.hash_seed, a), b), c)
        x = 231232
        y = 1232
        [a, b, hash] = self.hash_32_mix(a, b, hash)
        [c, x, hash] = self.hash_32_mix(c, x, hash)
        [y, a, hash] = self.hash_32_mix(y, a, hash)
        [b, x, hash] = self.hash_32_mix(b, x, hash)
        [y, c, hash] = self.hash_32_mix(y, c, hash)
        return hash

    def hash_32_4(self, a, b, c, d):
        hash = pow(pow(pow(pow(self.hash_seed, a), b), c), d)
        x = 231232
        y = 1232
        [a, b, hash] = self.hash_32_mix(a, b, hash)
        [c, d, hash] = self.hash_32_mix(c, d, hash)
        [a, x, hash] = self.hash_32_mix(a, x, hash)
        [y, b, hash] = self.hash_32_mix(y, b, hash)
        [c, x, hash] = self.hash_32_mix(c, x, hash)
        [y, d, hash] = self.hash_32_mix(y, d, hash)
        return hash

    def hash_32_5(self, a, b, c, d, e):
        hash = pow(pow(pow(pow(pow(self.hash_seed, a), b), c), d), e)
        x = 231232
        y = 1232
        [a, b, hash] = self.hash_32_mix(a, b, hash)
        [c, d, hash] = self.hash_32_mix(c, d, hash)
        [e, x, hash] = self.hash_32_mix(e, x, hash)
        [y, a, hash] = self.hash_32_mix(y, a, hash)
        [b, x, hash] = self.hash_32_mix(b, x, hash)
        [y, c, hash] = self.hash_32_mix(y, c, hash)
        [d, x, hash] = self.hash_32_mix(d, x, hash)
        [y, e, hash] = self.hash_32_mix(y, e, hash)
        return hash

