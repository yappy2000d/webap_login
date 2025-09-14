# Webapp Captcha

用於高科校務通的驗證碼辨識套件。

## Prerequisites

- Dart SDK
- Flutter SDK
- A Mobile Device or Emulator

### 在 Windows 下構建 tensorflowlite_c.dll

```
git clone https://github.com/tensorflow/tensorflow.git tensorflow_src
mkdir tflite_build
cd tflite_build
cmake -S ../tensorflow_src/tensorflow/lite/c -B build -A x64 -DCMAKE_BUILD_TYPE=Release -DTFLITE_ENABLE_C_API=ON -DTF_MAJOR_VERSION=2 -DTF_MINOR_VERSION=11 -DTF_PATCH_VERSION=0 -DTF_VERSION_SUFFIX=''
cmake --build build --config Release --target install
```

編譯完成後將 `tflite_build/build/Release/tensorflowlite_c.dll` 複製到專案目錄下的 `blobs` 資料夾中。

接著將以下內容新增到 `windows/CMakeLists.txt`：

```
# get tf lite binaries
install(
  FILES ${PROJECT_BUILD_DIR}/../blobs/libtensorflowlite_c-win.dll 
  DESTINATION ${INSTALL_BUNDLE_DATA_DIR}/../blobs/
)
```

## Setup

由於 TfLite 只支援 arm64 架構，因此需要在 arm64 的設備上運行。
