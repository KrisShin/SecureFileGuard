from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QRadioButton, QVBoxLayout, QWidget

from interface.custom_widget import MyQLabelTip, PasswordToggleWidget
from module.common import handle_set_strong_password
from module.file_apis import file_edit, get_file_list, varify_file_password
from setting.config_loader import config
from setting.global_variant import gcache


def setup_file_edit_ui(main_window: QMainWindow, content_widget: QWidget):
    """显示文件编辑界面（居中版本）"""
    # 清空右侧区域
    if content_widget.layout():
        QWidget().setLayout(content_widget.layout())

    # 创建主容器
    content_widget.setLayout(QVBoxLayout())
    content_widget.layout().setContentsMargins(0, 0, 0, 0)

    # 添加居中容器
    center_container = QWidget()
    center_container.setMinimumSize(600, 400)  # 设置最小显示区域
    center_container.setLayout(QVBoxLayout())
    center_container.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)

    # 创建表单容器（带固定高度）
    form_container = QWidget()
    form_container.setStyleSheet(
        """
        background: rgba(0,0,0,0.2);
        border-radius: 12px;
    """
    )

    # 构建表单内容
    _build_edit_form(main_window, form_container)

    # 添加到布局结构
    center_container.layout().addWidget(form_container)
    content_widget.layout().addWidget(center_container, 1)  # 使用stretch填充空间


def _build_edit_form(main_window: QMainWindow, container: QWidget):
    container.setLayout(QVBoxLayout())
    container.layout().setContentsMargins(40, 30, 40, 30)

    # 标题
    title = QLabel("文件编辑")
    title.setStyleSheet("font-size: 18px; font-weight: 500; color: #fff; background:transparent;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.layout().addWidget(title)

    # 下拉单选框
    container.file_selector = QComboBox()
    container.file_selector.setFixedHeight(35)
    container.file_selector.setStyleSheet("height:35px;border-radius: 12px; background: rgba(0, 0, 0, 0.6);")

    # 从数据库获取文件列表并填充
    main_window.file_list = get_file_list(gcache.current_user)
    container.file_selector.addItems([f"{f['file_name']}-{f['algorithm']}" for f in main_window.file_list])
    main_window.current_file = main_window.file_list[0] if main_window.file_list else None
    main_window.unlock = False
    container.file_selector.currentIndexChanged.connect(lambda index: on_file_selected(index, main_window, container))

    # 文件路径输入框（只读）
    container.file_path = QLineEdit(placeholderText="请选择文件...", readOnly=True)
    container.file_path.setFixedHeight(35)
    container.file_path.setDisabled(True)
    container.file_path_container = QHBoxLayout()
    # 选择文件按钮
    btn_select_file = QPushButton("选择文件")
    btn_select_file.setDisabled(True)
    btn_select_file.setStyleSheet("padding:8px; background: rgba(0, 180, 120, 0.8);")
    btn_select_file.clicked.connect(lambda: select_file(container))

    container.file_path_container.addWidget(container.file_path)
    container.file_path_container.addWidget(btn_select_file)

    # 文件名输入框（可编辑）
    container.file_name = QLineEdit(placeholderText="文件名")
    container.file_name.setFixedHeight(35)

    # 加密算法单选框
    container.algorithm_group = QButtonGroup(container)
    container.aes_radio = QRadioButton("AES")
    container.des_radio = QRadioButton("DES")
    container.des3_radio = QRadioButton("3DES")
    container.sm4_radio = QRadioButton("SM4")
    container.aes_radio.setFixedHeight(35)
    container.des_radio.setFixedHeight(35)
    container.des3_radio.setFixedHeight(35)
    container.sm4_radio.setFixedHeight(35)

    # 添加到组，保证单选
    container.algorithm_group.addButton(container.aes_radio)
    container.algorithm_group.addButton(container.des_radio)
    container.algorithm_group.addButton(container.des3_radio)
    container.algorithm_group.addButton(container.sm4_radio)

    # 默认选中 config.security.default_algorithm
    algorithm = config.security.default_algorithm
    if main_window.current_file:
        container.file_path.setText(main_window.current_file['file_path'])
        container.file_name.setText(main_window.current_file['file_name'])
        algorithm = main_window.current_file['algorithm']

    if algorithm == "AES":
        container.aes_radio.setChecked(True)
    elif algorithm == "DES":
        container.des_radio.setChecked(True)
    elif algorithm == "3DES":
        container.des3_radio.setChecked(True)
    elif algorithm == "SM4":
        container.sm4_radio.setChecked(True)

    algorithm_layout = QHBoxLayout()
    algorithm_layout.addWidget(container.aes_radio)
    algorithm_layout.addWidget(container.des_radio)
    algorithm_layout.addWidget(container.des3_radio)
    algorithm_layout.addWidget(container.sm4_radio)

    # 密码输入框
    container.password = PasswordToggleWidget(placeholder='输入加密密码', style='height:35px;border-radius: 12px; background: rgba(0, 0, 0, 0.2);')
    container.password.setFixedHeight(35)

    # 生成强密码按钮
    container.decrypted_btn = QPushButton("解密文件")
    container.decrypted_btn.setFixedSize(150, 40)
    container.decrypted_btn.setStyleSheet(
        """
        QPushButton {
            background: rgba(180, 0, 120, 0.8);
            color: white;
            border-radius: 12px;
            font-size: 14px;
        }
        QPushButton:hover { background: #c353c3; }
        """
    )

    container.decrypted_btn.clicked.connect(lambda: (unlock_file(main_window, container)))
    # 生成强密码按钮
    container.generate_btn = QPushButton("生成强密码")
    container.generate_btn.setFixedSize(150, 40)
    container.generate_btn.setStyleSheet(
        """
        QPushButton {
            background: rgba(0, 180, 120, 0.8);
            color: white;
            border-radius: 12px;
            font-size: 14px;
        }
        QPushButton:hover { background: #67c23a; }
        """
    )

    container.generate_btn.clicked.connect(lambda: (handle_set_strong_password(container, container.password)))
    # 提交按钮
    container.btn_submit = QPushButton("提交")
    container.btn_submit.setFixedSize(150, 40)
    container.btn_submit.setStyleSheet(
        """ QPushButton {
            background: rgba(0,20,200, 0.8);
            color: white;
            border-radius: 12px;
            font-size: 14px;
        }
        QPushButton:hover { background: #66b1ff; }"""
    )
    container.btn_submit.clicked.connect(lambda: submit(main_window, container))

    label_hint = QLabel("* 选择文件之后请先输入密码解锁之后才能编辑!")
    label_hint.setStyleSheet("color: red; font-size: 14px; background: transparent")
    # 布局管理
    form_layout = QFormLayout()
    form_layout.addRow("", label_hint)
    form_layout.addRow("选择文件:", container.file_selector)
    form_layout.addRow("文件路径:", container.file_path_container)
    form_layout.addRow("文件名:", container.file_name)
    form_layout.addRow("加密算法:", algorithm_layout)
    form_layout.addRow("密码:", container.password)
    form_layout.labelForField(container.file_selector).setStyleSheet("background: transparent")
    form_layout.labelForField(container.file_path_container).setStyleSheet("background: transparent")
    form_layout.labelForField(container.file_name).setStyleSheet("background: transparent")
    form_layout.labelForField(algorithm_layout).setStyleSheet("background: transparent")
    form_layout.labelForField(container.password).setStyleSheet("background: transparent")

    button_layout = QHBoxLayout()
    button_layout.addWidget(container.decrypted_btn)
    button_layout.addWidget(container.generate_btn)
    button_layout.addWidget(container.btn_submit)

    set_widget_unlock(main_window, container, main_window.unlock)

    main_layout = QVBoxLayout()
    main_layout.addLayout(form_layout)
    main_layout.addLayout(button_layout)
    main_layout.setAlignment(Qt.AlignCenter)

    # 整体布局结构
    container.layout().addSpacing(20)
    container.layout().addLayout(main_layout)
    container.layout().addStretch(1)


def on_file_selected(index: int, main_window: QMainWindow, container: QWidget):
    """当选择文件时，禁用控件并显示提示"""
    if index >= 0:
        set_widget_unlock(main_window, container, False)  # 显示提示信息
        current_file = main_window.file_list[index]
        container.file_path.setText(current_file['file_path'])
        container.file_name.setText(current_file['file_name'])
        match current_file['algorithm']:
            case 'AES':
                container.aes_radio.setChecked(True)
            case 'DES':
                container.des_radio.setChecked(True)
            case '3DES':
                container.des3_radio.setChecked(True)
            case 'SM4':
                container.sm4_radio.setChecked(True)
        container.a
        main_window.current_file = current_file


def set_widget_unlock(main_window: QMainWindow, container: QWidget, unlock: bool = False):
    container.file_name.setDisabled(not unlock)
    container.aes_radio.setDisabled(not unlock)
    container.des_radio.setDisabled(not unlock)
    container.des3_radio.setDisabled(not unlock)
    container.sm4_radio.setDisabled(not unlock)
    # container.password.setDisabled(not unlock)
    container.decrypted_btn.setDisabled(unlock)
    container.generate_btn.setDisabled(not unlock)
    container.btn_submit.setDisabled(not unlock)
    if main_window.unlock != unlock:
        main_window.unlock = unlock


def select_file(container: QWidget):
    file_dialog = QFileDialog(container)
    file_path, _ = file_dialog.getOpenFileName(container, "选择文件", "", "所有文件 (*.*)")
    if file_path:
        container.selected_file = file_path
        container.file_path.setText(file_path)
        container.file_name.setText(file_path.split("/")[-1])


def submit(main_window: QMainWindow, container: QWidget):
    selected_algorithm = get_selected_algorithm(container)
    password: str = container.password.text()
    filename: str = container.file_name.text()

    is_success, file_path_or_message = file_edit(password, main_window.current_file['id'], selected_algorithm, gcache.current_user['username'], filename)
    MyQLabelTip(file_path_or_message, container, is_success)


def unlock_file(main_window: QMainWindow, container: QWidget):
    file = main_window.current_file
    password: str = container.password.text()

    is_success, message = varify_file_password(file, password)
    if is_success:
        set_widget_unlock(main_window, container, True)
    MyQLabelTip(message, container, is_success)


def get_selected_algorithm(container_widget):
    if container_widget.aes_radio.isChecked():
        return "AES"
    elif container_widget.des_radio.isChecked():
        return "DES"
    elif container_widget.des3_radio.isChecked():
        return "3DES"
    elif container_widget.sm4_radio.isChecked():
        return "SM4"
    return ""
