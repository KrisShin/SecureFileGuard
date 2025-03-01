from pathlib import Path
from PySide6.QtCore import QObject, Signal, QSettings


BASE_PATH = Path(__file__).parent.parent  # 当前项目根目录
CONFIG_PATH = BASE_PATH / 'config.yaml'  # 配置文件uri
SPLASH_FILE = 'splash.png'


class GlobalCache(QObject):
    _instance = None
    current_user_changed = Signal(str)  # 当前用户变化的信号

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._current_user = {}
            cls._instance._settings = QSettings("Kris", "SecureFileGuard")
        return cls._instance

    @property
    def current_user(self) -> str:
        return self._current_user

    @current_user.setter
    def current_user(self, value: str):
        if self._current_user != value:
            self._current_user = value
            self.current_user_changed.emit(value)
            self.save_setting("current_user", value)

    def save_setting(self, key: str, value):
        """持久化存储到系统注册表/配置文件"""
        self._settings.setValue(key, value)

    def load_setting(self, key: str, default=None):
        """从配置文件加载"""
        return self._settings.value(key, default)


gcache = GlobalCache()
