import numpy as np
from PIL import Image

key = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
table = [np.array(Image.open(f"assets/{k}.bmp")) for k in key]

def cossim(image1: np.ndarray, image2: np.ndarray) -> float:
    """Compute the Cosine similarity between two images."""
    if image1.shape != image2.shape:
        raise ValueError(f"Images must have the same shape. Got {image1.shape} and {image2.shape}")
    dot_product = np.sum(image1 * image2)
    norm1 = np.sqrt(np.sum(image1 ** 2))
    norm2 = np.sqrt(np.sum(image2 ** 2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.abs(dot_product / (norm1 * norm2))


def get_character(image: np.ndarray) -> str:
    """Get the character represented by the image."""
    # Resize the image to 22x22 and place it in the middle of a 22x22 canvas
    canva = np.zeros((22, 22), dtype=np.uint8)
    h, w = image.shape
    canva[(22 - h) // 2:(22 - h) // 2 + h, (22 - w) // 2:(22 - w) // 2 + w] = image
    # Compute the distances to all character templates
    distances = [cossim(canva, template) for template in table]
    # Find the index of the minimum distance
    min_index = np.argmin(distances)
    return key[min_index]