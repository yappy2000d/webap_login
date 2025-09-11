from unittest import result
import numpy as np
from PIL import Image
from glob import glob

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tflite import get_captcha_result

paths = glob('test/eucdist/success/*.bmp')

err_cnt = 0

for path in paths:
    ans = path.split("/")[-1].split(".")[0]

    img = Image.open(path)
    captcha_answer = get_captcha_result(np.array(img))

    if len(captcha_answer) != 4:
        err_cnt += 1
    elif captcha_answer != ans:
        # print(f"Expected: {ans}, Got: {captcha_answer}")
        err_cnt += 1    
    else:
        pass

total = len(paths)
print(f"Errors: {err_cnt} / {total}")
print(f"Accuracy: {(total - err_cnt) / total * 100:.2f}%")

