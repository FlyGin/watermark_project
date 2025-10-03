
from watermark.algorithms import lsb, dct, dwt, cnn_autoencoder

# Словарь доступных алгоритмов
algorithms = {
    "lsb": lsb,
    "dct": dct,
    "dwt": dwt,
    "cnn_ae": cnn_autoencoder
}

def embed(image, secret, params=None, method="lsb"):
    """
    Универсальная функция внедрения водяного знака.
    :param image: np.ndarray — исходное изображение
    :param secret: любой тип — секрет/водяной знак
    :param params: dict — параметры внедрения для метода
    :param method: str — название алгоритма
    :return: np.ndarray — изображение с внедрённым водяным знаком
    """
    if params is None:
        params = {}
    if method not in algorithms:
        raise ValueError(f"Алгоритм '{method}' не поддерживается.")
    return algorithms[method].embed(image, secret, params)
