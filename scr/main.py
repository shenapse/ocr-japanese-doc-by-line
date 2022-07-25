from traceback import print_tb

from Convertor import Convertor
from File import File
from Frame import Frame
from Type_Alias import Mat, Path


def show_files(dir: str | Path, ext: str = "pdf", recursive=False):
    dir_path = Path(dir)
    if not dir_path.is_dir():
        raise ValueError(f"Invalid argument. Not a directory: {dir}")
    f = File(dir_path)
    f.read_dir(ext=ext, root=dir_path, recursive=recursive)
    f.print()


def show_file(file: Path | str):
    path = Path(file)
    if not path.is_file():
        raise ValueError(f"Invalid argument. Not a directory: {file}")
    f = File(path)
    f.read_file(path=path)
    f.print()


def get_processed_imgs(imgs: list[Mat]) -> list[Mat]:
    return [Frame(img).get_processed_img() for img in imgs]


def preview_contours(file_or_dir: Path | str, ext: str = "pdf", recursive=False):
    path = Path(file_or_dir)
    if not path.exists():
        raise ValueError(f"Invalid argument. Not exists: {file_or_dir}")
    f: File = File()
    if path.is_file():
        f.read_file(path)
    else:
        f.read_dir(ext=ext, root=path, recursive=recursive)
    for i in range(0, len(f.dirs())):
        fn: File = f.get_nth(i)
        # for file in fn.file_sets()[0]:
        reader = Convertor()
        reader.read_file(fn)
        imgs_out: list[Mat] = get_processed_imgs(reader.get_img)
        # save
        reader.read_Mat_imgs(imgs_out)
        reader.save_imgs()


if __name__ == "__main__":
    file: str = "./test/005.png"
    dir_cur: Path = Path("./")
    # show_files(dir=dir_cur, recursive=True)
    preview_contours(file)
    # preview_contours(dir_cur)
