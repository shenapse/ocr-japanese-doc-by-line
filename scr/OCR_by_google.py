from __future__ import annotations

import abc
from itertools import chain
from math import floor
from os.path import getsize
from typing import Final, TypeGuard

import numpy as np
from google.cloud import vision
from google.cloud.vision_v1.types.image_annotator import AnnotateImageResponse as Response

from Rect import Rect
from Type_Alias import Contour, Path, Point_dtype

# from google.cloud.vision_v1.types.text_annotation import Symbol
# from google.cloud.vision_v1.types.text_annotation import TextAnnotation
# from google.cloud.vision_v1.types.geometry import BoundingPoly


class Box(Rect):
    def __init__(self, text: str, rect: Rect):
        self.text: str = text
        super().__init__(rect)


class IOCR(metaclass=abc.ABCMeta):
    """Interface for COR class"""

    @abc.abstractclassmethod
    def read_img(self, img_path: Path) -> None:
        raise NotImplementedError()

    @abc.abstractclassmethod
    def get_text(self) -> str:
        raise NotImplementedError()


class OCR(IOCR):
    def __init__(self):
        self._empty_response: Final = Response()
        self._max_img_size: Final[int] = 20 * 10**6
        # dummy response to mean there is no valid response
        self._response: Response = self._empty_response
        self._lines: list[list[Box]] = []

    @property
    def response(self) -> Response:
        return self._response

    def get_lines(self) -> list[list[Box]]:
        return self._lines

    def is_response_set(self) -> TypeGuard[Response]:
        return self.response != self._empty_response

    def read_img(self, img_path: Path) -> None:
        """set response property by reading image file."""
        if not self.check_size(img_path):
            msg: str = f"Invalid img size. Got {getsize(str(img_path))/(10**6)} MB. It must be under {self._max_img_size//(10**6)} MB."
            raise ValueError(msg)
        client = vision.ImageAnnotatorClient()
        self._response = client.document_text_detection(  # type: ignore
            image=vision.Image(content=self.get_byte_img(img_path)),
            image_context={"language_hints": ["ja", "eng"]},
        )
        # clear old lines
        self._lines = []

    def get_byte_img(self, img_path: Path) -> bytes:
        with open(str(img_path), mode="rb") as img:
            return img.read()

    def check_size(self, img_path: Path) -> bool:
        return 0 < getsize(str(img_path)) < self._max_img_size

    def read_response(self, res: Response) -> None:
        """directly set response property without reading image file."""
        self._response = res
        # clear old lines
        self._lines = []

    def _get_vertical_threshold(self, boxes: list[Box], scale: float = 0.7) -> int:
        """used for classifying bounding boxes"""
        assert boxes != []
        h_array = np.array([b.height for b in boxes])
        return floor(np.median(h_array) * scale)

    def _get_horizontal_threshold_iqr(self, line: list[Box], scale: float = 1.5) -> int:
        """threshold for each line by which we decide whether to insert a space character between characters in that line.
        this thr is determined by the iqr of x-interval of boxes in the line.
        """
        x_interval: list[int] = [box.x - (line[i - 1].x + line[i - 1].width) for i, box in enumerate(line) if 0 < i]
        # this list might be empty. in that case an arbitrary is returned
        if x_interval == []:
            return self._max_img_size
        q3, q1 = np.percentile(x_interval, [75, 25])
        iqr = q3 - q1
        return floor(q3 + scale * iqr)

    def _get_horizontal_threshold_height_base(self, line: list[Box], scale: float = 0.8) -> int:
        """threshold for each line by which we decide whether to insert a space character between characters in that line.
        this threshold is determined relative to the heigh of rect accommodating the entire line.
        """
        # calculate the height of accommodating rect of the line
        y_max: int = 0
        y_min: int = self._max_img_size
        for box in line:
            y_min = min(y_min, box.y)
            y_max = max(y_max, box.y + box.height)
        return floor(scale * abs(y_max - y_min))

    def _get_horizontal_threshold(self, line: list[Box]) -> int:
        return min(self._get_horizontal_threshold_iqr(line), self._get_horizontal_threshold_height_base(line))

    def _set_sorted_lines(self):
        """set self.lines property.
        self.lines is an empty list until this method is called.
        elements in each line in self.lines corresponds to
        those in the each line in the img.
        """
        assert self.is_response_set()
        # store recognized elements
        boxes: list[Box] = []
        pages = self.response.full_text_annotation.pages
        assert len(pages) > 0
        for page in pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        for symbol in word.symbols:
                            ver = symbol.bounding_box.vertices
                            x: int = ver[0].x
                            y: int = ver[0].y
                            w: int = ver[1].x - x
                            h: int = ver[3].y - y
                            text = symbol.text
                            p: tuple[int, int] = (x, y)
                            rect = Rect((p, w, h))
                            box = Box(text, rect)
                            boxes.append(box)
        # At this point, boxes are not necessarily sorted in a reasonable order.
        # Group boxes by row. the rows are sorted from top to bottom.
        # elements in each grouped row should then be sorted left-to-right.
        boxes.sort(key=lambda box: box.y)
        line: list[Box] = []
        lines: list[list[Box]] = []
        threshold: int = self._get_vertical_threshold(boxes=boxes)
        y_ref: int = -1
        for box in boxes:
            if y_ref == -1:
                y_ref = box.y
            elif abs(y_ref - box.y) <= threshold:
                pass
            else:
                y_ref = -1
                line.sort(key=lambda box: box.x)
                lines.append(line)
                line = []
            line.append(box)
        line.sort(key=lambda box: box.x)
        lines.append(line)
        self._lines = lines

    def _get_lines_with_inserted_space(self) -> list[list[Box]]:
        """insert space between each character in line for all line in lines.
        space is inserted if two adjacent characters c1 and c2 satisfy distance(c1,c2)>threshold
        """
        # insert
        lines: list[list[Box]] = []
        for line in self._lines:
            if line == []:
                continue
            thr: int = self._get_horizontal_threshold(line)
            new_line: list[Box] = []
            box_last: Box = line[0]
            for box in line:
                # compare current box and the last box
                # if they are distanced enough, a space character is inserted
                if box.x - (box_last.x + box_last.width) > thr:
                    # create space box that lies between these two boxes
                    # at the time of writing, width and height of the new rect is not interesting
                    # because they are no longer used for any of the process that follow
                    rect = Rect(((box_last.upper_left + box.upper_left) // 2, thr // 2, box.height))
                    new_line.append(Box(text=" ", rect=rect))
                new_line.append(box)
                box_last = box
            lines.append(new_line)
        return lines

    def _merge_lines(self):
        """merge each line, which is a list, of the sorted lines
        so that i-th element in the self.lines represent i-th row in the img.
        """
        for i, line in enumerate(self.get_lines()):
            text_merged: str = "".join([box.text for box in line])
            # create an bigger accommodating rect
            ul, _, _ = line[0].get_rect_property()
            p, w, h = line[-1].get_rect_property()
            lr = p + np.array([w, h])
            # rect uses only the first and third property of contours.
            con: Contour = np.array([ul, ul, lr, lr]).astype(Point_dtype)
            rect = Rect(con)
            self._lines[i] = [Box(text=text_merged, rect=rect)]

    def get_text(self) -> str:
        if not self.is_response_set():
            print("no response is set. the input file includes blank page?")
            return ""
        if self.get_lines() == []:
            self._set_sorted_lines()
            self._lines = self._get_lines_with_inserted_space()
        if any(len(line) != 1 for line in self.get_lines()):
            self._merge_lines()
        return "\n".join([box.text for box in chain.from_iterable(self.get_lines())])
