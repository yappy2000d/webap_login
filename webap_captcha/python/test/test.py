import numpy as np
from PIL import Image

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import utils

image = utils.get_captcha_image()
# image = np.array(Image.open('result/captcha.bmp'))

Image.fromarray(image).save('result/captcha.bmp')

image_bin = utils.binarize_image(image, utils.ostu_threshold(image))

Image.fromarray(image_bin).save('result/captcha_bin.bmp')

labels_im, num_labels = utils.label(255 - image_bin)
print(f"Number of connected components: {num_labels}")

for label in range(1, num_labels + 1):
    component = np.zeros_like(labels_im, dtype=np.uint8)
    component[labels_im == label] = 255

    # 用矩形框出连通域
    ys, xs = np.where(labels_im == label)
    if len(xs) == 0 or len(ys) == 0:
        continue
    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()

    if x_max - x_min < 5 or y_max - y_min < 5:
        continue  # 忽略过小的连通域
    print(f"Component {label}: x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")
    Image.fromarray(component).save(f'result/component_{label}.bmp')
    # Image.fromarray(rect_image).save(f'result/component_{label}_rect.bmp')

