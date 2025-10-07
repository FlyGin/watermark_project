import numpy as np
import cv2


def embed_text(image: np.ndarray, secret_text: str, params: dict) -> np.ndarray:
    """
    Внедрение текстовой строки в изображение методом DCT.
    
    Args:
        image: Исходное изображение (numpy массив)
        secret_text: Строка для встраивания
        params: Словарь параметров:
            - 'strength': коэффициент силы встраивания (по умолчанию 10)
            - 'block_size': размер блока для DCT (по умолчанию 8)
    
    Returns:
        Изображение с внедрённым текстом
    """
    strength = params.get("strength", 10)
    block_size = params.get("block_size", 8)
    
    # Преобразуем текст в биты
    secret_bytes = secret_text.encode("utf-8")
    secret_bits = ''.join(format(b, '08b') for b in secret_bytes)
    total_bits = len(secret_bits)
    
    # Работаем с копией изображения в формате float
    stego = image.astype(np.float32)
    
    # Если изображение цветное, работаем только с Y-каналом (YCrCb)
    if len(stego.shape) == 3:
        stego_ycrcb = cv2.cvtColor(stego.astype(np.uint8), cv2.COLOR_BGR2YCrCb)
        y_channel = stego_ycrcb[:, :, 0].astype(np.float32)
    else:
        y_channel = stego.copy()
    
    h, w = y_channel.shape
    max_blocks = (h // block_size) * (w // block_size)
    
    if total_bits > max_blocks:
        raise ValueError(f"Текст слишком длинный! Максимум {max_blocks} бит, требуется {total_bits}")
    
    bit_idx = 0
    
    # Проходим по блокам изображения
    for i in range(0, h - block_size + 1, block_size):
        for j in range(0, w - block_size + 1, block_size):
            if bit_idx >= total_bits:
                break
            
            # Извлекаем блок
            block = y_channel[i:i+block_size, j:j+block_size]
            
            # Применяем DCT
            dct_block = cv2.dct(block)
            
            # Встраиваем бит в средний коэффициент DCT (например, [4, 4])
            # Используем простую модуляцию на основе знака
            bit_value = int(secret_bits[bit_idx])
            coeff = dct_block[4, 4]
            
            # Квантуем с использованием strength
            quantized = round(coeff / strength)
            
            # Встраиваем бит через модуляцию 2
            if bit_value == 1:
                if quantized % 2 == 0:
                    quantized += 1
            else:  # bit_value == 0
                if quantized % 2 != 0:
                    quantized += 1
            
            dct_block[4, 4] = quantized * strength
            
            # Обратное DCT преобразование
            idct_block = cv2.idct(dct_block)
            y_channel[i:i+block_size, j:j+block_size] = idct_block
            
            bit_idx += 1
        
        if bit_idx >= total_bits:
            break
    
    # Собираем изображение обратно
    if len(stego.shape) == 3:
        stego_ycrcb[:, :, 0] = np.clip(y_channel, 0, 255).astype(np.uint8)
        stego = cv2.cvtColor(stego_ycrcb, cv2.COLOR_YCrCb2BGR)
    else:
        stego = np.clip(y_channel, 0, 255).astype(np.uint8)
    
    return stego


def extract_text(image: np.ndarray, params: dict) -> str:
    """
    Извлечение текста из изображения с DCT водяным знаком.
    
    Args:
        image: Изображение с встроенным текстом
        params: Словарь параметров:
            - 'length': количество символов для извлечения
            - 'block_size': размер блока DCT (по умолчанию 8)
    
    Returns:
        Извлечённая текстовая строка
    """
    length = params.get("length")
    if length is None:
        raise ValueError("Необходимо указать 'length' в параметрах!")
    
    strength = params.get("strength", 10)
    block_size = params.get("block_size", 8)
    num_bits = length * 8
    
    # Преобразуем изображение
    if len(image.shape) == 3:
        image_ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        y_channel = image_ycrcb[:, :, 0].astype(np.float32)
    else:
        y_channel = image.astype(np.float32)
    
    h, w = y_channel.shape
    bits = []
    bit_idx = 0
    
    # Проходим по блокам
    for i in range(0, h - block_size + 1, block_size):
        for j in range(0, w - block_size + 1, block_size):
            if bit_idx >= num_bits:
                break
            
            # Извлекаем блок
            block = y_channel[i:i+block_size, j:j+block_size]
            
            # Применяем DCT
            dct_block = cv2.dct(block)
            
            # Извлекаем бит из коэффициента [4, 4]
            # Декодируем через проверку остатка от деления
            coeff = dct_block[4, 4]
            quantized = round(coeff / strength)
            bit = 1 if (abs(quantized) % 2) == 1 else 0
            bits.append(bit)
            
            bit_idx += 1
        
        if bit_idx >= num_bits:
            break
    
    # Конвертируем биты в байты и затем в строку
    secret_bytes = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_bits = bits[i:i+8]
            byte_value = int(''.join(map(str, byte_bits)), 2)
            secret_bytes.append(byte_value)
    
    return bytes(secret_bytes).decode("utf-8", errors="replace")
