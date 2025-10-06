import numpy as np
from .lsb_text import embed_text, extract_text
from .lsb_image import embed_image, extract_image

def embed(image, secret, params):
    """
    Фасад для LSB-алгоритма: выбирает нужную реализацию в зависимости от типа секрета.
    Если secret — строка, использует embed_text.
    Если secret — np.ndarray, использует embed_image.
    """
    if isinstance(secret, str):
        return embed_text(image, secret, params)
    elif isinstance(secret, np.ndarray):
        return embed_image(image, secret, params)
    else:
        raise ValueError("Secret должен быть str (текст) или np.ndarray (картинка)")
    
    from watermark.embedding import embed
from PIL import Image
import numpy as np
import os

def embed_watermark(parent):
    cover_path = getattr(parent, "cover_path", None)
    wm_path = getattr(parent, "wm_path", None)
    text = parent.lineedit_wm.text()
    if not cover_path or (not wm_path and not text):
        QMessageBox.warning(parent, "Ошибка", "Не выбран исходный файл или знак.")
        return
    cover = np.array(Image.open(cover_path))
    params = {"depth": 1}  # или другое значение, если пользователь выбирает depth
    try:
        # если выбран файл водяного знака и он - изображение (не .txt)
        ext = os.path.splitext(wm_path)[1].lower() if wm_path else ""
        if wm_path and ext in (".jpg", ".jpeg", ".png", ".bmp"):
            secret = np.array(Image.open(wm_path))
            result = embed(cover, secret, params, method="lsb")
            Image.fromarray(result).save("stego_result.png")
            parent.result_text.append("Встраивание изображения завершено. stеgo_result.png сохранено.")
        else:
            # иначе — берем текст из поля
            secret = text
            result = embed(cover, secret, params, method="lsb")
            Image.fromarray(result).save("stego_result.png")
            parent.result_text.append("Текст внедрен. stego_result.png сохранено.")
    except Exception as exc:
        parent.result_text.append(f"Ошибка: {exc}")


def extract(image, params):
    """
    Фасад для извлечения: выбирает реализацию по параметрам.
    Если в params есть 'length' — извлекает текст.
    Если есть 'secret_shape' — извлекает изображение.
    """
    if 'length' in params:
        return extract_text(image, params)
    elif 'secret_shape' in params:
        return extract_image(image, params)
    else:
        raise ValueError("Для извлечения необходимо указать либо 'length', либо 'secret_shape' в параметрах.")
