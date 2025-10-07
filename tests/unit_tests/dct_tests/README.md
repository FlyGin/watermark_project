# DCT Unit Tests

Юнит-тесты для алгоритма встраивания водяных знаков на основе DCT (Discrete Cosine Transform).

## Структура

```
dct_tests/
├── __init__.py
├── test_dct_text.py    # Тесты для текстовых водяных знаков
└── test_dct_image.py   # Тесты для графических водяных знаков
```

## Запуск тестов

### Все DCT тесты
```bash
python -m unittest discover -s tests/unit_tests/dct_tests
```

### Только текстовые тесты
```bash
python -m unittest tests.unit_tests.dct_tests.test_dct_text
```

### Только тесты изображений
```bash
python -m unittest tests.unit_tests.dct_tests.test_dct_image
```

### Конкретный тест
```bash
python -m unittest tests.unit_tests.dct_tests.test_dct_text.TestDCTText.test_dct_text_embed_extract_basic
```

## Описание тестов

### test_dct_text.py (7 тестов)

1. **test_dct_text_embed_extract_basic** - Базовая проверка встраивания и извлечения текста
2. **test_dct_text_different_strengths** - Тесты с различными значениями силы встраивания (10, 15, 20, 30)
3. **test_dct_text_grayscale_image** - Работа с чёрно-белыми изображениями
4. **test_dct_text_cyrillic** - Поддержка кириллицы и UTF-8
5. **test_dct_text_long_message** - Встраивание длинных текстовых сообщений
6. **test_dct_text_capacity_error** - Проверка исключения при превышении ёмкости
7. **test_dct_text_empty_string** - Обработка пустых строк

### test_dct_image.py (9 тестов)

1. **test_dct_image_embed_extract_basic** - Базовая проверка встраивания и извлечения изображения
2. **test_dct_image_color_secret** - Работа с цветными секретными изображениями
3. **test_dct_image_different_strengths** - Тесты с различными значениями силы (10, 15, 25, 40)
4. **test_dct_image_small_secret** - Встраивание маленьких изображений
5. **test_dct_image_rectangular_secret** - Прямоугольные секретные изображения
6. **test_dct_image_capacity_error** - Проверка исключения при превышении ёмкости
7. **test_dct_image_grayscale_to_color** - Встраивание ч/б секрета в цветное изображение
8. **test_dct_image_binary_secret** - Бинарные изображения (только 0 и 255)
9. **test_dct_image_single_pixel** - Однопиксельные секреты

## Особенности DCT алгоритма

- **Блочная обработка**: DCT работает с блоками 8x8 пикселей
- **Ёмкость**: 1 бит на блок (ограничено по сравнению с LSB)
- **Робастность**: Более устойчив к сжатию и модификациям
- **Качество**: Минимальные визуальные искажения при правильных параметрах

## Параметры алгоритма

- `strength` (по умолчанию 10-15): Сила встраивания водяного знака
  - Меньшие значения: меньше искажений, хуже устойчивость
  - Большие значения: больше искажений, лучше устойчивость
- `block_size` (по умолчанию 8): Размер блока для DCT преобразования
- `length`: Длина текста в байтах (для извлечения текста)
- `secret_shape`: Форма секретного изображения (для извлечения изображения)

## Результаты тестирования

```
Ran 16 tests in 0.415s
OK
```

Все тесты успешно пройдены ✓
