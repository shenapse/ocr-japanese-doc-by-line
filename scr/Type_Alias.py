import pathlib
from typing import TypeAlias

from cv2 import Mat
from nptyping import Int, NDArray, Shape
from PIL import JpegImagePlugin, PngImagePlugin

PIL_png: TypeAlias = PngImagePlugin.PngImageFile
PIL_jpg: TypeAlias = JpegImagePlugin.JpegImageFile
PIL_Img: TypeAlias = PIL_png | PIL_jpg

Path: TypeAlias = pathlib.Path
Paths: TypeAlias = list[Path]
PurePath: TypeAlias = pathlib.PurePath
PurePaths: TypeAlias = list[PurePath]
FileNames: TypeAlias = list[list[str]]

Point: TypeAlias = NDArray[Shape["2"], Int]
Point_Like: TypeAlias = Point | tuple[int, int] | list[int]
Contour: TypeAlias = NDArray[Shape["4,1,2"], Int]
Contours: TypeAlias = NDArray[Shape["*,4,1,2"], Int]
MatMat: TypeAlias = list[list[Mat]]
# Img: TypeAlias = Mat | NDArray[Shape["*,*"], UInt8] | NDArray[Shape["*,*,3"], UInt8]
