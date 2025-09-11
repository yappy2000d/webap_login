import numpy as np
from io import BytesIO
from PIL import Image

from random import random
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import eucdist
import utils
import segment

URL = "https://webap0.nkust.edu.tw/nkust/"

seg_err_cnt = 0

def login(
    session: requests.Session, url: str, username: str, password: str
) -> bool:
    global seg_err_cnt
    result = True

    response = session.get(url + "index.html", verify="nkust.pem")
    text = response.text

    # Captcha
    response_validate = session.get(
        url=url + f"validateCode.jsp?it={random()}",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://webap0.nkust.edu.tw/nkust/",
        },
        verify="nkust.pem"
    )

    if response_validate.status_code != 200:
        raise ConnectionError("Failed to get captcha image")

    img = Image.open(BytesIO(response_validate.content))
    
    img_bin = utils.binarize_image(np.array(img), 138)
    labels_im, num_labels = segment.label(img_bin, background=255)
    chars = segment.segment_characters(labels_im, num_labels)

    captcha_answer = ''

    if len(chars) != 4:
        seg_err_cnt += 1
        img.save(f"test/segment/failed/unknown/{seg_err_cnt}.bmp")
        result = False
    else:
        for char in chars:
            character = eucdist.get_character(char)
            captcha_answer += character

    payload = {"uid": username, "pwd": password, "etxt_code": captcha_answer}

    response = session.post(url + "perchk.jsp", data=payload, verify="nkust.pem")
    text = response.text

    # print(text)
    
    if "驗證碼錯誤" in text:
        try:
            img.save(f"test/eucdist/failed/{captcha_answer}.bmp")
        except ValueError:
            pass
        result = False
    else:
        img.save(f"test/eucdist/success/{captcha_answer}.bmp")

    return result


if __name__ == "__main__":

    import os

    username = os.getenv("NKUST_ID", "")
    password = os.getenv("NKUST_PASSWORD", "")

    if not username or not password:
        raise ValueError("Please set NKUST_ID and NKUST_PASSWORD environment variables")

   
    total = 5000
    err_count = 0
    for i in range(total):
        session = requests.Session()
        result = login(session, URL, username, password)
        session.close()
        err_count += 0 if result else 1
        print(f"\r{i+1} / {total}", end="")

    print(f"Segmentation errors: {seg_err_cnt} / {total}")
    print(f"Error: {err_count} / {total}")
    print(f"Accuracy: {(total - err_count) / total * 100:.2f}%")
