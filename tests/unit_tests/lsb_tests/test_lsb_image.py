import unittest
import numpy as np
from watermark.embedding import embed
from watermark.extraction import extract
import matplotlib.pyplot as plt


class TestLSBImage(unittest.TestCase):
    def test_lsb_image_embed_extract(self):
        # Исходная картинка
        cover = np.zeros((128, 128), dtype=np.uint8)
        # Секретная мини-картинка
        secret = np.random.randint(0, 255, (16, 16), dtype=np.uint8)
        params = {"depth": 1}
        # Внедряем картинку (SECRET SHAPE для извлечения!)
        stego = embed(cover, secret, params, method="lsb")
        params["secret_shape"] = secret.shape
        recovered = extract(stego, params, method="lsb")
        np.testing.assert_array_equal(secret, recovered)
        

if __name__ == "__main__":
    unittest.main()
