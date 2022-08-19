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
    size: int
    choices: List[List[Optional[Choice]]]

    @property
    def width(self) -> int:
        return 1 << (self.size - 1)

    @property
    def depth(self) -> int:
        return 2 * self.size - 1

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
        return Routing(size, choices)


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
