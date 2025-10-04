import os
import random
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import datetime
import sys

from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim

from watermark.embedding import embed
from watermark.extraction import extract

def run_demo(typeOfAlgorithm):
    """
    Демонстрация стеганографии с текстом.
    Выбирается случайное изображение и случайная фраза из файла.
    Фраза внедряется в изображение, затем извлекается обратно.
    Результаты сохраняются, визуализируются и анализируются.
    """

    # Выбор случайного изображения
    image_dir = "tests/test_data/images_source"
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))]
    cover_filename = random.choice(image_files)
    cover_path = os.path.join(image_dir, cover_filename)
    print("Выбранное изображение:", cover_filename)
    cover_img = np.array(Image.open(cover_path).convert("RGB"))

    # Выбор случайной фразы
    phrases_path = "tests/test_data/strings/simple_phrases.txt"
    with open(phrases_path, encoding="utf-8") as f:
        phrases = [line.strip() for line in f if line.strip()]
    secret_text = random.choice(phrases)
    print("Выбрана фраза:", secret_text)
    secret_bytes = secret_text.encode("utf-8")

    params = {"depth": 1}
    # Внедрение
    stego_img = embed(cover_img, secret_text, params, method=typeOfAlgorithm)

    # Извлечение
    params["length"] = len(secret_bytes)
    extracted_text = extract(stego_img, params, method=typeOfAlgorithm)
    print("Извлечённый текст:", extracted_text)

    # ---- МЕТРИКИ ----
    psnr_value = psnr(cover_img, stego_img)
    ssim_value = ssim(cover_img, stego_img, channel_axis=-1)
    match_text = (secret_text == extracted_text)
    overlap = sum(a == b for a, b in zip(secret_text, extracted_text))
    frac = overlap / max(len(secret_text), len(extracted_text)) if max(len(secret_text), len(extracted_text)) > 0 else 1.0

    print("\n--- Метрики качества ---")
    print(f"PSNR (дБ):        {psnr_value:.2f}")
    print(f"SSIM:             {ssim_value:.4f}")
    print(f"Тексты совпадают: {'Да' if match_text else 'Нет'}")
    print(f"Доля совпадения:  {frac:.2f}")

    # ---- СОХРАНЕНИЕ ----
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = f"tests/integration_tests/{typeOfAlgorithm}_tests/results/text/result_{now}"
    os.makedirs(result_dir, exist_ok=True)

    # Визуализация 4 панели
    fig = plt.figure(figsize=(14, 5))

    ax1 = fig.add_subplot(1, 4, 1)
    ax1.imshow(cover_img)
    ax1.set_title("Исходное изображение")
    ax1.axis("off")

    ax2 = fig.add_subplot(1, 4, 2)
    ax2.text(0.5, 0.5, secret_text, ha='center', va='center', fontsize=13, wrap=True)
    ax2.set_facecolor('whitesmoke')
    ax2.set_title("Секретная фраза")
    ax2.axis("off")

    ax3 = fig.add_subplot(1, 4, 3)
    ax3.imshow(stego_img)
    ax3.set_title("Стего изображение")
    ax3.axis("off")

    ax4 = fig.add_subplot(1, 4, 4)
    ax4.text(0.5, 0.5, extracted_text, ha='center', va='center', fontsize=13, wrap=True)
    ax4.set_facecolor('whitesmoke')
    ax4.set_title("Восстановленная фраза")
    ax4.axis("off")

    plt.tight_layout()
    plt.show()

    # Сохраняем общую визуализацию!
    result_img_path = os.path.join(result_dir, f"visual_result_{now}.png")
    fig.savefig(result_img_path, bbox_inches='tight')
    print(f"Общий результат сохранён: {result_img_path}")

    # Сохраняем метрики в текстовый файл
    metrics_path = os.path.join(result_dir, "metrics.txt")
    with open(metrics_path, "w", encoding="utf-8") as f:
        f.write(f"Исходное изображение: {cover_filename}\n")
        f.write(f"Секретная фраза: {secret_text}\n")
        f.write(f"Восстановленная фраза: {extracted_text}\n")
        f.write(f"PSNR (дБ): {psnr_value:.2f}\n")
        f.write(f"SSIM: {ssim_value:.4f}\n")
        f.write(f"Доля совпадения: {frac:.2f}\n")
        f.write(f"Тексты совпадают: {'Да' if match_text else 'Нет'}\n")
    print(f"Метрики сохранены: {metrics_path}")

    # Завершить выполнение
    sys.exit(0)

def lsb_text_demo():
    run_demo("lsb")

def main_menu():
    while True:
        print("\n--- Главный интеграционный тест ---")
        print("1. Встраивание текста методом LSB (lsb_text)")
        # Здесь позже будет, например:
        # print("2. Встраивание текста методом DCT (dct_text)")
        print("0. Выход")
        choice = input("Ваш выбор: ")
        if choice == "1":
            lsb_text_demo()
        # elif choice == "2":
        #     dct_text_demo()
        elif choice == "0":
            break
        else:
            print("Ошибка! Повторите ввод.")

if __name__ == "__main__":
    main_menu()
