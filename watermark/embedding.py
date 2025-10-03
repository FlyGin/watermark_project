from watermark.algorithms import lsb, dct, dwt, cnn_autoencoder

algorithms = {
    "lsb": lsb,
    "dct": dct,
    "dwt": dwt,
    "cnn_ae": cnn_autoencoder
}

def embed(image, secret, params=None, method="lsb"):
    """
    Универсальная функция внедрения водяного знака.
    :param image: np.ndarray
    :param secret: str или np.ndarray
    :param params: dict
    :param method: str
    :return: np.ndarray
    """
    if params is None:
        params = {}
    if method not in algorithms:
        raise ValueError(f"Алгоритм '{method}' не поддерживается.")
    return algorithms[method].embed(image, secret, params)
