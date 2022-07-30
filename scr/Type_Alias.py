import pathlib
from typing import TypeAlias

from cv2 import Mat
from nptyping import Int, NDArray, Shape
from numpy import int32, uint8
from PIL import JpegImagePlugin, PngImagePlugin

PIL_png: TypeAlias = PngImagePlugin.PngImageFile
PIL_jpg: TypeAlias = JpegImagePlugin.JpegImageFile
PIL_Img: TypeAlias = PIL_png | PIL_jpg
PIL_Imgs: TypeAlias = list[PIL_Img]

Path: TypeAlias = pathlib.Path
Paths: TypeAlias = list[Path]
Save_Result: TypeAlias = tuple[Path, bool]

# geometry
__Point_dtype: TypeAlias = Int
Point: TypeAlias = NDArray[Shape["2"], __Point_dtype]
Point_Like: TypeAlias = Point | tuple[int, int] | list[int]
Contour: TypeAlias = NDArray[Shape["4,1,2"], __Point_dtype]
Contours: TypeAlias = NDArray[Shape["*,4,1,2"], __Point_dtype]
Rect_Like_: TypeAlias = tuple[Point_Like, int, int]
Point_dtype: TypeAlias = int32

# pixel
Mats = list[Mat]
Pixel_dtype: TypeAlias = uint8
