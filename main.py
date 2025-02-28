import sys
import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from interface.splash_sfg import SplashScreen
from interface.window_login import LoginWindow
from setting.config_loader import config
from db_data.manager import db  # 初始化数据库

if __name__ == "__main__":
    db.init_amdin_user()
    app = QApplication(sys.argv)

    # 第一步：显示启动页
    splash = SplashScreen()
    splash.show()
    login_window = LoginWindow()
    login_window.login_success.connect(login_window.show_main)

    # 设置定时器
    QTimer.singleShot(
        config.other.splash_timeout,
        lambda: (
            login_window.show(),  # 显示登录窗口
            splash.close(),  # 关闭启动页
            splash.deleteLater(),  # 释放启动页内存
        ),
    )

    app.exec()
