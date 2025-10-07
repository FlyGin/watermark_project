import numpy as np
import cv2


def embed_image(image: np.ndarray, secret_img: np.ndarray, params: dict) -> np.ndarray:
    """
    Внедрение секретного изображения в исходное изображение методом DCT.
    
    Args:
        image: Исходное изображение-контейнер
        secret_img: Секретное изображение для встраивания
        params: Словарь параметров:
            - 'strength': коэффициент силы встраивания (по умолчанию 15)
            - 'block_size': размер блока для DCT (по умолчанию 8)
    
    Returns:
        Изображение с внедрённым секретным изображением
    """
    strength = params.get("strength", 15)
    block_size = params.get("block_size", 8)
    
    # Преобразуем секретное изображение в биты
    flat_secret = secret_img.flatten()
    secret_bits = ''.join(format(byte, '08b') for byte in flat_secret)
    total_bits = len(secret_bits)
    
    # Работаем с копией изображения
    stego = image.astype(np.float32)
    
    # Если цветное изображение, работаем с Y-каналом
    if len(stego.shape) == 3:
        stego_ycrcb = cv2.cvtColor(stego.astype(np.uint8), cv2.COLOR_BGR2YCrCb)
        y_channel = stego_ycrcb[:, :, 0].astype(np.float32)
    else:
        y_channel = stego.copy()
    
    h, w = y_channel.shape
    max_blocks = (h // block_size) * (w // block_size)
    
    if total_bits > max_blocks:
        raise ValueError(f"Секретное изображение слишком большое! Максимум {max_blocks} бит, требуется {total_bits}")
    
    bit_idx = 0
    
    # Встраиваем биты в DCT коэффициенты
    for i in range(0, h - block_size + 1, block_size):
        for j in range(0, w - block_size + 1, block_size):
            if bit_idx >= total_bits:
                break
            
            # Извлекаем блок
            block = y_channel[i:i+block_size, j:j+block_size]
            
            # DCT преобразование
            dct_block = cv2.dct(block)
            
            # Встраиваем бит в средне-частотный коэффициент
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
            
            # Обратное DCT
            idct_block = cv2.idct(dct_block)
            y_channel[i:i+block_size, j:j+block_size] = idct_block
            
            bit_idx += 1
        
        if bit_idx >= total_bits:
            break
    
    # Собираем изображение
    if len(stego.shape) == 3:
        stego_ycrcb[:, :, 0] = np.clip(y_channel, 0, 255).astype(np.uint8)
        stego = cv2.cvtColor(stego_ycrcb, cv2.COLOR_YCrCb2BGR)
    else:
        stego = np.clip(y_channel, 0, 255).astype(np.uint8)
    
    return stego


def extract_image(image: np.ndarray, params: dict) -> np.ndarray:
    """
    Извлечение секретного изображения из контейнера с DCT водяным знаком.
    
    Args:
        image: Изображение-контейнер с встроенным секретом
        params: Словарь параметров:
            - 'secret_shape': форма секретного изображения (tuple)
            - 'block_size': размер блока DCT (по умолчанию 8)
    
    Returns:
        Извлечённое секретное изображение
    """
    secret_shape = params.get("secret_shape")
    if secret_shape is None:
        raise ValueError("Необходимо указать 'secret_shape' в параметрах!")
    
    strength = params.get("strength", 15)
    block_size = params.get("block_size", 8)
    num_secret_pixels = np.prod(secret_shape)
    num_bits = num_secret_pixels * 8
    
    # Преобразуем изображение
    if len(image.shape) == 3:
        image_ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        y_channel = image_ycrcb[:, :, 0].astype(np.float32)
    else:
        y_channel = image.astype(np.float32)
    
    h, w = y_channel.shape
    bits = []
    bit_idx = 0
    
    # Извлекаем биты из DCT коэффициентов
    for i in range(0, h - block_size + 1, block_size):
        for j in range(0, w - block_size + 1, block_size):
            if bit_idx >= num_bits:
                break
            
            # Извлекаем блок
            block = y_channel[i:i+block_size, j:j+block_size]
            
            # DCT преобразование
            dct_block = cv2.dct(block)
            
            # Извлекаем бит из коэффициента
            # Декодируем через проверку остатка от деления
            coeff = dct_block[4, 4]
            quantized = round(coeff / strength)
            bit = 1 if (abs(quantized) % 2) == 1 else 0
            bits.append(bit)
            
            bit_idx += 1
        
        if bit_idx >= num_bits:
            break
    
    # Конвертируем биты обратно в байты
    secret_bytes = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_bits = bits[i:i+8]
            byte_value = int(''.join(map(str, byte_bits)), 2)
            secret_bytes.append(byte_value)
    
    # Восстанавливаем форму секретного изображения
    result = np.array(secret_bytes, dtype=np.uint8)
    
    # Обрезаем до нужного размера и восстанавливаем форму
    result = result[:num_secret_pixels].reshape(secret_shape)
    
    return result
