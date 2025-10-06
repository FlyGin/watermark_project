# gui/events.py
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image
import numpy as np
import os
from watermark.embedding import embed
from watermark.extraction import extract

def connect_events(parent):
    parent.btn_load_cover.clicked.connect(lambda: load_cover_file(parent))
    parent.btn_load_wm.clicked.connect(lambda: load_wm_file(parent))
    parent.btn_embed.clicked.connect(lambda: embed_watermark(parent))
    parent.btn_extract.clicked.connect(lambda: extract_watermark(parent))
    parent.btn_reset.clicked.connect(lambda: reset_gui(parent))
    
    # При вводе текста очищаем предпросмотр секретного изображения
    parent.lineedit_wm.textChanged.connect(lambda text: on_text_input_changed(parent, text))

def on_text_input_changed(parent, text):
    """Обработчик изменения текста в поле ввода секрета"""
    if text.strip():  # Если введен текст
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
    """Загружает изображение и отображает его в QLabel с масштабированием"""
    try:
        # Загружаем изображение
        pil_image = Image.open(image_path)
        
        # Конвертируем в RGB если нужно
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Масштабируем изображение с сохранением пропорций
        pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Конвертируем в QPixmap
        # Сначала сохраняем во временный буфер
        import io
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(img_buffer.getvalue())
        
        # Отображаем в label
        label_widget.setPixmap(pixmap)
        label_widget.setStyleSheet("border: 2px solid #4CAF50;")  # Зеленая рамка для загруженного изображения
        
        return True
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        return False

def load_cover_file(parent):
    fname, _ = QFileDialog.getOpenFileName(parent, "Выберите исходный файл", "", "Images (*.png *.jpg *.bmp *.jpeg);;All Files (*)")
    if fname:
        parent.cover_path = fname
        parent.result_text.append(f"Загружен исходный файл: {fname}")
        
        # Отображаем предпросмотр
        if load_and_display_image(fname, parent.cover_image_label):
            parent.result_text.append("✅ Предпросмотр исходного изображения загружен")
        else:
            parent.result_text.append("⚠️ Не удалось загрузить предпросмотр исходного изображения")

def load_wm_file(parent):
    fname, _ = QFileDialog.getOpenFileName(parent, "Выберите файл водяного знака", "", "Images (*.png *.jpg *.bmp);;Text files (*.txt);;All Files (*)")
    if fname:
        parent.wm_path = fname
        parent.result_text.append(f"Загружен файл водяного знака: {fname}")
        
        # Очищаем текстовое поле, так как выбран файл
        parent.lineedit_wm.clear()
        
        # Проверяем, является ли файл изображением
        if os.path.splitext(fname)[1].lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
            # Отображаем предпросмотр изображения
            if load_and_display_image(fname, parent.secret_image_label):
                parent.result_text.append("✅ Предпросмотр секретного изображения загружен")
            else:
                parent.result_text.append("⚠️ Не удалось загрузить предпросмотр секретного изображения")
        else:
            # Для текстовых файлов показываем заглушку
            parent.secret_image_label.clear()
            parent.secret_image_label.setText("📄 Текстовый файл")
            parent.secret_image_label.setStyleSheet("border: 2px solid #2196F3; color: #2196F3;")  # Синяя рамка для текста
            parent.result_text.append("📄 Загружен текстовый файл")

def embed_watermark(parent):
    # LSB встраивание
    cover_path = getattr(parent, "cover_path", None)
    wm_path = getattr(parent, "wm_path", None)
    text = parent.lineedit_wm.text().strip()

    if not cover_path:
        QMessageBox.warning(parent, "Ошибка", "Не выбран исходный файл.")
        return
        
    if not wm_path and not text:
        QMessageBox.warning(parent, "Ошибка", "Не выбран водяной знак (файл или текст).")
        return
    
    try:
        # Загружаем исходное изображение
        cover = np.array(Image.open(cover_path))
        
        # Получаем выбранную глубину из спиннера
        depth = parent.spinbox_depth.value()
        params = {"depth": depth}

        # Определяем тип секрета
        if text:  # Если введён текст
            secret = text
            parent.embedded_secret_type = "text"
            parent.embedded_secret_length = len(text.encode("utf-8"))
            parent.embedded_depth = depth  # Сохраняем используемую глубину
        elif wm_path:  # Если выбран файл
            if os.path.splitext(wm_path)[1].lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
                secret = np.array(Image.open(wm_path))
                parent.embedded_secret_type = "image"
                parent.embedded_secret_shape = secret.shape
                parent.embedded_depth = depth  # Сохраняем используемую глубину
            else:
                # Пробуем прочитать как текстовый файл
                with open(wm_path, 'r', encoding='utf-8') as f:
                    secret = f.read()
                parent.embedded_secret_type = "text"
                parent.embedded_secret_length = len(secret.encode("utf-8"))
                parent.embedded_depth = depth  # Сохраняем используемую глубину

        # Встраиваем с помощью LSB
        result = embed(cover, secret, params, method="lsb")
        
        # Сохраняем результат
        output_path = "stego_result.png"
        Image.fromarray(result).save(output_path)
        parent.result_text.append(f"✅ Встраивание успешно! Результат сохранён: {output_path}")
        parent.stego_path = output_path  # Сохраняем путь для извлечения
        
    except Exception as exc:
        parent.result_text.append(f"❌ Ошибка встраивания: {exc}")
        

def extract_watermark(parent):
    # LSB извлечение
    stego_path = getattr(parent, "stego_path", None) or getattr(parent, "cover_path", None)
    
    if not stego_path:
        QMessageBox.warning(parent, "Ошибка", "Не выбран файл для извлечения.")
        return
    
    # Проверяем, что у нас есть информация о том, что было встроено
    secret_type = getattr(parent, "embedded_secret_type", None)
    if not secret_type:
        QMessageBox.warning(parent, "Ошибка", "Неизвестно, что было встроено. Сначала выполните встраивание.")
        return
    
    try:
        # Загружаем стего-изображение
        stego_image = np.array(Image.open(stego_path))
        
        # Используем сохранённую глубину или текущую из спиннера
        depth = getattr(parent, "embedded_depth", parent.spinbox_depth.value())
        params = {"depth": depth}
        
        # Добавляем нужные параметры в зависимости от типа секрета
        if secret_type == "text":
            params["length"] = getattr(parent, "embedded_secret_length", 10)  # fallback
        elif secret_type == "image":
            params["secret_shape"] = getattr(parent, "embedded_secret_shape", (64, 64, 3))  # fallback
        
        # Извлекаем
        extracted = extract(stego_image, params, method="lsb")
        
        # Отображаем результат
        if isinstance(extracted, str):
            parent.result_text.append(f"🔍 Извлечённый текст: '{extracted}'")
        else:
            # Сохраняем извлечённое изображение
            output_path = "extracted_secret.png"
            Image.fromarray(extracted).save(output_path)
            parent.result_text.append(f"🔍 Извлечённое изображение сохранено: {output_path}")
            
    except Exception as exc:
        parent.result_text.append(f"❌ Ошибка извлечения: {exc}")

def reset_gui(parent):
    parent.lineedit_wm.clear()
    parent.result_text.clear()
    parent.spinbox_depth.setValue(1)  # Сброс глубины к значению по умолчанию
    
    # Очищаем предпросмотры изображений
    parent.cover_image_label.clear()
    parent.cover_image_label.setText("Изображение не загружено")
    parent.cover_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    
    parent.secret_image_label.clear() 
    parent.secret_image_label.setText("Изображение не загружено")
    parent.secret_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    
    # Очищаем пути и мета-информацию
    for attr in ['cover_path', 'wm_path', 'stego_path', 'embedded_secret_type', 
                 'embedded_secret_length', 'embedded_secret_shape', 'embedded_depth']:
        if hasattr(parent, attr):
            delattr(parent, attr)
