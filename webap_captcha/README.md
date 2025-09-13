# WebAp Captcha

用來通過校務系統圖形驗證的程式。目前有三種 OCR：
- cosine similarity: 使用餘弦相似來辨識文字。
- euclidean distance：以歐式距離來辨識文字。
- tflite：以深度學習模型來辨識文字。（目前 APP 使用此方式）

## Coding Language

- Dart: 以 Dart 撰寫的版本，是實際用於 APP 的版本。將以此版本來比較不同方式的速度。
- Python: 以 Python 撰寫的版本，用於功能驗證。將以此版本來比較不同方式的準確率。

