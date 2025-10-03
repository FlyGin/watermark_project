import numpy as np
from watermark.embedding import embed
from watermark.extraction import extract

def main():
    # Пример исходного изображения (256x256x3)
    test_image = np.zeros((256, 256, 3), dtype=np.uint8)

    # Текстовый секрет
    test_secret = "Hello, Stego!"

    params = {"depth": 1}

    # Внедрение LSB (вызывает фасад lsb.py, который делегирует в text.py)
    stego_image = embed(test_image, test_secret, params, method="lsb")
    print("Внедрение завершено. Размер стегоизображения:", stego_image.shape)

    # Для извлечения текстового секрета необходимо указать его длину
    params["length"] = len(test_secret)
    recovered_secret = extract(stego_image, params, method="lsb")
    print("Извлечённый секрет:", recovered_secret)

if __name__ == "__main__":
    main()
