# gui/layout.py
# ============================================================================
# ФАЙЛ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА (UI)
# ============================================================================
# Этот файл отвечает за создание внешнего вида программы - где располагаются
# кнопки, поля ввода, окна предпросмотра и другие элементы интерфейса.
# 
# Основные компоненты PyQt5 для создания интерфейса:
# - QWidget: базовый виджет-контейнер
# - QVBoxLayout/QHBoxLayout: размещение виджетов вертикально/горизонтально
# - QLabel: текстовые надписи
# - QPushButton: кнопки для нажатия
# - QComboBox: выпадающий список
# - QSpinBox: поле для ввода чисел с кнопками +/-
# - QLineEdit: поле для ввода текста
# - QTextEdit: многострочное текстовое поле
# - QFrame: рамка-контейнер для группировки элементов
# ============================================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QFileDialog, QLineEdit, QSpinBox,
    QScrollArea, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

def create_main_layout(parent):
    """
    ========================================================================
    ГЛАВНАЯ ФУНКЦИЯ СОЗДАНИЯ ИНТЕРФЕЙСА
    ========================================================================
    Эта функция создает весь интерфейс программы и возвращает готовый виджет.
    
    Аргументы:
    - parent: главное окно программы, к которому привязываются все элементы
    
    Возвращает:
    - main_widget: готовый виджет с полным интерфейсом
    
    Структура интерфейса (сверху вниз):
    1. Выбор алгоритма и глубины встраивания
    2. Кнопки загрузки файлов
    3. Поле ввода текста (альтернатива файлу)
    4. Окна предпросмотра изображений
    5. Кнопки действий (встроить/извлечь/сбросить)
    6. Область вывода результатов
    ========================================================================
    """
    # Создаем главный контейнер - это основа всего интерфейса
    main_widget = QWidget(parent)
    main_widget.setSizePolicy(main_widget.sizePolicy().Expanding, main_widget.sizePolicy().Expanding)
    # Создаем вертикальную компоновку - все элементы будут располагаться сверху вниз
    layout = QVBoxLayout(main_widget)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)
    
    # ========================================================================
    # СЕКЦИЯ 1: ВЫБОР АЛГОРИТМА И НАСТРОЕК
    # ========================================================================
    # Здесь пользователь выбирает алгоритм стеганографии и его параметры
    
    # Создаем горизонтальную компоновку для размещения элементов в одну строку
    algo_layout = QHBoxLayout()
    
    # --- Выбор алгоритма стеганографии ---
    label_algo = QLabel("Алгоритм:")  # Текстовая надпись
    combo_algo = QComboBox()          # Выпадающий список
    combo_algo.addItems(["LSB", "DCT"])  # Доступные алгоритмы: LSB и DCT
    
    # --- Параметры для LSB ---
    label_depth = QLabel("Глубина:")  # Надпись для поля глубины
    spinbox_depth = QSpinBox()        # Поле для ввода числа с кнопками +/-
    spinbox_depth.setRange(1, 8)      # Диапазон: от 1 до 8 бит
    spinbox_depth.setValue(1)         # Значение по умолчанию: 1 бит
    spinbox_depth.setSuffix(" бит")   # Добавляем текст после числа
    
    # --- Параметры для DCT ---
    label_strength = QLabel("Сила:")  # Надпись для силы встраивания
    spinbox_strength = QSpinBox()     # Поле для ввода силы
    spinbox_strength.setRange(5, 50)  # Диапазон: от 5 до 50
    spinbox_strength.setValue(15)     # Значение по умолчанию: 15
    spinbox_strength.setVisible(False)  # Скрываем по умолчанию
    label_strength.setVisible(False)    # Скрываем надпись
    
    label_block_size = QLabel("Размер блока:")  # Надпись для размера блока
    spinbox_block_size = QSpinBox()              # Поле для размера блока
    spinbox_block_size.setRange(4, 16)           # Диапазон: от 4 до 16
    spinbox_block_size.setValue(8)               # Значение по умолчанию: 8
    spinbox_block_size.setVisible(False)         # Скрываем по умолчанию
    label_block_size.setVisible(False)           # Скрываем надпись
    
    # Размещаем все элементы в горизонтальную компоновку
    algo_layout.addWidget(label_algo)
    algo_layout.addWidget(combo_algo)
    algo_layout.addWidget(label_depth)
    algo_layout.addWidget(spinbox_depth)
    algo_layout.addWidget(label_strength)
    algo_layout.addWidget(spinbox_strength)
    algo_layout.addWidget(label_block_size)
    algo_layout.addWidget(spinbox_block_size)
    algo_layout.addStretch()  # Добавляем растягивающийся элемент для красивого выравнивания
    
    # Добавляем всю секцию в главную вертикальную компоновку
    layout.addLayout(algo_layout)
    

    # ========================================================================
    # СЕКЦИЯ 2 и 3: ЗАГРУЗКА ИСХОДНОГО ИЗОБРАЖЕНИЯ И ВОДЯНОГО ЗНАКА
    # ========================================================================
    # В этой секции используется табличный лайаут (QGridLayout) для размещения
    # кнопок загрузки и окон предпросмотра. Элементы располагаются следующим образом:
    # - Левый столбец: кнопка загрузки исходного изображения и его предпросмотр
    # - Правый столбец: кнопка загрузки водяного знака (или ввода текста) и его предпросмотр


    upload_preview_layout_grid = QGridLayout()

    # --- 1 колонка: Исходное изображение ---
    btn_load_cover = QPushButton("Загрузить исходное изображение")
    upload_preview_layout_grid.addWidget(btn_load_cover, 0, 0)

    cover_preview_frame = QFrame()
    cover_preview_frame.setFrameStyle(QFrame.StyledPanel)
    cover_preview_layout = QVBoxLayout(cover_preview_frame)
    cover_preview_label = QLabel("Исходное изображение")
    cover_preview_label.setAlignment(Qt.AlignCenter)
    cover_preview_layout.addWidget(cover_preview_label)
    cover_image_label = QLabel("Изображение не загружено")
    cover_image_label.setAlignment(Qt.AlignCenter)
    cover_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    cover_image_label.setScaledContents(True)
    from PyQt5.QtWidgets import QSizePolicy
    cover_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    cover_preview_layout.addWidget(cover_image_label)
    upload_preview_layout_grid.addWidget(cover_preview_frame, 1, 0)

    # --- 2 колонка: Водяной знак ---
    wm_upload_layout = QVBoxLayout()
    btn_load_wm = QPushButton("Загрузить файл водяного знака / текста")
    wm_upload_layout.addWidget(btn_load_wm)
    # Информационная строка вместо поля ввода текста
    info_label = QLabel("Можно загрузить изображение \nили .txt файл для встраивания текста.")
    info_label.setStyleSheet("color: #888; font-size: 12px;")
    wm_upload_layout.addWidget(info_label)
    upload_preview_layout_grid.addLayout(wm_upload_layout, 0, 1)

    secret_preview_frame = QFrame()
    secret_preview_frame.setFrameStyle(QFrame.StyledPanel)
    secret_preview_layout = QVBoxLayout(secret_preview_frame)
    secret_preview_label = QLabel("Секретное изображение/текст")
    secret_preview_label.setAlignment(Qt.AlignCenter)
    secret_preview_layout.addWidget(secret_preview_label)
    secret_image_label = QLabel("Файл не загружен")
    secret_image_label.setAlignment(Qt.AlignCenter)
    secret_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    secret_image_label.setScaledContents(True)
    secret_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    secret_preview_layout.addWidget(secret_image_label)
    upload_preview_layout_grid.addWidget(secret_preview_frame, 1, 1)

    # --- 3 колонка: Встраивание и результат ---
    embed_layout = QVBoxLayout()
    btn_embed = QPushButton("🔒 Встроить")
    btn_save_result = QPushButton("💾 Сохранить результат")
    btn_save_result.setEnabled(False)  # Неактивна, пока нет результата
    embed_layout.addWidget(btn_embed)
    embed_layout.addWidget(btn_save_result)
    upload_preview_layout_grid.addLayout(embed_layout, 0, 2)

    stego_preview_frame = QFrame()
    stego_preview_frame.setFrameStyle(QFrame.StyledPanel)
    stego_preview_layout = QVBoxLayout(stego_preview_frame)
    stego_preview_label = QLabel("Стегоизображение/текст")
    stego_preview_label.setAlignment(Qt.AlignCenter)
    stego_preview_layout.addWidget(stego_preview_label)
    stego_image_label = QLabel("Нет результата")
    stego_image_label.setAlignment(Qt.AlignCenter)
    stego_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    stego_image_label.setScaledContents(True)
    stego_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    stego_preview_layout.addWidget(stego_image_label)
    upload_preview_layout_grid.addWidget(stego_preview_frame, 1, 2)

    # --- 4 колонка: Извлечение и восстановленный секрет ---
    extract_layout = QVBoxLayout()
    btn_extract = QPushButton("🔍 Извлечь")
    btn_save_secret = QPushButton("💾 Сохранить восстановленный секрет")
    btn_save_secret.setEnabled(False)
    extract_layout.addWidget(btn_extract)
    extract_layout.addWidget(btn_save_secret)
    upload_preview_layout_grid.addLayout(extract_layout, 0, 3)

    restored_preview_frame = QFrame()
    restored_preview_frame.setFrameStyle(QFrame.StyledPanel)
    restored_preview_layout = QVBoxLayout(restored_preview_frame)
    restored_preview_label = QLabel("Восстановленный секрет (извлечён)")
    restored_preview_label.setAlignment(Qt.AlignCenter)
    restored_preview_layout.addWidget(restored_preview_label)
    restored_image_label = QLabel("Нет результата")
    restored_image_label.setAlignment(Qt.AlignCenter)
    restored_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    restored_image_label.setScaledContents(True)
    restored_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    restored_preview_layout.addWidget(restored_image_label)
    upload_preview_layout_grid.addWidget(restored_preview_frame, 1, 3)

    layout.addLayout(upload_preview_layout_grid)
    
    
    # ========================================================================
    # СЕКЦИЯ 5: КНОПКИ ОСНОВНЫХ ДЕЙСТВИЙ
    # ========================================================================
    # Три главные кнопки для выполнения операций стеганографии
    
    actions_layout = QHBoxLayout()
    btn_reset = QPushButton("🗑️ Сбросить")
    actions_layout.addWidget(btn_reset)
    layout.addLayout(actions_layout)
    
    # ========================================================================
    # СЕКЦИЯ 6: ОБЛАСТЬ ВЫВОДА РЕЗУЛЬТАТОВ
    # ========================================================================
    # Текстовая область для отображения сообщений о ходе выполнения операций
    
    result_label = QLabel("Результат:")  # Заголовок для области результатов
    result_text = QTextEdit()            # Многострочное текстовое поле
    result_text.setReadOnly(True)        # Только для чтения (пользователь не может редактировать)
    # В этой области будут отображаться:
    # - Сообщения о загрузке файлов
    # - Результаты встраивания/извлечения
    # - Ошибки и предупреждения
    
    layout.addWidget(result_label)
    layout.addWidget(result_text)
    
    # ========================================================================
    # СОХРАНЕНИЕ ССЫЛОК НА ВИДЖЕТЫ
    # ========================================================================
    # Сохраняем ссылки на все важные виджеты в объекте parent, чтобы
    # к ним можно было обращаться из других файлов (например, events.py)
    # 
    # Это позволяет обработчикам событий получать доступ к элементам интерфейса:
    # - Читать значения из полей ввода
    # - Изменять содержимое текстовых областей
    # - Обновлять изображения в окнах предпросмотра
    
    parent.combo_algo = combo_algo
    parent.spinbox_depth = spinbox_depth
    parent.label_depth = label_depth
    parent.spinbox_strength = spinbox_strength
    parent.label_strength = label_strength
    parent.spinbox_block_size = spinbox_block_size
    parent.label_block_size = label_block_size
    parent.btn_load_cover = btn_load_cover
    parent.btn_load_wm = btn_load_wm
    parent.info_label = info_label
    parent.btn_embed = btn_embed
    parent.btn_save_result = btn_save_result
    parent.btn_extract = btn_extract
    parent.btn_save_secret = btn_save_secret
    parent.btn_reset = btn_reset
    parent.result_text = result_text
    parent.cover_image_label = cover_image_label
    parent.secret_image_label = secret_image_label
    parent.stego_image_label = stego_image_label
    parent.restored_image_label = restored_image_label

    # Возвращаем готовый виджет с полным интерфейсом
    return main_widget
