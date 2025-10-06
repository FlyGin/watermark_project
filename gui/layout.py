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
    
    # Создаем вертикальную компоновку - все элементы будут располагаться сверху вниз
    layout = QVBoxLayout(main_widget)
    
    # ========================================================================
    # СЕКЦИЯ 1: ВЫБОР АЛГОРИТМА И НАСТРОЕК
    # ========================================================================
    # Здесь пользователь выбирает алгоритм стеганографии и его параметры
    
    # Создаем горизонтальную компоновку для размещения элементов в одну строку
    algo_layout = QHBoxLayout()
    
    # --- Выбор алгоритма стеганографии ---
    label_algo = QLabel("Алгоритм:")  # Текстовая надпись
    combo_algo = QComboBox()          # Выпадающий список
    combo_algo.addItems(["LSB"])      # Пока доступен только алгоритм LSB
    # В будущем можно добавить: ["LSB", "DCT", "DWT"]
    
    # --- Выбор глубины встраивания ---
    label_depth = QLabel("Глубина:")  # Надпись для поля глубины
    spinbox_depth = QSpinBox()        # Поле для ввода числа с кнопками +/-
    spinbox_depth.setRange(1, 8)      # Диапазон: от 1 до 8 бит
    spinbox_depth.setValue(1)         # Значение по умолчанию: 1 бит
    spinbox_depth.setSuffix(" бит")   # Добавляем текст после числа
    
    # Размещаем все элементы в горизонтальную компоновку
    algo_layout.addWidget(label_algo)
    algo_layout.addWidget(combo_algo)
    algo_layout.addWidget(label_depth)
    algo_layout.addWidget(spinbox_depth)
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

    upload_preview_layout = QHBoxLayout()  # Основная горизонтальная компоновка
    upload_preview_layout_grid = QGridLayout()  # Основная горизонтальная компоновка

    # Исходное изображение

    # Кнопка загрузки исходного изображения
    btn_load_cover = QPushButton("Загрузить исходное изображение")
    upload_preview_layout_grid.addWidget(btn_load_cover, 0, 0)

    # Предпросмотр исходного изображения
    cover_preview_frame = QFrame()
    cover_preview_frame.setFrameStyle(QFrame.StyledPanel)
    cover_preview_layout = QVBoxLayout(cover_preview_frame)

    cover_preview_label = QLabel("Исходное изображение")
    cover_preview_label.setAlignment(Qt.AlignCenter)
    cover_preview_layout.addWidget(cover_preview_label)

    cover_image_label = QLabel("Изображение не загружено")
    cover_image_label.setAlignment(Qt.AlignCenter)
    cover_image_label.setMinimumSize(200, 150)
    cover_image_label.setMaximumSize(250, 200)
    cover_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    cover_image_label.setScaledContents(False)
    cover_preview_layout.addWidget(cover_image_label)

    upload_preview_layout_grid.addWidget(cover_preview_frame, 1, 0)
    
    # ПРАВАЯ ЧАСТЬ: Водяной знак

    #отдельный бокс под загрузку водяного знака
    wm_upload_layout = QVBoxLayout()
    # Кнопка загрузки водяного знака
    btn_load_wm = QPushButton("Загрузить файл водяного знака")
    wm_upload_layout.addWidget(btn_load_wm)

    # Поле для ввода текста (альтернатива загрузке файла)
    lineedit_wm = QLineEdit()
    lineedit_wm.setPlaceholderText("Введите текст для встраивания...")
    wm_upload_layout.addWidget(lineedit_wm)

    upload_preview_layout_grid.addLayout(wm_upload_layout, 0, 1)

    # Предпросмотр водяного знака
    secret_preview_frame = QFrame()
    secret_preview_frame.setFrameStyle(QFrame.StyledPanel)
    secret_preview_layout = QVBoxLayout(secret_preview_frame)

    secret_preview_label = QLabel("Секретное изображение")
    secret_preview_label.setAlignment(Qt.AlignCenter)
    secret_preview_layout.addWidget(secret_preview_label)

    secret_image_label = QLabel("Изображение не загружено")
    secret_image_label.setAlignment(Qt.AlignCenter)
    secret_image_label.setMinimumSize(200, 150)
    secret_image_label.setMaximumSize(250, 200)
    secret_image_label.setStyleSheet("border: 2px dashed #aaa; color: #666;")
    secret_image_label.setScaledContents(True)
    secret_preview_layout.addWidget(secret_image_label)

    upload_preview_layout_grid.addWidget(secret_preview_frame, 1, 1)

    layout.addLayout(upload_preview_layout_grid)
    
    
    # ========================================================================
    # СЕКЦИЯ 5: КНОПКИ ОСНОВНЫХ ДЕЙСТВИЙ
    # ========================================================================
    # Три главные кнопки для выполнения операций стеганографии
    
    actions_layout = QHBoxLayout()  # Размещаем кнопки горизонтально
    
    # Кнопка встраивания водяного знака
    btn_embed = QPushButton("🔒 Встроить")
    # Эта кнопка запускает процесс встраивания секрета в исходное изображение
    
    # Кнопка извлечения водяного знака
    btn_extract = QPushButton("🔍 Извлечь")
    # Эта кнопка извлекает секрет из стего-изображения
    
    # Кнопка сброса всех настроек
    btn_reset = QPushButton("🗑️ Сбросить")
    # Очищает все поля, сбрасывает настройки и предпросмотры
    
    actions_layout.addWidget(btn_embed)
    actions_layout.addWidget(btn_extract)
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
    
    parent.combo_algo = combo_algo           # Выбор алгоритма
    parent.spinbox_depth = spinbox_depth     # Поле глубины встраивания
    parent.btn_load_cover = btn_load_cover   # Кнопка загрузки исходного изображения
    parent.btn_load_wm = btn_load_wm         # Кнопка загрузки водяного знака
    parent.lineedit_wm = lineedit_wm         # Поле ввода текста
    parent.btn_embed = btn_embed             # Кнопка встраивания
    parent.btn_extract = btn_extract         # Кнопка извлечения
    parent.btn_reset = btn_reset             # Кнопка сброса
    parent.result_text = result_text         # Область вывода результатов
    parent.cover_image_label = cover_image_label     # Окно предпросмотра исходного изображения
    parent.secret_image_label = secret_image_label   # Окно предпросмотра секретного изображения
    
    # Возвращаем готовый виджет с полным интерфейсом
    return main_widget
