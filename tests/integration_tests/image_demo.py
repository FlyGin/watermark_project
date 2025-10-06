import numpy as np
from PIL import Image
import os
from watermark.embedding import embed
from watermark.extraction import extract

def run_demo():
    """Демо встраивания изображения в изображение с помощью LSB"""
    print("\n--- LSB Image Demo ---")
    
    # Создаем тестовое исходное изображение
    cover_image = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
    print(f"Создано исходное изображение размером: {cover_image.shape}")
    
    # Создаем тестовое секретное изображение (меньшего размера)
    secret_image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    print(f"Создано секретное изображение размером: {secret_image.shape}")
    
    # Параметры встраивания
    params = {
        "depth": 2,
        "secret_shape": secret_image.shape
    }
    
    try:
        # Встраивание
        print("Выполняется встраивание...")
        stego_image = embed(cover_image, secret_image, params, method="lsb")
        print("✅ Встраивание успешно завершено!")
        
        # Извлечение
        print("Выполняется извлечение...")
        extracted_image = extract(stego_image, params, method="lsb")
        print("✅ Извлечение успешно завершено!")
        
        # Проверка качества
        if isinstance(extracted_image, np.ndarray) and extracted_image.shape == secret_image.shape:
            # Вычисляем MSE (Mean Squared Error)
            mse = np.mean((secret_image - extracted_image) ** 2)
            print(f"MSE между оригиналом и извлеченным: {mse:.2f}")
            
            if mse < 10:
                print("🎉 Отличное качество восстановления!")
            elif mse < 50:
                print("✅ Хорошее качество восстановления")
            else:
                print("⚠️ Качество восстановления требует улучшения")
        else:
            print("❌ Ошибка: извлеченное изображение имеет неправильный формат")
            
    except Exception as e:
        print(f"❌ Ошибка в демо: {e}")
    
    print("Демо завершено.\n")

if __name__ == "__main__":
    run_demo()
