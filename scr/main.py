from itertools import chain
from sys import argv
from typing import Optional

from google.cloud import vision

from Convertor import Convertor
from File import File
from Frame import Frame
from Type_Alias import Mat, Path


# for preview
def show_files(file_or_dir: Path | str, ext: str = "pdf"):
    get_file_obj(file_or_dir, ext).print()


def get_file_obj(file_or_dir: Path | str, ext: str = "pdf") -> File:
    path = Path(file_or_dir)
    if not path.exists():
        raise ValueError(f"Invalid argument. Not exists: {file_or_dir}")
    f: File = File()
    if path.is_file():
        f.read_file(path)
    else:
        f.read_dir(ext=ext, dir=path)
    return f


def get_framed_imgs(imgs: list[Mat]) -> list[Mat]:
    return [Frame(img).get_framed_img() for img in imgs]


def preview_contours(
    file_or_dir: Path | str, ext: str = "pdf", dir_out: Optional[Path] = None
):
    f: File = get_file_obj(file_or_dir, ext)
    dir_: Path = f.root if dir_out is None else dir_out
    convertor = Convertor()
    convertor.read_file(f)
    imgs_out: list[Mat] = get_framed_imgs(convertor.imgs)
    # save
    convertor.read_Mat_imgs(imgs_out)
    convertor.save_imgs(dir=dir_)


# for ocr
def get_cropped_imgs(imgs: list[Mat]) -> list[Mat]:
    return list(chain.from_iterable([Frame(img).get_cropped_imgs() for img in imgs]))


def ocr_by_cloud_vision_api(
    file_or_dir: Path | str,
    ext: str = "pdf",
    dir_out: Optional[Path] = None,
    language_hints: list[str] = ["ja", "eng"],
) -> None:
    file: File = get_file_obj(file_or_dir, ext)
    # get cropped imgs
    convertor = Convertor()
    convertor.read_file(file)
    imgs_crroped: list[Mat] = get_cropped_imgs(convertor.imgs)
    # turn them into binary form
    convertor.read_Mat_imgs(imgs_crroped)
    imgs_byte = convertor.generate_bytes_imgs()
    # ocr and format texts
    client = vision.ImageAnnotatorClient()
    responses = [
        client.document_text_detection(
            image=vision.Image(content=img),
            image_context={"language_hints": language_hints},
        )
        for img in imgs_byte
    ]
    output_text = ""
    for response in responses:
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        output_text += "".join([symbol.text for symbol in word.symbols])
            output_text += "\n"
    # save text
    dir_: Path = file.root if dir_out is None else dir_out
    txt_path: Path = dir_ / f"{file.paths[0].stem}.txt"
    with open(txt_path, mode="w") as f:
        f.write(output_text)


if __name__ == "__main__":
    dir_out: Path = Path("./out")
    # preview files
    # show_files(path)
    # preview contours
    # list_args: list[str] = argv[1:]
    # for path_str in list_args:
    #     preview_contours(file_or_dir=path_str, dir_out=dir_out)

    # ocr
    file_path: str = argv[1]
    ocr_by_cloud_vision_api(file_or_dir=file_path, ext="pdf", dir_out=dir_out)
