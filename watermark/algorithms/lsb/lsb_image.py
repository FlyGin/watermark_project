import numpy as np

def embed_image(image: np.ndarray, secret_img: np.ndarray, params: dict) -> np.ndarray:
    """
    Внедряет секретное изображение в исходное методом LSB.
    image — исходное изображение (numpy-массив)
    secret_img — секретное изображение, такое же или меньше по размеру
    params — должен содержать 'depth'
    """
    depth = params.get("depth", 1)
    flat_secret = secret_img.flatten()  # переводим картинку в 1D
    total_bits = flat_secret.size * 8   # всего бит в картинке
    max_capacity = image.size * depth   # сколько бит можно внедрить
    if total_bits > max_capacity:
        raise ValueError("Секрет слишком большой для внедрения!")
    # Переводим байты секрета в битовую строку
    secret_bits = ''.join(format(byte, '08b') for byte in flat_secret)
    stego = image.flatten().astype(int)
    bit_idx = 0
    for i in range(len(stego)):
        for d in range(depth):
            if bit_idx < total_bits:
                stego[i] &= ~(1 << d)
                stego[i] |= (int(secret_bits[bit_idx]) << d)
                bit_idx += 1
            else:
                break
    stego = np.array(stego, dtype=np.uint8).reshape(image.shape)
    return stego

def extract_image(image: np.ndarray, params: dict) -> np.ndarray:
    """
    Извлекает секретное изображение из исходной картинки.
    image — картинка-носитель
    params — должен содержать 'depth' и 'secret_shape' (размер внедрённого секрета)
    """
    depth = params.get("depth", 1)
    secret_shape = params.get("secret_shape")  # кортеж (h, w) или (h, w, c)
    if secret_shape is None:
        raise ValueError("Нужно указать 'secret_shape'!")
    num_secret_pixels = np.prod(secret_shape)  # сколько всего элементов
    num_bits = num_secret_pixels * 8          # сколько бит
    bits = []
    stego = image.flatten()
    bit_idx = 0
    for i in range(len(stego)):
        for d in range(depth):
            if bit_idx < num_bits:
                bits.append((stego[i] >> d) & 1)  # из каждого пикселя забираем бит
                bit_idx += 1
    secret_bytes = [int(''.join(str(bits[j]) for j in range(i*8, (i+1)*8)), 2) for i in range(num_secret_pixels)]
    # Собираем секрет обратно в форму оригинальной картинки
    result = np.array(secret_bytes, dtype=np.uint8).reshape(secret_shape)
    return result
