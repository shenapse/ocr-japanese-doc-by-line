from __future__ import annotations

import abc
import itertools
from typing import Any, Optional

import cv2
import numpy as np
from pdf2image import convert_from_path

from File import File
from Type_Alias import Mat, MatMat, Path, Paths, PIL_Img


class IConvertor(metaclass=abc.ABCMeta):
    """Interface for File class"""

    @abc.abstractclassmethod
    def read_file(self, file: File) -> None:
        raise NotImplementedError()

    def read_Mat_imgs(self, imgs: MatMat) -> None:
        raise NotImplementedError()

    def save_imgs(self) -> None:
        raise NotImplementedError()

    def get_file(self) -> File:
        raise NotImplementedError()

    def get_img(self) -> MatMat:
        raise NotImplementedError()

    def get_imgs_byte(self) -> list[bytes]:
        raise NotImplementedError()


class Convertor(IConvertor):
    def __init__(self) -> None:
        self.__file: Optional[File] = None
        self.__imgs: list[Mat] = []
        self.__imgs_byte: list[bytes] = []

    @property
    def get_file(self) -> File:
        assert self.__file is not None
        return self.__file

    @property
    def get_img(self) -> list[Mat]:
        assert self.__imgs != []
        return self.__imgs

    @property
    def get_imgs_byte(self) -> list[bytes]:
        assert self.__imgs_byte != []
        return self.__imgs_byte

    def read_Mat_imgs(self, imgs: list[Mat]) -> None:
        # write after frame class is done.
        # also, determine in what form __img_bytes should be stored.
        self.__imgs = imgs
        pass

    def read_file(self, file: File, which_sets: int = 0) -> None:
        assert file is not None
        sets: Paths = file.file_sets()[which_sets]
        if file.is_img_file():
            self.__imgs = [cv2.imread(str(p)) for p in sets]
        else:
            self.__imgs = self.__pdf_paths_to_cv(sets)
        self.__file = file

    def __is_None_or_error(self, obj: Any) -> bool:
        if obj is not None:
            err_msg: str = f"{obj} is not None. Can't overwrite."
            raise ValueError(err_msg)
        return True

    # def get_byte_img(self, format=".jpeg", img: Optional[Mat] = None) -> bytes:
    #     # write after finishing frame class
    #     img_use = img if img is not None else self.__imgs
    #     assert img_use is not None
    #     _, encoded = cv2.imencode(format, img_use)
    #     return encoded.tobytes()

    def __pil2cv(self, pil_img: PIL_Img) -> Mat:
        """PIL -> OpenCV"""
        image_array: Mat = np.array(pil_img, dtype=np.uint8)
        if image_array.ndim == 2:  # gray
            pass
        elif image_array.shape[2] == 3:  # colored
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        elif image_array.shape[2] == 4:  # transparent
            raise TypeError("Image is with Transparent background")
        return image_array

    def __pdf_paths_to_cv(self, paths: Paths, fmt="jpg", dpi=200) -> list[Mat]:
        # turn a list of lists into a list
        images: list[PIL_Img] = list(
            itertools.chain.from_iterable(
                [convert_from_path(p, fmt=fmt, dpi=dpi) for p in paths]
            )
        )
        return [self.__pil2cv(img) for img in images]

    def save_img(self, img: Mat, name: str, dir: Path) -> bool:
        d: Path = dir if dir.is_dir() else dir.parent
        file_path: Path = d / name
        return cv2.imwrite(str(file_path), img)

    def save_imgs(
        self, suffix: str = "_preview", fmt_default: str = "jpg", which_set: int = 0
    ):
        assert (f := self.__file) is not None
        # write better error handling
        assert self.__imgs != []
        ex_paths: list[tuple[Path, int]] = f.get_paths_with_pages()[which_set]
        sum_pages: int = sum([item[1] for item in ex_paths])
        assert len(self.__imgs) == sum_pages
        fmt = f.ext if f.ext in f.img_ext else fmt_default
        suffix = suffix if suffix != "" else "_preview"
        dir: Path = f.dirs()[which_set]

        suf_list: list[str] = list(
            itertools.chain.from_iterable(
                [
                    ["{}_{:0>2}".format(suffix, i) for i in range(0, m)]
                    for _, m in ex_paths
                ]
            )
        )
        names: list[Path] = f.get_expanded_paths()[which_set]
        # save img files in dirs
        # returns idx at which save failed
        pair_fail: list[tuple[Path, Mat]] = []
        for d, img in enumerate(self.__imgs):
            name: str = f"{names[d].stem}{suf_list[d]}.{fmt}"
            file_path: str = str(dir / name)
            if not cv2.imwrite(file_path, img):
                pair_fail.append((ex_paths[d][0], img))
        return pair_fail

    def print(self):
        print(f"number of imgs: {len(self.__imgs)}")
        if (f := self.__file) is not None:
            f.print()
        else:
            print("No file is set in Convertor instance.")

    # def display_img(self) -> None:
    #     """Open a np.array image in a normal window.
    #     This method is specifically for opening an image.
    #     It should be closed manually, for instance by close_all_img().
    #     """
    #     cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    #     cv2.imshow("image", self.img)
    #     cv2.waitKey(1)

    # def close_all_img(self) -> None:
    #     """Immediately close all displayed images"""
    #     cv2.destroyAllWindows()
    #     cv2.waitKey(1)
