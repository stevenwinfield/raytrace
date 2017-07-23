import random
import time

class LCG(random.Random):
    """A linear congruential generator.

    x_{n+1} = (a * x_n + c) mod m
    """

    def __init__(self, a, c, m, x0=None):
        self.a = a
        self.c = c
        self.m = m
        self.x = x0 or int(time.time() % m)

    def __iter__(self):
        return self

    def __next__(self):
        self.x = (self.a * self.x + self.c) % self.m
        return self.x

    def random(self):
        return self.__next__() / self.m

    def seed(self, value):
        self.x = int(value) % self.m

    def getstate(self):
        return (self.a, self.c, self.m, self.x)

    __getstate__ = getstate

    def setstate(self, state):
        self.a, self.c, self.m, self.x = state

    __setstate__ = setstate

    def randbits(self, k):
        m_bits = self.m.bit_length()
        # Don't use the most significant bit - it probably won't be uniformly distributed
        chunk_size = m_bits - 1
        mask = (1 << chunk_size) - 1  # chunk_size 1's
        result = 0
        loops, remainder = divmod(k, chunk_size)
        if remainder > 0:
            loops += 1
        for _ in loops:
            result <<= chunk_size
            result += self.__next__() & mask
        # Trim off extra bits
        result >>= loops * chunk_size - k
        return result