from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QLabel,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Qt

from module.common import generate_strong_password
from module.custom_widget import PasswordToggleWidget
from module.user_apis import change_password
from setting.global_variant import gcache


def set_user_manage_ui(main_window: QMainWindow, content_widget: QWidget):
    """显示密码修改界面（居中版本）"""
    # 清空右侧区域
    if content_widget.layout():
        QWidget().setLayout(content_widget.layout())

    # 创建主容器
    content_widget.setLayout(QVBoxLayout())
    content_widget.layout().setContentsMargins(0, 0, 0, 0)

    # 添加居中容器
    center_container = QWidget()
    center_container.setMinimumSize(600, 400)  # 设置最小显示区域
    center_container.setLayout(QVBoxLayout())
    center_container.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)

    # 创建表单容器（带固定高度）
    form_container = QWidget()
    form_container.setStyleSheet(
        """
        background: rgba(0,0,0,0.2);
        border-radius: 12px;
    """
    )

    # 构建表单内容
    _build_user_table(main_window, form_container)

    # 添加到布局结构
    center_container.layout().addWidget(form_container)
    content_widget.layout().addWidget(center_container, 1)  # 使用stretch填充空间


def _build_user_table(main_window: QMainWindow, container: QWidget):
    """构建用户管理页面"""
    container.setLayout(QVBoxLayout())
    container.layout().setContentsMargins(40, 30, 40, 30)

    # 标题
    title = QLabel("用户管理")
    title.setStyleSheet("font-size: 18px; font-weight: 500; color: #fff; background:transparent;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.layout().addWidget(title)
    # 搜索栏布局
    search_layout = QHBoxLayout()
    search_layout.setContentsMargins(0, 0, 0, 20)
    search_input = QLineEdit()
    search_input.setPlaceholderText("输入用户名或手机号搜索...")
    search_input.setStyleSheet(
        """
        QLineEdit {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: #fff;
        }
    """
    )
    search_btn = QPushButton("搜索")
    search_btn.setStyleSheet(
        """
        QPushButton {
            background: #409EFF;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
        }
        QPushButton:hover { background: #66b1ff; }
    """
    )
    search_layout.addWidget(search_input)
    search_layout.addWidget(search_btn, 0, Qt.AlignmentFlag.AlignRight)

    # 表格
    table = QTableWidget()
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(["用户名", "手机号", "邮箱", "上次登录时间", "操作"])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setStyleSheet(
        """
        QTableWidget {
            background: white;
            border: none;
            border-radius: 4px;
        }
        QHeaderView::section {
            background: #f5f7fa;
            color: #606266;
            padding: 8px;
        }
        QTableWidget::item {
            color: #303133;
            border-bottom: 1px solid #ebeef5;
        }
    """
    )
    table.setRowHeight(0, 48)  # 设置行高

    # 添加测试数据
    for i in range(2):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(f"user_{i+1}"))
        table.setItem(row, 1, QTableWidgetItem(f"1380013800{i}"))
        table.setItem(row, 2, QTableWidgetItem(f"user{i}@example.com"))
        table.setItem(row, 3, QTableWidgetItem("2024-02-20 14:30:00"))

        # 删除按钮
        btn = QPushButton("删除")
        btn.setStyleSheet(
            """
            QPushButton {
                background: #f56c6c;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover { background: #ff7875; }
        """
        )
        btn.clicked.connect(lambda _, r=row: _handle_delete_user(r))
        table.setCellWidget(row, 4, btn)

    # 组装布局
    container.layout().addSpacing(20)
    container.layout().addLayout(search_layout)
    container.layout().addWidget(table)
    container.layout().addStretch(1)


def _handle_delete_user(row: int):
    """处理删除用户操作"""
    # 这里应该添加实际的删除逻辑，如数据库操作等
    print(f"删除第 {row} 行用户")  # 示例打印
