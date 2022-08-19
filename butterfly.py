import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

SLATE = "#334155"
PINK = "#EC4899"


@dataclass
class CanvasConfig:
    width: float
    height: float


class SVGDrawer:
    def __init__(self, canvas: CanvasConfig):
        self._buf = f'<svg width="{canvas.width}" height="{canvas.height}" viewBox="0 0 1 1">'

    def circle(self, x: float, y: float, r: float):
        self._buf += f'<circle cx="{x}" cy="{y}" r="{r}"/>'

    def line(self, stroke: str, w: float, x1: float, y1: float, x2: float, y2: float):
        self._buf += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="square"/>'

    def output(self) -> str:
        self._buf += '</svg>'
        return self._buf


class RoutingDrawer:
    def __init__(self, depth: int, width: int, node_diameter: float):
        # Depth + 1 node layers, depth routing layers
        self._slice_width = 1 / (2 * depth + 1)
        # So that nodes occupy 1 / 2 a slice
        self._node_radius = self._slice_width / 4
        self._line_width = self._node_radius / 4
        self._slice_height = 1 / width

        # Get the height of the canvas based on the absolute node diameter size
        canvas_width = 2 * node_diameter / self._slice_width
        # Similar trick for the height, since a vertical slice is 2 nodes in width
        canvas_height = 2 * node_diameter / self._slice_height

        self._svg = SVGDrawer(CanvasConfig(
            width=canvas_width, height=canvas_height)
        )

    def _node_center(self, pos: Tuple[int, int]) -> Tuple[float, float]:
        x = self._slice_width * (2 * pos[0]) + self._slice_width / 2
        y = self._slice_height * pos[1] + self._slice_height / 2
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

    def draw_svg(self, node_diameter: float) -> str:
        drawer = RoutingDrawer(self.depth, 1 << self.size, node_diameter)
        for col in range(self.depth + 1):
            for row in range(1 << self.size):
                drawer.node((col, row))

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
                front = mask_front & j
                back = mask_back & j
                a = (front << 1) | back
                b = (front << 1) | middle | back
                if choice == Choice.Swap:
                    drawer.connection(PINK, (i, a), (i + 1, b))
                    drawer.connection(PINK, (i, b), (i + 1, a))
                else:
                    drawer.connection(SLATE, (i, a), (i + 1, a))
                    drawer.connection(SLATE, (i, b), (i + 1, b))

        return drawer.output()


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
