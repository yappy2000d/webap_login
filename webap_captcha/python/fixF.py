"""
修復成功
只是 FQ4E 會變 FQ4F
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
    ("F1PJ", "test/eucdist/failed/P1PJ.bmp"),
    ("F7RO", "test/eucdist/failed/P7RO.bmp"),
    ("W8FV", "test/eucdist/failed/W8PV.bmp"),
]

# for answer, path in images:
#     img = Image.open(path)
#     img_bin = np.array(img)
#     img_bin = utils.binarize_image(np.array(img), 138)
#     labels_im, num_labels = segment.label(img_bin, background=255)
#     result = segment.segment_characters(labels_im, num_labels)

    
#     if not os.path.exists("assets/FixF"):
#         os.makedirs("assets/FixF")

#     Image.fromarray(result[answer.index("F")]).save(f"assets/FixF/{uuid4()}.bmp")

# F = glob("assets/F/*.bmp")
# FixF = glob("assets/FixF/*.bmp")    

# avgf = np.zeros((22, 22), dtype=np.float64)
# for f in F:
#     img = np.array(Image.open(f)).astype(np.uint16)

#     canva = np.zeros((22, 22), dtype=np.uint16)

#     # 將圖片至於中心
#     h, w = img.shape
#     canva[(22 - h) // 2 : (22 - h) // 2 + h, (22 - w) // 2 : (22 - w) // 2 + w] = img

#     avgf += canva
# avgf = avgf / len(F)
# avgfixf = np.zeros((22, 22), dtype=np.float64)
# for f in FixF:
#     img = np.array(Image.open(f)).astype(np.uint16)

#     canva = np.zeros((22, 22), dtype=np.uint16)

#     # 將圖片至於中心
#     h, w = img.shape
#     canva[(22 - h) // 2 : (22 - h) // 2 + h, (22 - w) // 2 : (22 - w) // 2 + w] = img

#     avgfixf += canva
# avgfixf = avgfixf / len(FixF)

# final = avgf * 0.5 + avgfixf * 0.5
# final = final // 1

# print(final)

# # 102, 153, 187
# Image.fromarray(np.where(final >= 127, 255, 0).astype(np.uint8)).save("assets/F.bmp")

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
