# gui/layout.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QFileDialog, QLineEdit, QSpinBox,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

def create_main_layout(parent):
    main_widget = QWidget(parent)
    layout = QVBoxLayout(main_widget)
    
    # 1. Выбор алгоритма и глубины
    algo_layout = QHBoxLayout()
    
    # Выбор алгоритма
    label_algo = QLabel("Алгоритм:")
    combo_algo = QComboBox()
    combo_algo.addItems(["LSB"])  # Только LSB
    
    # Выбор глубины
    label_depth = QLabel("Глубина:")
    spinbox_depth = QSpinBox()
    spinbox_depth.setRange(1, 8)  # Глубина от 1 до 8 бит
    spinbox_depth.setValue(1)     # По умолчанию 1 бит
    spinbox_depth.setSuffix(" бит")
    
    algo_layout.addWidget(label_algo)
    algo_layout.addWidget(combo_algo)
    algo_layout.addWidget(label_depth)
    algo_layout.addWidget(spinbox_depth)
    algo_layout.addStretch()  # Добавляем растяжение для красивого выравнивания
    layout.addLayout(algo_layout)
    
    # 2. Загрузка исходного файла
    file_layout = QHBoxLayout()
    btn_load_cover = QPushButton("Загрузить исходное изображение")
    file_layout.addWidget(btn_load_cover)
    layout.addLayout(file_layout)
    
    # 3. Водяной знак: выбор файла или ввод текста
    wm_layout = QHBoxLayout()
    btn_load_wm = QPushButton("Загрузить файл водяного знака")
    wm_layout.addWidget(btn_load_wm)
    label_or_text = QLabel("или введите текст:")
    wm_layout.addWidget(label_or_text)
    lineedit_wm = QLineEdit()
    lineedit_wm.setPlaceholderText("Введите текст для встраивания...")
    wm_layout.addWidget(lineedit_wm)
    layout.addLayout(wm_layout)
    
    # 4. Предпросмотр загруженных изображений
    preview_layout = QHBoxLayout()
    
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
    cover_image_label.setScaledContents(True)
    cover_preview_layout.addWidget(cover_image_label)
    
    # Предпросмотр секретного изображения  
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
    
    preview_layout.addWidget(cover_preview_frame)
    preview_layout.addWidget(secret_preview_frame)
    layout.addLayout(preview_layout)
    
    # 5. Кнопки действий
    actions_layout = QHBoxLayout()
    btn_embed = QPushButton("🔒 Встроить")
    btn_extract = QPushButton("🔍 Извлечь")
    btn_reset = QPushButton("🗑️ Сбросить")
    actions_layout.addWidget(btn_embed)
    actions_layout.addWidget(btn_extract)
    actions_layout.addWidget(btn_reset)
    layout.addLayout(actions_layout)
    
    # 6. Вывод результата
    result_label = QLabel("Результат:")
    result_text = QTextEdit()
    result_text.setReadOnly(True)
    layout.addWidget(result_label)
    layout.addWidget(result_text)
    
    # Сохранить виджеты в parent для доступа в events.py
    parent.combo_algo = combo_algo
    parent.spinbox_depth = spinbox_depth
    parent.btn_load_cover = btn_load_cover
    parent.btn_load_wm = btn_load_wm
    parent.lineedit_wm = lineedit_wm
    parent.btn_embed = btn_embed
    parent.btn_extract = btn_extract
    parent.btn_reset = btn_reset
    parent.result_text = result_text
    parent.cover_image_label = cover_image_label
    parent.secret_image_label = secret_image_label
    
    return main_widget
