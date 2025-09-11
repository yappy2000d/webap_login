"""
修復失敗
Expected: 7IMH, Got: TIMH
Expected: 7NCM, Got: TNCM
"""

from PIL import Image
import numpy as np
import os
from uuid import uuid4
from glob import glob

import segment
import utils
import eucdist

images = [
    ("7IMH", "test/eucdist/failed/TIMH.bmp"),
    ("7NCM", "test/eucdist/failed/TNCM.bmp"),
]

for answer, path in images:
    img = Image.open(path)
    img_bin = np.array(img)
    img_bin = utils.binarize_image(np.array(img), 138)
    labels_im, num_labels = segment.label(img_bin, background=255)
    result = segment.segment_characters(labels_im, num_labels)

    if not os.path.exists(f"assets/Fix7"):
        os.makedirs(f"assets/Fix7")
    
    Image.fromarray(result[answer.index("7")]).save(f"assets/Fix7/{uuid4()}.bmp")

Seven = glob("assets/7/*.bmp")
Fix7 = glob("assets/Fix7/*.bmp")

avg7 = np.zeros((22, 22), dtype=np.float64)
for s in Seven:
    img = np.array(Image.open(s)).astype(np.uint16)

    canva = np.zeros((22, 22), dtype=np.uint16)

    # 將圖片至於中心
    h, w = img.shape
    canva[(22 - h) // 2 : (22 - h) // 2 + h, (22 - w) // 2 : (22 - w) // 2 + w] = img

    avg7 += canva
avg7 = avg7 / len(Seven)

avgfix7 = np.zeros((22, 22), dtype=np.float64)
for s in Fix7:
    img = np.array(Image.open(s)).astype(np.uint16)

    canva = np.zeros((22, 22), dtype=np.uint16)

    # 將圖片至於中心
    h, w = img.shape
    canva[(22 - h) // 2 : (22 - h) // 2 + h, (22 - w) // 2 : (22 - w) // 2 + w] = img

    avgfix7 += canva
avgfix7 = avgfix7 / len(Fix7)

final = avg7 * 1 + avgfix7 * 0
final = final // 1

print(final)

Image.fromarray(np.where(final >= 153, 255, 0).astype(np.uint8)).save("assets/7.bmp")


# test
for ans, path in images:
    img = np.array(Image.open(path))
    img_bin = utils.binarize_image(np.array(img), 138)
    labels_im, num_labels = segment.label(img_bin, background=255)
    chars = segment.segment_characters(labels_im, num_labels)

    result = ''
    for char in chars:
        character = eucdist.get_character(char)
        result += character

    if result != ans:
        print(f"Fix Expected: {ans}, Got: {result}")

images = glob("test/eucdist/success/*.bmp") + glob("test/tflite/success/*.bmp")
for path in images:
    ans = path.split("/")[-1].split(".")[0]
    img = np.array(Image.open(path))
    img_bin = utils.binarize_image(np.array(img), 138)
    labels_im, num_labels = segment.label(img_bin, background=255)
    chars = segment.segment_characters(labels_im, num_labels)

    if len(chars) != 4:
        continue

    result = ''
    for char in chars:
        character = eucdist.get_character(char)
        result += character

    if result != ans:
        print(f"Expected: {ans}, Got: {result}")
