"""
透過 TFLite 產生的資料來生成驗證碼圖片
"""

import numpy as np
from PIL import Image
from glob import glob
import os

from uuid import uuid4
import segment
import utils

for path in glob("test/tflite/success/*.bmp"):
    answer = path.rsplit("/")[-1].split(".")[0]
    image = Image.open(path)
    img = np.array(image)

    img_bin = utils.binarize_image(img, 132)

    labels_im, num_labels = segment.label(img_bin, background=255)

    result = segment.segment_characters(labels_im, num_labels)

    if len(result) != 4:
        image.save(f'test/segment/failed/{answer}.bmp')
        continue

    for i, img in enumerate(result):
        # check if folder exists
        if not os.path.exists(f"assets/{answer[i]}"):
            os.makedirs(f"assets/{answer[i]}")
        Image.fromarray(img.astype(np.uint8)).save(f"assets/{answer[i]}/{uuid4()}.bmp")

for char in os.listdir("assets"):
    images = glob(f"assets/{char}/*.bmp")

    avg = np.zeros((22, 22), dtype=np.uint8)

    for path in images:
        img = np.array(Image.open(path))

        
        canva = np.zeros((22, 22), dtype=np.uint8)

        #將圖片至於中心
        h, w = img.shape
        canva[(22 - h) // 2:(22 - h) // 2 + h, (22 - w) // 2:(22 - w) // 2 + w] = img

        avg += canva // len(images)

    avg = np.where(avg > 100, 255, 0)

    Image.fromarray(avg.astype(np.uint8)).save(f"assets/{char}.bmp")
