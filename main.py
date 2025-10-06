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
        test_image = np.zeros((256, 256, 3), dtype=np.uint8)
        test_secret = "Hello, Stego!"
        params = {"depth": 1}
        stego_image = embed(test_image, test_secret, params, method="lsb")
        print("Внедрение завершено. Размер стегоизображения:", stego_image.shape)
        params["length"] = len(test_secret.encode("utf-8"))
        recovered_secret = extract(stego_image, params, method="lsb")
        print("Извлечённый секрет:", recovered_secret)

    def run_integration_test_menu():
        while True:
            print("\n--- Integration tests ---")
            print("1. Встроить текст в изображение (random demo)")
            print("2. Встроить изображение (lsb_image_demo)")
            print("0. Назад")
            choice = input("Ваш выбор: ")
            if choice == "1":
                from tests.integration_tests.text_demo import main_menu as main_menu_text_demo
                main_menu_text_demo()
            elif choice == "2":
                from tests.integration_tests.image_demo import run_demo as run_lsb_image_demo
                run_lsb_image_demo()
            elif choice == "0":
                return
            else:
                print("Ошибка ввода! Повторите выбор.")

    def run_unit_test_menu():
        while True:
            print("\n--- Unit tests ---")
            print("1. LSB Text")
            print("2. LSB Image")
            print("0. Назад")
            choice = input("Ваш выбор: ")
            if choice == "1":
                os.system("python -m unittest tests.unit_tests.lsb_tests.test_lsb_text")
            elif choice == "2":
                os.system("python -m unittest tests.unit_tests.lsb_tests.test_lsb_image")
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
