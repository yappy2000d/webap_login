from glob import glob
from PIL import Image
import numpy as np
import os
from uuid import uuid4

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import utils
import segment
import tflite

paths = glob('test/eucdist/failed/*.bmp')

for path in paths:
    name = path.split("/")[-1].split(".")[0]
    if name.count('O') != 1:
        continue

    img = Image.open(path)
    captcha_answer = tflite.get_captcha_result(np.array(img))

    if captcha_answer != name.replace('O', 'Q'):
        continue
    
    img_bin = utils.binarize_image(np.array(img), 138)
    labels_im, num_labels = segment.label(img_bin, background=255)
    result = segment.segment_characters(labels_im, num_labels)

    if not os.path.exists(f"assets/FixQ"):
        os.makedirs(f"assets/FixQ")

    Image.fromarray(result[name.index('O')]).save(f"assets/FixQ/{uuid4()}.bmp")

Q = glob(f"assets/Q/*.bmp")
FixQ = glob(f"assets/FixQ/*.bmp")

avgq = np.zeros((22, 22), dtype=np.float64)

for q in Q:
    img = np.array(Image.open(q)).astype(np.uint16)

    canva = np.zeros((22, 22), dtype=np.uint16)

    #將圖片至於中心
    h, w = img.shape
    canva[(22 - h) // 2:(22 - h) // 2 + h, (22 - w) // 2:(22 - w) // 2 + w] = img

    avgq += canva

avgq = avgq / len(Q)

avgfixq = np.zeros((22, 22), dtype=np.float64)
for q in FixQ:
    img = np.array(Image.open(q)).astype(np.uint16)

    canva = np.zeros((22, 22), dtype=np.uint16)

    #將圖片至於中心
    h, w = img.shape
    canva[(22 - h) // 2:(22 - h) // 2 + h, (22 - w) // 2:(22 - w) // 2 + w] = img

    avgfixq += canva
avgfixq = avgfixq / len(FixQ)

final = (avgq + avgfixq)//2

Image.fromarray(np.where(final >= 128, 255, 0).astype(np.uint8)).save("assets/Q.bmp")


