from dataclasses import dataclass

import numpy as np
import pytesseract
from imgcat import imgcat
from PIL import Image
from skimage import data, filters, io

from conf import Config


@dataclass
class task:
    save_path = Config.captcha_masks_path

    def gray(self):
        print(self.img_path)
        img = io.imread(self.img_path, as_gray=True)  # 变成灰度图
        thresh = filters.threshold_otsu(img)  # 自动确定二值化的阈值
        bwimg = img <= thresh  # 留下小于阈值的部分，及黑的部分
        print(thresh)
        # img = filters.sobel(img)
        # img = Image.open(self.img_path).convert("L")
        # img = img.point(lambda x: 255 if x > 200 or x == 0 else x)
        # img = img.point(lambda x: 0 if x < 255 else 255, "1")
        self.img = bwimg
        # code = pytesseract.image_to_string(self.img, lang="snum").replace(" ", "")
        imgcat(self.img)
        # print(code)

    def generate_mask(self):
        # arr = np.zeros(self.img.size[::-1], np.float)
        imarr = np.array(self.img, dtype=np.float)
        # arr = arr + imarr
        # arr = np.array(np.round(arr), dtype=np.uint8)
        self.img = Image.fromarray(imarr, mode="L")
        code = pytesseract.image_to_string(self.img, lang="snum").replace(" ", "")
        imgcat(self.img)
        print(code)

    def run(self, path):
        self.img_path = str(path)
        self.gray()
        # self.generate_mask()
        # self.clean()


worker = task()
list(map(worker.run, list(Config.captcha_path.glob("*.png"))[:10]))
