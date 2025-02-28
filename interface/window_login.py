from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PySide6.QtCore import Signal

from setting.config_loader import config
from setting.window_main import MainWindow


class LoginWindow(QWidget):
    login_success = Signal()  # 自定义登录成功信号

    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录")
        self.resize(config.other.width, config.other.height)

        # 创建控件
        self.username = QLineEdit(placeholderText="用户名")
        self.password = QLineEdit(placeholderText="密码", echoMode=QLineEdit.Password)
        self.btn_login = QPushButton("登录")

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.btn_login)
        self.setLayout(layout)

        # 连接信号
        self.btn_login.clicked.connect(self.authenticate)

    def authenticate(self):
        # 简单验证逻辑（示例）
        if self.username.text() == "admin" and self.password.text() == "123456":
            self.login_success.emit()
            self.close()
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误")

    # 第三步：登录成功后显示主窗口
    def show_main(self):
        main_window = MainWindow()
        main_window.show()
