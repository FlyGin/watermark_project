import numpy as np

def embed_text(image: np.ndarray, secret_text: str, params: dict) -> np.ndarray:
    """
    Внедрение текстовой строки в изображение методом LSB.
    image — исходное изображение, numpy-массив
    secret_text — строка, которую нужно спрятать
    params — словарь с параметрами ('depth' — количество младших битов)
    Возвращает изображение с внедрённым секретом.
    """
    depth = params.get("depth", 1)
    # Преобразуем секрет в байты
    secret_bytes = secret_text.encode("utf-8")
    # Переводим байты текста в строку битов
    secret_bits = ''.join(format(b, '08b') for b in secret_bytes)
    total_bits = len(secret_bits)
    # Выделяем память под копию изображения и чтобы избежать проблем с типами
    stego = image.flatten().astype(int)
    max_capacity = stego.size * depth
    if total_bits > max_capacity:
        raise ValueError("Текст слишком длинный для внедрения!")
    # Записываем биты текста в младшие биты
    bit_idx = 0
    for i in range(len(stego)):
        for d in range(depth):
            if bit_idx < total_bits:
                # Очищаем нужный бит
                stego[i] &= ~(1 << d)
                # Вставляем бит секрета
                stego[i] |= (int(secret_bits[bit_idx]) << d)
                bit_idx += 1
            else:
                break
    # Переводим обратно в массив uint8 и исходную форму
    stego = np.array(stego, dtype=np.uint8).reshape(image.shape)
    return stego

def extract_text(image: np.ndarray, params: dict) -> str:
    """
    Извлекает встроенный текст из изображения (LSB).
    image — картинка, numpy-массив
    params — должен содержать 'depth' и 'length' (количество символов)
    Возвращает строку.
    """
    depth = params.get("depth", 1)
    length = params.get("length")  # сколько символов было внедрено
    if length is None:
        raise ValueError("Нужно указать 'length' в параметрах!")
    num_bits = length * 8
    stego = image.flatten()
    bits = []
    bit_idx = 0
    for i in range(len(stego)):
        for d in range(depth):
            if bit_idx < num_bits:
                bits.append((stego[i] >> d) & 1)  # забираем нужный младший бит
                bit_idx += 1
    # Собираем биты в байты, затем в строку
    secret_bytes = [int(''.join(str(bits[b*8 + i]) for i in range(8)), 2) for b in range(length)]
    return bytes(secret_bytes).decode("utf-8", errors="replace")
