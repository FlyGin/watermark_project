# gui/events.py
# ============================================================================
# ФАЙЛ ОБРАБОТКИ СОБЫТИЙ И ЛОГИКИ РАБОТЫ ПРОГРАММЫ
# ============================================================================
# Этот файл содержит всю логику работы GUI-приложения:
# - Обработчики нажатий на кнопки
# - Функции загрузки и обработки файлов
# - Алгоритмы встраивания и извлечения водяных знаков
# - Управление предпросмотром изображений
# - Обработка ошибок и вывод результатов
#
# Основной принцип: каждая кнопка в интерфейсе связана с функцией в этом файле
# через механизм сигналов и слотов PyQt5 (connect_events)
# ============================================================================

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image      # Библиотека для работы с изображениями
import numpy as np         # Библиотека для работы с массивами (изображения как массивы пикселей)
import os                  # Функции для работы с файловой системой
from watermark.embedding import embed      # Наши функции встраивания водяных знаков
from watermark.extraction import extract   # Наши функции извлечения водяных знаков

def connect_events(parent):
    """
    ========================================================================
    ПОДКЛЮЧЕНИЕ ОБРАБОТЧИКОВ СОБЫТИЙ
    ========================================================================
    Эта функция связывает кнопки интерфейса с функциями обработки.
    Когда пользователь нажимает кнопку, автоматически вызывается
    соответствующая функция.
    
    Принцип работы PyQt5:
    - widget.clicked.connect(function) - связывает нажатие с функцией
    - lambda - позволяет передать дополнительные аргументы в функцию
    ========================================================================
    """
    # Связываем кнопки с функциями обработки:
    parent.btn_load_cover.clicked.connect(lambda: load_cover_file(parent))
    parent.btn_load_wm.clicked.connect(lambda: load_wm_file(parent))
    parent.btn_embed.clicked.connect(lambda: embed_watermark(parent))
    parent.btn_extract.clicked.connect(lambda: extract_watermark(parent))
    parent.btn_save_result.clicked.connect(lambda: save_stego_result(parent))
    parent.btn_save_secret.clicked.connect(lambda: save_extracted_secret(parent))
    parent.btn_reset.clicked.connect(lambda: reset_gui(parent))

    # Обработчик клика по превью секретного изображения
    parent.secret_image_label.mousePressEvent = lambda event: on_secret_preview_clicked(parent, event)
    # Обработчик клика по превью восстановленного секрета
    parent.restored_image_label.mousePressEvent = lambda event: on_restored_secret_preview_clicked(parent, event)
import tempfile
def on_restored_secret_preview_clicked(parent, event):
    """
    Обработчик клика по QLabel превью восстановленного секрета.
    Если секрет — текст, сохраняет его во временный txt-файл и открывает.
    """
    secret = getattr(parent, "extracted_secret", None)
    secret_type = getattr(parent, "embedded_secret_type", None)
    if secret_type == "text" and secret:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
                tmp.write(secret)
                tmp_path = tmp.name
            import sys
            if sys.platform.startswith('win'):
                os.startfile(tmp_path)
            elif sys.platform.startswith('darwin'):
                import subprocess
                subprocess.call(['open', tmp_path])
            else:
                import subprocess
                subprocess.call(['xdg-open', tmp_path])
        except Exception as e:
            QMessageBox.warning(parent, "Ошибка", f"Не удалось открыть файл: {e}")

def on_secret_preview_clicked(parent, event):
    """
    Обработчик клика по QLabel превью секретного изображения.
    Если выбран секрет типа текст, показывает заглушку (например, QMessageBox).
    """
    import subprocess
    import sys
    secret_type = getattr(parent, "secret_type", None)
    wm_path = getattr(parent, "wm_path", None)
    if secret_type == "text" and wm_path:
        try:
            if sys.platform.startswith('win'):
                os.startfile(wm_path)
            elif sys.platform.startswith('darwin'):
                subprocess.call(['open', wm_path])
            else:
                subprocess.call(['xdg-open', wm_path])
        except Exception as e:
            QMessageBox.warning(parent, "Ошибка", f"Не удалось открыть файл: {e}")

def on_text_input_changed(parent, text):
    """
    ========================================================================
    ОБРАБОТЧИК ИЗМЕНЕНИЯ ТЕКСТА В ПОЛЕ ВВОДА СЕКРЕТА
    ========================================================================
    Эта функция вызывается каждый раз, когда пользователь изменяет текст
    в поле ввода секретного сообщения.
    
    Логика работы:
    - Если текст введен → показываем индикатор "Текст введен"
    - Если текст очищен → возвращаем состояние "Изображение не загружено"
    - При вводе текста автоматически очищается путь к файлу водяного знака
    ========================================================================
    """
    if text.strip():  # Если введен текст (не пустая строка)
        # Очищаем предпросмотр секретного изображения и показываем индикатор текста
        parent.secret_image_label.clear()
        parent.secret_image_label.setText("💬 Текст введен")
        parent.secret_image_label.setStyleSheet("border: 2px solid #FF9800; color: #FF9800;")  # Оранжевая рамка для введенного текста
        
        # Очищаем путь к файлу водяного знака, если есть
        if hasattr(parent, 'wm_path'):
            delattr(parent, 'wm_path')
    else:
        # Если текст очищен, возвращаем исходное состояние
        parent.secret_image_label.setText("Изображение не загружено")
        parent.secret_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")

def load_and_display_image(image_path, label_widget, max_size=(250, 200)):
    """
    ========================================================================
    ЗАГРУЗКА И ОТОБРАЖЕНИЕ ИЗОБРАЖЕНИЯ В ОКНЕ ПРЕДПРОСМОТРА
    ========================================================================
    Эта функция загружает изображение из файла и отображает его в указанном
    виджете QLabel с автоматическим масштабированием.
    
    Аргументы:
    - image_path: путь к файлу изображения
    - label_widget: виджет QLabel для отображения
    - max_size: максимальный размер (ширина, высота) в пикселях
    
    Возвращает:
    - True: если изображение успешно загружено
    - False: если произошла ошибка
    
    Особенности:
    - Автоматически конвертирует изображение в RGB формат
    - Сохраняет пропорции при масштабировании
    - Использует высококачественный алгоритм LANCZOS
    ========================================================================
    """
    try:
        # Загружаем изображение с помощью библиотеки PIL
        pil_image = Image.open(image_path)
        # Конвертируем в RGB если нужно (для совместимости)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        # Конвертируем PIL изображение в QPixmap для PyQt5
        import io
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(img_buffer.getvalue())
        label_widget.setPixmap(pixmap)
        label_widget.setStyleSheet("border: 2px solid #4CAF50;")  # Зеленая рамка для загруженного изображения
        return True
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return False

def load_cover_file(parent):
    """
    ========================================================================
    ЗАГРУЗКА ИСХОДНОГО ИЗОБРАЖЕНИЯ (КОНТЕЙНЕРА)
    ========================================================================
    Эта функция вызывается при нажатии кнопки "Загрузить исходное изображение".
    Открывает диалог выбора файла и загружает выбранное изображение.
    
    Что происходит:
    1. Открывается диалог выбора файла с фильтром изображений
    2. Выбранный путь сохраняется в parent.cover_path
    3. Загружается предпросмотр изображения
    4. Выводится сообщение о результате в область результатов
    ========================================================================
    """
    fname, _ = QFileDialog.getOpenFileName(parent, "Выберите исходный файл", "", "Images (*.png *.jpg *.bmp *.jpeg);;All Files (*)")
    if fname:  # Если пользователь выбрал файл (не нажал "Отмена")
        parent.cover_path = fname  # Сохраняем путь к файлу
        parent.result_text.append(f"Загружен исходный файл: {fname}")
        
        # Отображаем предпросмотр изображения
        if load_and_display_image(fname, parent.cover_image_label):
            parent.result_text.append("✅ Предпросмотр исходного изображения загружен")
        else:
            parent.result_text.append("⚠️ Не удалось загрузить предпросмотр исходного изображения")

def load_wm_file(parent):
    """
    ========================================================================
    ЗАГРУЗКА ФАЙЛА ВОДЯНОГО ЗНАКА (СЕКРЕТНЫХ ДАННЫХ)
    ========================================================================
    Эта функция вызывается при нажатии кнопки "Загрузить файл водяного знака".
    Поддерживает два типа файлов:
    - Изображения (PNG, JPG, BMP) - для встраивания изображения в изображение
    - Текстовые файлы (TXT) - для встраивания текста из файла
    
    Логика работы:
    1. Открывается диалог выбора файла
    2. Автоматически очищается поле ввода текста (исключает конфликт)
    3. Определяется тип файла по расширению
    4. Для изображений - загружается предпросмотр
    5. Для текстовых файлов - показывается специальная иконка
    ========================================================================
    """
    fname, _ = QFileDialog.getOpenFileName(parent, "Выберите файл водяного знака", "", "Images (*.png *.jpg *.bmp);;Text files (*.txt);;All Files (*)")
    if fname:
        parent.wm_path = fname
        parent.result_text.append(f"Загружен файл водяного знака: {fname}")
        ext = os.path.splitext(fname)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            if load_and_display_image(fname, parent.secret_image_label):
                parent.result_text.append("✅ Предпросмотр секретного изображения загружен")
            else:
                parent.result_text.append("⚠️ Не удалось загрузить предпросмотр секретного изображения")
            parent.secret_type = "image"
        elif ext == ".txt":
            parent.secret_image_label.clear()
            parent.secret_image_label.setText("📄 Текстовый файл для встраивания")
            parent.secret_image_label.setStyleSheet("border: 2px solid #2196F3; color: #2196F3;")
            parent.secret_type = "text"
            parent.result_text.append("📄 Загружен текстовый файл")
        else:
            parent.secret_image_label.clear()
            parent.secret_image_label.setText("❓ Неизвестный формат")
            parent.secret_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
            parent.secret_type = None

def embed_watermark(parent):
    """
    ========================================================================
    ВСТРАИВАНИЕ ВОДЯНОГО ЗНАКА В ИЗОБРАЖЕНИЕ
    ========================================================================
    Главная функция программы! Встраивает секретные данные в изображение
    с использованием выбранного алгоритма стеганографии.
    
    Поддерживаемые типы секретов:
    - Текст (введенный в поле или из текстового файла)
    - Изображение (из файла PNG/JPG/BMP)
    
    Этапы работы:
    1. Проверка входных данных (есть ли исходное изображение и секрет)
    2. Загрузка и подготовка данных
    3. Определение типа секрета и его параметров
    4. Вызов алгоритма встраивания
    5. Сохранение результата в файл
    6. Сохранение метаинформации для последующего извлечения
    ========================================================================
    """
    # ========================================================================
    # ЭТАП 1: ПОЛУЧЕНИЕ И ПРОВЕРКА ВХОДНЫХ ДАННЫХ
    # ========================================================================
    
    cover_path = getattr(parent, "cover_path", None)
    wm_path = getattr(parent, "wm_path", None)
    secret_type = getattr(parent, "secret_type", None)
    # Проверяем, выбрано ли исходное изображение
    if not cover_path:
        QMessageBox.warning(parent, "Ошибка", "Не выбран исходный файл.")
        return
    if not wm_path or not secret_type:
        QMessageBox.warning(parent, "Ошибка", "Не выбран водяной знак (файл или текст).")
        return
    try:
        # ====================================================================
        # ЭТАП 2: ЗАГРУЗКА И ПОДГОТОВКА ДАННЫХ
        # ====================================================================
        
        # Загружаем исходное изображение как массив пикселей
        cover = np.array(Image.open(cover_path))
        
        # Получаем параметры алгоритма из интерфейса
        depth = parent.spinbox_depth.value()  # Глубина встраивания (1-8 бит)
        params = {"depth": depth}

        # ====================================================================
        # ЭТАП 3: ОПРЕДЕЛЕНИЕ ТИПА СЕКРЕТА И ЕГО ОБРАБОТКА
        # ====================================================================
        
        if secret_type == "text":
            with open(wm_path, 'r', encoding='utf-8') as f:
                secret = f.read()
            parent.embedded_secret_type = "text"
            parent.embedded_secret_length = len(secret.encode("utf-8"))
            parent.embedded_depth = depth
        elif secret_type == "image":
            secret = np.array(Image.open(wm_path))
            parent.embedded_secret_type = "image"
            parent.embedded_secret_shape = secret.shape
            parent.embedded_depth = depth

        # ====================================================================
        # ЭТАП 4: ВСТРАИВАНИЕ СЕКРЕТА В ИЗОБРАЖЕНИЕ
        # ====================================================================
        
        # Вызываем алгоритм встраивания (из модуля watermark.embedding)
        result = embed(cover, secret, params, method="lsb")
        
        # ====================================================================
        # ЭТАП 5: СОХРАНЕНИЕ РЕЗУЛЬТАТА
        # ====================================================================
        
        # Сохраняем стего-изображение во временный путь, но не сохраняем автоматически
        parent.stego_result = result
        parent.result_text.append(f"✅ Встраивание успешно! Результат готов для предпросмотра и сохранения.")
        parent.btn_save_result.setEnabled(True)
        # Показываем превью стегоизображения (всегда изображение)
        img = Image.fromarray(result)
        import io
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        parent.stego_image_label.setPixmap(pixmap)
        parent.stego_image_label.setStyleSheet("border: 2px solid #4CAF50;")
        
    except Exception as exc:
        # Обработка ошибок (неправильный формат файла, нехватка места и т.д.)
        parent.result_text.append(f"❌ Ошибка встраивания: {exc}")
        

def extract_watermark(parent):
    """
    ========================================================================
    ИЗВЛЕЧЕНИЕ ВОДЯНОГО ЗНАКА ИЗ СТЕГО-ИЗОБРАЖЕНИЯ
    ========================================================================
    Эта функция извлекает секретные данные из стего-изображения, созданного
    функцией embed_watermark().
    
    Важно: для успешного извлечения нужна метаинформация о том, что было
    встроено (тип секрета, размер, глубина). Эта информация сохраняется
    автоматически при встраивании.
    
    Этапы работы:
    1. Проверка наличия стего-изображения и метаинформации
    2. Загрузка стего-изображения
    3. Подготовка параметров для извлечения
    4. Вызов алгоритма извлечения
    5. Отображение или сохранение результата
    ========================================================================
    """
    # ========================================================================
    # ЭТАП 1: ПОЛУЧЕНИЕ И ПРОВЕРКА ДАННЫХ ДЛЯ ИЗВЛЕЧЕНИЯ
    # ========================================================================
    
    # Ищем файл для извлечения: сначала stego_result.png, потом исходный файл
    stego_result = getattr(parent, "stego_result", None)
    secret_type = getattr(parent, "embedded_secret_type", None)
    if stego_result is None or not secret_type:
        QMessageBox.warning(parent, "Ошибка", "Нет стего-результата для извлечения.")
        return
    try:
        # ====================================================================
        # ЭТАП 2: ЗАГРУЗКА СТЕГО-ИЗОБРАЖЕНИЯ
        # ====================================================================
        stego_image = stego_result
        # ====================================================================
        # ЭТАП 3: ПОДГОТОВКА ПАРАМЕТРОВ ДЛЯ ИЗВЛЕЧЕНИЯ
        # ====================================================================
        depth = getattr(parent, "embedded_depth", parent.spinbox_depth.value())
        params = {"depth": depth}
        if secret_type == "text":
            params["length"] = getattr(parent, "embedded_secret_length", 10)
        elif secret_type == "image":
            params["secret_shape"] = getattr(parent, "embedded_secret_shape", (64, 64, 3))
        # ====================================================================
        # ЭТАП 4: ИЗВЛЕЧЕНИЕ СЕКРЕТНЫХ ДАННЫХ
        # ====================================================================
        extracted = extract(stego_image, params, method="lsb")
        # ====================================================================
        # ЭТАП 5: ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА
        # ====================================================================
        if isinstance(extracted, str):
            parent.extracted_secret = extracted
            parent.result_text.append(f"🔍 Извлечённый текст готов для предпросмотра и сохранения.")
            parent.restored_image_label.clear()
            parent.restored_image_label.setText("📄 Восстановленный текст")
            parent.restored_image_label.setStyleSheet("border: 2px solid #2196F3; color: #2196F3;")
        else:
            parent.extracted_secret = extracted
            parent.result_text.append(f"🔍 Восстановленное изображение готов для предпросмотра и сохранения.")
            img = Image.fromarray(extracted)
            import io
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())
            parent.restored_image_label.setPixmap(pixmap)
            parent.restored_image_label.setStyleSheet("border: 2px solid #4CAF50;")
        parent.btn_save_secret.setEnabled(True)
    except Exception as exc:
        parent.result_text.append(f"❌ Ошибка извлечения: {exc}")

def reset_gui(parent):
    """
    ========================================================================
    СБРОС ИНТЕРФЕЙСА К ИСХОДНОМУ СОСТОЯНИЮ
    ========================================================================
    Эта функция вызывается при нажатии кнопки "Сбросить" и очищает все
    поля, настройки и состояние программы.
    
    Что очищается:
    - Поле ввода текста водяного знака
    - Область вывода результатов
    - Настройка глубины возвращается к 1 биту
    - Окна предпросмотра изображений
    - Все сохранённые пути к файлам и метаинформация
    
    Это полезно для начала новой операции "с чистого листа".
    ========================================================================
    """
    # ====================================================================
    # ОЧИСТКА ПОЛЕЙ ВВОДА И НАСТРОЕК
    # ====================================================================
    
    parent.result_text.clear()
    parent.spinbox_depth.setValue(1)
    parent.cover_image_label.clear()
    parent.cover_image_label.setText("Изображение не загружено")
    parent.cover_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    parent.secret_image_label.clear()
    parent.secret_image_label.setText("Файл не загружен")
    parent.secret_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    parent.stego_image_label.clear()
    parent.stego_image_label.setText("Нет результата")
    parent.stego_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    parent.restored_image_label.clear()
    parent.restored_image_label.setText("Нет результата")
    parent.restored_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    parent.btn_save_result.setEnabled(False)
    parent.btn_save_secret.setEnabled(False)
    attributes_to_clear = [
        'cover_path', 'wm_path', 'stego_result', 'embedded_secret_type', 'embedded_secret_length', 'embedded_secret_shape', 'embedded_depth', 'secret_type', 'extracted_secret'
    ]
    for attr in attributes_to_clear:
        if hasattr(parent, attr):
            delattr(parent, attr)

# ========== Новый обработчик: сохранить стего-результат ==========
def save_stego_result(parent):
    result = getattr(parent, 'stego_result', None)
    if result is None:
        QMessageBox.warning(parent, "Ошибка", "Нет результата для сохранения.")
        return
    fname, _ = QFileDialog.getSaveFileName(parent, "Сохранить стего-изображение", "stego_result.png", "Images (*.png *.jpg *.bmp)")
    if fname:
        Image.fromarray(result).save(fname)
        parent.result_text.append(f"💾 Стего-изображение сохранено: {fname}")

# ========== Новый обработчик: сохранить восстановленный секрет ==========
def save_extracted_secret(parent):
    secret = getattr(parent, 'extracted_secret', None)
    secret_type = getattr(parent, 'embedded_secret_type', None)
    if secret is None or secret_type is None:
        QMessageBox.warning(parent, "Ошибка", "Нет восстановленного секрета для сохранения.")
        return
    if secret_type == "image":
        fname, _ = QFileDialog.getSaveFileName(parent, "Сохранить восстановленное изображение", "extracted_secret.png", "Images (*.png *.jpg *.bmp)")
        if fname:
            Image.fromarray(secret).save(fname)
            parent.result_text.append(f"💾 Восстановленное изображение сохранено: {fname}")
    elif secret_type == "text":
        fname, _ = QFileDialog.getSaveFileName(parent, "Сохранить восстановленный текст", "extracted_secret.txt", "Text files (*.txt)")
        if fname:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(secret)
            parent.result_text.append(f"💾 Восстановленный текст сохранён: {fname}")
