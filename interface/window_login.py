from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QHBoxLayout,
    QFormLayout,
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QPixmap

from module.custom_widget import PasswordToggleWidget
from module.user_apis import login, register
from setting.config_loader import config
from interface.window_main import MainWindow


class LoginWindow(QWidget):
    login_success = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录")
        self.resize(config.other.width, config.other.height)
        self.setup_ui()

    def set_background(self, img_path):
        """设置背景"""
        pixmap = QPixmap(img_path).scaled(self.size(), Qt.KeepAspectRatioByExpanding)

        scaled_pixmap = pixmap.scaled(
            self.size(),  # 使用窗口实际尺寸
            Qt.AspectRatioMode.IgnoreAspectRatio,  # 忽略宽高比
            Qt.TransformationMode.SmoothTransformation,  # 平滑缩放
        )
        self.background.setPixmap(scaled_pixmap)
        self.background.setGeometry(0, 0, self.width(), self.height())  # 铺满整个窗口
        self.background.setAlignment(Qt.AlignCenter)

    def authenticate(self):
        # 简化版验证逻辑
        username = self.username.text()
        password = self.password_widget.text()

        if not all((username, password)):
            QMessageBox.warning(self, "错误", "请输入用户名和密码")
            return
        is_success, (title, message) = login(username, password)
        if not is_success:
            QMessageBox.warning(self, title, message)
            return
        else:
            self.main_window = MainWindow()
            self.login_success.emit()
            self.show_main()
            QTimer.singleShot(200, self.close)

    def show_main(self):
        self.main_window.destroyed.connect(QApplication.quit)
        self.main_window.show()

    def setup_ui(self):
        # 背景设置
        self.background = QLabel(self)
        self.set_background(Path(config.path.static) / 'bg.png')
        # 主控件
        self.username = QLineEdit(placeholderText="请输入用户名")

        # 自定义密码组件
        self.password_widget = PasswordToggleWidget()

        # 额外的字段（用于注册）
        self.phone = QLineEdit(placeholderText="请输入手机号")
        self.email = QLineEdit(placeholderText="请输入邮箱")

        # 初始隐藏注册字段
        self.phone.hide()
        self.email.hide()

        # 操作按钮
        self.btn_switch = QPushButton("前往注册", objectName="btnSwitch")
        self.btn_submit = QPushButton("登 录", objectName="btnSubmit")

        # TODO: 测试数据
        self.username.setText('admin')
        self.password_widget.setText('123qwe')

        # 表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.addRow(QLabel("用户名："), self.username)
        form_layout.addRow(QLabel("密码："), self.password_widget)  # 使用密码容器
        form_layout.addRow(QLabel("手机号："), self.phone)
        form_layout.addRow(QLabel("邮箱："), self.email)

        # 动态调整行可见性
        self.phone.label = form_layout.labelForField(self.phone)
        self.email.label = form_layout.labelForField(self.email)
        self.phone.label.hide()
        self.email.label.hide()

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_switch)
        btn_layout.addWidget(self.btn_submit)
        btn_layout.setSpacing(15)

        # 容器布局
        container_layout = QVBoxLayout()
        container_layout.addLayout(form_layout)
        container_layout.addSpacing(20)
        container_layout.addLayout(btn_layout)
        container_layout.addStretch()

        # 容器样式
        container = QWidget()
        container.setLayout(container_layout)
        container.setStyleSheet(
            """
            QWidget {
                background: rgba(0, 0, 0, 0.4);
                border-radius: 12px;
                padding: 8px 20px;
            }
            QLabel {
                font-size: 14px;
                min-width: 40px;
                background: transparent;
            }
            QLineEdit {
                margin-top: 8px;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                min-width: 250px;
                background: transparent;
            }
            #btnSubmit {
                background-color: #0078d4;
                color: white;
            }
            #btnSubmit:hover { background-color: #006cbd; }
            #btnSwitch {
                background-color: #f0f0f0;
                color: #333;
            }
            #btnSwitch:hover { background-color: #e0e0e0; }
        """
        )

        # 主窗口布局
        main_layout = QVBoxLayout(self)
        main_layout.addStretch()
        main_layout.addWidget(container, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        # 信号连接
        self.btn_switch.clicked.connect(self.toggle_form_mode)
        self.btn_submit.clicked.connect(self.handle_submit)

    def toggle_form_mode(self):
        """切换登录/注册模式"""
        is_reg_mode = self.btn_switch.text() == "前往注册"

        # 切换字段可见性
        self.phone.setVisible(is_reg_mode)
        self.email.setVisible(is_reg_mode)
        self.phone.label.setVisible(is_reg_mode)
        self.email.label.setVisible(is_reg_mode)

        # 切换按钮文本
        self.btn_switch.setText("前往登录" if is_reg_mode else "前往注册")
        self.btn_submit.setText("注 册" if is_reg_mode else "登 录")

        # 清空输入框
        if not is_reg_mode:
            # self.username.clear()
            # self.password.clear()
            self.phone.clear()
            self.email.clear()

    def handle_submit(self):
        """统一处理提交操作"""
        if self.btn_submit.text() == "登 录":
            self.authenticate()
        else:
            self.handle_register()

    def handle_register(self):
        """处理注册逻辑"""
        regist_data = {
            'username': self.username.text().strip(),
            'password': self.password_widget.text().strip(),
            'phone': self.phone.text().strip() or None,
            'email': self.email.text().strip() or None,
        }

        is_success, (title, message) = register(regist_data)
        if is_success:
            # 创建自定义消息框
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("注册成功")
            msg_box.setText("注册成功，请登录")
            msg_box.setIcon(QMessageBox.Information)

            # 添加自定义按钮并绑定切换事件
            ok_button = msg_box.addButton("前往登录", QMessageBox.AcceptRole)
            ok_button.clicked.connect(self.toggle_form_mode)

            msg_box.exec()
        else:
            QMessageBox.warning(self, title, message)
