import abc

import cv2
import numpy as np
from nptyping import NDArray, assert_isinstance
from sklearn.cluster import KMeans

from Rect import Contours, Rect, Rects
from Type_Alias import Mat


class IFrame(metaclass=abc.ABCMeta):
    """Interface for Frame class"""

    # @abc.abstractclassmethod
    # def read_img(self, img: Mat) -> None:
    #     # read cv2 matrix style image
    #     raise NotImplementedError()

    @abc.abstractclassmethod
    def process(self) -> None:
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_rectangles(self) -> Rects:
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_contours(self) -> Contours:
        raise NotImplementedError()


class Frame(IFrame, Rects):
    img: Mat
    gray_img: Mat
    # height:int
    # width:int

    def __init__(self, img: Mat) -> None:
        assert self.__check_rgb_img(img)
        self.img = img
        # cv2.cvtColor accepts img:Mat, not Img
        self.gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.height = img.shape[0]
        self.width = img.shape[1]
        # Rects.__init__(self, contours=self.__find_contours())
        super().__init__(contours=self.__find_contours())

    # def read_img(self, img: Img) -> None:
    #     self.__check_rgb_img(img)
    #     self.img = img

    def get_rectangles(self) -> Rects:
        return self.get_rects()

    def get_contours(self) -> Contours:
        return self.get_contours()

    def __check_rgb_img(self, img: Mat, np_dtype=np.uint8) -> bool:
        # instance check
        assert_isinstance(img, NDArray)
        # dtype check
        assert np.issubdtype(img.dtype, np_dtype)
        # shape check
        assert img.ndim in (2, 3)
        if len(S := img.shape) == 3:
            assert S[-1] == 3
        return True

    def __to_odd(self, x: int) -> int:
        return x if x % 2 == 1 else x - 1

    def __get_effective_zone(
        self, offset_percent: int = 1, thr: int = 250
    ) -> tuple[int, int, int, int]:
        # blur the image and turn it into black-white
        gauss_x: int = self.__to_odd(max(offset_percent * self.width // 100, 1))
        gauss_y: int = self.__to_odd(max(offset_percent * self.height // 100, 1))
        img_blur: Mat = cv2.GaussianBlur(
            self.gray_img, (self.__to_odd(gauss_x), self.__to_odd(gauss_y)), 0
        )
        _, img_thr = cv2.threshold(img_blur, thr, 255, cv2.THRESH_BINARY)
        img_reversed: Mat = cv2.bitwise_not(img_thr)
        contours, _ = cv2.findContours(
            img_reversed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        # get the right and left end
        left_end: int = self.width
        right_end: int = 0
        upper_end: int = self.height
        lower_end: int = 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            left_end = min(left_end, x)
            right_end = max(right_end, x + w)
            upper_end = min(upper_end, y)
            lower_end = max(lower_end, y + h)
        return left_end, right_end, upper_end, lower_end

    def __generate_frame(self, blur_rate: int = 2) -> Mat:
        """generate a temporary frame to be processed further."""

        def generate_row_label_Kmeans(img: Mat, n_clusters=3):
            """generate label for each row"""
            # make sure that input image has no columns
            if img.shape[0] != img.size:
                raise TypeError(
                    "img has multiple columns. It should be of at most 1 column."
                )
            model = KMeans(n_clusters=n_clusters)
            model.fit(img_r := img.reshape(-1, 1))
            return model.predict(img_r), model.cluster_centers_

        img_blur = cv2.GaussianBlur(
            self.gray_img,
            (
                self.__to_odd(blur_rate * (w := self.width) // 100),
                self.__to_odd(blur_rate * (h := self.height) // 100),
            ),
            3,
        )
        avg_color_per_row = np.average(img_blur, axis=1)
        # detect by kmeans the rows of no information
        labels, centers = generate_row_label_Kmeans(avg_color_per_row, 3)
        # this cluster has very unlikely to intersect text
        label_for_absence = np.argmax(centers)
        # create frame for contours.
        # it should have the same size as input image
        frame = np.zeros((h, w, 3), np.uint8)
        frame += 255  # make them all white
        if np.any(labels != label_for_absence):
            frame[labels != label_for_absence] = 0

        # fill non-effective zone black
        left_end, right_end, _, _ = self.__get_effective_zone()
        # fill horizontal end
        frame[0:h, 0:left_end] = 255
        frame[0:h, right_end:w] = 255
        frame = cv2.bitwise_not(frame)
        _, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def __find_contours(self) -> Contours:
        contours, _ = cv2.findContours(
            self.__generate_frame(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return np.array(contours)

    def expand_contours(self, contours: Contours):
        """expand in y-axis each contour to the internal division point (IVP) of neighboring contours.
        IVP is calculated based on the heights of two neighboring contours.
        """
        Len = len(contours)
        contours = sort_contours(contours)
        # calculate ratio of internal division by which the amount of expansion is determined
        # the ratio is based on the squared heights of adjacent contours
        contours_height = get_contours_height(contours)
        height_sq = contours_height**2
        denom = np.roll(height_sq, -1) + height_sq
        ratio_for_lower = height_sq[:-1] / denom[:-1]
        # vertical distance between neighboring contours
        dist = np.array(
            [(contours[i + 1][0] - contours[i][1]) for i in range(0, Len - 1)]
        )
        dist = np.array(dist, dtype=np.int32).flatten()[1::2]
        # amount of expansion
        plus_for_lower_contour = np.array(ratio_for_lower * dist, dtype=np.int32)
        plus_for_upper_contour = (
            dist - plus_for_lower_contour
        )  # amount for the upper of edge of lower contours
        for i in range(0, Len):
            if i < Len - 1:
                contours[i] = __get_expanded_contour(
                    contours[i], plus_for_upper_contour[i], expand_upper_edge=False
                )
                contours[i + 1] = __get_expanded_contour(
                    contours[i + 1], plus_for_lower_contour[i], expand_upper_edge=True
                )
            # expand the free edge of the first and the last contour by the same amount
            if i == 0:
                contours[i] = __get_expanded_contour(
                    contours[i], plus_for_upper_contour[i], expand_upper_edge=True
                )
            if i == Len - 2:
                contours[i + 1] = __get_expanded_contour(
                    contours[i + 1], plus_for_lower_contour[i], expand_upper_edge=False
                )
        return contours


if __name__ == "__main__":
    # import cv2

    img_path = "006.png"
    img = cv2.imread(img_path)
    f = Frame(img)
    print(f"ok! {img_path}")
    print(f"width = {f.width}")
    f.sort()
    print(f"rects = {f.rects[0].get_rect_property()}")
