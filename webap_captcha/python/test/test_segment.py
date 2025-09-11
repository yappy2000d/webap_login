from PIL import Image
import numpy as np

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import utils

image = utils.get_captcha_image()
# image = np.array(Image.open("test/fail cases/CCL_B_0.bmp"))

Image.fromarray(image).save("result/captcha.bmp")

# image_bin = utils.binarize_image(image, utils.ostu_threshold(image))
image_bin = utils.binarize_image(image, 132)

Image.fromarray(image_bin).save("result/captcha_bin.bmp")

labels_im, num_labels = utils.label(image_bin, background=255)

result = utils.segment_characters(labels_im, num_labels)

for i, img in enumerate(result):
    Image.fromarray(img.astype(np.uint8)).save(f"result/char_{i}.bmp")

print(f"Number of connected components: {len(result)}")
