from __future__ import annotations

import itertools
from typing import Final, Optional

from PyPDF2 import PdfFileReader

from Type_Alias import Path, Paths


class File:
    # class var
    __img_ext: Final = ["jpeg", "jpg", "png", "gif"]
    __bound_ext: Final = ["pdf"]
    __supported_ext: Final = __img_ext + __bound_ext
    # instance var
    # __root_path: Path
    # __dirs: Paths
    # __ext: Optional[str] = None
    # __file_sets: list[Paths]

    def __init__(
        self,
        root: str | Path = Path.cwd(),
        dirs: Paths = [],
        file_sets: list[Paths] = [],
        ext: Optional[str] = None,
    ) -> None:
        self.__root_path: Path = Path(root)
        self.__dirs: Paths = dirs
        self.__ext: Optional[str] = None
        self.__file_sets: list[Paths] = file_sets
        self.__ext: Optional[str] = ext
        pass

    def root_path(self, as_abs: bool = False) -> Path:
        return self.__root_path.resolve() if as_abs else self.__root_path

    def dirs(self, as_abs=False) -> Paths:
        return [p.resolve() for p in self.__dirs] if as_abs else self.__dirs

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
        if self.__ext is None:
            raise ValueError("File.__ext has not been set.")
        return self.__ext

    def file_sets(self, as_abs: bool = False) -> list[Paths]:
        return (
            [[p.resolve() for p in paths] for paths in self.__file_sets]
            if as_abs
            else self.__file_sets
        )

    def read_file(self, path: Path) -> None:
        assert path.is_file()
        assert (ext := self.__get_ext(path)) in self.supported_ext
        self.__ext = ext
        self.__root_path = path.parent
        self.__dirs = [self.root_path()]
        self.__file_sets = [[path]]

    def read_dir(self, ext: str, root: Path = Path.cwd(), recursive=False) -> None:
        assert ext in self.supported_ext
        self.__ext = ext
        assert self.__is_valid_path(root)
        self.__root_path = root
        dirs: Paths = self.__scan_dirs(root) if recursive else [root]
        self.__file_sets = [
            f for dir in dirs if (f := self.__list_files(ext, dir)) != []
        ]
        # construct self.__dirs as it might have no files with the asked ext.
        # Skip such uninteresting folders
        if self.__file_sets is not None:
            self.__dirs = [f[0].parent for f in self.__file_sets]
        else:
            raise Exception(f"{self.__class__}.file_sets is not set.")

    def is_empty(self) -> bool:
        return self.file_sets == []

    def is_set(self) -> bool:
        return self.__ext is not None

    def print(self):
        print(f"root:\n{self.root_path(as_abs=True)}\n")
        print(f"extension:\n{self.ext}\n")
        print(f"directory:\n{self.dirs(as_abs=True)}\n")
        print(f"file with n pages:\n{self.get_paths_with_pages(as_abs=True)}")

    def __get_ext(self, file_path: Path) -> str:
        return file_path.suffix[1:]

    def __scan_dirs(self, dir: Path) -> Paths:
        assert self.__is_valid_path(dir)
        return list(dir.glob("**"))

    def __list_files(self, ext: str, dir: Path) -> Paths:
        assert self.__is_valid_path(dir)
        key = ".".join(["*", ext])
        return sorted([f for f in list(dir.glob(key)) if f.is_file()])

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

    def get_expanded_paths(self) -> list[Paths]:
        assert self.__file_sets is not None
        if self.is_img_file():
            return self.__file_sets
        elif self.is_bound_file():
            return [
                list(
                    itertools.chain.from_iterable(
                        [[p for _ in range(0, self.n_pages(p))] for p in ps]
                    )
                )
                for ps in self.__file_sets
            ]
        else:
            raise ValueError(f"{self.__class__}.ext = {self.ext} unexpected.")

    def get_paths_with_pages(self, as_abs=False) -> list[list[tuple[Path, int]]]:
        assert (f := self.__file_sets) is not None
        return [
            [((p.resolve() if as_abs else p), self.n_pages(p)) for p in ps] for ps in f
        ]

    def n_pages(self, path: Path) -> int:
        return (
            1
            if self.__get_ext(path) in File.__img_ext
            else PdfFileReader(path).getNumPages()
        )

    def get_nth(self, n: int) -> File:
        return File(
            root=self.root_path(),
            dirs=[self.dirs()[n]],
            file_sets=[self.file_sets()[n]],
            ext=self.ext,
        )


if __name__ == "__main__":

    path = "./"
    f = File(path)
    f.read_dir(ext="pdf", recursive=True)
    f.print()
    # print(f.get_expanded_paths())
