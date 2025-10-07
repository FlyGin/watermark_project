import numpy as np
from .dct_text import embed_text, extract_text
from .dct_image import embed_image, extract_image


def embed(image, secret, params):
    """
    Фасад для DCT-алгоритма: выбирает нужную реализацию в зависимости от типа секрета.
    
    Args:
        image: Исходное изображение (numpy массив)
        secret: Секрет для встраивания (str для текста, np.ndarray для изображения)
        params: Словарь параметров алгоритма:
            - 'strength': коэффициент силы встраивания
            - 'block_size': размер блока для DCT (по умолчанию 8)
    
    Returns:
        Изображение с встроенным водяным знаком
    
    Raises:
        ValueError: Если тип секрета не поддерживается
    """
    if isinstance(secret, str):
        return embed_text(image, secret, params)
    elif isinstance(secret, np.ndarray):
        return embed_image(image, secret, params)
    else:
        raise ValueError("Secret должен быть str (текст) или np.ndarray (изображение)")


def extract(image, params):
    """
    Фасад для извлечения: выбирает реализацию по параметрам.
    
    Args:
        image: Изображение с встроенным водяным знаком
        params: Словарь параметров:
            - 'length': количество символов (для текста)
            - 'secret_shape': форма секретного изображения (для изображения)
            - 'block_size': размер блока DCT (по умолчанию 8)
    
    Returns:
        Извлечённый секрет (str или np.ndarray)
    
    Raises:
        ValueError: Если не указаны необходимые параметры
    """
    if 'length' in params:
        return extract_text(image, params)
    elif 'secret_shape' in params:
        return extract_image(image, params)
    else:
        raise ValueError("Для извлечения необходимо указать либо 'length', либо 'secret_shape' в параметрах.")
