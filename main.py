import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from db_data.manager import db  # 初始化数据库
from interface.splash_sfg import SplashScreen
from interface.window_login import LoginWindow
from setting.config_loader import config

if __name__ == "__main__":
    db.init_amdin_user()
    app = QApplication(sys.argv)

    # 第一步：显示启动页
    splash = SplashScreen()
    splash.show()
    login_window = LoginWindow()  # 初始化登录页面
    login_window.login_success.connect(login_window.show_main)  # 连接登录之后展示主页面

    # 设置定时器
    QTimer.singleShot(
        config.other.splash_timeout,  # 从设置读取启动页展示时间
        lambda: (
            login_window.show(),  # 显示登录窗口
            splash.close(),  # 关闭启动页
            splash.deleteLater(),  # 释放启动页内存
        ),
    )

    app.exec()  # 没有活跃页面时退出程序
