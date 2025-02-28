from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
)
from PySide6.QtCore import Qt

from setting.config_loader import config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主界面")
        self.resize(config.other.width, config.other.height)

        # 添加界面内容
        label = QLabel("欢迎进入主界面！", self)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
