from pathlib import Path
import re
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QHBoxLayout,
    QDialog,
    QFormLayout,
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QPixmap

from db_data.manager import db
from module.user_apis import verify_password
from setting.config_loader import config
from setting.global_variant import gcache
from interface.window_main import MainWindow


class LoginWindow(QWidget):
    login_success = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录")
        self.resize(config.other.width, config.other.height)
        self.setup_ui()

    def setup_ui(self):
        # 背景设置
        self.background = QLabel(self)
        self.set_background(Path(config.path.static) / 'bg.png')

        # 创建主控件
        self.username = QLineEdit(placeholderText="请输入用户名")
        self.password = QLineEdit(placeholderText="请输入密码", echoMode=QLineEdit.Password)
        self.btn_login = QPushButton("登 录", objectName="btnLogin")
        self.btn_register = QPushButton("注 册", objectName="btnRegister")

        # TODO: 测试使用账号密码
        self.username.setText('admin')
        self.password.setText('123qwe')

        # 表单布局
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.addRow(QLabel("用户名："), self.username)
        form_layout.addRow(QLabel("密码："), self.password)

        # 按钮水平布局
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_register)
        btn_layout.addWidget(self.btn_login)
        btn_layout.setSpacing(15)

        # 组合容器布局
        container_layout = QVBoxLayout()
        container_layout.addLayout(form_layout)
        container_layout.addSpacing(20)
        container_layout.addLayout(btn_layout)
        container_layout.addStretch()

        # 带背景的容器
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
            #btnLogin, #btnRegister {
                padding: 10px 30px;
                border-radius: 6px;
                font-weight: 500;
            }
            #btnLogin {
                background-color: #0078d4;
                color: white;
            }
            #btnLogin:hover {
                background-color: #006cbd;
            }
            #btnRegister {
                background-color: #f0f0f0;
                color: #333;
            }
            #btnRegister:hover {
                background-color: #e0e0e0;
            }
        """
        )

        # 窗口主布局（居中显示表单）
        main_layout = QVBoxLayout(self)
        main_layout.addStretch()
        main_layout.addWidget(container, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        # 信号连接
        self.btn_login.clicked.connect(self.authenticate)
        self.btn_register.clicked.connect(self.show_register_dialog)

        self.setStyleSheet(
            """
    QWidget {
        font-family: '微软雅黑';
        font-size: 14px;
    }
    QLineEdit {
        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 4px;
        min-width: 250px;
    }
    QPushButton {
        background: #0078d4;
        color: white;
        padding: 8px 20px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background: #006cbd;
    }
"""
        )

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

    def show_register_dialog(self):
        """注册对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("注册账号")

        # 注册表单字段
        form = QFormLayout()
        reg_username = QLineEdit()
        reg_password = QLineEdit(echoMode=QLineEdit.Password)
        reg_phone = QLineEdit()
        reg_email = QLineEdit()
        btn_submit = QPushButton("提交注册")

        form.addRow("用户名:", reg_username)
        form.addRow("密码:", reg_password)
        form.addRow("手机号:", reg_phone)
        form.addRow("邮箱:", reg_email)
        form.addRow(btn_submit)

        # 提交验证
        def submit():
            # 此处添加数据库插入逻辑
            if not all([reg_username.text(), reg_password.text()]):
                QMessageBox.warning(dialog, "错误", "用户名和密码必填")
                return
            user_data = {
                'username': reg_username.text(),
                'password': reg_password.text(),
            }

            # 验证手机格式
            if reg_phone.text():
                if not re.match(r'^1[3-9]\d{9}$', reg_phone.text()):
                    QMessageBox.warning(dialog, "错误", "手机号格式不正确")
                    return
                user_data['phone'] = reg_phone.text()

            # 验证邮箱格式
            if reg_email.text():
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', reg_email.text()):
                    QMessageBox.warning(dialog, "错误", "邮箱格式不正确")
                    return
                user_data['email'] = reg_email.text()

            dialog.accept()
            db.create_user(user_data)
            QMessageBox.information(self, "成功", "注册成功，请登录")

        btn_submit.clicked.connect(submit)
        dialog.setLayout(form)
        dialog.exec()

    def authenticate(self):
        # 简化版验证逻辑
        username = self.username.text()
        password = self.password.text()

        if not all((username, password)):
            QMessageBox.warning(self, "错误", "请输入用户名和密码")
            return
        user_obj = db.get_user(username)
        if not user_obj:
            QMessageBox.warning(self, "错误", "用户名不存在, 请先注册")
            return

        # 数据库验证逻辑应在此处实现
        if verify_password(password, user_obj['password']):
            gcache.current_user = user_obj
            self.main_window = MainWindow()
            self.login_success.emit()
            self.show_main()
            QTimer.singleShot(200, self.close)
        else:
            QMessageBox.warning(self, "错误", "密码错误")

    def show_main(self):
        self.main_window.destroyed.connect(QApplication.quit)
        self.main_window.show()
