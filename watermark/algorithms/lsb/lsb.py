import numpy as np
from .lsb_text import embed_text, extract_text
from .lsb_image import embed_image, extract_image

def embed(image, secret, params):
    """
    Фасад для LSB-алгоритма: выбирает нужную реализацию в зависимости от типа секрета.
    Если secret — строка, использует embed_text.
    Если secret — np.ndarray, использует embed_image.
    """
    if isinstance(secret, str):
        return embed_text(image, secret, params)
    elif isinstance(secret, np.ndarray):
        return embed_image(image, secret, params)
    else:
        raise ValueError("Secret должен быть str (текст) или np.ndarray (картинка)")

def extract(image, params):
    """
    Фасад для извлечения: выбирает реализацию по параметрам.
    Если в params есть 'length' — извлекает текст.
    Если есть 'secret_shape' — извлекает изображение.
    """
    if 'length' in params:
        return extract_text(image, params)
    elif 'secret_shape' in params:
        return extract_image(image, params)
    else:
        raise ValueError("Для извлечения необходимо указать либо 'length', либо 'secret_shape' в параметрах.")
