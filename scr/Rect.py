from __future__ import annotations

from typing import Any, Final, Iterable, TypeGuard

import numpy as np
from nptyping import NDArray

from Type_Alias import Contour, Contours, Point, Point_dtype, Point_Like, Rect_Like_


class Rect:
    # class var
    __point_shape: Final = (1, 2)
    __contour_shape: Final = (4, 1, 2)
    # instance var
    # upper_left: Point
    # width: int
    # height: int

    @property
    def x(self) -> int:
        return self.upper_left[0][0]

    @property
    def y(self) -> int:
        return self.upper_left[0][1]

    def __init__(self, x: Contour | Rect | Rect_Like_):
        if isinstance(x, NDArray) and self.__is_contour(x):
            p, _, u, _ = x
            w, h = (u - p).reshape(2)
            self.upper_left: Point = p
            self.width: int = w
            self.height: int = h
        elif isinstance(x, Rect):
            self.upper_left = x.upper_left
            self.width: int = x.width
            self.height: int = x.height
        elif self.__is_Rect_like(x) and not isinstance(x, Rect):
            # not Rect above is just for avoid IDE warning
            p, w, h = x
            assert self.__is_Point_Like(p)
            self.upper_left = self.__to_Point(p)
            self.width = w
            self.height = h
        else:
            raise TypeError("Rects failed to initialize. Invalid type.")

    def __lt__(self, other) -> bool:
        # compare by upper-left y
        return self.y < other.y

    def __is_Point(self, x: Point_Like) -> TypeGuard[Point]:
        return (
            isinstance(x, NDArray)
            and x.shape == self.__point_shape
            and x.dtype == Point_dtype
        )

    def __is_Point_Like(self, x: Any) -> TypeGuard[Point_Like]:
        return (
            True
            if isinstance(x, NDArray) and self.__is_Point(x)
            else isinstance(x, (list, tuple))
            and len(x) == 2
            and isinstance(x[0], int)
            and isinstance(x[1], int)
            and x[0] >= 0
            and x[1] >= 0
        )

    def __to_Point(self, p: Point_Like) -> Point:
        return p if self.__is_Point(p) else np.array([p], dtype=Point_dtype)

    def __is_contour(self, x: NDArray[Any, Any]) -> TypeGuard[Contour]:
        return (
            isinstance(x, NDArray)
            and x.shape == self.__contour_shape
            and x.dtype == Point_dtype
        )

    def __is_Rect_like(
        self, x: Rect | Rect_Like_ | Iterable
    ) -> TypeGuard[Rect_Like_ | Rect]:
        return (
            True
            if isinstance(x, Rect)
            else isinstance(x, tuple)
            and len(x) == 3
            and self.__is_Point_Like(x[0])
            and isinstance(x[1], int)
            and isinstance(x[2], int)
            and x[1] > 0
            and x[2] > 0
        )

    # def set_rect(self, p: Point_Like, width: int, height: int) -> Rect:
    #     self.__check_points([p])
    #     assert width >= 0
    #     assert height >= 0
    #     self.upper_left: Point = np.array(p)
    #     self.width: int = width
    #     self.height: int = height
    #     return self

    # def set_rect_from_points(
    #     self, upper_left: Point_Like, lower_right: Point_Like
    # ) -> Rect:
    #      self.__check_points([upper_left, lower_right])
    #     height: int = lower_right[1] - upper_left[1]
    #     width: int = lower_right[0] - upper_left[0]
    #     return self.set_rect(np.array(upper_left), width, height)

    # def set_rect_from_contour(self, contour) -> Rect:
    #     upper_left, _, lower_right, _ = contour
    #     return self.set_rect_from_points(upper_left[0], lower_right[0])

    # def __is_valid_rect(self) -> bool:
    #     return (
    #         assert_isinstance(self.upper_left, Point)
    #         and self.width >= 0
    #         and self.height >= 0
    #     )

    # def __check_points(self, ps: list[Point_Like]) -> bool:
    #     for p in ps:
    #         if isinstance(p, (list, tuple)):
    #             assert len(p) == 2
    #         else:
    #             assert_isinstance(p, Point)
    #     return True

    def get_rect_property(self) -> tuple[Point, int, int]:
        # assert self.__is_valid_rect()
        return self.upper_left, self.width, self.height

    def get_corner_points(self) -> tuple[Point, Point, Point, Point]:
        h = self.height
        w = self.width
        return (
            self.upper_left,
            self.upper_left + np.array([0, h], dtype=Point_dtype),
            self.upper_left + np.array([w, h], dtype=Point_dtype),
            self.upper_left + np.array([w, 0], dtype=Point_dtype),
        )

    def get_contour(self) -> Contour:
        return np.array(self.get_corner_points()).reshape(4, 1, 2)

    def expand_above(self, amount: int) -> None:
        self.upper_left -= np.array([0, amount])
        self.height += amount

    def expand_below(self, amount: int) -> None:
        self.height += amount


class Rects(list[Rect]):
    __contour_shape: Final = (4, 1, 2)

    def __init__(self, arg: Iterable[Rect] | Contours):
        if self.__is_contours(arg):
            super().__init__([Rect(c) for c in arg])
        elif all(isinstance(x, Rect) for x in arg):
            super().__init__(arg)
        else:
            msg = "arg must be of type either iterable[rect] or contours"
            raise TypeError(msg)

    def __is_contours(self, x: Any) -> TypeGuard[Contours]:
        return (
            isinstance(x, NDArray)
            and x.shape[1:] == self.__contour_shape
            and x.dtype == Point_dtype
        )

    def get_rects_obj(self) -> Rects:
        return self

    def get_contours(self) -> Contours:
        return np.array([rect.get_contour() for rect in self]).astype("int")

    def sort(self, reverse=False) -> None:
        # Rect.__lt__() governs the way rects is sorted
        super().sort(reverse=reverse)

    def sorted(self, reverse=False) -> Rects:
        r = Rects(self)
        r.sort(reverse=reverse)
        return r


if __name__ == "__main__":
    x = [1, 2]
    r = Rect((x, 1, 2))
    # print(f"r = {r.get_rect_property()}")
    # con = r.get_contour()
    # print(f"con = {con}")
    # rc = Rect(con)
    # print(f"rc = {rc.get_rect_property()}")
    # rs = Rects(np.array([r.get_contour()]))
    # r2 = Rect(r)
    # print(f"typeof r2 = {type(r2)}")
    # print(r2.get_corner_points())
    y = [0, 1]
    r2 = Rect((y, 1, 2))
    rs = Rects([r, r2])
    print(f"rects = {rs.get_contours()}")
    print("sort rects")
    rs.sort()
    print(f"sorted rects = {rs.get_contours()}")
