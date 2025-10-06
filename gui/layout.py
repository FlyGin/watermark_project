# gui/layout.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QFileDialog, QLineEdit, QSpinBox
)

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
    
    # 4. Кнопки действий
    actions_layout = QHBoxLayout()
    btn_embed = QPushButton("🔒 Встроить")
    btn_extract = QPushButton("🔍 Извлечь")
    btn_reset = QPushButton("🗑️ Сбросить")
    actions_layout.addWidget(btn_embed)
    actions_layout.addWidget(btn_extract)
    actions_layout.addWidget(btn_reset)
    layout.addLayout(actions_layout)
    
    # 5. Вывод результата
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
    
    return main_widget
