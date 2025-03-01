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
    QApplication,
)
from PySide6.QtCore import Qt

from module.common import generate_strong_password
from module.user_apis import change_password, edit_profile
from setting.global_variant import gcache


def set_change_password_ui(main_window: QMainWindow, content_widget: QWidget):
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
    form_container.setFixedSize(500, 300)  # 固定表单尺寸
    form_container.setStyleSheet(
        """
        background: rgba(0,0,0,0.2);
        border-radius: 12px;
    """
    )

    # 构建表单内容
    _build_password_form(main_window, form_container)

    # 添加到布局结构
    center_container.layout().addWidget(form_container)
    content_widget.layout().addWidget(center_container, 1)  # 使用stretch填充空间


def _build_password_form(main_window: QMainWindow, container: QWidget):
    """构建表单内容"""
    container.setLayout(QVBoxLayout())
    container.layout().setContentsMargins(40, 30, 40, 30)

    # 标题
    title = QLabel("修改用户密码")
    title.setStyleSheet("font-size: 18px; font-weight: 500; color: #fff; background:transparent;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.layout().addWidget(title)

    # 表单字段
    form_layout = QFormLayout()
    form_layout.setVerticalSpacing(25)
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

    # 联系电话
    main_window.org_password_edit = QLineEdit(placeholderText="请输入原密码", echoMode=QLineEdit.Password)
    main_window.org_password_edit.setFixedHeight(35)

    # 电子邮箱
    main_window.new_password_edit = QLineEdit(placeholderText="请输入新密码", echoMode=QLineEdit.Password)
    main_window.new_password_edit.setFixedHeight(35)

    label_phone = QLabel("原密码：")
    label_email = QLabel("新密码：")
    label_phone.setStyleSheet('background:transparent')
    label_email.setStyleSheet('background:transparent')

    # 添加表单行
    form_layout.addRow(label_phone, main_window.org_password_edit)
    form_layout.addRow(label_email, main_window.new_password_edit)

    # 按钮容器重构
    btn_container = QWidget()
    btn_container.setLayout(QHBoxLayout())
    btn_container.layout().setContentsMargins(0, 20, 0, 0)
    btn_container.layout().setSpacing(20)  # 增加按钮间距

    # 生成强密码按钮
    generate_btn = QPushButton("生成强密码")
    generate_btn.setFixedSize(150, 40)
    generate_btn.setStyleSheet(
        """
        QPushButton {
            background: rgba(0, 180, 120, 0.8);
            color: white;
            border-radius: 12px;
            font-size: 14px;
        }
        QPushButton:hover { background: #67c23a; }
        """
    )

    generate_btn.clicked.connect(lambda: (handel_set_strong_password(main_window)))

    # 提交按钮（保持原有样式）
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
    submit_btn.clicked.connect(lambda: handle_change_password(main_window))

    # 布局调整
    btn_container.layout().addStretch(1)
    btn_container.layout().addWidget(generate_btn)
    btn_container.layout().addWidget(submit_btn)
    btn_container.layout().addStretch(1)
    btn_container.setStyleSheet("background: transparent")

    # 整体布局结构
    container.layout().addSpacing(20)
    container.layout().addLayout(form_layout)
    container.layout().addWidget(btn_container)
    container.layout().addStretch(1)


def handel_set_strong_password(main_window: QMainWindow):
    password = generate_strong_password()
    main_window.new_password_edit.setText(password)
    clipboard = QApplication.clipboard()
    clipboard.setText(password)
    QMessageBox.information(main_window, '提示', "密码已生成并复制到剪贴板")


def handle_change_password(main_window: QMainWindow):
    """处理密码修改提交"""
    org_password = main_window.org_password_edit.text().strip()
    new_password = main_window.new_password_edit.text().strip()
    if not all((org_password, new_password)):
        QMessageBox.warning(main_window, "错误", "原密码和新密码不能为空")
        return

    try:
        params = {'org_password': org_password, 'new_password': new_password}
        is_success, (title, message) = change_password(gcache.current_user['username'], params)
        if is_success:
            QMessageBox.information(main_window, "成功", "修改成功, 请重新登录")
            main_window.logout()
        else:
            QMessageBox.warning(main_window, title, message)
    except Exception as e:
        QMessageBox.critical(main_window, "操作失败", f"更新过程中发生错误：{str(e)}")
