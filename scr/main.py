from typing import Optional

from Convertor import Convertor
from File import File
from OCR_by_google import OCR
from Type_Alias import Path, Paths


# for preview
def preview_files(file_or_dir: Path | str, ext: str = "pdf"):
    """preview information of files that will be read by ocr.

    Args:
        file_or_dir: A path of file or directory.

        ext: file extension you intend.
        used only when you provide a directory path.
    """
    get_file_obj(file_or_dir, ext, expand=False)[0].print()


def get_file_obj(
    file_or_dir: Path | str, ext: str = "pdf", expand: bool = True
) -> tuple[File, File]:
    """get file objects that holds the directory structure of intended path.

    Args:
        file_or_dir: A path of file or directory.

        ext: file extension you intend.
        used only when you provide a directory path.

        expand: whether to expand zip or pdf file to individual img files
        in a new directory and return the directory
        as the second of the returned values.

    Return:

        1st: File object of the file_or_dir.

        2nd: Equal to 1st unless expand is true and 1st contains zip or pdf.
        Otherwise equal to a File object of the newly created directory.
    """
    path = Path(file_or_dir)
    if not path.exists():
        raise ValueError(f"Invalid argument. Not exists: {file_or_dir}")
    f: File = File()
    # set appropriate path
    if path.is_file():
        f.read_file(path)
    else:
        f.read_dir(ext=ext, dir=path)
    if not expand:
        return f, f
    # expand compressed file
    else:
        f_read: File = f
        if f.is_compressed_file():
            f_read = f.get_unzip_file()
        elif f.is_pdf_file():
            c = Convertor()
            c.read_file(f)
            f_read = c.save_pdf_pages()
        return f, f_read


def get_text_from_imgs(img_paths: Paths) -> str:
    """concatenate all the read text of images."""
    texts: list[str] = []
    for img_path in img_paths:
        ocr = OCR()
        ocr.read_img(img_path=img_path)
        texts.append(ocr.get_text())
    return "\n".join(texts)


def ocr_by_cloud_vision_api(
    file_or_dir: Path | str,
    ext: str = "zip",
    dir_out: Optional[Path] = None,
    name_out: Optional[str] = None,
) -> None:
    """ocr by google cloud vision api.

    Args:
        file_or_dir: A path of file or directory.

        ext: file extension you intend.
        used only when you provide a directory path.

        dir_out: destination directory of the output text file.
        The default uses that of file_or_path.

        name_out: stem name for the output text file.
        Default uses the file name file name if input is single zip or pdf,
        and the name of the first file (like 005.png -> 005.txt)
        in the directory if image files are provided.
        Note that the latter case could overwrite an output text file.
    """
    f, f_read = get_file_obj(file_or_dir, ext)
    ocr_text: str = get_text_from_imgs(f_read.paths)
    # save text
    text_path, success = save_text(
        text=ocr_text, file=f, dir_out=dir_out, name_out=name_out
    )
    if not success:
        msg = f"Error occurred while trying to save ocr text {text_path}"
        raise Exception(msg)


def save_text(
    text: str,
    file: File,
    dir_out: Optional[Path] = None,
    name_out: Optional[str] = None,
) -> tuple[Path, bool]:
    save_dir: Path = file.root if dir_out is None else dir_out
    stem_name: str = f"{file.paths[0].stem}" if name_out is None else name_out
    text_path: Path = save_dir / f"{stem_name}.txt"
    with open(text_path, mode="w") as tf:
        tf.write(text)
    return text_path, text_path.exists()


if __name__ == "__main__":
    # preview files to read
    file = "./sample/algebra"
    preview_files(file_or_dir=file, ext="png")
    dir_out: Path = Path("./out")
    name_out = Path(file).name
    ocr_by_cloud_vision_api(
        file_or_dir=file, ext="png", dir_out=dir_out, name_out=name_out
    )
