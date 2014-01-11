'''
Created on Dec 3, 2013

@author: lwan1@utk.edu
'''

class CrushHash():
    '''
    class for crush hash function
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.hash_seed = 1315423911

    def hash_32_mix(self, a, b, c):
        '''
        mix 3 32-bit values reversibly.
        For every delta with one or two bits set, and the deltas of all three
        high bits or all three low bits, whether the original value of a,b,c
        is almost all zero or is uniformly distributed,
        * If mix() is run forward or backward, at least 32 bits in a,b,c
        have at least 1/4 probability of changing.
        * If mix() is run forward, every bit of c will change between 1/3 and
        2/3 of the time.  (Well, 22/100 and 78/100 for some 2-bit deltas.)
        '''
        # Need to constrain U32 to only 32 bits using the & 0xffffffff
        # since Python has no native notion of integers limited to 32 bit
        # http://docs.python.org/library/stdtypes.html#numeric-types-int-float-long-complex
        a = int(a)
        b = int(b)
        c = int(c)
        a &= 0xffffffff; b &= 0xffffffff; c &= 0xffffffff
        a -= b; a -= c; a ^= (c>>13); a &= 0xffffffff
        b -= c; b -= a; b ^= (a<<8); b &= 0xffffffff
        c -= a; c -= b; c ^= (b>>13); c &= 0xffffffff
        a -= b; a -= c; a ^= (c>>12); a &= 0xffffffff
        b -= c; b -= a; b ^= (a<<16); b &= 0xffffffff
        c -= a; c -= b; c ^= (b>>5); c &= 0xffffffff
        a -= b; a -= c; a ^= (c>>3); a &= 0xffffffff
        b -= c; b -= a; b ^= (a<<10); b &= 0xffffffff
        c -= a; c -= b; c ^= (b>>15); c &= 0xffffffff
        return a, b, c

    def hash_32_1(self, a):
        a &= 0xffffffff
        hash = self.hash_seed^a
        b = a
        x = 231232
        y = 1232
        [b, x, hash] = self.hash_32_mix(b, x, hash)
        [y, a, hash] = self.hash_32_mix(y, a, hash)
        return hash

    def hash_32_2(self, a, b):
        a &= 0xffffffff
        b &= 0xffffffff
        hash = self.hash_seed^a^b
        x = 231232
        y = 1232
        [a, b, hash] = self.hash_32_mix(a, b, hash)
        [x, a, hash] = self.hash_32_mix(x, a, hash)
        [b, y, hash] = self.hash_32_mix(b, y, hash)
        return hash

    def hash_32_3(self, a, b, c):
        a &= 0xffffffff
        b &= 0xffffffff
        c &= 0xffffffff
        hash = self.hash_seed^a^b^c
        x = 231232
        y = 1232
        [a, b, hash] = self.hash_32_mix(a, b, hash)
        [c, x, hash] = self.hash_32_mix(c, x, hash)
        [y, a, hash] = self.hash_32_mix(y, a, hash)
        [b, x, hash] = self.hash_32_mix(b, x, hash)
        [y, c, hash] = self.hash_32_mix(y, c, hash)
        return hash

    def hash_32_4(self, a, b, c, d):
        a &= 0xffffffff
        b &= 0xffffffff
        c &= 0xffffffff
        d &= 0xffffffff
        hash = self.hash_seed^a^b^c^d
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
        a &= 0xffffffff
        b &= 0xffffffff
        c &= 0xffffffff
        d &= 0xffffffff
        e &= 0xffffffff
        hash = self.hash_seed^a^b^c^d^e
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

