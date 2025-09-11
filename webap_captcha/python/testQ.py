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
import eucdist

paths = glob('test/eucdist/failed/*.bmp')

for path in paths:
    name = path.split("/")[-1].split(".")[0]

    img = Image.open(path)
    captcha_answer = tflite.get_captcha_result(np.array(img))
    
    img_bin = utils.binarize_image(np.array(img), 138)
    labels_im, num_labels = segment.label(img_bin, background=255)
    chars = segment.segment_characters(labels_im, num_labels)

    result = ''
    for char in chars:
        character = eucdist.get_character(char)
        result += character

    if result != captcha_answer:
        print(f"Expected: {captcha_answer}, Got: {result}")
    else:
        print(f"Correct: {path}")
