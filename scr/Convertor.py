from __future__ import annotations

import abc
import itertools
import pathlib
from datetime import datetime as dt
from fileinput import filename
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

    def read_Mat_img(self, imgs: MatMat) -> None:
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
    __file: Optional[File]
    __imgs: Optional[MatMat]
    __imgs_byte: Optional[list[bytes]]

    def __init__(self) -> None:
        self.__imgs = None

    @property
    def get_file(self) -> File:
        assert self.__file is not None
        return self.__file

    @property
    def get_img(self) -> MatMat:
        assert self.__imgs is not None
        return self.__imgs

    @property
    def get_imgs_byte(self) -> list[bytes]:
        assert self.__imgs_byte is not None
        return self.__imgs_byte

    def read_Mat_img(self, imgs: list[Mat]) -> None:
        # write after frame class is done.
        # also, determine in what form __img_bytes should be stored.
        pass

    def read_file(self, file: File) -> None:
        if not file.is_set():
            raise UnboundLocalError(f"{file.__doc__} has scanned nothing.")
        # prevent overwriting imgs
        assert self.__imgs is None
        if file.is_img_file():
            self.__imgs = [
                [cv2.imread(str(p)) for p in paths] for paths in file.file_sets
            ]
        elif file.is_bound_file():
            self.__imgs = [self.__pdf_paths_to_cv(ps) for ps in file.file_sets]
        else:  # for safety
            raise ValueError(f"{file.__class__}.ext = {file.ext} unexpected.")
        self.__file = file

    def __is_None_or_error(self, obj: Any) -> bool:
        if obj is not None:
            err_msg: str = f"{obj} is not None. Can't overwrite."
            raise ValueError(err_msg)
        return True

    def get_byte_img(self, format=".jpeg", img: Optional[Mat] = None) -> bytes:
        # write after finishing frame class
        img_use = img if img is not None else self.__imgs
        assert img_use is not None
        _, encoded = cv2.imencode(format, img_use)
        return encoded.tobytes()

    def __pil2cv(self, pil_img: PIL_Img):
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

    def save_imgs(
        self,
        save_in_dirs: bool = True,
        suffix: Optional[str] = None,
        fmt_default: str = "jpg",
    ):
        assert (f := self.__file) is not None
        # write better error handling
        assert self.__imgs is not None
        ex_paths: list[Paths] = f.get_expanded_paths()
        assert len(ex_paths) == len(self.__imgs)
        fmt = f.ext if f.ext in f.img_ext else fmt_default

        def gen_suf(suf: Optional[str]) -> str:
            return suf if suf is not None else dt.now().strftime("_%Y%m%d")
            # return suf if suf is not None else dt.now().strftime("_%Y%m%d_%s%f")

        # save img files in dirs
        # returns idx at which
        pair_fail: list[tuple[Path, Mat]] = []
        for d, imgs in enumerate(self.__imgs):
            assert len(ex_paths[d]) == len(self.__imgs[d])
            dir = f.dirs[d] if save_in_dirs else f.root_path
            for i, img in enumerate(imgs):
                file_name: str = f"{ex_paths[d][i].stem}{gen_suf(suffix)}.{fmt}"
                file_path: str = str(dir / file_name)
                if not cv2.imwrite(file_path, img):
                    pair_fail.append((ex_paths[d][i], img))
        return pair_fail

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


if __name__ == "__main__":
    import pprint

    f = File("./")
    f.scan_files(ext="png", recursive=True)
    # print(f.file_sets)
    # pprint.pprint(f.get_expanded_paths())
    c = Convertor()
    c.read_file(f)
    print(c.save_imgs(save_in_dirs=False))
    # f = Convertor().set_path(img_path)
    # f.pdf_to_cv(img_path)
    # print("ok! " + f"{img_path}")
