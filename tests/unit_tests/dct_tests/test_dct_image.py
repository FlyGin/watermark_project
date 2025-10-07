import unittest
import numpy as np
from watermark.embedding import embed
from watermark.extraction import extract


class TestDCTImage(unittest.TestCase):
    """
    Юнит-тесты для DCT алгоритма встраивания и извлечения изображений.
    """
    
    def test_dct_image_embed_extract_basic(self):
        """Базовый тест встраивания и извлечения изображения"""
        # Создаём контейнер (увеличим размер для DCT)
        cover = np.random.randint(50, 200, (256, 256), dtype=np.uint8)
        # Секретное изображение (маленькое)
        secret = np.random.randint(0, 255, (8, 8), dtype=np.uint8)
        params = {"strength": 15, "block_size": 8}
        
        # Внедряем изображение
        stego = embed(cover, secret, params, method="dct")
        
        # Извлекаем (нужно указать форму!)
        params["secret_shape"] = secret.shape
        recovered = extract(stego, params, method="dct")
        
        # Проверяем, что форма совпадает
        self.assertEqual(secret.shape, recovered.shape)
        
        # Проверяем схожесть (DCT не идеально восстанавливает, но должно быть близко)
        # Используем среднюю абсолютную ошибку
        mae = np.mean(np.abs(secret.astype(float) - recovered.astype(float)))
        self.assertLess(mae, 50, f"MAE слишком высокая: {mae}")
    
    def test_dct_image_color_secret(self):
        """Тест с цветным секретным изображением"""
        cover = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
        secret = np.random.randint(0, 255, (8, 8, 3), dtype=np.uint8)
        params = {"strength": 20, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        params["secret_shape"] = secret.shape
        recovered = extract(stego, params, method="dct")
        
        self.assertEqual(secret.shape, recovered.shape)
        
        mae = np.mean(np.abs(secret.astype(float) - recovered.astype(float)))
        self.assertLess(mae, 50, f"MAE для цветного изображения: {mae}")
    
    def test_dct_image_different_strengths(self):
        """Тест с различными значениями силы встраивания"""
        cover = np.random.randint(50, 200, (512, 512), dtype=np.uint8)
        secret = np.random.randint(0, 255, (8, 8), dtype=np.uint8)
        
        for strength in [10, 15, 25, 40]:
            with self.subTest(strength=strength):
                params = {"strength": strength, "block_size": 8}
                stego = embed(cover, secret, params, method="dct")
                
                params["secret_shape"] = secret.shape
                recovered = extract(stego, params, method="dct")
                
                self.assertEqual(secret.shape, recovered.shape)
    
    def test_dct_image_small_secret(self):
        """Тест с маленьким секретным изображением"""
        cover = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
        secret = np.random.randint(0, 255, (8, 8), dtype=np.uint8)
        params = {"strength": 15, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        params["secret_shape"] = secret.shape
        recovered = extract(stego, params, method="dct")
        
        self.assertEqual(secret.shape, recovered.shape)
    
    def test_dct_image_rectangular_secret(self):
        """Тест с прямоугольным секретным изображением"""
        cover = np.random.randint(50, 200, (512, 512), dtype=np.uint8)
        secret = np.random.randint(0, 255, (16, 8), dtype=np.uint8)
        params = {"strength": 20, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        params["secret_shape"] = secret.shape
        recovered = extract(stego, params, method="dct")
        
        self.assertEqual(secret.shape, recovered.shape)
    
    def test_dct_image_capacity_error(self):
        """Тест на ошибку при превышении ёмкости"""
        cover = np.random.randint(50, 200, (64, 64), dtype=np.uint8)
        # Слишком большой секрет
        secret = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        params = {"strength": 15, "block_size": 8}
        
        with self.assertRaises(ValueError):
            embed(cover, secret, params, method="dct")
    
    def test_dct_image_grayscale_to_color(self):
        """Тест встраивания ч/б секрета в цветное изображение"""
        cover = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
        secret = np.random.randint(0, 255, (16, 16), dtype=np.uint8)
        params = {"strength": 15, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        params["secret_shape"] = secret.shape
        recovered = extract(stego, params, method="dct")
        
        self.assertEqual(secret.shape, recovered.shape)
    
    def test_dct_image_binary_secret(self):
        """Тест с бинарным секретным изображением"""
        cover = np.random.randint(50, 200, (256, 256), dtype=np.uint8)
        secret = np.random.choice([0, 255], size=(8, 8)).astype(np.uint8)
        params = {"strength": 20, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        params["secret_shape"] = secret.shape
        recovered = extract(stego, params, method="dct")
        
        self.assertEqual(secret.shape, recovered.shape)
    
    def test_dct_image_single_pixel(self):
        """Тест с однопиксельным секретом"""
        cover = np.random.randint(50, 200, (128, 128), dtype=np.uint8)
        secret = np.array([[128]], dtype=np.uint8)
        params = {"strength": 15, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        params["secret_shape"] = secret.shape
        recovered = extract(stego, params, method="dct")
        
        self.assertEqual(secret.shape, recovered.shape)


if __name__ == "__main__":
    unittest.main()
