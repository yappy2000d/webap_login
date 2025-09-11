## Prerequisites

- uv
- tflite only support Linux or MacOS, Windows is not supported.

## Setup

```
cd webap_captcha/python/
uv sync
```

## Usage

1. 先以 test_tflite.py 測試 TFLite 模型準確度的同時，蒐集驗證圖片
2. 再以 character_gen.py 產生各個字元的圖片
3. 有了字元圖片後，就可以測試 cossim 或 eucdist 的準確度

## Todo

- [X] Tflite
- [X] Segmentation
- [X] Cosine similarity
- [X] Euclidean distance

## Test

| Method | Error/Total | Accuracy |
|--------|-------------|----------|
| TFLite | 844/1000    | 15.60%   |
| Cossim | 1365/1365   | 0%       |
| Eucdist| 4917/5000   | 98.34%   |

there are 41 errors Eucdist are caused by wrong segmentation.