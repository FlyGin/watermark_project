from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QFileDialog, QLineEdit
)

def create_main_layout(parent):
    main_widget = QWidget(parent)
    layout = QVBoxLayout(main_widget)
    
    # 1. Выбор алгоритма
    algo_layout = QHBoxLayout()
    label_algo = QLabel("Алгоритм:")
    combo_algo = QComboBox()
    combo_algo.addItems(["LSB", "DCT", "DWT", "CNN"])
    algo_layout.addWidget(label_algo)
    algo_layout.addWidget(combo_algo)
    layout.addLayout(algo_layout)
    
    # 2. Загрузка исходного файла
    file_layout = QHBoxLayout()
    btn_load_cover = QPushButton("Загрузить исходный файл")
    file_layout.addWidget(btn_load_cover)
    layout.addLayout(file_layout)
    
    # 3. Водяной знак: выбор файла или ввод текста
    wm_layout = QHBoxLayout()
    btn_load_wm = QPushButton("Загрузить файл водяного знака")
    wm_layout.addWidget(btn_load_wm)
    label_or_text = QLabel("или введите текст:")
    wm_layout.addWidget(label_or_text)
    lineedit_wm = QLineEdit()
    wm_layout.addWidget(lineedit_wm)
    layout.addLayout(wm_layout)
    
    # 4. Кнопки действий
    actions_layout = QHBoxLayout()
    btn_embed = QPushButton("Встроить")
    btn_extract = QPushButton("Извлечь")
    btn_reset = QPushButton("Сбросить")
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
    
    # Можно добавить ещё превью изображения/ошибки и др. 
    
    # — сохранить виджеты в parent для доступа в events.py
    parent.combo_algo = combo_algo
    parent.btn_load_cover = btn_load_cover
    parent.btn_load_wm = btn_load_wm
    parent.lineedit_wm = lineedit_wm
    parent.btn_embed = btn_embed
    parent.btn_extract = btn_extract
    parent.btn_reset = btn_reset
    parent.result_text = result_text
    # ... далее любые дополнительные элементы
    
    return main_widget
