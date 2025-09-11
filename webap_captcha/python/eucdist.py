import numpy as np
from PIL import Image

key = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
table = [np.array(Image.open(f"assets/{k}.bmp")) for k in key]

def eucdist(image1: np.ndarray, image2: np.ndarray) -> float:
    """Compute the Euclidean distance between two images."""
    if image1.shape != image2.shape:
        raise ValueError(f"Images must have the same shape. Got {image1.shape} and {image2.shape}")
    return np.sqrt(np.sum((image1 - image2) ** 2))


def get_character(image: np.ndarray) -> str:
    """Get the character represented by the image."""
       # Resize the image to 22x22 and place it in the middle of a 22x22 canvas
    canva = np.zeros((22, 22), dtype=np.uint8)
    h, w = image.shape
    canva[(22 - h) // 2:(22 - h) // 2 + h, (22 - w) // 2:(22 - w) // 2 + w] = image
    # Compute the distances to all character templates
    distances = [eucdist(canva, template) for template in table]
    # Find the index of the minimum distance
    min_index = np.argmin(distances)
    return key[min_index]
