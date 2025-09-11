import glob
from PIL import Image
import numpy as np

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import utils
import segment
import eucdist

paths = glob.glob("test/tflite/success/*.bmp")

seg_err_cnt = 0
compare_err_cnt = 0
cnt = 0

for path in paths:
    ans = path.split("/")[-1].split(".")[0]

    image = Image.open(path)
    img = np.array(image)

    img_bin = utils.binarize_image(img, 132)
    labels_im, num_labels = segment.label(img_bin, background=255)
    chars = segment.segment_characters(labels_im, num_labels)

    if len(chars) != 4:
        seg_err_cnt += 1
    else:
        result = ''
        for char in chars:
            character = eucdist.get_character(char)
            result += character
    
        if result != ans:
            print(f"Expected: {ans}, Got: {result}")
            compare_err_cnt += 1

    cnt += 1

print(f"Segmentation errors: {seg_err_cnt} / {cnt}")
print(f"Comparison errors: {compare_err_cnt} / {cnt}")
print(f"Error: {seg_err_cnt + compare_err_cnt} / {cnt}")
print(f"Accuracy: {(cnt - (seg_err_cnt + compare_err_cnt)) / cnt * 100:.2f}%")