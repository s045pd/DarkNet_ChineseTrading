import warnings
from random import choice

import numpy as np
from matplotlib import pyplot as plt
from skimage import filters, io, measure, morphology

from conf import Config


def skim(name):
    img = io.imread(name, as_gray=True)  # 变成灰度图
    thresh = filters.threshold_otsu(img)  # 自动确定二值化的阈值
    bwimg = img <= thresh  # 留下小于阈值的部分，及黑的部分
    b = morphology.remove_small_objects(
        bwimg, 40
    )  # 去掉小于40的连通域，可以先全局看看连通域的大小和位置后决定去掉的阈值
    labels = measure.label(b)
    label_att = measure.regionprops(labels)
    arr = []
    for la in label_att:
        (x, y, w, h) = la.bbox
        # print((x,y,w,h))
        bei = round((h - y) / 15)
        if bei > 1:  # 宽度超过30像素的，说明有粘连，从中切开
            for i in range(bei):
                arr.append(
                    (x, y + round((h - y) / 2) * i, w, y + round((h - y) / 2) * (i + 1))
                )
        elif (y > 10) and (h < 100):
            arr.append((x, y, w, h))

    b = b * img
    b[np.where(b != 0)] = 1
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig = plt.figure()
        for id, (x, y, w, h) in enumerate(arr):
            roi = b[x:w, y:h]
            thr = roi.copy()
            # io.imsave('seg1-{}.jpg',thr)
            ax = fig.add_subplot(1, 4, id + 1)
            ax.imshow(thr)
    plt.show()


def ty(name):
    # for i in range(1,10):
    img = io.imread(name)
    img[np.where(img > 235)] = 255
    img[np.where(img < 15)] = 255
    imgray = color.rgb2gray(img)
    thresh = filters.threshold_otsu(imgray)
    # bwimg =(imgray <= thresh)
    bwimg = morphology.closing(imgray <= thresh, morphology.square(3))
    b = morphology.remove_small_objects(bwimg, 20)
    labels = measure.label(b)
    label_att = measure.regionprops(labels)
    arr = []

    for la in label_att:
        (x, y, w, h) = la.bbox
        bei = round((h - y) / 15)
        if bei > 1:
            for i in range(bei):
                arr.append(
                    (x, y + round((h - y) / 2) * i, w, y + round((h - y) / 2) * (i + 1))
                )
        elif (y > 10) and (h < 100):
            arr.append((x, y, w, h))
            if (
                (len(arr) > 1) and (h - y) < 12 and (arr[-2][3] - arr[-2][1] < 12)
            ):  # 干扰线去狠了导致断开验证码断开了要拼接一下
                arr[-1] = (x, arr[-2][1], w, h)
                del arr[-2]

    b = b * imgray
    b[np.where(b != 0)] = 1
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig = plt.figure()
        for id, (x, y, w, h) in enumerate(arr):
            roi = b[x:w, y:h]
            thr = roi.copy()
            # io.imsave('new{}-{}.png'.format(1,id+1), thr)
            ax = fig.add_subplot(1, len(arr), id + 1)
            ax.imshow(thr)
        plt.show()


target = choice(list(Config.captcha_path.glob("*.png")))

ty(str(target))
