from __future__ import annotations

import abc
import itertools
from typing import Optional

import cv2
import img2pdf  # type: ignore
import numpy as np
from pdf2image import convert_from_path

from File import File
from Type_Alias import Mat, Path, Paths, PIL_Img


class IConvertor(metaclass=abc.ABCMeta):
    """Interface for File class"""

    @abc.abstractclassmethod
    def read_file(self, file: File) -> None:
        raise NotImplementedError()

    def read_Mat_imgs(self, imgs: list[Mat]) -> None:
        raise NotImplementedError()

    def save_imgs(self) -> None:
        raise NotImplementedError()

    def file(self) -> File:
        raise NotImplementedError()

    def imgs(self) -> list[Mat]:
        raise NotImplementedError()

    def imgs_byte(self) -> list[bytes]:
        raise NotImplementedError()

    def print(self) -> None:
        raise NotImplementedError()


class Convertor(IConvertor):
    def __init__(self) -> None:
        self.__file: Optional[File] = None
        self.__imgs: list[Mat] = []
        self.__imgs_byte: list[bytes] = []

    @property
    def file(self) -> File:
        assert self.__file is not None
        return self.__file

    @property
    def imgs(self) -> list[Mat]:
        assert self.__imgs != []
        return self.__imgs

    @property
    def imgs_byte(self) -> list[bytes]:
        if self.__imgs_byte == []:
            self.__imgs_byte = self.generate_bytes_imgs()
        return self.__imgs_byte

    def read_Mat_imgs(self, imgs: list[Mat]) -> None:
        # write after frame class is done.
        # also, determine in what form __img_bytes should be stored.
        self.__imgs = imgs
        pass

    def read_file(self, file: File) -> None:
        assert file is not None
        sets: Paths = file.paths
        if file.is_img_file():
            self.__imgs = [cv2.imread(str(p)) for p in sets]
        else:
            self.__imgs = self.__pdf_paths_to_cv(sets)
        self.__file = file

    def generate_bytes_imgs(self, format: str = ".jpeg") -> list[bytes]:
        assert (imgs := self.__imgs) != []
        self.__imgs_byte = [cv2.imencode(format, i)[1].tobytes() for i in imgs]
        return self.imgs_byte

    def __pil2cv(self, pil_img: PIL_Img) -> Mat:
        """PIL -> OpenCV"""
        image_array: Mat = np.array(pil_img, dtype=np.uint8)
        if image_array.ndim == 2:  # gray
            pass
        elif image_array.shape[2] == 3:  # colored
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        elif image_array.shape[2] == 4:  # transparent
            raise TypeError("Image is with Transparent part.")
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
        dir: Optional[Path] = None,
        suffix: str = "_preview",
        fmt_default: str = "jpeg",
    ):
        assert (f := self.file) is not None
        assert self.imgs != []
        dir_: Path = f.root if dir is None else dir
        if self.file.is_bound_file():
            self.__save_pdf(suffix=suffix, dir=dir_)
            return
        ex_paths: list[tuple[Path, int]] = f.get_paths_with_pages()
        sum_pages: int = sum([item[1] for item in ex_paths])
        assert len(self.imgs) == sum_pages
        fmt = f.ext if f.ext in f.img_ext else fmt_default
        suffix = suffix if suffix != "" else "_preview"

        suf_list: list[str] = list(
            itertools.chain.from_iterable(
                [
                    ["{}_{:0>2}".format(suffix, i) for i in range(0, m)]
                    for _, m in ex_paths
                ]
            )
        )
        names: list[Path] = f.get_expanded_paths()
        # save img files in dir
        for d, img in enumerate(self.__imgs):
            name: str = f"{names[d].stem}{suf_list[d]}.{fmt}"
            file_path: str = str(dir_ / name)
            if not cv2.imwrite(file_path, img):
                print(f"save failed: {file_path}")

    def __save_pdf(self, dir: Path, suffix: str = "_preview"):
        file_name: str = f"{self.file.paths[0].stem}{suffix}.pdf"
        out_path: Path = dir / file_name
        with open(out_path, "wb") as f:
            f.write(img2pdf.convert(self.imgs_byte))

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
