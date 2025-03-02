from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QLabel,
)
from PySide6.QtCore import Qt

from module.user_apis import edit_profile
from setting.global_variant import gcache


def set_edit_profile_ui(main_window: QMainWindow, content_widget: QWidget):
    """显示编辑信息界面（居中版本）"""
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
    _build_profile_form(main_window, form_container)

    # 添加到布局结构
    center_container.layout().addWidget(form_container)
    content_widget.layout().addWidget(center_container, 1)  # 使用stretch填充空间


def _build_profile_form(main_window: QMainWindow, container: QWidget):
    """构建表单内容"""
    container.setLayout(QVBoxLayout())
    container.layout().setContentsMargins(40, 30, 40, 30)

    # 标题
    title = QLabel("编辑用户信息")
    title.setStyleSheet("font-size: 18px; font-weight: 500; color: #fff; background:transparent;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.layout().addWidget(title)

    # 表单字段
    form_layout = QFormLayout()
    form_layout.setVerticalSpacing(25)
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

    # 联系电话
    main_window.new_phone_edit = QLineEdit()
    if gcache.current_user and gcache.current_user['phone']:
        main_window.new_phone_edit.setText(gcache.current_user['phone'])
    main_window.new_phone_edit.setPlaceholderText("请输入11位手机号")
    main_window.new_phone_edit.setFixedHeight(35)

    # 电子邮箱
    main_window.new_email_edit = QLineEdit()
    if gcache.current_user and gcache.current_user['email']:
        main_window.new_email_edit.setText(gcache.current_user['email'])
    main_window.new_email_edit.setPlaceholderText("输入有效邮箱地址")
    main_window.new_email_edit.setFixedHeight(35)

    label_phone = QLabel("联系电话：")
    label_email = QLabel("电子邮箱：")
    label_phone.setStyleSheet('background:transparent')
    label_email.setStyleSheet('background:transparent')

    # 添加表单行
    form_layout.addRow(label_phone, main_window.new_phone_edit)
    form_layout.addRow(label_email, main_window.new_email_edit)

    # 按钮容器
    btn_container = QWidget()
    btn_container.setLayout(QHBoxLayout())
    btn_container.layout().setContentsMargins(0, 20, 0, 0)

    # 提交按钮
    submit_btn = QPushButton("提交修改")
    submit_btn.setFixedSize(150, 40)
    submit_btn.setStyleSheet(
        """
        QPushButton {
            background: rgba(0,20,200, 0.8);
            color: white;
            border-radius: 12px;
            font-size: 14px;
        }
        QPushButton:hover { background: #66b1ff; }
    """
    )
    submit_btn.clicked.connect(lambda: handle_edit_profile(main_window))

    # 布局组装
    btn_container.layout().addStretch(1)
    btn_container.layout().addWidget(submit_btn)
    btn_container.layout().addStretch(1)
    btn_container.setStyleSheet("background: transparent")

    # 整体布局结构
    container.layout().addSpacing(20)
    container.layout().addLayout(form_layout)
    container.layout().addWidget(btn_container)
    container.layout().addStretch(1)


def handle_edit_profile(main_window: QMainWindow):
    """处理编辑信息提交"""
    new_phone = main_window.new_phone_edit.text().strip()
    new_email = main_window.new_email_edit.text().strip()

    # 更新用户信息（示例逻辑）
    try:
        # 这里应该添加实际的数据库更新操作
        params = {}
        if new_phone and new_phone != gcache.current_user['phone']:
            params['phone'] = new_phone
        if new_email and new_email != gcache.current_user['email']:
            params['email'] = new_email
        if params:
            is_success, (title, message) = edit_profile(gcache.current_user['username'], params)
            if is_success:
                QMessageBox.information(main_window, "成功", "修改成功")
            else:
                QMessageBox.warning(main_window, title, message)
    except Exception as e:
        QMessageBox.critical(main_window, "操作失败", f"更新过程中发生错误：{str(e)}")
