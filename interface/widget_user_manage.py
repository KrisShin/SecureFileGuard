from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from interface.custom_widget import MyQLabelTip
from module.user_apis import delete_user, get_user_list
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
    search_input.setPlaceholderText("输入用户名或手机号或邮箱搜索...")
    search_input.setStyleSheet(
        """
        QLineEdit {
            padding: 8px 12px;
            border-radius: 4px;
            background: rgba(0,0,0,0.4);
        }
    """
    )
    search_btn = QPushButton("搜索")
    search_btn.setStyleSheet(
        """
        QPushButton {
            background: #409EFF44;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
        }
        QPushButton:hover { background: #66b1ff; }
    """
    )
    search_btn.clicked.connect(lambda: load_table_data(container, search_input.text()))
    search_layout.addWidget(search_input)
    search_layout.addWidget(search_btn, 0, Qt.AlignmentFlag.AlignRight)

    # 表格
    container.table = QTableWidget()
    container.table.setColumnCount(6)
    container.table.setHorizontalHeaderLabels(["序号", "用户名", "手机号", "邮箱", "上次登录时间", "操作"])
    container.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    container.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    container.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
    container.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
    container.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
    container.table.verticalHeader().setVisible(False)
    container.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    container.table.setStyleSheet(
        """
        QTableWidget {
            background: rgba(0,0,0,0.6);
            # border: 1px solid #ebeef5;
            border-radius: 4px;
        }
        QHeaderView::section {
            background: rgba(0,0,0,0.4);
            color: #ccc;
            padding: 8px;
        }
        QTableWidget::item {
            color: #ddd;
            border-bottom: 1px solid #ebeef5;
        }
    """
    )
    container.table.setRowHeight(0, 48)  # 设置行高
    container.table.setFixedHeight(400)
    load_table_data(container)

    # 组装布局
    container.layout().addSpacing(20)
    container.layout().addLayout(search_layout)
    container.layout().addWidget(container.table)
    container.layout().addStretch(1)


def _handle_delete_user(container: QWidget, row_index: int):
    """处理删除用户操作"""
    delete_user(gcache.current_user, container.user_list[row_index]['username'])
    load_table_data(container, container.query)


def load_table_data(container: QWidget, query: str = ''):
    user_list = get_user_list(gcache.current_user, query)
    MyQLabelTip(f"查询完成, 共{len(user_list)}条数据!", container)
    container.user_list = user_list
    container.query = query
    container.table.setRowCount(0)
    table = container.table
    for index, user in enumerate(user_list):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(str(index + 1)))
        table.setItem(row, 1, QTableWidgetItem(user['username']))
        table.setItem(row, 2, QTableWidgetItem(user['phone']))
        table.setItem(row, 3, QTableWidgetItem(user['email']))
        table.setItem(row, 4, QTableWidgetItem(user['last_login']))

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
        btn.clicked.connect(lambda _, r=row: _handle_delete_user(container, r))
        if user['role'] == 'user':
            table.setCellWidget(row, 5, btn)
