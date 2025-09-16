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
- [ ] Improve segmentation
- [X] Impove Euclidean distance
  - [X] Fix Q sometimes wrong to O
  - [X] Fix F sometimes wrong to P
  - [ ] Fix 7 sometimes wrong to T (impossible? need more data)

## File structure

```
character_gen.py: 生成比對用的圖片
cossim.py: cosine similarity
eucdist.py: euclidean distance
fix7.py: 改善7時常辨識錯誤的問題
fixF.py: 改善F時常辨識錯誤的問題
fixQ.py: 改善Q時常辨識錯誤的問題
nkust.pem: 用於爬蟲SSL驗證
pyproject.toml: Python專案檔案
segment.py: 用於取出文字
畫圖.ipynb: 用來繪製統計結果的圖
```
