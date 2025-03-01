from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

from interface.widget_edit_password import set_change_password_ui
from interface.widget_edit_profile import set_edit_profile_ui
from setting.config_loader import config
from setting.global_variant import gcache


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主界面")
        self.resize(config.other.width, config.other.height)
        self.user = gcache.current_user
        self.init_ui()

    def init_ui(self):
        # 创建主布局容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 水平布局：左侧菜单 + 右侧内容
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        layout.setSpacing(0)  # 移除间距

        # 左侧菜单区域
        self.menu_widget = QWidget()
        self.menu_widget.setStyleSheet("background: rgba(0,0,0,0.3)")
        self.menu_widget.setFixedWidth(200)
        layout.addWidget(self.menu_widget)

        # 右侧内容区域
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: rgba(255,255,255,0.2)")
        layout.addWidget(self.content_widget, 1)

        # 背景设置
        self.background = QLabel(self)
        self.background.lower()
        self.set_background(Path(config.path.static) / 'bg.png')

        # 初始化菜单
        self.init_menu()
        self.open_password_change()

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

    def init_menu(self):
        # 菜单项配置
        base_buttons = [
            ("文件管理", self.open_file_manager),
            ("文件上传", self.open_file_upload),
            ("文件编辑", self.open_file_edit),
            ("编辑信息", self.open_profile_edit),
            ("修改密码", self.open_password_change),
        ]

        # 管理员专属按钮
        admin_buttons = [("用户管理", self.open_user_management)]

        # 通用底部按钮
        bottom_buttons = [("退出登录", self.logout), ("结束程序", self.close)]

        # 创建菜单布局
        menu_layout = QVBoxLayout(self.menu_widget)
        menu_layout.setContentsMargins(10, 20, 10, 20)
        menu_layout.setSpacing(10)

        # 添加普通用户按钮
        for text, callback in base_buttons:
            self.create_menu_button(text, callback, menu_layout)

        # 添加管理员专属按钮
        if self.user['role'] == 'admin':
            for text, callback in admin_buttons:
                self.create_menu_button(text, callback, menu_layout)

        # 添加底部按钮
        menu_layout.addStretch(1)  # 添加弹性空间
        transparent = 0.2
        for text, callback in bottom_buttons:
            self.create_menu_button(text, callback, menu_layout, style=f"background-color: rgba(255, 50, 0, {transparent});")
            transparent += 0.2

    def create_menu_button(self, text, callback, layout, style=""):
        """创建统一风格的菜单按钮"""
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setStyleSheet(
            f"""
            QPushButton {{ 
                text-align: left; 
                padding-left: 20px;
                border: none;
                border-radius: 12px;
                {style}
            }}
            QPushButton:hover {{ background-color: #159acdff; }}
        """
        )
        btn.clicked.connect(callback)
        layout.addWidget(btn)

    # 以下为功能方法示例 ---------------------------------
    def open_file_manager(self):
        print("打开文件管理")
        # 清空右侧区域并加载对应内容

    def open_file_upload(self):
        print("打开文件上传")
        # 清空右侧区域并加载对应内容

    def open_file_edit(self):
        print("打开文件编辑")
        # 清空右侧区域并加载对应内容

    def open_profile_edit(self):
        set_edit_profile_ui(self, self.content_widget)

    def open_password_change(self):
        set_change_password_ui(self, self.content_widget)

    def open_user_management(self):
        print("打开用户管理")
        # 管理员专属功能

    def logout(self):
        """退出登录处理"""
        from interface.window_login import LoginWindow

        self.login_window = LoginWindow()
        self.login_window.show()

        gcache.current_user = {}
        # 触发登录窗口重新显示
        QTimer.singleShot(200, lambda: (self.close()))

        self.close()
