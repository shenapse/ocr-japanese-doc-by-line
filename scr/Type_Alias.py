import pathlib
from typing import TypeAlias

from cv2 import Mat
from nptyping import Int, NDArray, Shape
from numpy import int32, uint8
from PIL import JpegImagePlugin, PngImagePlugin

PIL_png: TypeAlias = PngImagePlugin.PngImageFile
PIL_jpg: TypeAlias = JpegImagePlugin.JpegImageFile
PIL_Img: TypeAlias = PIL_png | PIL_jpg

Path: TypeAlias = pathlib.Path
Paths: TypeAlias = list[Path]

# geometry
__Point_dtype: TypeAlias = Int
Point: TypeAlias = NDArray[Shape["2"], __Point_dtype]
Point_Like: TypeAlias = Point | tuple[int, int] | list[int]
Contour: TypeAlias = NDArray[Shape["4,1,2"], __Point_dtype]
Contours: TypeAlias = NDArray[Shape["*,4,1,2"], __Point_dtype]
Rect_Like_: TypeAlias = tuple[Point_Like, int, int]
Point_dtype: TypeAlias = int32

# pixel
MatMat: TypeAlias = list[list[Mat]]
Pixel_dtype: TypeAlias = uint8
