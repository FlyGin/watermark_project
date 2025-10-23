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

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton, QLabel, QTabWidget, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image      # Библиотека для работы с изображениями
import numpy as np         # Библиотека для работы с массивами (изображения как массивы пикселей)
import cv2                 # Библиотека OpenCV для обработки изображений
import os                  # Функции для работы с файловой системой
from watermark.embedding import embed      # Наши функции встраивания водяных знаков
from watermark.extraction import extract   # Наши функции извлечения водяных знаков
from utils.image_metrics import calculate_image_metrics, format_metrics as format_image_metrics
from utils.text_metrics import calculate_text_metrics, format_metrics as format_text_metrics

# ============================================================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: КРАТКОЕ ОПИСАНИЕ КАЧЕСТВА
# ============================================================================

def get_quality_description(metrics):
    """
    Возвращает краткое описание качества на основе метрик.
    Используется для компактного отображения в главном окне.
    
    Для изображений: оценка по PSNR и SSIM
    Для текста: оценка по accuracy и similarity
    """
    if 'psnr' in metrics:  # Метрики изображения
        psnr = metrics['psnr']
        ssim = metrics['ssim']
        
        if psnr == float('inf'):
            return "✅ Отлично (идентичны, PSNR=∞)"
        elif psnr >= 40:
            return f"✅ Отлично (PSNR={psnr:.2f} дБ, SSIM={ssim:.4f})"
        elif psnr >= 30:
            return f"✅ Хорошо (PSNR={psnr:.2f} дБ, SSIM={ssim:.4f})"
        elif psnr >= 20:
            return f"⚠️ Удовлетворительно (PSNR={psnr:.2f} дБ, SSIM={ssim:.4f})"
        else:
            return f"❌ Низкое (PSNR={psnr:.2f} дБ, SSIM={ssim:.4f})"
    
    elif 'accuracy' in metrics:  # Метрики текста
        accuracy = metrics['accuracy']
        # Используем правильный ключ из calculate_text_metrics()
        similarity = metrics.get('similarity_ratio', metrics.get('similarity', 0)) * 100
        
        if accuracy >= 99.9:
            return f"✅ Отлично (Точность={accuracy:.2f}%, Схожесть={similarity:.2f}%)"
        elif accuracy >= 95:
            return f"✅ Хорошо (Точность={accuracy:.2f}%, Схожесть={similarity:.2f}%)"
        elif accuracy >= 80:
            return f"⚠️ Удовлетворительно (Точность={accuracy:.2f}%, Схожесть={similarity:.2f}%)"
        else:
            return f"❌ Низкое (Точность={accuracy:.2f}%, Схожесть={similarity:.2f}%)"
    
    return "❓ Неизвестно"

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
    parent.btn_show_metrics.clicked.connect(lambda: show_metrics_dialog(parent))
    
    # Обработчик смены алгоритма
    parent.combo_algo.currentTextChanged.connect(lambda: on_algorithm_changed(parent))

    # Обработчик клика по превью секретного изображения
    parent.secret_image_label.mousePressEvent = lambda event: on_secret_preview_clicked(parent, event)
    # Обработчик клика по превью восстановленного секрета
    parent.restored_image_label.mousePressEvent = lambda event: on_restored_secret_preview_clicked(parent, event)

import tempfile

def show_metrics_dialog(parent):
    """
    ========================================================================
    ПОКАЗ ДИАЛОГА С ПОДРОБНЫМИ МЕТРИКАМИ
    ========================================================================
    Открывает модальное окно с детальной информацией о метриках качества.
    Показывает две вкладки:
    1. Метрики стегоизображения (исходное vs стего)
    2. Метрики восстановленного секрета (оригинальный vs извлечённый)
    ========================================================================
    """
    # Проверяем наличие метрик
    if not hasattr(parent, 'stego_metrics') and not hasattr(parent, 'secret_metrics'):
        QMessageBox.information(parent, "Метрики недоступны", 
                               "Метрики ещё не вычислены. Выполните встраивание и извлечение.")
        return
    
    # Создаём диалоговое окно
    dialog = QDialog(parent)
    dialog.setWindowTitle("📊 Подробные метрики качества")
    dialog.setMinimumSize(700, 500)
    
    layout = QVBoxLayout(dialog)
    
    # Создаём вкладки
    tabs = QTabWidget()
    
    # Вкладка 1: Метрики стегоизображения
    if hasattr(parent, 'stego_metrics'):
        stego_tab = QWidget()
        stego_layout = QVBoxLayout(stego_tab)
        
        stego_label = QLabel("🖼️ Сравнение: Исходное изображение vs Стегоизображение")
        stego_label.setStyleSheet("font-weight: bold; font-size: 12pt; color: #2196F3; padding: 5px;")
        stego_layout.addWidget(stego_label)
        
        stego_text = QTextEdit()
        stego_text.setReadOnly(True)
        stego_text.setText(parent.stego_metrics)
        stego_text.setStyleSheet("font-family: Consolas, monospace; font-size: 10pt;")
        stego_layout.addWidget(stego_text)
        
        tabs.addTab(stego_tab, "🖼️ Стегоизображение")
    
    # Вкладка 2: Метрики восстановленного секрета
    if hasattr(parent, 'secret_metrics'):
        secret_tab = QWidget()
        secret_layout = QVBoxLayout(secret_tab)
        
        secret_label = QLabel("🔐 Сравнение: Оригинальный секрет vs Восстановленный секрет")
        secret_label.setStyleSheet("font-weight: bold; font-size: 12pt; color: #4CAF50; padding: 5px;")
        secret_layout.addWidget(secret_label)
        
        secret_text = QTextEdit()
        secret_text.setReadOnly(True)
        secret_text.setText(parent.secret_metrics)
        secret_text.setStyleSheet("font-family: Consolas, monospace; font-size: 10pt;")
        secret_layout.addWidget(secret_text)
        
        tabs.addTab(secret_tab, "🔐 Секрет")
    
    layout.addWidget(tabs)
    
    # Кнопка закрытия
    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    btn_close = QPushButton("Закрыть")
    btn_close.clicked.connect(dialog.close)
    btn_close.setMinimumWidth(100)
    btn_layout.addWidget(btn_close)
    layout.addLayout(btn_layout)
    
    # Показываем диалог
    dialog.exec_()

def on_algorithm_changed(parent):
    """
    ========================================================================
    ОБРАБОТЧИК СМЕНЫ АЛГОРИТМА
    ========================================================================
    Эта функция вызывается при изменении выбора алгоритма в combo_algo.
    Показывает/скрывает соответствующие параметры для выбранного алгоритма.
    
    LSB параметры: depth (глубина)
    DCT параметры: strength (сила), block_size (размер блока)
    ========================================================================
    """
    algorithm = parent.combo_algo.currentText()
    
    if algorithm == "LSB":
        # Показываем параметры LSB
        parent.label_depth.setVisible(True)
        parent.spinbox_depth.setVisible(True)
        # Скрываем параметры DCT
        parent.label_strength.setVisible(False)
        parent.spinbox_strength.setVisible(False)
        parent.label_block_size.setVisible(False)
        parent.spinbox_block_size.setVisible(False)
    elif algorithm == "DCT":
        # Скрываем параметры LSB
        parent.label_depth.setVisible(False)
        parent.spinbox_depth.setVisible(False)
        # Показываем параметры DCT
        parent.label_strength.setVisible(True)
        parent.spinbox_strength.setVisible(True)
        parent.label_block_size.setVisible(True)
        parent.spinbox_block_size.setVisible(True)

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
        # Принудительно конвертируем в RGB, чтобы избежать проблем с RGBA
        cover = np.array(Image.open(cover_path).convert('RGB'))
        
        # Получаем выбранный алгоритм
        algorithm = parent.combo_algo.currentText().lower()
        
        # Получаем параметры алгоритма из интерфейса
        if algorithm == "lsb":
            depth = parent.spinbox_depth.value()  # Глубина встраивания (1-8 бит)
            params = {"depth": depth}
        elif algorithm == "dct":
            strength = parent.spinbox_strength.value()  # Сила встраивания (5-50)
            block_size = parent.spinbox_block_size.value()  # Размер блока (4-16)
            params = {"strength": strength, "block_size": block_size}
        else:
            raise ValueError(f"Неизвестный алгоритм: {algorithm}")

        # ====================================================================
        # ЭТАП 3: ОПРЕДЕЛЕНИЕ ТИПА СЕКРЕТА И ЕГО ОБРАБОТКА
        # ====================================================================
        
        if secret_type == "text":
            # Попытка чтения с разными кодировками
            encodings = ['utf-8', 'cp1251', 'latin-1']
            secret = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(wm_path, 'r', encoding=encoding) as f:
                        secret = f.read()
                    used_encoding = encoding
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            # latin-1 должна всегда сработать (читает любые байты 0-255)
            # Если не удалось прочитать ни одной кодировкой (что невозможно с latin-1)
            if secret is None:
                # На всякий случай, читаем как latin-1 напрямую
                with open(wm_path, 'r', encoding='latin-1') as f:
                    secret = f.read()
                used_encoding = 'latin-1'
                parent.result_text.append(f"⚠️ Файл прочитан с кодировкой latin-1 (универсальная)")
            else:
                parent.result_text.append(f"ℹ️ Текст прочитан с кодировкой: {used_encoding}")
            
            # Сохраняем кодировку для последующего использования
            parent.embedded_text_encoding = used_encoding
            
            # Проверка на пустой текст
            if not secret.strip():
                raise ValueError("Текстовый файл пуст или содержит только пробелы")
            
            # Проверка на слишком большой текст (для GUI предупреждение)
            text_size_bytes = len(secret.encode("utf-8"))
            if text_size_bytes > 10000:  # 10 KB
                parent.result_text.append(f"⚠️ Большой текст ({text_size_bytes} байт). Может потребоваться большой контейнер.")
            
            # Проверка ёмкости контейнера
            h, w = cover.shape[:2]
            if algorithm == "lsb":
                # Для LSB: capacity = w * h * channels * depth / 8
                channels = 3 if len(cover.shape) == 3 else 1
                capacity_bits = w * h * channels * depth
                capacity_bytes = capacity_bits // 8
            elif algorithm == "dct":
                # Для DCT: capacity = (w // block_size) * (h // block_size) бит
                capacity_bits = (w // block_size) * (h // block_size)
                capacity_bytes = capacity_bits // 8
            
            required_bytes = text_size_bytes
            
            if required_bytes > capacity_bytes:
                # Вычисляем рекомендуемый размер контейнера
                if algorithm == "lsb":
                    min_pixels = required_bytes * 8 // (channels * depth)
                    min_side = int(np.sqrt(min_pixels)) + 1
                elif algorithm == "dct":
                    min_blocks = required_bytes * 8
                    min_side = int(np.sqrt(min_blocks)) * block_size + block_size
                
                error_msg = (
                    f"Текст слишком большой для выбранного контейнера!\n\n"
                    f"Размер контейнера: {w}×{h}\n"
                    f"Ёмкость: {capacity_bytes} байт ({capacity_bits} бит)\n"
                    f"Требуется: {required_bytes} байт ({required_bytes * 8} бит)\n\n"
                    f"Рекомендации:\n"
                    f"1. Используйте контейнер минимум {min_side}×{min_side}\n"
                    f"2. Уменьшите размер текста (сейчас {text_size_bytes} байт)\n"
                )
                
                if algorithm == "dct":
                    error_msg += f"3. Используйте LSB алгоритм (выше ёмкость)\n"
                elif algorithm == "lsb" and depth < 8:
                    error_msg += f"3. Увеличьте глубину встраивания (сейчас {depth})\n"
                
                QMessageBox.warning(parent, "Недостаточная ёмкость", error_msg)
                parent.result_text.append(f"❌ Текст слишком большой: требуется {required_bytes} байт, доступно {capacity_bytes} байт")
                return
            
            parent.embedded_secret_type = "text"
            parent.embedded_secret_length = text_size_bytes
            parent.original_secret = secret  # Сохраняем оригинальный секрет для метрик
            if algorithm == "lsb":
                parent.embedded_depth = depth
            elif algorithm == "dct":
                parent.embedded_strength = strength
                parent.embedded_block_size = block_size
        elif secret_type == "image":
            # Загружаем секретное изображение и принудительно конвертируем в RGB
            secret = np.array(Image.open(wm_path).convert('RGB'))
            
            # Проверка ёмкости для изображений (только для LSB, для DCT есть автоматическое масштабирование)
            if algorithm == "lsb":
                h, w = cover.shape[:2]
                channels = 3 if len(cover.shape) == 3 else 1
                capacity_bits = w * h * channels * depth
                capacity_bytes = capacity_bits // 8
                
                required_bytes = secret.size
                
                if required_bytes > capacity_bytes:
                    # Вычисляем рекомендуемый размер контейнера
                    min_pixels = required_bytes * 8 // (channels * depth)
                    min_side = int(np.sqrt(min_pixels)) + 1
                    
                    error_msg = (
                        f"Секретное изображение слишком большое для контейнера!\n\n"
                        f"Размер контейнера: {w}×{h}\n"
                        f"Ёмкость: {capacity_bytes} байт\n"
                        f"Секретное изображение: {secret.shape}\n"
                        f"Требуется: {required_bytes} байт\n\n"
                        f"Рекомендации:\n"
                        f"1. Используйте контейнер минимум {min_side}×{min_side}\n"
                        f"2. Уменьшите секретное изображение\n"
                        f"3. Увеличьте глубину встраивания (сейчас {depth})\n"
                        f"4. Используйте DCT с автоматическим масштабированием\n"
                    )
                    
                    QMessageBox.warning(parent, "Недостаточная ёмкость", error_msg)
                    parent.result_text.append(f"❌ Изображение слишком большое: требуется {required_bytes} байт, доступно {capacity_bytes} байт")
                    return
            
            parent.embedded_secret_type = "image"
            parent.embedded_secret_shape = secret.shape  # Исходный размер
            parent.embedded_original_secret_shape = secret.shape  # Для восстановления после масштабирования
            parent.original_secret = secret.copy()  # Сохраняем оригинальный секрет для метрик
            if algorithm == "lsb":
                parent.embedded_depth = depth
            elif algorithm == "dct":
                parent.embedded_strength = strength
                parent.embedded_block_size = block_size

        # Сохраняем используемый алгоритм
        parent.embedded_algorithm = algorithm

        # ====================================================================
        # ЭТАП 4: ВСТРАИВАНИЕ СЕКРЕТА В ИЗОБРАЖЕНИЕ
        # ====================================================================
        
        # Перехватываем вывод для информирования о масштабировании
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # Вызываем алгоритм встраивания (из модуля watermark.embedding)
        result = embed(cover, secret, params, method=algorithm)
        
        # Получаем вывод о масштабировании (если было)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Если было масштабирование, выводим предупреждение
        if output:
            parent.result_text.append(output.strip())
            # Обновляем сохранённую форму секрета на реальную (после масштабирования)
            if secret_type == "image" and algorithm == "dct":
                # После масштабирования нужно обновить embedded_secret_shape
                # Получим информацию из вывода
                import re
                match = re.search(r'→ \(([^)]+)\)', output)
                if match:
                    shape_str = match.group(1)
                    shape_parts = [int(x.strip()) for x in shape_str.split(',')]
                    parent.embedded_secret_shape = tuple(shape_parts)
                    parent.result_text.append(f"ℹ️ Размер встроенного секрета обновлён: {parent.embedded_secret_shape}")
        
        # ====================================================================
        # ЭТАП 5: СОХРАНЕНИЕ РЕЗУЛЬТАТА
        # ====================================================================
        
        # Сохраняем стего-изображение во временный путь, но не сохраняем автоматически
        parent.stego_result = result
        parent.result_text.append(f"✅ Встраивание успешно! Результат готов для предпросмотра и сохранения.")
        parent.btn_save_result.setEnabled(True)
        
        # ====================================================================
        # ЭТАП 5.1: РАСЧЁТ МЕТРИК ДЛЯ СТЕГОИЗОБРАЖЕНИЯ
        # ====================================================================
        
        try:
            # Расчёт метрик качества (исходное vs стегоизображение)
            stego_metrics = calculate_image_metrics(cover, result)
            formatted_stego_metrics = format_image_metrics(stego_metrics)
            
            # Сохраняем подробные метрики для диалога
            parent.stego_metrics = formatted_stego_metrics
            
            # Получаем краткую сводку (общую оценку качества)
            quality_desc = get_quality_description(stego_metrics)
            
            # Отображаем только краткую сводку в главном окне
            parent.metrics_summary_text.clear()
            parent.metrics_summary_text.append(f"🖼️ Стегоизображение: {quality_desc}")
            
            # Активируем кнопку просмотра подробных метрик
            parent.btn_show_metrics.setEnabled(True)
            
            parent.result_text.append("📊 Метрики стегоизображения рассчитаны")
        except Exception as metrics_error:
            parent.result_text.append(f"⚠️ Не удалось рассчитать метрики стегоизображения: {metrics_error}")
        
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
        
        # Получаем используемый алгоритм
        algorithm = getattr(parent, "embedded_algorithm", "lsb")
        
        # ====================================================================
        # ЭТАП 3: ПОДГОТОВКА ПАРАМЕТРОВ ДЛЯ ИЗВЛЕЧЕНИЯ
        # ====================================================================
        if algorithm == "lsb":
            depth = getattr(parent, "embedded_depth", parent.spinbox_depth.value())
            params = {"depth": depth}
        elif algorithm == "dct":
            strength = getattr(parent, "embedded_strength", parent.spinbox_strength.value())
            block_size = getattr(parent, "embedded_block_size", parent.spinbox_block_size.value())
            params = {"strength": strength, "block_size": block_size}
        else:
            raise ValueError(f"Неизвестный алгоритм: {algorithm}")
        
        if secret_type == "text":
            params["length"] = getattr(parent, "embedded_secret_length", 10)
        elif secret_type == "image":
            params["secret_shape"] = getattr(parent, "embedded_secret_shape", (64, 64, 3))
        
        # ====================================================================
        # ЭТАП 4: ИЗВЛЕЧЕНИЕ СЕКРЕТНЫХ ДАННЫХ
        # ====================================================================
        extracted = extract(stego_image, params, method=algorithm)
        
        # ====================================================================
        # ЭТАП 5: ОТОБРАЖЕНИЕ РЕЗУЛЬТАТА
        # ====================================================================
        if isinstance(extracted, str):
            parent.extracted_secret = extracted
            parent.result_text.append(f"🔍 Извлечённый текст готов для предпросмотра и сохранения.")
            parent.restored_image_label.clear()
            parent.restored_image_label.setText("📄 Восстановленный текст")
            parent.restored_image_label.setStyleSheet("border: 2px solid #2196F3; color: #2196F3;")
            
            # Вычисляем и отображаем метрики для текста
            if hasattr(parent, 'original_secret') and isinstance(parent.original_secret, str):
                try:
                    metrics = calculate_text_metrics(parent.original_secret, extracted)
                    
                    # Проверяем, что метрики получены корректно
                    if not metrics or not isinstance(metrics, dict):
                        raise ValueError("Метрики не были рассчитаны")
                    
                    formatted = format_text_metrics(metrics)
                    
                    # Сохраняем подробные метрики для диалога
                    parent.secret_metrics = formatted
                    
                    # Получаем краткую сводку
                    quality_desc = get_quality_description(metrics)
                    
                    # Добавляем краткую сводку к существующему тексту (уже есть метрики стего)
                    current_summary = parent.metrics_summary_text.toPlainText()
                    if current_summary:
                        parent.metrics_summary_text.append(f"\n🔐 Восстановленный секрет: {quality_desc}")
                    else:
                        parent.metrics_summary_text.setText(f"🔐 Восстановленный секрет: {quality_desc}")
                    
                    # Активируем кнопку просмотра подробных метрик
                    parent.btn_show_metrics.setEnabled(True)
                    
                except Exception as metrics_error:
                    parent.result_text.append(f"⚠️ Не удалось рассчитать метрики текста: {metrics_error}")
                    parent.metrics_summary_text.append(f"\n🔐 Восстановленный секрет: ⚠️ Метрики недоступны")
            
        else:
            # Проверяем, было ли масштабирование при встраивании
            original_shape = getattr(parent, "embedded_original_secret_shape", None)
            if original_shape and extracted.shape != original_shape:
                parent.result_text.append(f"ℹ️ Восстановленное изображение: {extracted.shape} (было масштабировано из {original_shape})")
                parent.result_text.append(f"💡 Совет: при сохранении можно масштабировать обратно к исходному размеру")
            
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
            
            # Вычисляем и отображаем метрики для изображения
            if hasattr(parent, 'original_secret') and isinstance(parent.original_secret, np.ndarray):
                try:
                    # Масштабируем извлечённое изображение до размера оригинального, если нужно
                    original_secret = parent.original_secret
                    if extracted.shape != original_secret.shape:
                        # Масштабируем извлечённое изображение к оригинальному размеру для сравнения
                        h_orig, w_orig = original_secret.shape[:2]
                        extracted_resized = cv2.resize(extracted, (w_orig, h_orig), interpolation=cv2.INTER_LINEAR)
                        metrics = calculate_image_metrics(original_secret, extracted_resized)
                        formatted = format_image_metrics(metrics)
                        formatted_with_note = (
                            f"📊 Метрики восстановленного секрета\n"
                            f"Оригинальный {original_secret.shape} vs "
                            f"Извлечённый {extracted.shape} → масштабирован до {extracted_resized.shape}\n\n" + 
                            formatted
                        )
                        # Сохраняем подробные метрики для диалога
                        parent.secret_metrics = formatted_with_note
                    else:
                        metrics = calculate_image_metrics(original_secret, extracted)
                        formatted = format_image_metrics(metrics)
                        # Сохраняем подробные метрики для диалога
                        parent.secret_metrics = formatted
                    
                    # Получаем краткую сводку
                    quality_desc = get_quality_description(metrics)
                    
                    # Добавляем краткую сводку к существующему тексту
                    current_summary = parent.metrics_summary_text.toPlainText()
                    if current_summary:
                        parent.metrics_summary_text.append(f"\n🔐 Восстановленный секрет: {quality_desc}")
                    else:
                        parent.metrics_summary_text.setText(f"🔐 Восстановленный секрет: {quality_desc}")
                    
                    # Активируем кнопку просмотра подробных метрик
                    parent.btn_show_metrics.setEnabled(True)
                    
                except Exception as metrics_error:
                    parent.result_text.append(f"⚠️ Не удалось рассчитать метрики изображения: {metrics_error}")
                    parent.metrics_summary_text.append(f"\n🔐 Восстановленный секрет: ⚠️ Метрики недоступны")
        
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
    parent.spinbox_strength.setValue(15)
    parent.spinbox_block_size.setValue(8)
    parent.combo_algo.setCurrentIndex(0)  # Вернуть на LSB
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
    
    # Очистка метрик
    parent.metrics_summary_text.clear()
    parent.btn_show_metrics.setEnabled(False)
    
    parent.btn_save_result.setEnabled(False)
    parent.btn_save_secret.setEnabled(False)
    attributes_to_clear = [
        'cover_path', 'wm_path', 'stego_result', 'embedded_secret_type', 
        'embedded_secret_length', 'embedded_secret_shape', 'embedded_depth', 
        'embedded_strength', 'embedded_block_size', 'embedded_algorithm',
        'embedded_original_secret_shape', 'secret_type', 'extracted_secret',
        'original_secret', 'stego_metrics', 'secret_metrics', 'embedded_text_encoding'
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
        # Проверяем, было ли масштабирование
        original_shape = getattr(parent, 'embedded_original_secret_shape', None)
        should_upscale = False
        
        if original_shape and secret.shape != original_shape:
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                parent, 
                'Масштабирование', 
                f'Изображение было масштабировано при встраивании.\n'
                f'Исходный размер: {original_shape}\n'
                f'Текущий размер: {secret.shape}\n\n'
                f'Масштабировать обратно к исходному размеру?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            should_upscale = (reply == QMessageBox.Yes)
        
        fname, _ = QFileDialog.getSaveFileName(parent, "Сохранить восстановленное изображение", "extracted_secret.png", "Images (*.png *.jpg *.bmp)")
        if fname:
            if should_upscale and original_shape:
                # Масштабируем обратно
                img = Image.fromarray(secret)
                if len(original_shape) == 3:
                    img = img.resize((original_shape[1], original_shape[0]), Image.LANCZOS)
                else:
                    img = img.resize((original_shape[1], original_shape[0]), Image.LANCZOS)
                img.save(fname)
                parent.result_text.append(f"💾 Восстановленное изображение масштабировано и сохранено: {fname}")
            else:
                Image.fromarray(secret).save(fname)
                parent.result_text.append(f"💾 Восстановленное изображение сохранено: {fname}")
    elif secret_type == "text":
        fname, _ = QFileDialog.getSaveFileName(parent, "Сохранить восстановленный текст", "extracted_secret.txt", "Text files (*.txt)")
        if fname:
            # Используем ту же кодировку, что была при чтении исходного файла
            encoding = getattr(parent, 'embedded_text_encoding', 'utf-8')
            with open(fname, 'w', encoding=encoding) as f:
                f.write(secret)
            parent.result_text.append(f"💾 Восстановленный текст сохранён: {fname} (кодировка: {encoding})")
