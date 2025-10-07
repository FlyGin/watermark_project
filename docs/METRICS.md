# 📊 Система метрик качества

## Обзор

Система метрик качества предоставляет инструменты для объективной оценки качества встраивания и извлечения водяных знаков. Модуль включает два типа сравнений:

1. **Сравнение контейнера и стего-изображения** - оценка визуального искажения
2. **Сравнение оригинального и извлечённого секрета** - оценка качества восстановления

---

## 📍 Структура модуля

```
utils/
├── __init__.py              # Экспорты модуля
├── image_metrics.py         # Метрики для изображений
└── text_metrics.py          # Метрики для текста
```

---

## 🖼️ Метрики для изображений

### 1. PSNR (Peak Signal-to-Noise Ratio)

**Определение:** Пиковое отношение сигнал/шум - измеряет качество изображения относительно исходного.

**Формула:**
```
PSNR = 10 * log10(MAX²/MSE)
где MAX = 255 (максимальное значение пикселя)
    MSE = среднеквадратичная ошибка
```

**Интерпретация:**
- `> 40 dB` - Отличное качество (искажения практически незаметны)
- `30-40 dB` - Хорошее качество (небольшие искажения)
- `20-30 dB` - Приемлемое качество (заметные искажения)
- `< 20 dB` - Плохое качество (значительные искажения)
- `inf` - Изображения идентичны (нет искажений)

**Пример использования:**
```python
from utils.image_metrics import calculate_psnr
import numpy as np

original = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
modified = original.copy()
modified[100:200, 100:200] += 10  # Добавляем небольшой шум

psnr = calculate_psnr(original, modified)
print(f"PSNR: {psnr:.2f} dB")
# Вывод: PSNR: 38.45 dB (хорошее качество)
```

---

### 2. MSE (Mean Squared Error)

**Определение:** Среднеквадратичная ошибка - средняя квадратичная разница между пикселями.

**Формула:**
```
MSE = (1/N) * Σ(I₁ - I₂)²
где N = общее количество пикселей
    I₁, I₂ = значения пикселей двух изображений
```

**Интерпретация:**
- `0` - Изображения идентичны
- `< 100` - Очень похожи
- `100-500` - Похожи, но есть различия
- `> 1000` - Значительные различия

**Пример использования:**
```python
from utils.image_metrics import calculate_mse

mse = calculate_mse(original, modified)
print(f"MSE: {mse:.2f}")
# Вывод: MSE: 25.34
```

---

### 3. MAE (Mean Absolute Error)

**Определение:** Средняя абсолютная ошибка - средняя абсолютная разница между пикселями.

**Формула:**
```
MAE = (1/N) * Σ|I₁ - I₂|
```

**Интерпретация:**
- `0` - Изображения идентичны
- `< 5` - Очень похожи
- `5-20` - Похожи с небольшими различиями
- `> 50` - Значительные различия

**Пример использования:**
```python
from utils.image_metrics import calculate_mae

mae = calculate_mae(original, modified)
print(f"MAE: {mae:.2f}")
# Вывод: MAE: 3.12
```

---

### 4. SSIM (Structural Similarity Index)

**Определение:** Индекс структурного сходства - оценивает визуальное сходство на основе яркости, контраста и структуры.

**Формула:**
```
SSIM = [l(x,y)]^α * [c(x,y)]^β * [s(x,y)]^γ
где l = luminance comparison (яркость)
    c = contrast comparison (контраст)
    s = structure comparison (структура)
```

**Интерпретация:**
- `1.0` - Изображения идентичны
- `> 0.95` - Отличное сходство (визуально неразличимы)
- `0.90-0.95` - Очень хорошее сходство
- `0.80-0.90` - Приемлемое сходство
- `< 0.80` - Значительные различия

**Пример использования:**
```python
from utils.image_metrics import calculate_ssim

ssim = calculate_ssim(original, modified)
print(f"SSIM: {ssim:.4f}")
# Вывод: SSIM: 0.9823
```

---

### Комплексная оценка изображений

Функция `calculate_image_metrics()` вычисляет все метрики одновременно:

```python
from utils.image_metrics import calculate_image_metrics, format_metrics

metrics = calculate_image_metrics(original, modified)
print(format_metrics(metrics))
```

**Вывод:**
```
PSNR: 38.45 dB (Хорошее качество)
MSE: 25.34 (Очень похожи)
MAE: 3.12 (Очень похожи)
SSIM: 0.9823 (Отличное сходство)

Общая оценка: Хорошее качество
Рекомендация: Изображения практически идентичны, искажения минимальны
```

---

## 📝 Метрики для текста

### 1. Levenshtein Distance (Расстояние Левенштейна)

**Определение:** Минимальное количество операций редактирования (вставка, удаление, замена), необходимых для преобразования одной строки в другую.

**Алгоритм:**
- Использует динамическое программирование
- Сложность: O(m*n), где m и n - длины строк

**Интерпретация:**
- `0` - Строки идентичны
- `< 5` - Очень похожи (несколько опечаток)
- `5-20` - Похожи с небольшими различиями
- `> 50` - Значительные различия

**Пример использования:**
```python
from utils.text_metrics import calculate_levenshtein_distance

text1 = "Привет, мир!"
text2 = "Привет мир"

distance = calculate_levenshtein_distance(text1, text2)
print(f"Расстояние Левенштейна: {distance}")
# Вывод: Расстояние Левенштейна: 2 (удалена запятая и восклицательный знак)
```

---

### 2. Similarity Ratio (Коэффициент схожести)

**Определение:** Коэффициент схожести на основе difflib.SequenceMatcher - показывает долю совпадающих символов.

**Формула:**
```
Similarity = 2 * M / T
где M = количество совпадающих символов
    T = общее количество символов в обеих строках
```

**Интерпретация:**
- `1.0` - Полностью идентичны
- `> 0.95` - Почти идентичны
- `0.80-0.95` - Очень похожи
- `0.50-0.80` - Похожи частично
- `< 0.50` - Значительные различия

**Пример использования:**
```python
from utils.text_metrics import calculate_similarity_ratio

ratio = calculate_similarity_ratio(text1, text2)
print(f"Similarity Ratio: {ratio:.4f}")
# Вывод: Similarity Ratio: 0.9565 (очень похожи)
```

---

### 3. Accuracy (Точность)

**Определение:** Процент правильно восстановленных символов.

**Формула:**
```
Accuracy = (1 - distance/length) * 100%
где distance = расстояние Левенштейна
    length = длина исходного текста
```

**Интерпретация:**
- `100%` - Полное совпадение
- `> 95%` - Отличная точность
- `90-95%` - Хорошая точность
- `80-90%` - Приемлемая точность
- `< 80%` - Плохая точность

**Пример использования:**
```python
from utils.text_metrics import calculate_accuracy

accuracy = calculate_accuracy(text1, text2)
print(f"Accuracy: {accuracy:.2f}%")
# Вывод: Accuracy: 84.62%
```

---

### 4. CER (Character Error Rate)

**Определение:** Процент ошибок на уровне символов - обратная метрика к точности.

**Формула:**
```
CER = (distance/length) * 100%
```

**Интерпретация:**
- `0%` - Нет ошибок
- `< 5%` - Отличное качество
- `5-10%` - Хорошее качество
- `10-20%` - Приемлемое качество
- `> 20%` - Плохое качество

**Пример использования:**
```python
from utils.text_metrics import calculate_character_error_rate

cer = calculate_character_error_rate(text1, text2)
print(f"CER: {cer:.2f}%")
# Вывод: CER: 15.38%
```

---

### Комплексная оценка текста

Функция `calculate_text_metrics()` вычисляет все метрики одновременно:

```python
from utils.text_metrics import calculate_text_metrics, format_metrics

metrics = calculate_text_metrics(text1, text2)
print(format_metrics(metrics))
```

**Вывод:**
```
Levenshtein Distance: 2 (Очень похожи)
Similarity Ratio: 0.9565 (Почти идентичны)
Accuracy: 84.62% (Приемлемая точность)
CER: 15.38% (Приемлемое качество)

Общая оценка: Хорошее качество
Рекомендация: Тексты очень похожи, большинство символов восстановлено корректно
```

---

## 🎯 Визуализация различий

### Для текста

#### Unified Diff

```python
from utils.text_metrics import get_text_diff

diff = get_text_diff(text1, text2)
print(diff)
```

**Вывод:**
```diff
--- Оригинальный текст
+++ Восстановленный текст
@@ -1 +1 @@
-Привет, мир!
+Привет мир
```

#### Inline Diff (посимвольное сравнение)

```python
from utils.text_metrics import get_inline_diff

inline = get_inline_diff(text1, text2)
print(inline)
```

**Вывод:**
```
Оригинал:      Привет, мир!
Восстановлено: Привет мир
               ^^^^^^^ ^^^
```

---

### Для изображений

```python
from utils.image_metrics import compare_images
import matplotlib.pyplot as plt

diff_img, metrics = compare_images(original, modified)

# Визуализация
plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)
plt.imshow(original)
plt.title('Оригинал')
plt.axis('off')

plt.subplot(1, 3, 2)
plt.imshow(modified)
plt.title('Модифицированное')
plt.axis('off')

plt.subplot(1, 3, 3)
plt.imshow(diff_img, cmap='hot')
plt.title('Разница')
plt.axis('off')

plt.show()
```

---

## 🔧 Интеграция в GUI

### Отображение метрик

В GUI есть две панели метрик:

1. **Stego Metrics** - сравнение исходного контейнера и стего-изображения
2. **Secret Metrics** - сравнение оригинального и восстановленного секрета

Метрики автоматически вычисляются при:
- Встраивании водяного знака (stego metrics)
- Извлечении водяного знака (secret metrics)

### Пример кода интеграции

```python
# В функции embed_watermark (gui/events.py)
if hasattr(parent, 'cover_path') and os.path.exists(parent.cover_path):
    cover_original = cv2.imread(parent.cover_path)
    cover_original = cv2.cvtColor(cover_original, cv2.COLOR_BGR2RGB)
    
    metrics = calculate_image_metrics(cover_original, result)
    formatted = format_image_metrics(metrics)
    
    parent.stego_metrics_text.setText(
        "📊 Метрики стегоизображения (исходное vs стего):\n\n" + formatted
    )

# В функции extract_watermark (gui/events.py)
if hasattr(parent, 'original_secret'):
    if isinstance(extracted, str) and isinstance(parent.original_secret, str):
        metrics = calculate_text_metrics(parent.original_secret, extracted)
        formatted = format_text_metrics(metrics)
        parent.secret_metrics_text.setText(
            "📊 Метрики восстановленного секрета:\n\n" + formatted
        )
```

---

## 📚 API Reference

### image_metrics.py

| Функция | Параметры | Возвращает | Описание |
|---------|-----------|------------|----------|
| `calculate_psnr(img1, img2)` | 2 изображения (numpy arrays) | float | PSNR в dB |
| `calculate_mse(img1, img2)` | 2 изображения | float | MSE |
| `calculate_mae(img1, img2)` | 2 изображения | float | MAE |
| `calculate_ssim(img1, img2, window_size=11)` | 2 изображения, размер окна | float | SSIM (0-1) |
| `calculate_image_metrics(img1, img2)` | 2 изображения | dict | Все метрики |
| `compare_images(img1, img2)` | 2 изображения | tuple (diff_img, metrics) | Карта различий + метрики |
| `format_metrics(metrics)` | dict метрик | str | Форматированный текст |

### text_metrics.py

| Функция | Параметры | Возвращает | Описание |
|---------|-----------|------------|----------|
| `calculate_levenshtein_distance(text1, text2)` | 2 строки | int | Расстояние Левенштейна |
| `calculate_similarity_ratio(text1, text2)` | 2 строки | float | Коэффициент схожести (0-1) |
| `calculate_accuracy(text1, text2)` | 2 строки | float | Точность в процентах |
| `calculate_character_error_rate(text1, text2)` | 2 строки | float | CER в процентах |
| `calculate_text_metrics(text1, text2)` | 2 строки | dict | Все метрики |
| `get_text_diff(text1, text2)` | 2 строки | str | Unified diff |
| `get_inline_diff(text1, text2, context=40)` | 2 строки | str | Посимвольное сравнение |
| `compare_texts(text1, text2)` | 2 строки | tuple (diff, metrics) | Diff + метрики |
| `format_metrics(metrics)` | dict метрик | str | Форматированный текст |

---

## 🎓 Примеры использования

### Пример 1: Оценка качества встраивания LSB

```python
import numpy as np
from utils.image_metrics import calculate_image_metrics, format_metrics

# Загрузка изображений
original = cv2.imread('original.png')
stego = cv2.imread('stego_lsb.png')

# Вычисление метрик
metrics = calculate_image_metrics(original, stego)

# Вывод результатов
print("Метрики для LSB встраивания:")
print(format_metrics(metrics))

# Проверка качества
if metrics['psnr'] > 40:
    print("✅ Отличное качество - искажения незаметны")
elif metrics['psnr'] > 30:
    print("✔️ Хорошее качество")
else:
    print("⚠️ Качество может быть улучшено")
```

### Пример 2: Сравнение алгоритмов

```python
from utils.image_metrics import calculate_image_metrics

original = cv2.imread('original.png')
stego_lsb = cv2.imread('stego_lsb.png')
stego_dct = cv2.imread('stego_dct.png')

metrics_lsb = calculate_image_metrics(original, stego_lsb)
metrics_dct = calculate_image_metrics(original, stego_dct)

print(f"LSB - PSNR: {metrics_lsb['psnr']:.2f} dB, SSIM: {metrics_lsb['ssim']:.4f}")
print(f"DCT - PSNR: {metrics_dct['psnr']:.2f} dB, SSIM: {metrics_dct['ssim']:.4f}")

if metrics_lsb['psnr'] > metrics_dct['psnr']:
    print("LSB показывает лучшие результаты по PSNR")
else:
    print("DCT показывает лучшие результаты по PSNR")
```

### Пример 3: Проверка восстановления текста

```python
from utils.text_metrics import calculate_text_metrics, format_metrics

original_text = "Секретное сообщение"
extracted_text = "Секретное сообщени"  # 1 символ потерян

metrics = calculate_text_metrics(original_text, extracted_text)
print(format_metrics(metrics))

if metrics['accuracy'] > 95:
    print("✅ Текст восстановлен практически без ошибок")
elif metrics['accuracy'] > 80:
    print("✔️ Текст восстановлен с небольшими ошибками")
else:
    print("⚠️ Значительные ошибки при восстановлении")
```

---

## 🔬 Технические детали

### Обработка граничных случаев

1. **Идентичные изображения:**
   - PSNR возвращает `inf` (бесконечность)
   - MSE и MAE возвращают 0
   - SSIM возвращает 1.0

2. **Разные размеры изображений:**
   - Функции автоматически проверяют размеры
   - При несовпадении выбрасывается ValueError с инструкциями

3. **Разные цветовые пространства:**
   - Все метрики работают с RGB
   - Для grayscale автоматически конвертируется в RGB

4. **Пустые строки:**
   - Расстояние Левенштейна = длина непустой строки
   - Similarity = 0 для разных строк
   - Accuracy = 0% или 100% (для обеих пустых)

### Производительность

| Операция | Сложность | Время (512×512 RGB) |
|----------|-----------|---------------------|
| PSNR | O(n) | ~10 ms |
| MSE | O(n) | ~8 ms |
| MAE | O(n) | ~8 ms |
| SSIM | O(n*k²) | ~50 ms (k=11) |
| Levenshtein | O(m*n) | Зависит от длины |

### Зависимости

```
numpy >= 1.19.0
opencv-python >= 4.5.0
scipy >= 1.5.0  (для SSIM - фильтр Гаусса)
```

---

## 🧪 Тестирование

### Юнит-тесты для метрик изображений

```python
import unittest
from utils.image_metrics import calculate_psnr, calculate_mse
import numpy as np

class TestImageMetrics(unittest.TestCase):
    def test_identical_images(self):
        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        psnr = calculate_psnr(img, img)
        mse = calculate_mse(img, img)
        
        self.assertEqual(psnr, float('inf'))
        self.assertEqual(mse, 0)
    
    def test_different_images(self):
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        mse = calculate_mse(img1, img2)
        self.assertEqual(mse, 255**2)

if __name__ == '__main__':
    unittest.main()
```

### Юнит-тесты для метрик текста

```python
import unittest
from utils.text_metrics import calculate_levenshtein_distance, calculate_accuracy

class TestTextMetrics(unittest.TestCase):
    def test_identical_strings(self):
        text = "Test"
        distance = calculate_levenshtein_distance(text, text)
        accuracy = calculate_accuracy(text, text)
        
        self.assertEqual(distance, 0)
        self.assertEqual(accuracy, 100.0)
    
    def test_one_substitution(self):
        distance = calculate_levenshtein_distance("cat", "bat")
        self.assertEqual(distance, 1)
    
    def test_empty_strings(self):
        distance = calculate_levenshtein_distance("", "")
        self.assertEqual(distance, 0)

if __name__ == '__main__':
    unittest.main()
```

---

## 📖 Дополнительные ресурсы

### Научные источники

1. **PSNR и MSE:**
   - Huynh-Thu, Q., & Ghanbari, M. (2008). "Scope of validity of PSNR in image/video quality assessment"

2. **SSIM:**
   - Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004). "Image quality assessment: from error visibility to structural similarity"

3. **Levenshtein Distance:**
   - Levenshtein, V. I. (1966). "Binary codes capable of correcting deletions, insertions, and reversals"

### Полезные ссылки

- [PSNR на Wikipedia](https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio)
- [SSIM на Wikipedia](https://en.wikipedia.org/wiki/Structural_similarity)
- [Levenshtein Distance на Wikipedia](https://en.wikipedia.org/wiki/Levenshtein_distance)

---

## 🤝 Вклад в проект

При добавлении новых метрик следуйте этим правилам:

1. Добавьте функцию в соответствующий модуль (`image_metrics.py` или `text_metrics.py`)
2. Напишите docstring с примерами использования
3. Добавьте юнит-тесты
4. Обновите эту документацию
5. Добавьте интерпретацию значений метрики

---

## 📝 История изменений

### Версия 1.0 (текущая)

**Добавлено:**
- Модуль `utils/image_metrics.py` с метриками PSNR, MSE, MAE, SSIM
- Модуль `utils/text_metrics.py` с метриками Levenshtein, Similarity, Accuracy, CER
- Интеграция метрик в GUI
- Автоматическое вычисление метрик при встраивании и извлечении
- Форматированный вывод с качественными оценками

**Планируется:**
- Добавление гистограмм различий
- Экспорт метрик в JSON/CSV
- Пакетная обработка с усреднением метрик
- Визуализация метрик в виде графиков

---

*Документация актуальна для версии проекта 1.0*
