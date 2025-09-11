```
.
│  
├─cossim
│      test_cossim.py
│
├─eucdist
│      test_eucdist.py
│
├─segment
│  │  test_segment.py
│  │
│  └─failed
│          failed.zip
│
└─tflite
    │  test_tflite.py
    │  test_tflite_aiohttp.py
    │
    ├─failed
    │      failed.zip
    │
    └─success
            success.zip
```

- test_tflite.py 是使用網路的驗證碼進行測試
- test_cossim.py 和 test_eucdist.py 是使用本地的驗證碼進行測試
- test_tflite_aiohttp 是為了更快的測試與抓取圖片，但無法取得正確的結果
- test_segment.py 用來測試分割文字