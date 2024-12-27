import io
from PIL import Image
import numpy.typing as npt
import numpy as np


def np2bytes(numpy_array: npt) -> bytes:
    """Convert a numpy array to bytes
    
    Args:
        numpy_array (npt): the numpy array to convert to bytes

    Returns:
        bytes: the byte stream of the numpy array
    """
    return numpy_array.tobytes()


def str2bytes(string: str) -> bytes:
    """Convert a string to bytes
    
    Args:
        string (str): the string to convert to bytes
    Outputs:
        bytes: the byte stream of the
    """
    return string.encode('utf-8')


def bytes2str(bytes: bytes) -> str:
    """Convert a byte stream into a string
    
    Args:
        bytes (bytes): the byte stream to convert to a string
    """
    return bytes.decode('utf-8')


def bytes2np(bytes_data: bytes) -> npt:
    """Convert a byte stream into a numpy array
    
    Args:
        bytes_data (bytes): the byte stream to convert to a numpy array
    
    Returns:
        npt: Numpy array of uint64 values
    """
    return np.frombuffer(bytes_data, dtype=np.uint64)


def pil2bytes(pil: Image, image_format: str = "JPEG", quality: int = 85) -> bytes:
    """Convert a PIL image to bytes
    
    Args:
        pil (Image): the PIL image to convert to bytes
        image_format (str, optional): the image format to use. Defaults to "JPEG".
        quality (int, optional): the quality of the image. Defaults to 85.

    Returns:
        bytes: the byte stream of the PIL image
    """
    if image_format.upper() == "JPEG" and pil.mode == "RGBA":
        pil = pil.convert("RGB")
    img_bytes = io.BytesIO()
    pil.save(img_bytes, format=image_format, quality=quality)
    return img_bytes.getvalue()


def bytes2pil(bytes: bytes) -> Image:
    """Convert a byte stream into a PIL image
    
    Args:
        bytes (bytes): the byte stream to convert to a PIL image

    Returns:
        Image: the PIL image
    
    """
    return Image.open(io.BytesIO(bytes))


