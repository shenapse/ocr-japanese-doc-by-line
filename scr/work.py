import cv2
import matplotlib
import numpy as np
from sklearn.cluster import KMeans

img_path = "003.png"


def refresh_img(img_path):
    return cv2.imread(img_path)


def refresh_img(img_path=img_path):
    return cv2.imread(img_path)


def get_gray_img(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def get_size(img):
    return img.shape[:2]


def to_odd(x: int):
    return x if x % 2 == 1 else x - 1


def display_img(mat):
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)  # 可変ウインドウ「image」を開く
    cv2.imshow("image", mat)  # imageウインドウの中に受け取った画像を展開する
    cv2.waitKey(1)


def close_all_img():
    cv2.destroyAllWindows()
    cv2.waitKey(1)


def get_bw_image(img, gauss_x: int, gauss_y: int, thr: int = 250):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(gray_img, (to_odd(gauss_x), to_odd(gauss_y)), 0)
    _, img_thr = cv2.threshold(img_blur, thr, 255, cv2.THRESH_BINARY)
    return cv2.bitwise_not(img_thr)


def get_effective_zone(img, offset_percent=1, thr=250):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = gray_img.shape[:2]
    img_reversed = get_bw_image(
        img=img,
        gauss_x=to_odd(max(offset_percent * width // 100, 1)),
        gauss_y=to_odd(max(offset_percent * height // 100, 1)),
        thr=thr,
    )
    contours, _ = cv2.findContours(
        img_reversed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    # get the right and left end
    left_end: int = width
    right_end: int = 0
    upper_end: int = height
    lower_end: int = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        left_end = min(left_end, x)
        right_end = max(right_end, x + w)
        upper_end = min(upper_end, y)
        lower_end = max(lower_end, y + h)
    return left_end, right_end, upper_end, lower_end
