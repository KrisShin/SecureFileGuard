from PySide6.QtWidgets import QWidget, QLineEdit, QToolButton, QHBoxLayout


class PasswordToggleWidget(QWidget):
    def __init__(self, parent=None, placeholder: str = '请输入密码'):
        super().__init__(parent)
        self.placeholder = placeholder
        self.init_ui()

    def init_ui(self):
        # 创建密码输入框和眼睛按钮
        self.password = QLineEdit(self, placeholderText=self.placeholder)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet("background: transparent;")

        self.toggle_button = QToolButton(self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setText("👁")  # 可以替换为 QIcon
        self.toggle_button.setStyleSheet("border: none; padding: 2px; background: transparent;")

        # 绑定切换事件
        self.toggle_button.toggled.connect(self.toggle_password_visibility)

        # 创建一个水平布局，将密码框和按钮放在一起
        password_layout = QHBoxLayout(self)
        password_layout.addWidget(self.password)
        password_layout.addWidget(self.toggle_button)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(5)

    def toggle_password_visibility(self, checked):
        """切换明文/密文"""
        self.password.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.toggle_button.setText("🙈" if checked else "👁")

    def setText(self, text: str):
        """设置密码"""
        self.password.setText(text)

    def text(self) -> str:
        """获取密码"""
        return self.password.text()
