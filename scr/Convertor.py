from __future__ import annotations

import abc
from typing import Optional

import cv2
import numpy as np
from pdf2image import convert_from_path

from File import File
from Type_Alias import Mat, Path, PIL_Img, PIL_Imgs, Save_Result

# from itertools import chain
# import img2pdf


class IConvertor(metaclass=abc.ABCMeta):
    """Interface for File class"""

    @abc.abstractclassmethod
    def read_file(self, file: File) -> None:
        raise NotImplementedError()

    def file(self) -> File:
        raise NotImplementedError()

    def imgs(self) -> list[Mat]:
        raise NotImplementedError()

    def imgs_byte(self) -> list[bytes]:
        raise NotImplementedError()


class Convertor(IConvertor):
    def __init__(self) -> None:
        self.__file: Optional[File] = None
        self.__imgs: list[Mat] = []

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
        return self.generate_bytes_imgs()

    def read_file(self, file: File) -> None:
        assert file is not None
        if file.is_img_file():
            self.__imgs = [cv2.imread(str(p)) for p in file.paths]
        elif file.is_pdf_file():
            self.__imgs = self.__pdf_paths_to_cv(file.paths[0])
        else:
            raise Exception("Invalid file. It must be img or pdf.")
        self.__file = file

    def generate_bytes_imgs(self, fmt: str = ".png") -> list[bytes]:
        return [cv2.imencode(fmt, img)[1].tobytes() for img in self.imgs]

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

    def __pdf_paths_to_cv(self, path: Path, fmt="png", dpi=150) -> list[Mat]:
        # turn a list of lists into a list
        images: PIL_Imgs = self.__pdf_path_to_pil(path, fmt, dpi)
        return [self.__pil2cv(img) for img in images]

    def __pdf_path_to_pil(self, path: Path, fmt="png", dpi=150) -> PIL_Imgs:
        return convert_from_path(path, fmt=fmt, dpi=dpi, grayscale=True)

    # def save_imgs(
    #     self,
    #     dir: Optional[Path] = None,
    #     suffix: str = "_preview",
    #     fmt_default: str = "png",
    # ) -> list[Save_Result]:
    #     assert (f := self.file) is not None
    #     assert self.imgs != []
    #     dir_: Path = f.root if dir is None else dir
    #     if self.file.is_pdf_file():
    #         return [self.__save_pdf(suffix=suffix, dir=dir_)]
    #     ex_paths: list[tuple[Path, int]] = f.get_paths_with_pages()
    #     sum_pages: int = f.get_total_pages()
    #     assert len(self.imgs) == sum_pages
    #     fmt = f.ext if f.ext in f.img_ext else fmt_default
    #     suffix = suffix if suffix != "" else "_preview"

    #     suf_list: list[str] = (
    #         [""]
    #         if sum_pages == 1
    #         else list(
    #             chain.from_iterable(
    #                 [
    #                     ["{}_{:0>2}".format(suffix, i) for i in range(0, m)]
    #                     for _, m in ex_paths
    #                 ]
    #             )
    #         )
    #     )
    #     names: list[Path] = f.get_expanded_paths()
    #     # save img files in dir
    #     res: list[tuple[Path, bool]] = []
    #     for d, img in enumerate(self.__imgs):
    #         name: str = f"{names[d].stem}{suf_list[d]}.{fmt}"
    #         file_path: Path = dir_ / name
    #         if not (ok := cv2.imwrite(str(file_path), img)):
    #             print(f"save failed: {str(file_path)}")
    #         res.append((file_path, ok))
    #     return res

    # def __save_pdf(self, dir: Path, suffix: str = "_preview") -> Save_Result:
    #     file_name: str = f"{self.file.paths[0].stem}{suffix}.pdf"
    #     out_path: Path = dir / file_name
    #     with open(out_path, "wb") as f:
    #         f.write(img2pdf.convert(self.imgs_byte))
    #     return (out_path, out_path.exists())

    def get_vconcate_img(self) -> Mat:
        """vertically paste imgs."""
        w_min = min(img.shape[1] for img in self.imgs)
        imgs_resized = [img[:, :w_min] for img in self.imgs]
        return np.vstack(imgs_resized)

    def save_vconcate_img(
        self, suffix: str = "_vconc", fmt: str = "png"
    ) -> Save_Result:
        dir: Path = self.file.root
        file_path: Path = dir / f"{self.file.paths[0].stem}{suffix}.{fmt}"
        success: bool = cv2.imwrite(str(file_path), self.get_vconcate_img())
        return file_path, success

    def save_pdf_pages(self, dpi=200, fmt="png") -> File:
        """save each pdf page in a new temporary directory."""
        if not self.file.is_pdf_file():
            raise Exception("File is not pdf.")
        dir: Path = self.file.root / "temp_pdf_pages"
        if not dir.exists():
            dir.mkdir()
        pdf_path: Path = self.file.paths[0]
        pages: PIL_Imgs = self.__pdf_path_to_pil(pdf_path, fmt=fmt, dpi=dpi)
        for i, page in enumerate(pages):
            file_name: str = f"{pdf_path.stem}_{i}.{fmt}"
            page.save(str(dir / file_name), "PNG")
        f = File()
        f.read_dir(ext=fmt, dir=dir)
        f.set_as_temp()
        return f
