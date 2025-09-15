# WebAp Captcha

用來通過校務系統圖形驗證的程式。目前有三種 OCR：
- cosine similarity: 使用餘弦相似來辨識文字。
- euclidean distance：以歐式距離來辨識文字。
- tflite：以深度學習模型來辨識文字。（目前 APP 使用此方式）

## Coding Language

- Dart: 以 Dart 撰寫的版本，是實際用於 APP 的版本。將以此版本來比較不同方式的速度。
- Python: 以 Python 撰寫的版本，用於功能驗證。將以此版本來比較不同方式的準確率。

## Test Results
### Accuracy

| Method | Error/Total | Accuracy |
|--------|-------------|----------|
| TFLite | 896/5084    | 82.38%   |
| Cossim | 1365/1365   | 0%       |
| Eucdist| 51/5000     | 98.98%   |

### Speed

Platform: Windows 11, Intel i5-1145G7 @ 2.60GHz, 16GB RAM  
tested on 16329 samples

| Method | Inference Time (ms) |
|-------|---------------------|
| EucDist | 47775 ms |
| TfLite | 39917 ms |

Platform: Android 15, MediaTek Dimensity 1080 @ 2.60GHz, 8GB RAM  
tested on 2001 samples

| Method | Inference Time (ms) |
|-------|---------------------|
| EucDist | 8863 ms |
| TfLite | 7616 ms |
