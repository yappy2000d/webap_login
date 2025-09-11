from __future__ import annotations
from io import BytesIO
import numpy as np
import requests
from PIL import Image
import urllib3


def get_captcha_image() -> np.ndarray[tuple[int, int], np.dtype[np.uint8]]:
    """
    Get the captcha image from the webap.
    """
    captcha_url = "https://webap.nkust.edu.tw/nkust/validateCode.jsp"

    # Disable warnings for unverified HTTPS requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    response = requests.get(
        captcha_url,
        verify=False,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://webap0.nkust.edu.tw/nkust/",
        },
    )

    print("Captcha image status code:", response.status_code)

    img = Image.open(BytesIO(response.content))
    img.save("captcha.bmp")

    return np.array(img, dtype=np.uint8)


def histogram(image: np.ndarray) -> np.ndarray:
    """
    Calculate the histogram of the image.
    """
    hist = np.zeros(256, dtype=int)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            hist[image[i, j]] += 1
    return hist


def ostu_threshold(image: np.ndarray) -> int:
    """
    Otsu's thresholding method.
    [source](https://en.wikipedia.org/wiki/Otsu%27s_method)
    """
    pixel_number = image.shape[0] * image.shape[1]
    mean_weight = 1.0 / pixel_number
    his, bins = histogram(image), np.arange(257)
    final_thresh = -1
    final_value = -1
    intensity_arr = np.arange(256)
    for t in bins[1:-1]:  # Exclude the first and last bin edges
        weight_background = np.sum(his[:t]) * mean_weight
        weight_foreground = np.sum(his[t:]) * mean_weight

        if weight_background == 0 or weight_foreground == 0:
            continue

        mean_background = np.sum(intensity_arr[:t] * his[:t]) / np.sum(his[:t])
        mean_foreground = np.sum(intensity_arr[t:] * his[t:]) / np.sum(his[t:])

        # Calculate Between Class Variance
        value = (
            weight_background
            * weight_foreground
            * (mean_background - mean_foreground) ** 2
        )

        # Check if new maximum found
        if value > final_value:
            final_thresh = t
            final_value = value

    return final_thresh


def binarize_image(image: np.ndarray, threshold: int) -> np.ndarray:
    """
    Binarize image using the given threshold.
    """
    result = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # Convert to grayscale using luminosity method
            # I = (image[i, j, 0] + image[i, j, 1] + image[i, j, 2]) // 3
            I = image[i, j, 0] // 3 + image[i, j, 1] // 3 + image[i, j, 2] // 3
            if I > threshold:
                result[i, j] = 255
            else:
                result[i, j] = 0
    return result
