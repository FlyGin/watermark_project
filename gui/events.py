# gui/events.py
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def connect_events(parent):
    parent.btn_load_cover.clicked.connect(lambda: load_cover_file(parent))
    parent.btn_load_wm.clicked.connect(lambda: load_wm_file(parent))
    parent.btn_embed.clicked.connect(lambda: embed_watermark(parent))
    parent.btn_extract.clicked.connect(lambda: extract_watermark(parent))
    parent.btn_reset.clicked.connect(lambda: reset_gui(parent))

def load_cover_file(parent):
    fname, _ = QFileDialog.getOpenFileName(parent, "Выберите исходный файл", "", "Images (*.png *.jpg *.bmp);;All Files (*)")
    if fname:
        parent.cover_path = fname
        parent.result_text.append(f"Загружен исходный файл: {fname}")

def load_wm_file(parent):
    fname, _ = QFileDialog.getOpenFileName(parent, "Выберите файл водяного знака", "", "Images (*.png *.jpg *.bmp);;Text files (*.txt);;All Files (*)")
    if fname:
        parent.wm_path = fname
        parent.result_text.append(f"Загружен файл водяного знака: {fname}")

def embed_watermark(parent):
    # Вариант — получить выбранный алгоритм, пути до файлов,/или текст
    algorithm = parent.combo_algo.currentText()
    cover = getattr(parent, "cover_path", None)
    wm = parent.lineedit_wm.text() or getattr(parent, "wm_path", None)
    if not cover or not wm:
        QMessageBox.warning(parent, "Ошибка", "Не выбран исходный файл или знак.")
        return
    # Тут — логика взаимодействия с embedding из watermark (заглушка):
    try:
        # from watermark.embedding import embed_image, ... # импортируешь нужное
        # result = embed_image(cover, wm, {'algorithm': algorithm})
        result = "Успешно встроено (заглушка)"  # подменишь на реальную интеграцию
        parent.result_text.append(result)
    except Exception as exc:
        parent.result_text.append(f"Ошибка: {exc}")

def extract_watermark(parent):
    algorithm = parent.combo_algo.currentText()
    cover = getattr(parent, "cover_path", None)
    if not cover:
        QMessageBox.warning(parent, "Ошибка", "Не выбран файл для извлечения.")
        return
    try:
        # from watermark.extraction import extract_image, ...
        # result = extract_image(cover, {'algorithm': algorithm})
        result = "Водяной знак: пример (заглушка)"  # подменишь на реальную интеграцию
        parent.result_text.append(result)
    except Exception as exc:
        parent.result_text.append(f"Ошибка: {exc}")

def reset_gui(parent):
    parent.lineedit_wm.clear()
    parent.result_text.clear()
    parent.cover_path = None
    parent.wm_path = None

