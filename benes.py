import random
from typing import Dict

Permutation = Dict[int, int]


def random_permutation(size: int) -> Permutation:
    """Generate a random permutation with 2^size elements.
    """
    count = 1 << size
    out = dict()
    for x in range(count):
        if x in out:
            continue
        y = random.randrange(count)
        out[x] = y
        out[y] = x
    return out
