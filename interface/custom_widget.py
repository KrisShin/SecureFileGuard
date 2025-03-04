from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QToolButton, QWidget

from setting.global_variant import DANGER_RGB, SUCCESS_RGB


class PasswordToggleWidget(QWidget):
    """自定义带密码展示切换按钮的密码输入框"""

    def __init__(self, parent=None, placeholder: str = '请输入密码', style: str = ''):
        super().__init__(parent)
        self.placeholder = placeholder
        self.css = style  # 可以传入自定义css
        self.init_ui()

    def init_ui(self):
        # 创建密码输入框和眼睛按钮
        self.password = QLineEdit(self, placeholderText=self.placeholder)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(f"{self.css}")

        self.toggle_button = QToolButton(self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setText("👁")  # 可以替换为 QIcon
        self.toggle_button.setStyleSheet(f"border: none; padding: 2px; background: transparent;")

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


class MyQLabelTip(QWidget):
    """自定义的通知标签"""

    def __init__(self, text: str, container: QWidget, is_success: bool = True):
        super().__init__(container)
        # 设置背景颜色
        bg_color = SUCCESS_RGB if is_success else DANGER_RGB

        # 创建半透明浮动标签
        tip_label = QLabel(text, container)
        tip_label.setStyleSheet(
            f"""
            QLabel {{ 
                background: rgba({bg_color}, 0.7); 
                color: white; 
                padding: 8px; 
                border-radius: 4px;
            }}
        """
        )
        # 根据字数计算显示长度
        tip_label.setFixedWidth(20 + len(text) * 12)
        tip_label.move(20, 20)  # 调整显示位置
        tip_label.show()

        # 设置2秒后自动关闭
        QTimer.singleShot(2000, tip_label.close)
