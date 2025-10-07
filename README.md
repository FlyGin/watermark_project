# WatermarkProject

Проект для встраивания и извлечения цифровых водяных знаков в изображения с использованием различных стеганографических алгоритмов.

## Возможности проекта

### Алгоритмы
- **LSB (Least Significant Bit)** - классический побитовый метод с высокой ёмкостью
- **DCT (Discrete Cosine Transform)** - частотный метод, устойчивый к сжатию ✨
- **DWT (Discrete Wavelet Transform)** - вейвлет-преобразование
- **CNN-автокодировщик** - метод на основе нейронных сетей

### Функциональность
- 🖥️ **Графический интерфейс (GUI)** - удобный интерфейс на PySimpleGUI
- 💻 **Консольный режим (CLI)** - интерактивное меню с демонстрациями
- 📝 **Текстовые водяные знаки** - встраивание текстовых сообщений
- 🖼️ **Графические водяные знаки** - встраивание изображений в изображения
- ✅ **Тестирование** - полный набор юнит и интеграционных тестов
- 📊 **Визуализация** - сравнение результатов с метриками качества

## Структура проекта
```
watermark_project/
├── main.py                # Точка входа (GUI/CLI)
├── gui/                   # Модули графического интерфейса
│   ├── window.py         # Главное окно
│   ├── layout.py         # Компоновка элементов
│   └── events.py         # Обработчики событий
├── watermark/             # Основной пакет алгоритмов
│   ├── embedding.py      # Универсальный интерфейс встраивания
│   ├── extraction.py     # Универсальный интерфейс извлечения
│   └── algorithms/       # Реализации алгоритмов
│       ├── lsb/          # LSB алгоритмы (текст + изображения)
│       ├── dct/          # DCT алгоритмы (текст + изображения) ✨
│       ├── dwt.py        # DWT алгоритм
│       └── cnn_autoencoder.py  # CNN автокодировщик
├── tests/                # Тесты
│   ├── integration_tests/ # Интеграционные тесты с визуализацией
│   │   ├── text_demo.py  # Демо для текста (LSB)
│   │   └── image_demo.py # Демо для изображений (LSB)
│   └── unit_tests/       # Юнит-тесты
│       ├── lsb_tests/    # Тесты для LSB (7 тестов)
│       └── dct_tests/    # Тесты для DCT (16 тестов) ✨
├── requirements.txt      # Зависимости проекта
├── README.md             # Основная документация
└── CLI_GUIDE.md          # Руководство по CLI ✨
```

## Запуск приложения

### Графический интерфейс (по умолчанию)
```bash
python main.py
```

### Консольный режим (CLI)
```bash
python main.py --cli
```

**CLI функции:**
- Базовые примеры встраивания (LSB и DCT)
- Интерактивные демонстрации с визуализацией
- Запуск юнит и интеграционных тестов
- Настройка параметров алгоритмов

Подробное руководство: [CLI_GUIDE.md](CLI_GUIDE.md)

## Гайд по запуску тестов

### Все тесты
```bash
python -m unittest discover -s tests
```

### Интеграционные тесты
```bash
python -m unittest discover -s tests/integration_tests
```

### Юнит-тесты
```bash
# Все юнит-тесты
python -m unittest discover -s tests/unit_tests

# Только LSB тесты
python -m unittest discover -s tests/unit_tests/lsb_tests

# Только DCT тесты
python -m unittest discover -s tests/unit_tests/dct_tests
```

### Результаты тестирования

**LSB тесты:**
- `test_lsb_text.py` - 1 тест ✓
- `test_lsb_image.py` - 1 тест ✓

**DCT тесты:**
- `test_dct_text.py` - 7 тестов ✓
- `test_dct_image.py` - 9 тестов ✓

**Итого:** 18 юнит-тестов, все успешно пройдены

## Алгоритмы

### LSB (Least Significant Bit)
**Принцип:** Встраивание данных в младшие биты пикселей

**Преимущества:**
- ✅ Высокая ёмкость (1-8 бит на пиксель)
- ✅ Простая реализация
- ✅ Минимальные визуальные искажения

**Недостатки:**
- ❌ Низкая устойчивость к модификациям
- ❌ Не устойчив к сжатию

**Параметры:**
- `depth` (1-8) - количество младших бит для встраивания

### DCT (Discrete Cosine Transform)
**Принцип:** Модификация частотных коэффициентов DCT в блоках 8x8

**Преимущества:**
- ✅ Устойчивость к JPEG сжатию
- ✅ Робастность к модификациям
- ✅ Минимальные визуальные искажения
- ✅ **Автоматическое масштабирование секрета** (новое!)

**Недостатки:**
- ❌ Низкая ёмкость (1 бит на блок 8x8)
- ❌ Более сложная реализация

**Параметры:**
- `strength` (10-30) - сила встраивания
- `block_size` (обычно 8) - размер блока DCT

**Автоматическое масштабирование:**
- Секретное изображение автоматически уменьшается, если превышает ёмкость контейнера
- Сохраняются пропорции изображения
- При извлечении можно восстановить исходный размер
- Подробнее: `DCT_AUTO_SCALING.md`

### Сравнение алгоритмов

| Характеристика | LSB | DCT |
|---------------|-----|-----|
| Ёмкость | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Робастность | ⭐ | ⭐⭐⭐⭐ |
| Визуальное качество | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Устойчивость к сжатию | ❌ | ✅ |
| Скорость | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Сложность реализации | ⭐ | ⭐⭐⭐ |

## Список зависимостей
Основные зависимости перечислены в `requirements.txt`. Для установки используйте:
```bash
pip install -r requirements.txt
```

**Основные библиотеки:**
- `numpy` - работа с массивами и математические операции
- `opencv-python` - обработка изображений и DCT преобразования
- `pillow` - загрузка и сохранение изображений
- `PySimpleGUI` - графический интерфейс
- `matplotlib` - визуализация результатов
- `scikit-image` - дополнительная обработка изображений (опционально)
- `tensorflow` - CNN автокодировщик (опционально)

## Примеры использования

### Пример 1: Встраивание текста (LSB)
```python
from watermark.embedding import embed
from watermark.extraction import extract
import numpy as np

# Создаём изображение
image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

# Встраиваем текст
secret = "Секретное сообщение"
params = {"depth": 1}
stego = embed(image, secret, params, method="lsb")

# Извлекаем текст
params["length"] = len(secret.encode("utf-8"))
recovered = extract(stego, params, method="lsb")
print(recovered)  # "Секретное сообщение"
```

### Пример 2: Встраивание текста (DCT)
```python
from watermark.embedding import embed
from watermark.extraction import extract
import numpy as np

# Создаём изображение
image = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)

# Встраиваем текст
secret = "DCT водяной знак"
params = {"strength": 15, "block_size": 8}
stego = embed(image, secret, params, method="dct")

# Извлекаем текст
params["length"] = len(secret.encode("utf-8"))
recovered = extract(stego, params, method="dct")
print(recovered)  # "DCT водяной знак"
```

### Пример 3: Встраивание изображения (DCT)
```python
from watermark.embedding import embed
from watermark.extraction import extract
import numpy as np

# Контейнер и секрет
cover = np.random.randint(50, 200, (512, 512, 3), dtype=np.uint8)
secret = np.random.randint(0, 255, (16, 16), dtype=np.uint8)

# Встраивание
params = {"strength": 20, "block_size": 8}
stego = embed(cover, secret, params, method="dct")

# Извлечение
params["secret_shape"] = secret.shape
recovered = extract(stego, params, method="dct")

# Проверка качества
mae = np.mean(np.abs(secret - recovered))
print(f"MAE: {mae:.2f}")
```

## Расширение функциональности

### Добавление нового алгоритма

1. Создайте модуль в `watermark/algorithms/` с функциями:
```python
def embed(image: np.ndarray, secret, params: dict) -> np.ndarray:
    """Встраивание водяного знака"""
    pass

def extract(image: np.ndarray, params: dict):
    """Извлечение водяного знака"""
    pass
```

2. Зарегистрируйте алгоритм в `watermark/algorithms/__init__.py`:
```python
from . import your_algorithm

__all__ = ['lsb', 'dct', 'dwt', 'your_algorithm']
```

3. Добавьте в словарь алгоритмов в `embedding.py` и `extraction.py`:
```python
algorithms = {
    "lsb": lsb,
    "dct": dct,
    "your_algorithm": your_algorithm
}
```

4. Создайте юнит-тесты в `tests/unit_tests/your_algorithm_tests/`

## Документация

### Основная документация:
- **[README.md](README.md)** - основная документация (этот файл)
- **[requirements.txt](requirements.txt)** - список зависимостей

### Руководства пользователя:
- **[CLI_GUIDE.md](docs/CLI_GUIDE.md)** - руководство по консольному интерфейсу
- **[GUI_DCT_GUIDE.md](docs/GUI_DCT_GUIDE.md)** - руководство по использованию DCT в GUI

### Техническая документация:
- **[DCT_AUTO_SCALING.md](docs/DCT_AUTO_SCALING.md)** - автоматическое масштабирование для DCT ✨
- **[QUICK_START_DCT_AUTOSCALE.md](docs/QUICK_START_DCT_AUTOSCALE.md)** - быстрый старт с DCT ✨
- **[ENCODING_FIX.md](docs/ENCODING_FIX.md)** - поддержка различных кодировок текста ✨
- **[CAPACITY_CHECK.md](docs/CAPACITY_CHECK.md)** - проверка ёмкости перед встраиванием ✨
- **[CHANGELOG_DCT_AUTOSCALE.md](docs/CHANGELOG_DCT_AUTOSCALE.md)** - история изменений ✨
- **[SUMMARY_IMPROVEMENTS.md](docs/SUMMARY_IMPROVEMENTS.md)** - сводка улучшений v1.1.x ✨

### Документация тестов:
- **[tests/unit_tests/dct_tests/README.md](tests/unit_tests/dct_tests/README.md)** - документация DCT тестов

## Технические детали

**Язык:** Python 3.8+  
**Лицензия:** Образовательный проект  
**Автор:** Разработано в рамках ВКР  

---

Если возникнут вопросы по запуску или структуре, смотрите дополнительные гайды в папке `helpers` или обращайтесь к автору проекта.