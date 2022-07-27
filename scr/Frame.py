from __future__ import annotations

import abc
from math import ceil

import cv2
import numpy as np
from nptyping import NDArray, assert_isinstance
from sklearn.cluster import KMeans

from Convertor import Convertor
from File import File
from Rect import Contours, Rects
from Type_Alias import Mat, Path, Pixel_dtype, Point_dtype


class IFrame(metaclass=abc.ABCMeta):
    """Interface for Frame class"""

    # @abc.abstractclassmethod
    # def read_img(self, img: Mat) -> None:
    #     # read cv2 matrix style image
    #     raise NotImplementedError()

    @abc.abstractclassmethod
    def get_processed_imgs(self, img: Mat) -> Mat:
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_rectangles(self) -> Rects:
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_contours(self) -> Contours:
        raise NotImplementedError()


class Frame(IFrame, Rects):
    # instance var
    # img: Mat
    # gray_img: Mat
    # height:int
    # width:int

    def __init__(
        self, img: Mat, blur_rate: float = 1.0, offset_rate: float = 3.0
    ) -> None:
        assert self.__check_rgb_img(img)
        self.img = img
        # cv2.cvtColor accepts img:Mat, not Img
        self.gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.height = img.shape[0]
        self.width = img.shape[1]
        self.__blur_rate: float = blur_rate
        self.__offset_rate: float = offset_rate
        # Rects.__init__(self, contours=self.__find_contours())
        super().__init__(arg=self.__find_rects())

    def get_contours(self) -> Contours:
        return Rects.get_contours(self)

    def __check_rgb_img(self, img: Mat) -> bool:
        # instance check
        assert_isinstance(img, NDArray)
        # dtype check
        assert np.issubdtype(img.dtype, Pixel_dtype)
        # shape check
        assert img.ndim in (2, 3)
        if len(S := img.shape) == 3:
            assert S[-1] == 3
        return True

    def __to_odd(self, x: float) -> int:
        y: int = ceil(x)
        return y if y % 2 == 1 else y - 1

    def __to_gray(self, img: Mat) -> Mat:
        L = len(img.shape)
        return img if L == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def __get_effective_zone(self, thr: int = 250) -> tuple[int, int, int, int]:
        w: int = self.width
        h: int = self.height
        offset_percent: float = self.__offset_rate
        # blur the image and turn it into black-white
        gauss_x: int = self.__to_odd(max(offset_percent * w // 100, 1))
        gauss_y: int = self.__to_odd(max(offset_percent * h // 100, 1))
        img_blur: Mat = cv2.GaussianBlur(
            self.gray_img, (self.__to_odd(gauss_x), self.__to_odd(gauss_y)), 0
        )
        _, img_thr = cv2.threshold(img_blur, thr, 255, cv2.THRESH_BINARY)
        img_reversed: Mat = cv2.bitwise_not(img_thr)
        contours, _ = cv2.findContours(
            img_reversed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        # get the right and left end
        left_end: int = w
        right_end: int = 0
        upper_end: int = h
        lower_end: int = 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            left_end = min(left_end, x)
            right_end = max(right_end, x + w)
            upper_end = min(upper_end, y)
            lower_end = max(lower_end, y + h)
        return left_end, right_end, upper_end, lower_end

    def generate_frame(self) -> Mat:
        """generate a temporary frame to be processed further."""
        w: int = self.width
        h: int = self.height
        blur_rate: float = self.__blur_rate

        def generate_row_label_Kmeans(img: Mat, n_clusters=3):
            """generate label for each row"""
            # make sure that input image has no columns
            if img.shape[0] != img.size:
                err_msg = "img has multiple columns. It must be of 1 column."
                raise TypeError(err_msg)
            model = KMeans(n_clusters=n_clusters)
            model.fit(img_r := img.reshape(-1, 1))
            return model.predict(img_r), model.cluster_centers_

        # add new
        def generate_pre_frame(img, blur_rate: float = blur_rate) -> Mat:
            img = self.__to_gray(img)
            size_x: int = self.__to_odd(blur_rate * (w // 100))
            size_y: int = self.__to_odd(blur_rate * (h // 100))
            img_blur = cv2.blur(src=img, ksize=(size_x, size_y))
            avg_color_per_row = np.average(img_blur, axis=1)
            # detect by kmeans the rows of no information
            labels, centers = generate_row_label_Kmeans(avg_color_per_row, 3)
            # this cluster has very unlikely to intersect text
            label_for_absence = np.argmax(centers)
            # create frame for contours.
            # it should have the same size as input image
            frame = np.zeros((h, w, 3), Pixel_dtype)
            frame += 255  # make them all white
            if np.any(labels != label_for_absence):
                frame[labels != label_for_absence] = 0
            return frame

        gray = self.gray_img.copy()
        # apply twice to overwhelm thin white
        frame = generate_pre_frame(gray)
        # cv2.imwrite("test_frame1.png", frame)
        frame = generate_pre_frame(frame, blur_rate=blur_rate / 2)
        # cv2.imwrite("test_frame2.png", frame)

        # fill non-effective zone black
        left_end, right_end, _, _ = self.__get_effective_zone()
        # fill horizontal end
        frame[0:h, 0:left_end] = 255
        frame[0:h, right_end:w] = 255
        frame = cv2.bitwise_not(frame)
        _, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
        # cv2.imwrite("test_frame3.png", frame)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def __find_rects(self) -> Rects:
        con, _ = cv2.findContours(
            self.generate_frame(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return Rects(np.array(con, dtype=Point_dtype)).sorted()

    def expand_rects(self) -> None:
        """expand in y-axis each rects.

        expand to the internal division point (IVP) of neighboring contours.
        IVP is calculated based on the heights**2 of two neighboring contours.
        """
        # assume self is sorted possibly by find_rects()
        Len = len(self)
        # calculate ratio of internal division
        # the ratio is used for the amount of expansion
        # it is based on the squared heights of adjacent contours
        contours_height: NDArray = np.array([r.height for r in self])
        height_sq = contours_height**2
        denom = np.roll(height_sq, -1) + height_sq
        ratio_for_lower = height_sq[:-1] / denom[:-1]
        # vertical distance between neighboring contours
        contours: Contours = self.get_contours()
        dist = np.array(
            [(contours[i + 1][0] - contours[i][1]) for i in range(0, Len - 1)]
        )
        dist = np.array(dist, dtype=Point_dtype).flatten()[1::2]
        # amount of expansion
        plus_for_lower_rect = np.array(ratio_for_lower * dist).astype(Point_dtype)
        plus_for_upper_rect = (dist - plus_for_lower_rect).astype(
            Point_dtype
        )  # amount for the upper of edge of lower contours
        for i in range(0, Len):
            if i < Len - 1:
                # expand up the upper rect
                self[i].expand_below(plus_for_upper_rect[i])
                # expand down the lower rect
                self[i + 1].expand_above(plus_for_lower_rect[i])
            # expand the edges of the first and last contour by the same amount
            if i == 0:
                self[i].expand_above(plus_for_upper_rect[i])
            if i == Len - 1:
                self[i].expand_below(plus_for_lower_rect[i - 1])

    def draw_contours(
        self, color: tuple[int, int, int] = (0, 255, 0), lw: int = 2
    ) -> Mat:
        return cv2.drawContours(self.img, self.get_contours(), -1, color, lw)

    def get_framed_img(self) -> Mat:
        self.expand_rects()
        return self.draw_contours()

    def get_cropped_imgs(self) -> list[Mat]:
        img: Mat = self.img
        images: list[Mat] = []
        for contour in self.get_contours():
            x, y, w, h = cv2.boundingRect(contour)
            u = y + h
            r = x + w
            images.append(img[y:u, x:r])
        return images


if __name__ == "__main__":
    # import cv2
    path = Path("./test/005.png")
    F = File()
    F.read_file(path)
    C = Convertor()
    C.read_file(F)
    imgs = C.imgs
    img: Mat = imgs[0]
    blur_rate = 1.0
    f = Frame(img, blur_rate=blur_rate)
    # save
    img_drawn: Mat = f.draw_contours()
    cv2.imwrite("test_frame_drawn.jpeg", img)
