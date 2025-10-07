"""
Модуль для расчёта метрик качества изображений
"""

import numpy as np
from typing import Dict, Tuple
import cv2


def calculate_psnr(original: np.ndarray, compared: np.ndarray) -> float:
    """
    Расчёт PSNR (Peak Signal-to-Noise Ratio) - пиковое отношение сигнал/шум
    
    PSNR измеряет качество восстановления изображения относительно оригинала.
    Чем выше PSNR, тем лучше качество (меньше искажений).
    
    Типичные значения:
    - > 40 dB: отличное качество, различия практически незаметны
    - 30-40 dB: хорошее качество, незначительные различия
    - 20-30 dB: приемлемое качество, заметные различия
    - < 20 dB: плохое качество, значительные искажения
    
    Args:
        original: Исходное изображение
        compared: Изображение для сравнения
    
    Returns:
        PSNR в децибелах (dB)
    """
    mse = np.mean((original.astype(float) - compared.astype(float)) ** 2)
    if mse == 0:
        return float('inf')  # Изображения идентичны
    
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return float(psnr)


def calculate_mse(original: np.ndarray, compared: np.ndarray) -> float:
    """
    Расчёт MSE (Mean Squared Error) - среднеквадратичная ошибка
    
    MSE измеряет среднее квадратичное различие между пикселями.
    Чем ниже MSE, тем меньше различий между изображениями.
    
    Типичные значения:
    - 0: изображения идентичны
    - < 100: очень похожие изображения
    - 100-1000: заметные различия
    - > 1000: значительные различия
    
    Args:
        original: Исходное изображение
        compared: Изображение для сравнения
    
    Returns:
        MSE значение
    """
    mse = np.mean((original.astype(float) - compared.astype(float)) ** 2)
    return float(mse)


def calculate_mae(original: np.ndarray, compared: np.ndarray) -> float:
    """
    Расчёт MAE (Mean Absolute Error) - средняя абсолютная ошибка
    
    MAE измеряет среднее абсолютное различие между пикселями.
    Чем ниже MAE, тем меньше различий.
    
    Args:
        original: Исходное изображение
        compared: Изображение для сравнения
    
    Returns:
        MAE значение
    """
    mae = np.mean(np.abs(original.astype(float) - compared.astype(float)))
    return float(mae)


def calculate_ssim(original: np.ndarray, compared: np.ndarray) -> float:
    """
    Расчёт SSIM (Structural Similarity Index) - индекс структурного сходства
    
    SSIM оценивает визуальное восприятие различий между изображениями,
    учитывая яркость, контраст и структуру.
    
    Значения SSIM находятся в диапазоне [-1, 1]:
    - 1: изображения идентичны
    - > 0.95: отличное качество, различия незаметны
    - 0.90-0.95: хорошее качество
    - 0.80-0.90: приемлемое качество
    - < 0.80: заметные различия
    
    Args:
        original: Исходное изображение
        compared: Изображение для сравнения
    
    Returns:
        SSIM значение от -1 до 1
    """
    # Преобразуем в grayscale если цветное
    if len(original.shape) == 3:
        original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        compared_gray = cv2.cvtColor(compared, cv2.COLOR_BGR2GRAY)
    else:
        original_gray = original
        compared_gray = compared
    
    # Параметры для SSIM
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2
    
    original_gray = original_gray.astype(np.float64)
    compared_gray = compared_gray.astype(np.float64)
    
    # Средние значения
    mu1 = cv2.GaussianBlur(original_gray, (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(compared_gray, (11, 11), 1.5)
    
    mu1_sq = mu1 ** 2
    mu2_sq = mu2 ** 2
    mu1_mu2 = mu1 * mu2
    
    # Дисперсии и ковариация
    sigma1_sq = cv2.GaussianBlur(original_gray ** 2, (11, 11), 1.5) - mu1_sq
    sigma2_sq = cv2.GaussianBlur(compared_gray ** 2, (11, 11), 1.5) - mu2_sq
    sigma12 = cv2.GaussianBlur(original_gray * compared_gray, (11, 11), 1.5) - mu1_mu2
    
    # SSIM формула
    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
    
    return float(ssim_map.mean())


def calculate_image_metrics(original: np.ndarray, compared: np.ndarray) -> Dict[str, float]:
    """
    Расчёт всех метрик качества для сравнения изображений
    
    Args:
        original: Исходное изображение
        compared: Изображение для сравнения
    
    Returns:
        Словарь с метриками: PSNR, MSE, MAE, SSIM
    """
    # Проверка размеров
    if original.shape != compared.shape:
        raise ValueError(f"Размеры изображений не совпадают: {original.shape} != {compared.shape}")
    
    metrics = {
        'psnr': calculate_psnr(original, compared),
        'mse': calculate_mse(original, compared),
        'mae': calculate_mae(original, compared),
        'ssim': calculate_ssim(original, compared)
    }
    
    return metrics


def compare_images(original: np.ndarray, compared: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Сравнение двух изображений с расчётом метрик и разностного изображения
    
    Args:
        original: Исходное изображение
        compared: Изображение для сравнения
    
    Returns:
        Кортеж: (разностное изображение, словарь метрик)
    """
    # Расчёт метрик
    metrics = calculate_image_metrics(original, compared)
    
    # Создание разностного изображения (абсолютная разница)
    diff = np.abs(original.astype(np.int16) - compared.astype(np.int16)).astype(np.uint8)
    
    # Увеличиваем контраст разностного изображения для лучшей видимости
    diff_enhanced = np.clip(diff * 10, 0, 255).astype(np.uint8)
    
    return diff_enhanced, metrics


def get_quality_description(metrics: Dict[str, float]) -> str:
    """
    Получить текстовое описание качества на основе метрик
    
    Args:
        metrics: Словарь с метриками
    
    Returns:
        Текстовое описание качества
    """
    psnr = metrics.get('psnr', 0)
    ssim = metrics.get('ssim', 0)
    
    if psnr == float('inf'):
        return "Изображения идентичны"
    elif psnr > 40 and ssim > 0.95:
        return "Отличное качество (различия незаметны)"
    elif psnr > 30 and ssim > 0.90:
        return "Хорошее качество (незначительные различия)"
    elif psnr > 20 and ssim > 0.80:
        return "Приемлемое качество (заметные различия)"
    else:
        return "Низкое качество (значительные искажения)"


def format_metrics(metrics: Dict[str, float]) -> str:
    """
    Форматирование метрик для вывода
    
    Args:
        metrics: Словарь с метриками
    
    Returns:
        Отформатированная строка с метриками
    """
    psnr = metrics.get('psnr', 0)
    mse = metrics.get('mse', 0)
    mae = metrics.get('mae', 0)
    ssim = metrics.get('ssim', 0)
    
    if psnr == float('inf'):
        psnr_str = "∞ (идентичны)"
    else:
        psnr_str = f"{psnr:.2f} dB"
    
    result = f"""Метрики качества изображения:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PSNR (Peak Signal-to-Noise Ratio): {psnr_str}
MSE  (Mean Squared Error):          {mse:.2f}
MAE  (Mean Absolute Error):         {mae:.2f}
SSIM (Structural Similarity):       {ssim:.4f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Оценка качества: {get_quality_description(metrics)}
"""
    return result
