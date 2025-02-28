import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from interface.splash_sfg import SplashScreen
from interface.window_login import LoginWindow
from setting.config_loader import config

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 第一步：显示启动页
    splash = SplashScreen()
    splash.show()
    login_window = LoginWindow()
    login_window.login_success.connect(login_window.show_main)

    # 设置定时器
    QTimer.singleShot(
        config.other.splash_timeout,
        lambda: (splash.close(), login_window.show(), splash.deleteLater()),  # 显示登录窗口  # 关闭启动页  # 释放启动页内存
    )

    app.exec()
