from __future__ import annotations

from typing import TypeAlias

import numpy as np
from nptyping import Int, NDArray, Shape, assert_isinstance

Point: TypeAlias = NDArray[Shape["2"], Int]
Point_Like: TypeAlias = Point | tuple[int, int] | list[int]
Contour: TypeAlias = NDArray[Shape["4,1,2"], Int]
Contours: TypeAlias = NDArray[Shape["*,4,1,2"], Int]


class Rect:
    upper_left: Point = np.array([0, 0])
    width: int = -1
    height: int = -1

    def __init__(self):
        # dummy property to be overwritten by set_rect* methods
        self.upper_left: Point = np.array([0, 0])
        self.width: int = -1
        self.height: int = -1

    def __lt__(self, other) -> bool:
        # compare by upper-left y
        return self.upper_left[1] < other.upper_left[1]

    def set_rect(self, p: Point_Like, width: int, height: int) -> Rect:
        self.__check_points([p])
        assert width >= 0
        assert height >= 0
        self.upper_left: Point = np.array(p)
        self.width: int = width
        self.height: int = height
        return self

    def set_rect_from_points(
        self, upper_left: Point_Like, lower_right: Point_Like
    ) -> Rect:
        self.__check_points([upper_left, lower_right])
        height: int = lower_right[1] - upper_left[1]
        width: int = lower_right[0] - upper_left[0]
        return self.set_rect(np.array(upper_left), width, height)

    def set_rect_from_contour(self, contour) -> Rect:
        upper_left, _, lower_right, _ = contour
        return self.set_rect_from_points(upper_left[0], lower_right[0])

    def __is_valid_rect(self) -> bool:
        return (
            assert_isinstance(self.upper_left, Point)
            and self.width >= 0
            and self.height >= 0
        )

    def __check_points(self, ps: list[Point_Like]) -> bool:
        for p in ps:
            if isinstance(p, (list, tuple)):
                assert len(p) == 2
            else:
                assert_isinstance(p, Point)
        return True

    def get_rect_property(self) -> tuple[Point, int, int]:
        assert self.__is_valid_rect()
        return self.upper_left, self.width, self.height

    def get_corner_points(self) -> tuple[Point, Point, Point, Point]:
        assert self.__is_valid_rect()
        lower_left: Point = self.upper_left + np.array([0, self.height])
        lower_right = lower_left + np.array([self.width, 0])
        upper_right = self.upper_left + np.array([self.width, 0])
        return self.upper_left, lower_left, lower_right, upper_right

    def get_contour(self) -> Contour:
        return np.array(self.get_corner_points()).reshape(4, 1, 2)

    def expand_above(self, amount: int) -> Rect:
        self.upper_left -= np.array([0, amount])
        self.height += amount
        return self

    def expand_below(self, amount: int) -> Rect:
        self.height += amount
        return self


class Rects(list[Rect]):
    def __init__(self, contours: Contours):
        contours = contours.astype("int")
        assert_isinstance(contours, Contours)
        super().__init__()
        self.rects = [Rect().set_rect_from_contour(c) for c in contours]

    def set_rects(self, list_rect: list[Rect]) -> Rects:
        self.rects = list_rect
        return self

    def get_rects_obj(self) -> Rects:
        return self

    def get_contours(self) -> Contours:
        return np.array([rect.get_contour() for rect in self.rects]).astype("int")

    def sort(self, reverse=False) -> None:
        # Rect.__lt__() governs the way rects is sorted
        self.rects.sort(reverse=reverse)


if __name__ == "__main__":
    x = (1, 2)
    r = Rect().set_rect(x, 1, 2)
    print(f"r = {r.get_rect_property()}")
    rs = Rects(np.array([r.get_contour()]))
    print
    print(isinstance(rs, Rects))
    print(isinstance(rs.get_contours(), Contours))
