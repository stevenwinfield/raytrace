import base64
import bisect
import functools
import operator
import struct
import random
import time
import zlib

from collections import defaultdict

class _LCG(random.Random):
    """A linear congruential generator.

    x_{n+1} = (a * x_n + c) mod m
    """

    def __init__(self, seed=None):
        self.a = None
        self.c = None
        self.m = None
        self.x = None
        self.period = None
        super().__init__(seed)

    def __str__(self):
        return "LCG(a={}, c={}, m={}, period={}, seed={})".format(self.a, self.c, self.m, self.period, self.x)

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            self.x = (self.a * self.x + self.c) % self.m
            if self.x < self.period:
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
        return (self.a, self.c, self.m, self.period, self.x)

    __getstate__ = getstate

    def setstate(self, state):
        self.a, self.c, self.m, self.period, self.x = state

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
        for _ in range(loops):
            result <<= chunk_size
            result += self.__next__() & mask
        # Trim off extra bits
        result >>= loops * chunk_size - k
        return result

def lcg(a, c, m, period=None, seed=None):
    period=period or m
    result = _LCG()
    result.a, result.c, result.m, result.period = a, c, m, period
    result.seed(seed)
    return result

def prime_index(n):
    ''' If prime, return n's index in the PRIMES array, else return None '''
    # Quick linear search for small values
    if n < 37:
        try:
            return PRIMES[:12].index(n)
        except ValueError:
            return None
    else:
    # Binary search for larger values
        index_upper_bound = min(n // 3, len(PRIMES))
        index = bisect.bisect_left(PRIMES, n, 0, index_upper_bound)
        if index != index_upper_bound and PRIMES[index] == n:
            return index
        else:
            return None

def prime_factorisation(n):
    ''' Compute the prime factorisation of n.
        Returns a defaultdict of {prime: power}.
    '''
    assert 1 <= n <= 10968163441, "n must be in the range [1, (10000th prime)^2]"
    result = defaultdict(int)

    # Quickly see if n is in our prime list
    if prime_index(n) is not None:
        result[n] = 1
        return result

    for p in PRIMES:
        if p > n:
            return result
        while n % p == 0:
            result[p] += 1
            n //= p
    # n is prime
    result[n] += 1
    return result

def expand(factorisation):
    ''' Return the number to which this factorisation belongs '''
    return functools.reduce(operator.mul, map(lambda el: el[0] ** el[1], factorisation.items()), 1)

def _test_prime_factorisation():
    assert all(n == expand(prime_factorisation(n)) for n in range(1,10000))

def lcg_with_period(period, max_attempts=10, _actual_period=None):
    # x_{n+1} = (a * x_n + c) mod m
    # a is in [1, m)   c in [0, m)    and m > 0
    # An LCG's period is at most m, for which:
    # c and m must be coprime
    # a - 1 must have all m's prime factors
    # if m is divisible by 4 then a - 1 must be too
    assert period > 2

    if max_attempts == 0:
        raise ValueError("Couldn't find LCG parameters with the required period")

    # Just set m to the required period
    m = period

    # Let's try to find a nice big prime for c that isn't in m's factors
    m_factorisation = prime_factorisation(m)
    if m > PRIMES[-1]:
        index_end = len(PRIMES)
    else:
        index_end = bisect.bisect_left(PRIMES, m, 0, min(m, len(PRIMES)))
    possibilities = set(PRIMES[:index_end]) - m_factorisation.keys()
    if len(possibilities) == 0:
        c = 1  # Guaranteed to be coprime with m
    else:
        c = max(possibilities)

    # Let's make (a - 1) as big as possible - it should have the same prime factorisation as m except
    # the lowest prime factor with power > 1 should be raised to a smaller power.
    # ...Unless that prime is 2, in which case the power cannot fall below 2 (for the divisible-by-4 condition above)
    for prime, power in sorted(m_factorisation.items()):
        if power > (2 if prime == 2 else 1):
            a = m // prime + 1
            break
    else:
        # Oh dear - we couldn't find an a < m that had all of m's prime factors and obeyed the divisible-by-4 condition.
        # Let's try again with a slightly higher period - when values greater than min_period are yielded by the LCG
        # they will need to be skipped
        return lcg_with_period(period + 1, max_attempts - 1, _actual_period or period)

    return lcg(a, c, m, period=_actual_period or period)

PRIMES = struct.unpack("<10000I", zlib.decompress(base64.b64decode(
"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"
"kTSRRf+X8L8IQe")))

period = 1920*1080
r = lcg_with_period(period)
s = {next(r) for _ in range(r.period + 10)}
print(r, len(s))