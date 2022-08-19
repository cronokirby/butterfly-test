import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class Choice(Enum):
    Pass = 0
    Swap = 1

    def __invert__(self) -> "Choice":
        return self.__class__(1 ^ self.value)


@dataclass
class Routing:
    depth: int
    width: int
    choices: List[List[Optional[Choice]]]

    @staticmethod
    def sized(size: int) -> "Routing":
        """Create a new routing network of a certain size.

        By default, no routing will be set.
        """
        depth = 2 * size - 1
        width = 1 << (size - 1)
        choices: List[List[Optional[Choice]]] = [
            [None for _ in range(width)] for _ in range(depth)
        ]
        return Routing(depth, width, choices)


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
