"""
這個腳本經過試驗是錯誤的，可能是因為以異布局方式請求時，伺服器對驗證碼的處理有差異。
請使用同步版本的腳本 test_tflite.py 來進行測試。
"""
import aiohttp
import numpy as np
from io import BytesIO
from PIL import Image

from random import random
import ssl
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tflite import get_captcha_result

URL = "https://webap0.nkust.edu.tw/nkust/"

ssl_context = ssl.create_default_context(cafile="nkust.pem")

async def login(
    session: aiohttp.ClientSession, url: str, username: str, password: str
) -> bool:
    result = True

    response = await session.get(url + "index.html", ssl=ssl_context)
    text = await response.text()

    # Captcha
    response_validate = await session.get(
        url=url + f"validateCode.jsp?it={random()}",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://webap0.nkust.edu.tw/nkust/",
        },
        ssl=ssl_context
    )

    if response_validate.status != 200:
        raise ConnectionError("Failed to get captcha image")
        
    img = await response_validate.content.read()
    img = Image.open(BytesIO(img))
    captcha_answer = get_captcha_result(np.array(img))

    if len(captcha_answer) != 4:
        result = False

    payload = {"uid": username, "pwd": password, "etxt_code": captcha_answer}

    response = await session.post(url + "perchk.jsp", data=payload, ssl=ssl_context)
    text = await response.text()

    # print(text)
    
    if "驗證碼錯誤" in text:
        result = False

    if result:
        img.save(f'test/tflite/success/{captcha_answer}.bmp')
    else:
        img.save(f'test/tflite/failed/{captcha_answer}.bmp')

    await session.close()

    return result


async def main(username: str, password: str) -> bool:
    async with aiohttp.ClientSession() as session:
        return await login(session, URL, username, password)


if __name__ == "__main__":

    import os
    import time

    username = os.getenv("NKUST_ID", "")
    password = os.getenv("NKUST_PASSWORD", "")

    if not username or not password:
        raise ValueError("Please set NKUST_ID and NKUST_PASSWORD environment variables")

    # 單次測試
    result = asyncio.run(main(username, password))

    total = 0
    for i in range(10):
        result = asyncio.run(main(username, password))
        total += 1 if result else 0

    print(f"Total successful logins: {total} / 10")

    # 並發批次測試
    # TOTAL = 5000
    # BATCH = 10
    # start = time.time()

    # async def batch_login():
    #     fail_count = 0
    #     async with aiohttp.ClientSession() as session:
    #         for i in range(0, TOTAL, BATCH):
    #             tasks = [login(session, URL, username, password) for _ in range(BATCH)]
    #             results = await asyncio.gather(*tasks, return_exceptions=True)
    #             batch_fail = sum(1 for r in results if r is False or isinstance(r, Exception))
    #             fail_count += batch_fail
    #             print(f"Batch {i//BATCH+1}: fail {batch_fail} / {BATCH}")
    #             await asyncio.sleep(0.5)  # 避免過度頻繁請求
    #     return fail_count

    # fail_count = asyncio.run(batch_login())
    # print(f"Total failed: {fail_count} / {TOTAL}")
    # print(f"Time elapsed: {time.time() - start:.2f} seconds")
