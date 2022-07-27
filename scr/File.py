from __future__ import annotations

import itertools
from pprint import pprint
from typing import Final

from PyPDF2 import PdfFileReader

from Type_Alias import Path, Paths


class File:
    # class var
    __img_ext: Final = ["jpeg", "jpg", "png", "gif"]
    __bound_ext: Final = ["pdf"]
    __supported_ext: Final = __img_ext + __bound_ext
    NOT_SET: Final = "NOT SET"
    # instance var
    # __root: Path
    # __ext: Optional[str] = None
    # __paths:Paths = []

    def __init__(self) -> None:
        self.__root: Path = Path.cwd()
        self.__paths: Paths = []
        self.__ext: str = File.NOT_SET

    @property
    def root(self) -> Path:
        return self.__root

    @property
    def paths(self) -> Paths:
        return self.__paths

    @property
    def supported_ext(self) -> list[str]:
        return File.__supported_ext

    @property
    def img_ext(self) -> list[str]:
        return File.__img_ext

    @property
    def bound_ext(self) -> list[str]:
        return File.__bound_ext

    @property
    def ext(self) -> str:
        if not self.is_set():
            raise ValueError("File.__ext has not been set.")
        return self.__ext

    def read_file(self, path: Path) -> None:
        assert path.is_file()
        assert (ext := self.__get_ext(path)) in self.supported_ext
        self.__ext = ext
        self.__root = path.parent
        self.__paths = [path]

    def read_dir(self, ext: str, dir: Path = Path.cwd()) -> None:
        assert dir.is_dir()
        assert ext in self.supported_ext
        assert self.__is_valid_path(dir)
        self.__ext = ext
        self.__root = dir
        key = ".".join(["*", ext])
        self.__paths = sorted([f for f in list(dir.glob(key)) if f.is_file()])

    def is_empty(self) -> bool:
        return self.paths == []

    def is_set(self) -> bool:
        return self.__ext != File.NOT_SET

    def print(self):
        pprint(f"root:{self.root.resolve()}")
        pprint(f"extension:{self.ext}")
        files = [] if self.is_empty() else self.get_paths_with_pages(True)
        pprint(f"file with n pages:{files}")

    def __get_ext(self, file_path: Path) -> str:
        return file_path.suffix[1:]

    def is_bound_file(self) -> bool:
        return self.ext in self.__bound_ext

    def is_img_file(self) -> bool:
        return self.ext in self.__img_ext

    def __is_valid_path(self, path: Path | Paths, raise_error=True) -> bool:
        # turn into list[path]
        path_list: Paths = path if isinstance(path, list) else [path]
        fault_path: list[str] = [str(p) for p in path_list if p.is_file()]
        if not (all_ok := len(fault_path) == 0) and raise_error:
            fault_path.append("invalid path:")
            fault_path.reverse()
            ValueError("\n".join(fault_path))
        return all_ok

    def get_expanded_paths(self) -> Paths:
        assert not self.is_empty()
        ps: Paths = self.paths
        if self.is_img_file():
            return ps
        elif self.is_bound_file():
            return list(
                itertools.chain.from_iterable(
                    [list(itertools.repeat(p, self.n_pages(p))) for p in ps]
                )
            )
        else:
            raise ValueError(f"{self.__class__}.ext = {self.ext} unexpected.")

    def get_paths_with_pages(self, as_abs=False) -> list[tuple[Path, int]]:
        assert not self.is_empty()
        ps: Paths = self.paths
        return [((p.resolve() if as_abs else p), self.n_pages(p)) for p in ps]

    def n_pages(self, path: Path) -> int:
        return (
            1
            if self.__get_ext(path) in File.__img_ext
            else PdfFileReader(path).getNumPages()
        )


if __name__ == "__main__":

    path = Path("./test/toc3.pdf")
    dir: Path = Path("./test")
    f = File()
    f.read_dir(ext="pdf", dir=dir)
    f.read_file(path)
    f.print()
