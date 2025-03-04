from pathlib import Path

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap, QResizeEvent
from PySide6.QtWidgets import QGraphicsBlurEffect, QGraphicsPixmapItem, QGraphicsScene, QWidget

from setting.config_loader import config
from setting.global_variant import SPLASH_FILE


class SplashScreen(QWidget):
    """启动页面"""

    def __init__(self):
        super().__init__()
        # 创建图片对象, 读取config中配置的背景图
        self.original_pixmap = QPixmap(Path(config.path.static) / SPLASH_FILE)

        # 窗口初始化设置
        self.setWindowFlag(Qt.FramelessWindowHint)  # 无边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景

        # 设置初始窗口尺寸（根据配置或图片比例）
        self.setMinimumSize(400, 300)  # 最小尺寸约束
        self.resize(QSize(config.other.width, config.other.height))

        # 字体初始化
        self.init_font()

        # 自动关闭定时器
        # QTimer.singleShot(config.other.splash_timeout, self.close)

    def init_font(self):
        """加载字体资源"""
        self.font = QFont("Microsoft YaHei")
        self.font.setWeight(QFont.Bold)

    def resizeEvent(self, event: QResizeEvent):
        """窗口大小改变时更新绘制"""
        self.update()
        super().resizeEvent(event)

    def paintEvent(self, event):
        """主绘制方法"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制缩放后的模糊背景
        self.draw_scaled_background(painter)

        # 绘制文字信息
        self.draw_text_info(painter)

        painter.end()

    def draw_scaled_background(self, painter: QPainter):
        """绘制自适应背景"""
        # 计算保持宽高比的缩放尺寸
        scaled_size = self.original_pixmap.size().scaled(self.size(), Qt.KeepAspectRatioByExpanding)

        # 创建临时缩放图片
        scaled_pixmap = self.original_pixmap.scaled(scaled_size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        # 应用模糊效果
        blurred_pixmap = self.apply_blur_effect(scaled_pixmap)

        # 居中绘制背景
        x = (self.width() - blurred_pixmap.width()) // 2
        y = (self.height() - blurred_pixmap.height()) // 2
        painter.drawPixmap(x, y, blurred_pixmap)

    def apply_blur_effect(self, pixmap: QPixmap) -> QPixmap:
        """应用高斯模糊效果"""
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)

        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(9)
        item.setGraphicsEffect(blur)

        scene.addItem(item)

        result_pixmap = QPixmap(pixmap.size())
        result_pixmap.fill(Qt.transparent)

        bg_painter = QPainter(result_pixmap)
        scene.render(bg_painter)
        bg_painter.end()

        return result_pixmap

    def draw_text_info(self, painter: QPainter):
        """绘制左侧文字信息"""
        # 文字颜色设置（深色半透明）
        text_color = QColor(230, 230, 230, 220)
        painter.setPen(text_color)

        # 文字布局参数
        margin_left = 50
        base_top = 300
        line_spacing = 30
        title_height = 60

        # 项目名称
        self.font.setPointSize(38)
        painter.setFont(self.font)
        painter.drawText(QRect(margin_left, base_top, 500, title_height), Qt.AlignLeft | Qt.AlignVCenter, config.app.name)

        self.font.setPointSize(14)
        # 版本信息
        painter.setFont(self.font)
        painter.drawText(
            QRect(margin_left, base_top + title_height + line_spacing, 400, line_spacing),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"版本: V{config.app.version}",
        )

        # 作者信息
        painter.setFont(self.font)
        painter.drawText(
            QRect(margin_left, base_top + title_height + line_spacing * 2, 400, line_spacing),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"开发者：{config.app.author}",
        )

        # 发布日期
        painter.setFont(self.font)
        painter.drawText(
            QRect(margin_left, base_top + title_height + line_spacing * 3, 400, line_spacing),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"发布日期：{config.app.release_date}",
        )
        # 欢迎
        painter.setFont(self.font)
        painter.drawText(
            QRect(margin_left, base_top + title_height + line_spacing * 4, 400, line_spacing),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"欢迎使用 {config.app.name} - V{config.app.version}",
        )
