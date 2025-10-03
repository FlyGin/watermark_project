import unittest
import numpy as np
from watermark.embedding import embed
from watermark.extraction import extract

class TestLSBText(unittest.TestCase):
    def test_lsb_text_embed_extract(self):
        # Исходная картинка
        cover = np.zeros((128, 128, 3), dtype=np.uint8)
        secret = "Стеганография LSB работает!"
        params = {"depth": 1}
        # Внедряем строку
        stego = embed(cover, secret, params, method="lsb")
        # Извлекаем (нужно указать длину!)
        secret_bytes = secret.encode("utf-8")
        params["length"] = len(secret_bytes)
        recovered = extract(stego, params, method="lsb")
        recovered = recovered[:len(secret)]  # Если нужно обрезать по символам
        self.assertEqual(secret, recovered)

if __name__ == "__main__":
    unittest.main()
