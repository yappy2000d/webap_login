import numpy as np
import requests
from PIL import Image
from ai_edge_litert.interpreter import Interpreter

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import get_captcha_image

model_url = "https://github.com/NKUST-ITC/NKUST-AP-Flutter/raw/fd06efbc54d3829fcca2c99c3517e1a2c6c903e0/assets/webap_captcha.tflite"

# Download model if not exists
model_path = "webap_captcha.tflite"
try:
    with open(model_path, "rb") as f:
        pass
except FileNotFoundError:
    print("Downloading model...")
    r = requests.get(model_url)
    with open(model_path, "wb") as f:
        f.write(r.content)


def convert2gray(img: np.ndarray) -> np.ndarray:
    """
    Convert image to grayscale using YCbCr conversion.
    [image](https://github.com/brendan-duncan/image/blob/0b22b993b43056040fb7026f2d1a68d461f2f2e0/lib/src/util/color_util.dart#L135)
    """
    if img.shape[2] == 3:
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray
    else:
        raise ValueError("Unsupported image format")


def normalize(img: np.ndarray, w: int, h: int, mean: float, std: float) -> np.ndarray:
    """
    Normalize image.
    """
    # img = (img - mean) / std  # [flutter_tflite](https://github.com/shaqian/flutter_tflite/blob/ce8075a391e02e0cc0bc6c2db950aa961a17d745/example/lib/main.dart#L145)
    img = (
        img / 255.0
    )  # [captcha_utils](https://github.com/NKUST-ITC/NKUST-AP-Flutter/blob/eb77232a1af1365da5e4610c145798f092c41933/lib/utils/captcha_utils.dart#L118)

    return img


labels = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
]

# img = get_captcha_image()
img = np.array(Image.open("test/fail cases/CCL_A_0.bmp"))

img_gray = convert2gray(img.astype(np.float32))

digitsCount = 4
imageHeight = 40
imageWidth = 85

target = []
result = ""

for i in range(digitsCount):
    # Crop image
    w = imageWidth // digitsCount
    h = imageHeight
    target = img_gray[0:h, i * w : (i + 1) * w]

    img_normalized = normalize(target, w, h, 127.5, 255.0)

    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_shape = input_details[0]["shape"]
    interpreter.set_tensor(
        input_details[0]["index"],
        img_normalized[np.newaxis, :, :, np.newaxis].astype(np.float32),
    )

    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]["index"])

    digit = labels[np.argmax(output_data)]
    result += digit

print("Captcha result:", result)
