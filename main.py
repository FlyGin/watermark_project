import numpy as np
from watermark.embedding import embed
from watermark.extraction import extract

def main():
    # Example date
    test_image = np.zeros((256, 256, 3), dtype=np.uint8)   # Placeholder for an actual image
    test_secret = "Hello, Stego!"                                # Пример секрета
    params = {"depth": 1}     

    # Внедрение (здесь 'lsb' — название метода, может быть любым из реализованных)
    stego_image = embed(test_image, test_secret, params, method="lsb")
    print("Внедрение завершено. Размер стегоизображения:", stego_image.shape)

    # Извлечение
    recovered_secret = extract(stego_image, params, method="lsb")
    print("Извлечённый секрет:", recovered_secret)

if __name__ == "__main__":
    main()