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
        self.__empty_response: Final = Response()
        self.__max_img_size: Final = 20 * 10**6
        # dummy response to mean there is no valid response
        self.__response: Response = self.__empty_response
        self.__lines: list[list[Box]] = []

    @property
    def response(self) -> Response:
        return self.__response

    def get_lines(self) -> list[list[Box]]:
        return self.__lines

    def is_response_set(self) -> TypeGuard[Response]:
        return self.response != self.__empty_response

    def read_img(self, img_path: Path) -> None:
        """set response property by reading image file."""
        if not self.check_size(img_path):
            msg: str = f"Invalid img size. Got {getsize(str(img_path))/(10**6)} MB. It must be under {self.__max_img_size//(10**6)} MB."
            raise ValueError(msg)
        client = vision.ImageAnnotatorClient()
        self.__response = client.document_text_detection(  # type: ignore
            image=vision.Image(content=self.get_byte_img(img_path)),
            image_context={"language_hints": ["ja", "eng"]},
        )
        # clear old lines
        self.__lines = []

    def get_byte_img(self, img_path: Path) -> bytes:
        with open(str(img_path), mode="rb") as img:
            return img.read()

    def check_size(self, img_path: Path) -> bool:
        return 0 < getsize(str(img_path)) < self.__max_img_size

    def read_response(self, res: Response) -> None:
        """directly set response propetry without reading image file."""
        self.__response = res
        # clear old lines
        self.__lines = []

    def __get_threshold(self, boxes: list[Box]) -> int:
        """used for classifying bounding boxes"""
        assert boxes != []
        h_array = np.array([b.height for b in boxes])
        return floor(np.median(h_array)) // 2

    def __set_sorted_lines(self):
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
        # At this point, boxes are not sorted in a reasonable order.
        # Group boxes by row. the rows are sorted from top to bottom.
        # elements in each grouped row should be sorted left-to-right.
        boxes.sort(key=lambda box: box.y)
        line: list[Box] = []
        lines: list[list[Box]] = []
        threshold: int = self.__get_threshold(boxes=boxes)
        y_ref: int = -1
        for box in boxes:
            if y_ref == -1:
                y_ref = box.y
            elif y_ref - threshold <= box.y <= y_ref + threshold:
                y_ref = box.y
            else:
                y_ref = -1
                line.sort(key=lambda box: box.x)
                lines.append(line)
                line = []
            line.append(box)
        line.sort(key=lambda box: box.x)
        lines.append(line)
        self.__lines = lines

    def __merge_lines(self):
        """merge each line, which is a list, of the sorted lines
        so that i-th element in the self.lines represent i-th row in the img.
        """
        for i, line in enumerate(self.get_lines()):
            text_merged: str = "".join([box.text for box in line])
            # create an bigger accommodating rect
            ul, _, _ = line[0].get_rect_property()
            p, w, h = line[-1].get_rect_property()
            lr = p + np.array([w, h])
            # rect uses only the first and third porperty of contours.
            con: Contour = np.array([ul, ul, lr, lr]).astype(Point_dtype)
            rect = Rect(con)
            self.__lines[i] = [Box(text=text_merged, rect=rect)]

    def get_text(self) -> str:
        if self.get_lines() == []:
            self.__set_sorted_lines()
        if any(len(line) != 1 for line in self.get_lines()):
            self.__merge_lines()
        lines: list[Box] = list(chain.from_iterable(self.get_lines()))
        return "\n".join([box.text for box in lines])


# sample
if __name__ == "__main__":
    img_file: Path = Path("./image_file_to_ocr.png")
    ocr = OCR()
    ocr.read_img(img_file)
    print(ocr.get_text())
