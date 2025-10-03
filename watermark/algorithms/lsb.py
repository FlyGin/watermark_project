# watermark/algorithms/lsb.py

import numpy as np

def embed(image: np.ndarray, secret_img: np.ndarray, params: dict) -> np.ndarray:
    """
    Внедрение секретного изображения в исходное методом младших битов.
    :param image: np.ndarray — исходное изображение-носитель
    :param secret_img: np.ndarray — секретное изображение (например, маленькая картинка)
    :param params: dict — параметры (depth — сколько битов использовать)
    :return: np.ndarray — изображение со встроенным секретом
    """
    depth = params.get("depth", 1)
    flat_secret = secret_img.flatten()
    total_bits = flat_secret.size * 8
    
    max_capacity = image.size * depth
    if total_bits > max_capacity:
        raise ValueError("Секретное изображение слишком большое для внедрения с выбранной глубиной LSB!")

    # Переводим все пиксели секрета в битовую строку
    secret_bits = ''.join(format(byte, '08b') for byte in flat_secret)
    stego = image.copy().flatten()

    bit_idx = 0
    for i in range(len(stego)):
        for d in range(depth):
            if bit_idx < total_bits:
                stego[i] &= ~(1 << d)
                stego[i] |= (int(secret_bits[bit_idx]) << d)
                bit_idx += 1
            else:
                break

    stego = stego.reshape(image.shape)
    return stego.astype(np.uint8)

def extract(image: np.ndarray, params: dict) -> np.ndarray:
    """
    Извлечение секретного изображения из исходного по методу LSB.
    :param image: np.ndarray — изображение с внедрённым секретом
    :param params: dict — параметры:
        - depth (сколько бит использовать),
        - secret_shape (shape внедрённого изображения)
    :return: np.ndarray — восстановленное секретное изображение
    """
    depth = params.get("depth", 1)
    secret_shape = params.get("secret_shape")  # пример: (h, w, 3) или (h, w)
    if secret_shape is None:
        raise ValueError("Необходимо указать 'secret_shape' в параметрах для извлечения!")

    num_secret_pixels = np.prod(secret_shape)
    num_bits = num_secret_pixels * 8
    bits = []

    stego = image.flatten()
    bit_idx = 0
    for i in range(len(stego)):
        for d in range(depth):
            if bit_idx < num_bits:
                bits.append((stego[i] >> d) & 1)
                bit_idx += 1
    
    # Список битов переводим обратно в байты
    secret_bytes = [int(''.join(str(bits[j]) for j in range(i*8, (i+1)*8)), 2) for i in range(num_secret_pixels)]
    result = np.array(secret_bytes, dtype=np.uint8).reshape(secret_shape)
    return result
