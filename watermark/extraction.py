#функция-диспетчер для выбора алгоритма извлечения
# watermark/extraction.py

from watermark.algorithms import lsb, dct, dwt, cnn_autoencoder

# Словарь доступных алгоритмов
algorithms = {
    "lsb": lsb,
    "dct": dct,
    "dwt": dwt,
    "cnn_ae": cnn_autoencoder
}

def extract(image, params=None, method="lsb"):
    """
    Универсальная функция извлечения водяного знака.
    :param image: np.ndarray — изображение со стего-данными
    :param params: dict — параметры извлечения для метода
    :param method: str — название алгоритма
    :return: любой тип — извлечённый секрет/водяной знак
    """
    if params is None:
        params = {}
    if method not in algorithms:
        raise ValueError(f"Алгоритм '{method}' не поддерживается.")
    return algorithms[method].extract(image, params)
