# Webapp Captcha

用於高科校務通的驗證碼辨識套件。

## Prerequisites

- Dart SDK
- Flutter SDK
- A Mobile Device or Emulator

### 在 Windows 下執行 tflite

1. 下載[預編譯的 TFLite](https://github.com/ValYouW/tflite-dist/releases/download/v2.11.0/tflite-dist.zip)。
2. 解壓縮並將其中的 `tensorflowlite_c.dll` 重新命名成 `libtensorflowlite_c-win.dll`。
3. 然後放到專案目錄的`flutter\bin\cache\artifacts\engine\windows-x64\blobs\`下。

## Test Results

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
