import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

SLATE = "#334155"
PINK = "#EC4899"


@dataclass
class CanvasConfig:
    width: float
    height: float


class SVGDrawer:
    def __init__(self, canvas: CanvasConfig):
        self._canvas = canvas
        self._buf = f'<svg width="{canvas.width}" height="{canvas.height}">'

    def circle(self, x: float, y: float, r: float):
        self._buf += f'<circle cx="{x}" cy="{y}" r="{r}"/>'

    def line(self, stroke: str, w: float, x1: float, y1: float, x2: float, y2: float):
        self._buf += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="square"/>'

    def output(self) -> str:
        self._buf += '</svg>'
        return self._buf


class RoutingDrawer:
    def __init__(self, depth: int, width: int, node_diameter: float):
        self._slice_width = 2 * node_diameter
        self._slice_height = self._slice_width
        canvas_width = (2 * depth + 3) * self._slice_width
        canvas_height = (2 + width) * self._slice_height
        self._node_radius = node_diameter / 2
        self._line_width = self._node_radius / 4

        self._svg = SVGDrawer(CanvasConfig(
            width=canvas_width, height=canvas_height)
        )

    def _node_center(self, pos: Tuple[int, int]) -> Tuple[float, float]:
        x = self._slice_width * (2 * pos[0] + 1) + self._slice_width / 2
        y = self._slice_height * (pos[1] + 1) + self._slice_height / 2
        return (x, y)

    def node(self, pos: Tuple[int, int]):
        x, y = self._node_center(pos)
        self._svg.circle(x, y, self._node_radius)

    def connection(self, stroke: str, src: Tuple[int, int], dst: Tuple[int, int]):
        x1, y1 = self._node_center(src)
        x1 += self._node_radius
        x2, y2 = self._node_center(dst)
        x2 -= self._node_radius
        self._svg.line(stroke, self._line_width, x1, y1, x2, y2)

    def output(self) -> str:
        return self._svg.output()


class Permutation:
    def __init__(self, mapping: Iterable[Tuple[int, int]]):
        self._forwards = {k: v for k, v in mapping}
        self._backwards = {v: k for k, v in self._forwards.items()}

    @staticmethod
    def random(size: int) -> "Permutation":
        count = 1 << size
        numbers = list(range(count))
        random.shuffle(numbers)
        return Permutation(enumerate(numbers))

    def __repr__(self):
        return f'<Permutation {self._forwards}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Permutation) and self._forwards == other._forwards

    def forwards(self, x: int) -> int:
        return self._forwards[x]

    def backwards(self, y: int) -> int:
        return self._backwards[y]


class Choice(Enum):
    Pass = 0
    Swap = 1

    def __invert__(self) -> "Choice":
        return self.__class__(1 ^ self.value)


@dataclass
class Routing:
    size: int
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
        return Routing(size, choices)

    @property
    def depth(self) -> int:
        return 2 * self.size - 1

    @property
    def width(self) -> int:
        return 1 << (self.size - 1)

    def _ordered_choices(self) -> Iterator[Tuple[int, Choice, int, int]]:
        middle_i = self.size
        reverse = False
        for i, col_choices in enumerate(self.choices):
            if reverse:
                middle_i += 1
            else:
                middle_i -= 1
                if middle_i == 0:
                    reverse = True
            middle = 1 << middle_i
            mask_back = middle - 1
            mask_front = ((1 << (self.size - 1)) - 1) ^ mask_back
            for j, choice in enumerate(col_choices):
                if choice is None:
                    continue
                front = mask_front & j
                back = mask_back & j
                a = (front << 1) | back
                b = (front << 1) | middle | back
                yield (i, choice, a, b)

    def permutation(self) -> Permutation:
        xs = list(range(1 << self.size))
        for _, choice, a, b in self._ordered_choices():
            if choice == Choice.Swap:
                xs[a], xs[b] = xs[b], xs[a]
        return Permutation((v, k) for k, v in enumerate(xs))

    def draw_svg(self, node_diameter: float) -> str:
        drawer = RoutingDrawer(self.depth, 1 << self.size, node_diameter)
        for col in range(self.depth + 1):
            for row in range(1 << self.size):
                drawer.node((col, row))

        for i, choice, a, b in self._ordered_choices():
            if choice == Choice.Swap:
                drawer.connection(PINK, (i, a), (i + 1, b))
                drawer.connection(PINK, (i, b), (i + 1, a))
            else:
                drawer.connection(SLATE, (i, a), (i + 1, a))
                drawer.connection(SLATE, (i, b), (i + 1, b))

        return drawer.output()


def _choice_for(bot: int, hi: int) -> Choice:
    return Choice(bot ^ hi)


def route_permutation(size: int, permutation: Permutation) -> Routing:
    routing = Routing.sized(size)
    queue: List[Tuple[int, Permutation, int, int]] = [
        (size, permutation, 0, 0)
    ]

    def go(size: int, permutation: Permutation, base_x: int, base_y: int):
        if size == 1:
            swap = permutation.forwards(0) != 0
            choice = Choice.Swap if swap else Choice.Pass
            routing.choices[base_x][base_y] = choice
            return

        e = 1 << (size - 1)
        mask = e - 1

        perms: List[Dict[int, int]] = [dict(), dict()]

        # First, assign a "color" (side) for each input node
        colors: Dict[int, int] = dict()
        for x in range(1 << size):
            # Follow a coloring path starting from x
            while x not in colors:
                colors[x] = 0
                x ^= e
                colors[x] = 1
                x = permutation.backwards(e ^ permutation.forwards(x))

        # With these consistent colors, we can now just assign routes directly.
        for x in range(1 << size):
            x_hi = x >> (size - 1)
            x_lo = x & mask

            y = permutation.forwards(x)
            y_hi = y >> (size - 1)
            y_lo = y & mask

            color = colors[x]

            front = base_x
            back = base_x + 2 * (size - 1)

            routing.choices[front][base_y + x_lo] = _choice_for(color, x_hi)
            routing.choices[back][base_y + y_lo] = _choice_for(color, y_hi)
            perms[color][x_lo] = y_lo

        queue.append(
            (size - 1, Permutation(perms[0].items()), base_x + 1, base_y)
        )
        queue.append(
            (size - 1, Permutation(perms[1].items()),
             base_x + 1, base_y + (1 << (size - 2)))
        )

    while queue:
        go(*queue.pop())

    return routing


def fuzz(size: int, rounds: int = 100):
    for _ in range(rounds):
        perm0 = Permutation.random(size)
        perm1 = route_permutation(size, perm0).permutation()
        assert perm0 == perm1
