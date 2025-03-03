from pathlib import Path
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QRadioButton,
    QButtonGroup,
    QFormLayout,
    QMainWindow,
    QWidget,
    QApplication,
    QMessageBox,
)
from PySide6.QtCore import Qt

from module.common import generate_strong_password, get_password_hash
from module.custom_widget import PasswordToggleWidget
from module.encrypt_apis import encrypt_file
from setting.config_loader import config
from setting.global_variant import DELIMITER, gcache
from db_data.manager import db


def setup_file_upload_ui(main_window: QMainWindow, content_widget: QWidget):
    """显示文件上传界面（居中版本）"""
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
    _build_upload_form(main_window, form_container)

    # 添加到布局结构
    center_container.layout().addWidget(form_container)
    content_widget.layout().addWidget(center_container, 1)  # 使用stretch填充空间


def _build_upload_form(main_window: QMainWindow, container: QWidget):
    container.setLayout(QVBoxLayout())
    container.layout().setContentsMargins(40, 30, 40, 30)

    # 标题
    title = QLabel("文件上传")
    title.setStyleSheet("font-size: 18px; font-weight: 500; color: #fff; background:transparent;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.layout().addWidget(title)

    # 文件路径输入框（只读）
    container.file_path = QLineEdit(placeholderText="请选择文件...", readOnly=True)
    container.file_path.setFixedHeight(35)
    container.file_path_container = QHBoxLayout()
    # 选择文件按钮
    btn_select_file = QPushButton("选择文件")
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
    default_algorithm = config.security.default_algorithm
    if default_algorithm == "AES":
        container.aes_radio.setChecked(True)
    elif default_algorithm == "DES":
        container.des_radio.setChecked(True)
    elif default_algorithm == "3DES":
        container.des3_radio.setChecked(True)
    elif default_algorithm == "SM4":
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
    generate_btn = QPushButton("生成强密码")
    generate_btn.setFixedSize(150, 40)
    generate_btn.setStyleSheet(
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

    generate_btn.clicked.connect(lambda: (handle_set_strong_password(container)))
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
    container.btn_submit.clicked.connect(lambda: submit(container))

    # 布局管理
    form_layout = QFormLayout()
    form_layout.addRow("文件路径:", container.file_path_container)
    form_layout.addRow("文件名:", container.file_name)
    form_layout.addRow("加密算法:", algorithm_layout)
    form_layout.addRow("密码:", container.password)
    form_layout.labelForField(container.file_path_container).setStyleSheet("background: transparent")
    form_layout.labelForField(container.file_name).setStyleSheet("background: transparent")
    form_layout.labelForField(algorithm_layout).setStyleSheet("background: transparent")
    form_layout.labelForField(container.password).setStyleSheet("background: transparent")

    button_layout = QHBoxLayout()
    button_layout.addWidget(generate_btn)
    button_layout.addWidget(container.btn_submit)

    main_layout = QVBoxLayout()
    main_layout.addLayout(form_layout)
    main_layout.addLayout(button_layout)
    main_layout.setAlignment(Qt.AlignCenter)

    # 整体布局结构
    container.layout().addSpacing(20)
    container.layout().addLayout(main_layout)
    container.layout().addStretch(1)


def handle_set_strong_password(container: QWidget):
    password = generate_strong_password()
    container.password.setText(password)
    clipboard = QApplication.clipboard()
    clipboard.setText(password)
    QMessageBox.information(container, '提示', "密码已生成并复制到剪贴板")


def select_file(container_widget):
    file_dialog = QFileDialog(container_widget)
    file_path, _ = file_dialog.getOpenFileName(container_widget, "选择文件", "", "所有文件 (*.*)")
    if file_path:
        container_widget.selected_file = file_path
        container_widget.file_path.setText(file_path)
        container_widget.file_name.setText(file_path.split("/")[-1])


def submit(container_widget: QWidget):
    selected_algorithm = get_selected_algorithm(container_widget)
    filename: str = container_widget.file_name.text()
    password: str = container_widget.password.text()

    if not container_widget.selected_file:
        print("请先选择文件！")
        return
    if not password:
        print("请输入加密密码！")
        return

    file_size = Path(container_widget.selected_file).stat().st_size

    is_success, iv_or_title, file_path_or_message, filled_password = encrypt_file(
        selected_algorithm, container_widget.selected_file, gcache.current_user['username'], filename, password
    )
    if is_success:
        db.upload_file(
            filled_password, get_password_hash(filled_password), iv_or_title, gcache.current_user['username'], file_path_or_message.as_posix(), selected_algorithm, file_size, filename
        )
        QMessageBox.information(container_widget, "成功", f"上传文件{filename}, {selected_algorithm}加密成功")
    else:
        QMessageBox.warning(container_widget, iv_or_title, file_path_or_message)


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
