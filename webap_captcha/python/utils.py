from __future__ import annotations
import numpy as np
from typing import Tuple, Iterable, List
import requests
from PIL import Image
import urllib3
from io import BytesIO


def get_captcha_image() -> np.ndarray[tuple[int, int], np.dtype[np.uint8]]:
    """
    Get the captcha image from the webap.
    """
    captcha_url = "https://webap.nkust.edu.tw/nkust/validateCode.jsp"

    # Disable warnings for unverified HTTPS requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    response = requests.get(
        captcha_url,
        verify=False,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://webap0.nkust.edu.tw/nkust/",
        },
    )

    print("Captcha image status code:", response.status_code)

    img = Image.open(BytesIO(response.content))
    img.save("captcha.bmp")

    return np.array(img, dtype=np.uint8)


def histogram(image: np.ndarray) -> np.ndarray:
    """
    Calculate the histogram of the image.
    """
    hist = np.zeros(256, dtype=int)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            hist[image[i, j]] += 1
    return hist


def ostu_threshold(image: np.ndarray) -> int:
    """
    Otsu's thresholding method.
    [source](https://en.wikipedia.org/wiki/Otsu%27s_method)
    """
    pixel_number = image.shape[0] * image.shape[1]
    mean_weight = 1.0 / pixel_number
    his, bins = histogram(image), np.arange(257)
    final_thresh = -1
    final_value = -1
    intensity_arr = np.arange(256)
    for t in bins[1:-1]:  # Exclude the first and last bin edges
        weight_background = np.sum(his[:t]) * mean_weight
        weight_foreground = np.sum(his[t:]) * mean_weight

        if weight_background == 0 or weight_foreground == 0:
            continue

        mean_background = np.sum(intensity_arr[:t] * his[:t]) / np.sum(his[:t])
        mean_foreground = np.sum(intensity_arr[t:] * his[t:]) / np.sum(his[t:])

        # Calculate Between Class Variance
        value = (
            weight_background
            * weight_foreground
            * (mean_background - mean_foreground) ** 2
        )

        # Check if new maximum found
        if value > final_value:
            final_thresh = t
            final_value = value

    return final_thresh


def binarize_image(image: np.ndarray, threshold: int) -> np.ndarray:
    """
    Binarize image using the given threshold.
    """
    result = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # Convert to grayscale using luminosity method
            # I = (image[i, j, 0] + image[i, j, 1] + image[i, j, 2]) // 3
            I = image[i, j, 0] // 3 + image[i, j, 1] // 3 + image[i, j, 2] // 3
            if I > threshold:
                result[i, j] = 255
            else:
                result[i, j] = 0
    return result


def label(
    input: np.ndarray,
    structure: np.ndarray | None = None,
    background: int | float = 0,
    dtype: np.dtype = np.dtype("int64"),
) -> Tuple[np.ndarray, int]:
    """
    以純 Python（使用 NumPy 做陣列容器）實作 ND 連通元件標記，語義類似 scipy.ndimage.label。

    參數
    - input: 任意維度的 NumPy 陣列。非零（或不等於 background）的元素視為前景。
    - structure: 布林 footprint，形狀需為 (3,)*ndim，且為中心對稱。
                 若為 None，使用「面相鄰」的預設連通（2D=4連通，3D=6連通，…）。
    - background: 視為背景的值（預設 0）。
    - dtype: 輸出標籤陣列的 dtype（預設 np.int64）。

    回傳
    - labels: 與 input 同形狀的整數陣列，前景區塊標為 1..N，背景為 0。
    - num_features: 連通元件個數 N。

    實作重點
    - 採單向掃描（C-order，最後一維最內層），僅使用「在掃描順序上已出現」的鄰域（因果鄰域）。
    - 使用 Union-Find（帶路徑壓縮）合併等價標籤。
    - 第二趟遍歷將每個標籤壓縮到其根，並重編成連續 1..N。
    """
    a = np.asarray(input)
    if a.ndim == 0 or a.size == 0:
        # 與 SciPy 行為一致：空或純標量無法標記
        raise ValueError("Cannot label scalars or empty arrays")

    # 前景判定：!= background 即視為前景
    # 若希望與 scipy.ndimage.label 的「非零即前景」一致，可讓 background=0。
    foreground = a != background

    # 構造/驗證 footprint
    if structure is None:
        structure = _default_structure(a.ndim)
    else:
        structure = np.asarray(structure, dtype=bool)
        _validate_structure(structure, a.ndim)

    # 計算「因果鄰域」的偏移（只包含掃描順序上已處理到的鄰居）
    neighbor_offsets = _compute_causal_neighbor_offsets(structure)

    # 輸出標籤陣列（先全部 0）
    labels = np.zeros(a.shape, dtype=dtype)

    # Union-Find 結構（標籤從 1 開始）
    parent: List[int] = [0]  # parent[0] 無用佔位，使索引與標籤一致
    rank: List[int] = [0]

    def uf_make() -> int:
        parent.append(len(parent))
        rank.append(0)
        return len(parent) - 1

    def uf_find(x: int) -> int:
        # 路徑壓縮
        root = x
        while parent[root] != root:
            root = parent[root]
        # 壓縮
        while parent[x] != x:
            x, parent[x] = parent[x], root
        return root

    def uf_union(x: int, y: int) -> int:
        rx, ry = uf_find(x), uf_find(y)
        if rx == ry:
            return rx
        if rank[rx] < rank[ry]:
            parent[rx] = ry
            return ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
            return rx
        else:
            parent[ry] = rx
            rank[rx] += 1
            return rx

    # 第一趟：指派臨時標籤並收集等價合併
    # 依 C-order 掃描（np.ndindex 即為 row-major）
    shape = a.shape
    for idx in np.ndindex(shape):
        if not foreground[idx]:
            continue

        neighbor_labels = []
        # 檢視所有「已出現」的鄰居
        for off in neighbor_offsets:
            nb = _add_tuple(idx, off)
            if _in_bounds(nb, shape):
                lab = labels[nb]
                if lab != 0:
                    neighbor_labels.append(int(lab))

        if not neighbor_labels:
            # 沒有已標記的鄰居 -> 新標籤
            new_lab = uf_make()
            labels[idx] = new_lab
        else:
            # 取最小標籤並與其他鄰居標籤合併
            m = min(neighbor_labels)
            for l in neighbor_labels:
                if l != m:
                    uf_union(m, l)
            labels[idx] = m

    # 第二趟：將每個標籤壓縮到 root，並重映射成 1..N
    if labels.max() == 0:
        return labels, 0

    # 找每個已用標籤的根
    used = np.unique(labels)
    used = used[used != 0].astype(int)
    roots = {lab: uf_find(lab) for lab in used}

    # 將根重編到 1..N
    root_set = []
    seen = set()
    for lab in used:
        r = roots[lab]
        if r not in seen:
            seen.add(r)
            root_set.append(r)
    root_set.sort()

    root_to_compact = {r: i + 1 for i, r in enumerate(root_set)}
    lab_to_compact = {lab: root_to_compact[roots[lab]] for lab in used}

    # 應用映射
    # 為了效率，先建立查表陣列（大小為 max(used)+1）
    max_lab = int(max(used))
    lut = np.zeros(max_lab + 1, dtype=labels.dtype)
    for lab, comp in lab_to_compact.items():
        lut[lab] = comp

    # 向量化映射（背景仍為 0）
    mask = labels != 0
    labels[mask] = lut[labels[mask].astype(int)]

    num_features = len(root_set)
    return labels, num_features


# -----------------------------
# 工具函式
# -----------------------------


def _default_structure(ndim: int) -> np.ndarray:
    """
    預設 footprint：面相鄰（Manhattan 距離為 1 的鄰居），形狀為 (3,)*ndim，布林。
    中心為 True。
    - 2D -> 4-連通
    - 3D -> 6-連通
    - ND -> face-connected
    """
    shape = (3,) * ndim
    s = np.zeros(shape, dtype=bool)
    center = tuple(1 for _ in range(ndim))
    s[center] = True
    for off in _all_offsets(ndim):
        if sum(abs(o) for o in off) == 1:
            s[_to_index(off)] = True
    return s


def _validate_structure(structure: np.ndarray, ndim: int) -> None:
    if structure.ndim != ndim:
        raise ValueError("Structuring element must have same # of dimensions as input")
    if set(structure.shape) != {3}:
        raise ValueError(
            f"Structuring element must be size 3 in every dimension, was {structure.shape}"
        )
    # 對稱性檢查
    if not np.array_equal(
        structure, structure[tuple(slice(None, None, -1) for _ in range(ndim))]
    ):
        raise ValueError("Structuring element is not symmetric")


def _all_offsets(ndim: int) -> Iterable[Tuple[int, ...]]:
    if ndim == 0:
        return
    # 產生 (-1,0,1)^ndim（不含全 0）
    from itertools import product

    for off in product((-1, 0, 1), repeat=ndim):
        if any(o != 0 for o in off):
            yield off


def _to_index(off: Tuple[int, ...]) -> Tuple[int, ...]:
    # 把偏移 -1/0/1 轉成 footprint 索引 0/1/2
    return tuple(o + 1 for o in off)


def _compute_causal_neighbor_offsets(structure: np.ndarray) -> List[Tuple[int, ...]]:
    """
    從 footprint 中挑出「因果」鄰域：
    - 僅包含在掃描順序（C-order，最後一維最先變動）上已經處理過的鄰居。
    檢測方法（lexicographic causal）：
    - 對偏移向量 off，從軸 0..nd-1 依序檢查：
      - 若遇到第一個非 0，且為 -1 -> 屬於因果鄰居（True）
      - 若為 +1 -> 非因果（False）
      - 若為 0 -> 繼續看下一軸
    - 全部為 0 則 False
    """
    ndim = structure.ndim
    offs = []
    for off in _all_offsets(ndim):
        if not structure[_to_index(off)]:
            continue
        if _is_lexicographically_negative(off):
            offs.append(off)
    return offs


def _is_lexicographically_negative(off: Tuple[int, ...]) -> bool:
    for o in off:
        if o < 0:
            return True
        if o > 0:
            return False
        # o == 0 -> 繼續
    return False


def _add_tuple(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def _in_bounds(idx: Tuple[int, ...], shape: Tuple[int, ...]) -> bool:
    return all(0 <= i < n for i, n in zip(idx, shape))


def segment_characters(labels_img: np.ndarray, num_labels: int) -> List[np.ndarray]:
    bboxes = []
    for i in range(1, num_labels + 1):
        ys, xs = np.where(labels_img == i)

        if len(xs) == 0 or len(ys) == 0:
            continue

        x_min, x_max = xs.min(), xs.max()
        y_min, y_max = ys.min(), ys.max()

        # filter small components
        if x_max - x_min < 5 or y_max - y_min < 5:
            continue

        bboxes.append({"label": i, "bbox": (x_min, y_min, x_max, y_max)})

    bboxes = sorted(bboxes, key=lambda x: x["bbox"][0])

    result = []
    for item in bboxes:
        # Crop to bounding box
        x_min, y_min, x_max, y_max = item["bbox"]
        char = labels_img[y_min : y_max + 1, x_min : x_max + 1]
        # Binarize character image
        char = np.where(char > 0, 255, 0).astype(np.uint8)

        result.append(char)

    return result
