import unittest
import numpy as np
from watermark.embedding import embed
from watermark.extraction import extract


class TestDCTText(unittest.TestCase):
    """
    Юнит-тесты для DCT алгоритма встраивания и извлечения текста.
    """
    
    def test_dct_text_embed_extract_basic(self):
        """Базовый тест встраивания и извлечения текста"""
        # Создаём исходное изображение
        cover = np.random.randint(50, 200, (128, 128, 3), dtype=np.uint8)
        secret = "DCT watermark test!"
        params = {"strength": 10, "block_size": 8}
        
        # Внедряем текст
        stego = embed(cover, secret, params, method="dct")
        
        # Извлекаем текст (нужно указать длину!)
        secret_bytes = secret.encode("utf-8")
        params["length"] = len(secret_bytes)
        recovered = extract(stego, params, method="dct")
        
        # Обрезаем до нужной длины
        recovered = recovered[:len(secret)]
        
        self.assertEqual(secret, recovered)
    
    def test_dct_text_different_strengths(self):
        """Тест с различными значениями силы встраивания"""
        cover = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
        secret = "Test different strength"
        
        for strength in [10, 15, 20, 30]:
            with self.subTest(strength=strength):
                params = {"strength": strength, "block_size": 8}
                stego = embed(cover, secret, params, method="dct")
                
                secret_bytes = secret.encode("utf-8")
                params["length"] = len(secret_bytes)
                recovered = extract(stego, params, method="dct")
                recovered = recovered[:len(secret)]
                
                self.assertEqual(secret, recovered)
    
    def test_dct_text_grayscale_image(self):
        """Тест с чёрно-белым изображением"""
        cover = np.random.randint(50, 200, (128, 128), dtype=np.uint8)
        secret = "Grayscale DCT test"
        params = {"strength": 15, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        secret_bytes = secret.encode("utf-8")
        params["length"] = len(secret_bytes)
        recovered = extract(stego, params, method="dct")
        recovered = recovered[:len(secret)]
        
        self.assertEqual(secret, recovered)
    
    def test_dct_text_cyrillic(self):
        """Тест с кириллицей"""
        cover = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
        secret = "Проверка кириллицы!"
        params = {"strength": 15, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        secret_bytes = secret.encode("utf-8")
        params["length"] = len(secret_bytes)
        recovered = extract(stego, params, method="dct")
        recovered = recovered[:len(secret)]
        
        self.assertEqual(secret, recovered)
    
    def test_dct_text_long_message(self):
        """Тест с длинным сообщением"""
        cover = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
        secret = "This is a longer message to test DCT watermarking with multiple blocks. " * 3
        params = {"strength": 10, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        secret_bytes = secret.encode("utf-8")
        params["length"] = len(secret_bytes)
        recovered = extract(stego, params, method="dct")
        recovered = recovered[:len(secret)]
        
        self.assertEqual(secret, recovered)
    
    def test_dct_text_capacity_error(self):
        """Тест на ошибку при превышении ёмкости"""
        cover = np.random.randint(50, 200, (64, 64, 3), dtype=np.uint8)
        # Слишком длинный текст для маленького изображения
        secret = "A" * 10000
        params = {"strength": 10, "block_size": 8}
        
        with self.assertRaises(ValueError):
            embed(cover, secret, params, method="dct")
    
    def test_dct_text_empty_string(self):
        """Тест с пустой строкой"""
        cover = np.random.randint(50, 200, (128, 128, 3), dtype=np.uint8)
        secret = ""
        params = {"strength": 10, "block_size": 8}
        
        stego = embed(cover, secret, params, method="dct")
        
        params["length"] = 0
        recovered = extract(stego, params, method="dct")
        
        self.assertEqual(secret, recovered)


if __name__ == "__main__":
    unittest.main()
