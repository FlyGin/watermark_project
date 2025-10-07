"""
Модуль для расчёта метрик качества текста
"""

from typing import Dict, List, Tuple
import difflib


def calculate_levenshtein_distance(original: str, compared: str) -> int:
    """
    Расчёт расстояния Левенштейна (Levenshtein Distance)
    
    Расстояние Левенштейна - это минимальное количество операций редактирования
    (вставка, удаление, замена символа), необходимых для преобразования
    одной строки в другую.
    
    Типичные значения:
    - 0: строки идентичны
    - 1-5: очень похожие строки (опечатки)
    - > 10: значительные различия
    
    Args:
        original: Исходная строка
        compared: Строка для сравнения
    
    Returns:
        Расстояние Левенштейна (количество операций)
    """
    len1, len2 = len(original), len(compared)
    
    # Создаём матрицу расстояний
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    # Инициализация первой строки и столбца
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j
    
    # Заполнение матрицы
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if original[i-1] == compared[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # удаление
                    dp[i][j-1],    # вставка
                    dp[i-1][j-1]   # замена
                )
    
    return dp[len1][len2]


def calculate_similarity_ratio(original: str, compared: str) -> float:
    """
    Расчёт коэффициента сходства строк
    
    Использует алгоритм SequenceMatcher из difflib для расчёта
    степени сходства двух строк.
    
    Значения находятся в диапазоне [0, 1]:
    - 1.0: строки идентичны
    - > 0.95: очень похожие строки
    - 0.80-0.95: похожие строки
    - < 0.80: значительные различия
    
    Args:
        original: Исходная строка
        compared: Строка для сравнения
    
    Returns:
        Коэффициент сходства от 0 до 1
    """
    return difflib.SequenceMatcher(None, original, compared).ratio()


def calculate_accuracy(original: str, compared: str) -> float:
    """
    Расчёт точности восстановления в процентах
    
    Точность = (1 - (расстояние / длина_оригинала)) * 100%
    
    Args:
        original: Исходная строка
        compared: Строка для сравнения
    
    Returns:
        Точность в процентах (0-100)
    """
    if len(original) == 0:
        return 100.0 if len(compared) == 0 else 0.0
    
    distance = calculate_levenshtein_distance(original, compared)
    accuracy = max(0, (1 - distance / len(original)) * 100)
    return accuracy


def calculate_character_error_rate(original: str, compared: str) -> float:
    """
    Расчёт Character Error Rate (CER) - коэффициент ошибок символов
    
    CER = расстояние_Левенштейна / длина_оригинала * 100%
    
    Типичные значения:
    - 0%: идентичные строки
    - < 5%: отличное качество
    - 5-10%: хорошее качество
    - > 10%: плохое качество
    
    Args:
        original: Исходная строка
        compared: Строка для сравнения
    
    Returns:
        CER в процентах
    """
    if len(original) == 0:
        return 0.0 if len(compared) == 0 else 100.0
    
    distance = calculate_levenshtein_distance(original, compared)
    cer = (distance / len(original)) * 100
    return cer


def calculate_text_metrics(original: str, compared: str) -> Dict[str, float]:
    """
    Расчёт всех метрик качества для сравнения текстов
    
    Args:
        original: Исходный текст
        compared: Текст для сравнения
    
    Returns:
        Словарь с метриками: Levenshtein, Similarity, Accuracy, CER
    """
    metrics = {
        'levenshtein_distance': calculate_levenshtein_distance(original, compared),
        'similarity_ratio': calculate_similarity_ratio(original, compared),
        'accuracy': calculate_accuracy(original, compared),
        'character_error_rate': calculate_character_error_rate(original, compared),
        'original_length': len(original),
        'compared_length': len(compared)
    }
    
    return metrics


def get_text_diff(original: str, compared: str, context_lines: int = 3) -> str:
    """
    Получить текстовое представление различий между строками
    
    Args:
        original: Исходный текст
        compared: Текст для сравнения
        context_lines: Количество строк контекста
    
    Returns:
        Unified diff строка
    """
    original_lines = original.splitlines(keepends=True)
    compared_lines = compared.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        compared_lines,
        fromfile='Оригинал',
        tofile='Восстановленный',
        lineterm='',
        n=context_lines
    )
    
    return ''.join(diff)


def get_inline_diff(original: str, compared: str) -> List[Tuple[str, str]]:
    """
    Получить посимвольное сравнение строк
    
    Возвращает список кортежей (тег, текст), где тег может быть:
    - 'equal': одинаковые символы
    - 'delete': удалённые символы
    - 'insert': вставленные символы
    - 'replace': заменённые символы
    
    Args:
        original: Исходный текст
        compared: Текст для сравнения
    
    Returns:
        Список кортежей (тег, текст)
    """
    matcher = difflib.SequenceMatcher(None, original, compared)
    result = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result.append(('equal', original[i1:i2]))
        elif tag == 'delete':
            result.append(('delete', original[i1:i2]))
        elif tag == 'insert':
            result.append(('insert', compared[j1:j2]))
        elif tag == 'replace':
            result.append(('delete', original[i1:i2]))
            result.append(('insert', compared[j1:j2]))
    
    return result


def compare_texts(original: str, compared: str) -> Tuple[str, Dict[str, float]]:
    """
    Сравнение двух текстов с расчётом метрик и unified diff
    
    Args:
        original: Исходный текст
        compared: Текст для сравнения
    
    Returns:
        Кортеж: (unified diff, словарь метрик)
    """
    metrics = calculate_text_metrics(original, compared)
    diff = get_text_diff(original, compared)
    
    return diff, metrics


def get_quality_description(metrics: Dict[str, float]) -> str:
    """
    Получить текстовое описание качества восстановления текста
    
    Args:
        metrics: Словарь с метриками
    
    Returns:
        Текстовое описание качества
    """
    accuracy = metrics.get('accuracy', 0)
    cer = metrics.get('character_error_rate', 100)
    
    if accuracy == 100.0:
        return "Идеальное восстановление (100%)"
    elif accuracy >= 99.0:
        return "Отличное качество (незначительные различия)"
    elif accuracy >= 95.0:
        return "Хорошее качество"
    elif accuracy >= 90.0:
        return "Приемлемое качество"
    elif accuracy >= 80.0:
        return "Удовлетворительное качество"
    else:
        return "Низкое качество (значительные ошибки)"


def format_metrics(metrics: Dict[str, float]) -> str:
    """
    Форматирование метрик для вывода
    
    Args:
        metrics: Словарь с метриками
    
    Returns:
        Отформатированная строка с метриками
    """
    distance = metrics.get('levenshtein_distance', 0)
    similarity = metrics.get('similarity_ratio', 0)
    accuracy = metrics.get('accuracy', 0)
    cer = metrics.get('character_error_rate', 0)
    orig_len = metrics.get('original_length', 0)
    comp_len = metrics.get('compared_length', 0)
    
    result = f"""Метрики качества текста:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Расстояние Левенштейна:  {distance} операций
Коэффициент сходства:    {similarity:.4f} ({similarity*100:.2f}%)
Точность восстановления: {accuracy:.2f}%
CER (Character Error Rate): {cer:.2f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Длина оригинала:         {orig_len} символов
Длина восстановленного:  {comp_len} символов
Разница в длине:         {abs(orig_len - comp_len)} символов
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Оценка качества: {get_quality_description(metrics)}
"""
    return result
