import numpy as np
from io import BytesIO
from PIL import Image

from random import random
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tflite import get_captcha_result

URL = "https://webap0.nkust.edu.tw/nkust/"

def login(
    session: requests.Session, url: str, username: str, password: str
) -> bool:
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
    captcha_answer = get_captcha_result(np.array(img))

    if len(captcha_answer) != 4:
        result = False

    payload = {"uid": username, "pwd": password, "etxt_code": captcha_answer}

    response = session.post(url + "perchk.jsp", data=payload, verify="nkust.pem")
    text = response.text

    # print(text)
    
    if "驗證碼錯誤" in text:
        result = False

    if result:
        img.save(f'test/tflite/success/{captcha_answer}.bmp')
    else:
        img.save(f'test/tflite/failed/{captcha_answer}.bmp')

    return result


if __name__ == "__main__":

    import os

    username = os.getenv("NKUST_ID", "")
    password = os.getenv("NKUST_PASSWORD", "")

    if not username or not password:
        raise ValueError("Please set NKUST_ID and NKUST_PASSWORD environment variables")

   
    total = 1000
    err_count = 0
    for i in range(total):
        session = requests.Session()
        result = login(session, URL, username, password)
        session.close()
        err_count += 1 if result else 0

    print(f"Error: {err_count} / {total}")
    print(f"Accuracy: {(total - err_count) / total * 100:.2f}%")
