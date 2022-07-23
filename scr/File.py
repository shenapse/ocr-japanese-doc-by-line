import itertools
from typing import Optional

from cv2 import projectPoints
from PyPDF2 import PdfFileReader

from Type_Alias import Path, Paths


class File:
    __img_ext: list[str] = ["jpeg", "jpg", "png", "gif"]
    __bound_ext: list[str] = ["pdf"]
    __supported_ext: list[str]
    __root_path: Path
    __dirs: Paths
    __ext: Optional[str] = None
    __file_sets: list[Paths]

    def __init__(self, path: Optional[str | Path] = None) -> None:
        self.__root_path = Path(Path.cwd()) if path is None else Path(path)
        self.__dirs = [self.__root_path]
        # fill the list of supported ext
        self.__supported_ext = self.__img_ext + self.__bound_ext
        pass

    @property
    def root_path(self) -> Path:
        return self.__root_path.resolve()

    @property
    def dirs(self) -> Paths:
        return self.__dirs

    @property
    def supported_ext(self) -> list[str]:
        return self.__supported_ext

    @property
    def img_ext(self) -> list[str]:
        return self.__img_ext

    @property
    def bound_ext(self) -> list[str]:
        return self.__bound_ext

    @property
    def file_sets(self) -> list[Paths]:
        return self.__file_sets

    @property
    def ext(self) -> str:
        if self.__ext is None:
            raise ValueError("File.__ext has not been set.")
        return self.__ext

    def scan_files(
        self, ext: str, root: Optional[Path] = None, recursive=False
    ) -> None:
        assert ext in self.__supported_ext
        self.__ext = ext
        root_: Path = self.__root_path if root is None else root
        assert self.__is_valid_path(root_)
        dirs: Paths = self.__scan_dirs(root_) if recursive else self.__dirs
        self.__file_sets = [
            f for dir in dirs if (f := self.__list_files(ext, dir)) != []
        ]
        # reconstruct self.__dirs as it might have no files with the asked ext.
        # Skip such uninteresting folders
        self.__dirs = [f[0].parent for f in self.file_sets]

    def is_empty(self) -> bool:
        return self.file_sets == []

    def is_set(self) -> bool:
        return self.__ext is not None

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
        if self.is_img_file():
            return self.file_sets
        elif self.is_bound_file():
            return [
                list(
                    itertools.chain.from_iterable(
                        [
                            [p for _ in range(0, PdfFileReader(p).getNumPages())]
                            for p in ps
                        ]
                    )
                )
                for ps in self.__file_sets
            ]
        else:
            raise ValueError(f"{self.__class__}.ext = {f.ext} unexpected.")


if __name__ == "__main__":
    from pprint import pprint

    path = "./"
    f = File(path)
    f.scan_files(ext="pdf", recursive=True)
    print(f.file_sets)
    print(f.dirs)
    print(f.get_expanded_paths())
