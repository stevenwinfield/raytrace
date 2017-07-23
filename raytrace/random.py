import sys
import random
import time

class _LCG(random.Random):
    """A linear congruential generator.

    x_{n+1} = (a * x_n + c) mod m
    """

    def __init__(self, seed=None):
        self.a = None
        self.c = None
        self.m = None
        self.x = None
        super().__init__(seed)

    def __iter__(self):
        return self

    def __next__(self):
        self.x = (self.a * self.x + self.c) % self.m
        return self.x

    def random(self):
        return self.__next__() / self.m

    def seed(self, a=None, _version=None):
        if self.m is None:
            return  # This instance isn't fully set up yet
        if a is None:
            try:
                self.x = random.SystemRandom().randrange(self.m)
            except NotImplementedError:
                self.x = int(time.time() % self.m)
        elif isinstance(a, (str, bytes, bytearray)):
            if isinstance(a, str):
                a = a.encode("utf8")
            self.x = int.from_bytes(a, "big", signed=False) % self.m
        elif isinstance(a, int):
            self.x = a % self.m
        else:
            raise TypeError("New seed must be an int, str, bytes, or bytearray - not " + type(a).__name__)

    def getstate(self):
        return (self.a, self.c, self.m, self.x)

    __getstate__ = getstate

    def setstate(self, state):
        self.a, self.c, self.m, self.x = state

    __setstate__ = setstate

    def getrandbits(self, k):
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

def lcg(a, c, m, seed=None):
    result = _LCG()
    result.a, result.c, result.m = a, c, m
    result.seed(seed)
    return result

#def lcg_with_period(period):


r = lcg(123, 456, 789)
for _ in range(100):
    print(next(r))
