import os
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QApplication,
    QFileDialog,
    QInputDialog,
)

from interface.custom_widget import MyQLabelTip
from module.file_apis import delete_file, download_file, get_file_list, varify_file_password
from setting.config_loader import config
from setting.global_variant import DELIMITER, gcache


def set_file_list_ui(main_window: QMainWindow, content_widget: QWidget):
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
    _build_file_list_table(main_window, form_container)

    # 添加到布局结构
    center_container.layout().addWidget(form_container)
    content_widget.layout().addWidget(center_container, 1)  # 使用stretch填充空间


def _build_file_list_table(main_window: QMainWindow, container: QWidget):
    """构建用户管理页面"""
    container.setLayout(QVBoxLayout())
    container.layout().setContentsMargins(40, 30, 40, 30)

    # 标题
    title = QLabel("文件管理")
    title.setStyleSheet("font-size: 18px; font-weight: 500; color: #fff; background:transparent;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.layout().addWidget(title)
    # 搜索栏布局
    search_layout = QHBoxLayout()
    search_layout.setContentsMargins(0, 0, 0, 20)
    search_input = QLineEdit()
    search_input.setPlaceholderText("输入文件名搜索...")
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
    container.table.setHorizontalHeaderLabels(["序号", "文件名", "加密算法", "上传用户", "修改时间", "操作"])
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


def load_table_data(container: QWidget, query: str = ''):
    file_list = get_file_list(gcache.current_user, query)
    MyQLabelTip(f"查询完成, 共{len(file_list)}条数据!", container)
    container.file_list = file_list
    container.query = query
    container.table.setRowCount(0)
    table = container.table
    for index, file in enumerate(file_list):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(str(index + 1)))
        table.setItem(row, 1, QTableWidgetItem(file['file_name']))
        table.setItem(row, 2, QTableWidgetItem(file['algorithm']))
        table.setItem(row, 3, QTableWidgetItem(file['user_name']))
        table.setItem(row, 4, QTableWidgetItem(file['modified_at']))

        option_widget = QWidget()
        option_widget.setStyleSheet("""background: transparent;""")
        button_layout = QHBoxLayout(option_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)  # 消除布局边距
        button_layout.setSpacing(4)  # 设置按钮间距为4px

        # 下载按钮（第5列）
        btn_download = create_download_button(container, file)

        # 删除按钮（第6列）
        btn_delete = create_delete_button(container, file)

        button_layout.addWidget(btn_download)
        button_layout.addWidget(btn_delete)
        # 管理员密码复制按钮（第7列）
        if gcache.current_user['role'] == 'admin':
            btn_copy = create_copy_button(container, file)
            button_layout.addWidget(btn_copy)
        container.table.setCellWidget(row, 5, option_widget)


def create_download_button(container, file):
    """创建下载按钮"""
    btn = QPushButton("下载")
    btn.setStyleSheet(
        """
        QPushButton {
            background: #409eff;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            border: none;
        }
        QPushButton:hover { background: #66b1ff; }
    """
    )
    btn.clicked.connect(lambda: _handle_download(container, file))
    return btn


def create_delete_button(container, file):
    """创建删除按钮"""
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
    btn.clicked.connect(lambda: _handle_delete(container, file))
    return btn


def create_copy_button(container, file):
    """创建复制密码按钮（仅管理员）"""
    btn = QPushButton("复制密码")
    btn.setStyleSheet(
        """
        QPushButton {
            background: #67c23a;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            border: none;
        }
        QPushButton:hover { background: #85ce61; }
    """
    )
    btn.clicked.connect(lambda: (QApplication.clipboard().setText(file['password'].replace(DELIMITER, '')), MyQLabelTip('复制密码成功', container)))
    return btn


def _handle_download(container, file):
    """处理下载操作"""
    if gcache.current_user['role'] == 'admin':
        path, _ = QFileDialog.getSaveFileName(container, "保存文件", os.path.join(config.path.download, file['file_name']), "All Files (*)")

        if path:
            is_success, msg = download_file(file, file['password'].replace(DELIMITER, ''), Path(path))
            MyQLabelTip(msg, container, is_success)
        else:
            MyQLabelTip("无效下载路径, 请确认", container)
        return
    # 输入密码对话框
    dialog = QInputDialog(container)  # container 作为父组件
    dialog.setWindowTitle("文件密码")
    dialog.setLabelText("请输入文件密码解密下载：")
    dialog.setTextEchoMode(QLineEdit.Password)

    # 关键配置：必须在调用 exec() 前设置按钮文本
    dialog.setOkButtonText("确认")
    dialog.setCancelButtonText("取消")

    password = ''
    # 显示对话框并获取结果
    if dialog.exec() == QInputDialog.DialogCode.Accepted:
        password = dialog.textValue()

    if password:
        # 选择保存路径
        is_password_correct, msg = varify_file_password(file, password)
        if is_password_correct:
            path, _ = QFileDialog.getSaveFileName(container, "保存文件", os.path.join(config.path.download, file['file_name']), "All Files (*)")

            if path:
                is_success, msg = download_file(file, password, Path(path))
                MyQLabelTip(msg, container, is_success)
                return
            else:
                MyQLabelTip("无效下载路径, 请确认", container)
                return
        MyQLabelTip("密码错误", container, False)


def _handle_delete(container, file):
    """处理删除操作"""
    if gcache.current_user['role'] == 'admin':
        is_success, msg = delete_file(gcache.current_user, file)
        if is_success:
            load_table_data(container, container.query)
        else:
            MyQLabelTip(msg, container)
        return
    # 验证密码对话框
    dialog = QInputDialog(container)  # container 作为父组件
    dialog.setWindowTitle("删除确认")
    dialog.setLabelText("请输入密码确认删除：")
    dialog.setTextEchoMode(QLineEdit.Password)

    # 关键配置：必须在调用 exec() 前设置按钮文本
    dialog.setOkButtonText("确认")
    dialog.setCancelButtonText("取消")

    password = ''
    # 显示对话框并获取结果
    if dialog.exec() == QInputDialog.DialogCode.Accepted:
        password = dialog.textValue()

    if password:
        # 验证密码（需要实现实际验证方法）
        is_password_correct, msg = varify_file_password(file, password)
        if is_password_correct:
            # 执行删除逻辑
            is_success, msg = delete_file(gcache.current_user, file)
            if is_success:
                load_table_data(container, container.query)
            MyQLabelTip(msg, container, is_success)
            return
        MyQLabelTip(msg, container, is_password_correct)
        return
    MyQLabelTip('请输入密码', container, False)
