from watermark.algorithms import lsb, dct, dwt, cnn_autoencoder

algorithms = {
    "lsb": lsb,
    "dct": dct,
    "dwt": dwt,
    "cnn_ae": cnn_autoencoder
}

def extract(image, params=None, method="lsb"):
    """
    Универсальная функция извлечения водяного знака.
    :param image: np.ndarray
    :param params: dict
    :param method: str
    :return: str, np.ndarray и др.
    """
    if params is None:
        params = {}
    if method not in algorithms:
        raise ValueError(f"Алгоритм '{method}' не поддерживается.")
    return algorithms[method].extract(image, params)
