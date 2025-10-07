import sys

def run_cli():
    import os
    import datetime
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image
    from watermark.embedding import embed
    from watermark.extraction import extract

    def run_basic_demo():
        print("\n--- Базовый пример встраивания текста ---")
        print("Выберите алгоритм:")
        print("1. LSB (Least Significant Bit)")
        print("2. DCT (Discrete Cosine Transform)")
        print("0. Назад")
        algo_choice = input("Ваш выбор: ")
        
        if algo_choice == "0":
            return
        elif algo_choice == "1":
            method = "lsb"
            test_image = np.zeros((256, 256, 3), dtype=np.uint8)
            test_secret = "Hello, Stego!"
            params = {"depth": 1}
            print(f"\nВстраивание текста методом LSB...")
            stego_image = embed(test_image, test_secret, params, method=method)
            print("Внедрение завершено. Размер стегоизображения:", stego_image.shape)
            params["length"] = len(test_secret.encode("utf-8"))
            recovered_secret = extract(stego_image, params, method=method)
            print("Извлечённый секрет:", recovered_secret)
        elif algo_choice == "2":
            method = "dct"
            test_image = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
            test_secret = "Hello, DCT Watermark!"
            params = {"strength": 10, "block_size": 8}
            print(f"\nВстраивание текста методом DCT...")
            stego_image = embed(test_image, test_secret, params, method=method)
            print("Внедрение завершено. Размер стегоизображения:", stego_image.shape)
            params["length"] = len(test_secret.encode("utf-8"))
            recovered_secret = extract(stego_image, params, method=method)
            print("Извлечённый секрет:", recovered_secret)
        else:
            print("Неверный выбор!")

    def run_dct_text_demo():
        """Демонстрация встраивания текста с помощью DCT алгоритма"""
        print("\n=== DCT: Демонстрация встраивания текста ===")
        
        # Создаём тестовое изображение
        cover = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
        secret_text = "Это секретное сообщение, встроенное с помощью DCT алгоритма! 🔒"
        
        print(f"Исходное изображение: {cover.shape}")
        print(f"Секретный текст: '{secret_text}'")
        print(f"Длина текста: {len(secret_text)} символов ({len(secret_text.encode('utf-8'))} байт)")
        
        # Параметры встраивания
        strength = int(input("Введите силу встраивания (рекомендуется 10-20): ") or "15")
        params = {"strength": strength, "block_size": 8}
        
        print("\nВстраивание...")
        stego = embed(cover, secret_text, params, method="dct")
        print("✓ Встраивание завершено")
        
        # Извлечение
        print("\nИзвлечение...")
        params["length"] = len(secret_text.encode("utf-8"))
        recovered = extract(stego, params, method="dct")
        recovered = recovered[:len(secret_text)]
        print(f"✓ Извлечённый текст: '{recovered}'")
        
        # Проверка
        if secret_text == recovered:
            print("\n✅ УСПЕХ! Текст восстановлен точно.")
        else:
            print("\n⚠️ ВНИМАНИЕ! Текст восстановлен с искажениями.")
            print(f"Совпадение: {sum(a == b for a, b in zip(secret_text, recovered))}/{len(secret_text)} символов")
        
        # Визуализация
        show_visual = input("\nПоказать визуализацию? (y/n): ")
        if show_visual.lower() == 'y':
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            axes[0].imshow(cover)
            axes[0].set_title("Исходное изображение")
            axes[0].axis('off')
            
            axes[1].imshow(stego)
            axes[1].set_title(f"Стегоизображение (DCT, strength={strength})")
            axes[1].axis('off')
            
            diff = np.abs(cover.astype(int) - stego.astype(int))
            axes[2].imshow(diff, cmap='hot')
            axes[2].set_title(f"Разница (макс={diff.max()})")
            axes[2].axis('off')
            
            plt.tight_layout()
            plt.show()
    
    def run_dct_image_demo():
        """Демонстрация встраивания изображения с помощью DCT алгоритма"""
        print("\n=== DCT: Демонстрация встраивания изображения ===")
        
        # Создаём изображения
        cover = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
        secret = np.random.randint(0, 255, (16, 16), dtype=np.uint8)
        
        print(f"Контейнер: {cover.shape}")
        print(f"Секретное изображение: {secret.shape}")
        print(f"Ёмкость: {(cover.shape[0]//8) * (cover.shape[1]//8)} бит")
        print(f"Требуется: {secret.size * 8} бит")
        
        # Параметры
        strength = int(input("Введите силу встраивания (рекомендуется 15-25): ") or "20")
        params = {"strength": strength, "block_size": 8}
        
        print("\nВстраивание...")
        stego = embed(cover, secret, params, method="dct")
        print("✓ Встраивание завершено")
        
        # Извлечение
        print("\nИзвлечение...")
        params["secret_shape"] = secret.shape
        recovered = extract(stego, params, method="dct")
        print(f"✓ Извлечённое изображение: {recovered.shape}")
        
        # Метрики качества
        mae = np.mean(np.abs(secret.astype(float) - recovered.astype(float)))
        mse = np.mean((secret.astype(float) - recovered.astype(float)) ** 2)
        psnr = 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')
        
        print(f"\n📊 Метрики восстановления:")
        print(f"  MAE (средняя абсолютная ошибка): {mae:.2f}")
        print(f"  MSE (среднеквадратичная ошибка): {mse:.2f}")
        print(f"  PSNR: {psnr:.2f} dB")
        
        if mae < 30:
            print("  ✅ Отличное качество восстановления!")
        elif mae < 50:
            print("  ⚠️ Удовлетворительное качество")
        else:
            print("  ❌ Низкое качество восстановления")
        
        # Визуализация
        show_visual = input("\nПоказать визуализацию? (y/n): ")
        if show_visual.lower() == 'y':
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            
            axes[0, 0].imshow(cover)
            axes[0, 0].set_title("Контейнер")
            axes[0, 0].axis('off')
            
            axes[0, 1].imshow(stego)
            axes[0, 1].set_title(f"Стегоизображение (strength={strength})")
            axes[0, 1].axis('off')
            
            diff_container = np.abs(cover.astype(int) - stego.astype(int))
            axes[0, 2].imshow(diff_container, cmap='hot')
            axes[0, 2].set_title(f"Разница контейнеров (макс={diff_container.max()})")
            axes[0, 2].axis('off')
            
            axes[1, 0].imshow(secret, cmap='gray')
            axes[1, 0].set_title("Исходное секретное изображение")
            axes[1, 0].axis('off')
            
            axes[1, 1].imshow(recovered, cmap='gray')
            axes[1, 1].set_title(f"Восстановленное (MAE={mae:.2f})")
            axes[1, 1].axis('off')
            
            diff_secret = np.abs(secret.astype(int) - recovered.astype(int))
            axes[1, 2].imshow(diff_secret, cmap='hot')
            axes[1, 2].set_title(f"Разница секретов (макс={diff_secret.max()})")
            axes[1, 2].axis('off')
            
            plt.tight_layout()
            plt.show()


    def run_integration_test_menu():
        while True:
            print("\n--- Integration tests ---")
            print("1. LSB: Встроить текст в изображение")
            print("2. LSB: Встроить изображение")
            print("3. DCT: Демо встраивания текста")
            print("4. DCT: Демо встраивания изображения")
            print("0. Назад")
            choice = input("Ваш выбор: ")
            if choice == "1":
                from tests.integration_tests.text_demo import main_menu as main_menu_text_demo
                main_menu_text_demo()
            elif choice == "2":
                from tests.integration_tests.image_demo import run_demo as run_lsb_image_demo
                run_lsb_image_demo()
            elif choice == "3":
                run_dct_text_demo()
            elif choice == "4":
                run_dct_image_demo()
            elif choice == "0":
                return
            else:
                print("Ошибка ввода! Повторите выбор.")

    def run_unit_test_menu():
        while True:
            print("\n--- Unit tests ---")
            print("1. LSB Text")
            print("2. LSB Image")
            print("3. DCT Text")
            print("4. DCT Image")
            print("5. Все LSB тесты")
            print("6. Все DCT тесты")
            print("7. Все Unit тесты")
            print("0. Назад")
            choice = input("Ваш выбор: ")
            if choice == "1":
                os.system("python -m unittest tests.unit_tests.lsb_tests.test_lsb_text")
            elif choice == "2":
                os.system("python -m unittest tests.unit_tests.lsb_tests.test_lsb_image")
            elif choice == "3":
                os.system("python -m unittest tests.unit_tests.dct_tests.test_dct_text")
            elif choice == "4":
                os.system("python -m unittest tests.unit_tests.dct_tests.test_dct_image")
            elif choice == "5":
                os.system("python -m unittest discover -s tests.unit_tests.lsb_tests")
            elif choice == "6":
                os.system("python -m unittest discover -s tests.unit_tests.dct_tests")
            elif choice == "7":
                os.system("python -m unittest discover -s tests.unit_tests")
            elif choice == "0":
                return
            else:
                print("Ошибка ввода! Повторите выбор.")

    def tests_menu():
        while True:
            print("\n--- Тесты ---")
            print("1. Integration tests")
            print("2. Unit tests")
            print("0. Назад")
            choice = input("Ваш выбор: ")
            if choice == "1":
                run_integration_test_menu()
            elif choice == "2":
                run_unit_test_menu()
            elif choice == "0":
                return
            else:
                print("Ошибка! Повторите выбор.")

    def main_menu():
        while True:
            print("\n--- Главное меню ---")
            print("1. Базовый пример")
            print("2. Тесты")
            print("0. Выход")
            choice = input("Ваш выбор: ")
            if choice == "1":
                run_basic_demo()
            elif choice == "2":
                tests_menu()
            elif choice == "0":
                sys.exit(0)
            else:
                print("Ошибка! Повторите выбор.")

    main_menu()

def run_gui():
    from gui.window import run
    run()

if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_gui()
