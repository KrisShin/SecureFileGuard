from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget

from interface.custom_widget import MyQLabelTip, PasswordToggleWidget
from module.common import handle_set_strong_password
from module.user_apis import change_password
from setting.global_variant import gcache


def set_change_password_ui(main_window: QMainWindow, content_widget: QWidget):
    """显示密码修改界面"""
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
    _build_password_form(main_window, form_container)

    # 添加到布局结构
    center_container.layout().addWidget(form_container)
    content_widget.layout().addWidget(center_container, 1)  # 使用stretch填充空间


def _build_password_form(main_window: QMainWindow, container: QWidget):
    """构建表单内容"""
    # 设置容器布局
    container.setLayout(QVBoxLayout())
    container.layout().setContentsMargins(40, 30, 40, 30)

    # 标题
    title = QLabel("修改用户密码")
    title.setStyleSheet("font-size: 18px; font-weight: 500; color: #fff; background:transparent;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    container.layout().addWidget(title)

    # 表单布局
    form_layout = QFormLayout()
    form_layout.setVerticalSpacing(25)
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

    # 原密码输入框
    main_window.org_password_edit = PasswordToggleWidget(
        placeholder='请输入原密码', style='height:35px;border-radius: 12px; background: rgba(0, 0, 0, 0.2);'
    )
    main_window.org_password_edit.setFixedHeight(35)

    # 新密码输入框
    main_window.new_password_edit = PasswordToggleWidget(
        placeholder='请输入新密码', style='height:35px;border-radius: 12px; background: rgba(0, 0, 0, 0.2);'
    )
    main_window.new_password_edit.setFixedHeight(35)

    # 设置标签背景透明
    label_phone = QLabel("原密码：")
    label_email = QLabel("新密码：")
    label_phone.setStyleSheet('background:transparent')
    label_email.setStyleSheet('background:transparent')

    # 添加表单行
    form_layout.addRow(label_phone, main_window.org_password_edit)
    form_layout.addRow(label_email, main_window.new_password_edit)

    # 按钮容器布局
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

    # 绑定生成强密码功能, 传入控件用于设置生成密码到控件中
    generate_btn.clicked.connect(lambda: (handle_set_strong_password(container, main_window.new_password_edit)))

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
    submit_btn.clicked.connect(lambda: handle_change_password(main_window, container))

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


def handle_change_password(main_window: QMainWindow, container: QWidget):
    """处理密码修改提交"""
    # 获取填入的原密码和新密码, 并去掉前后的空格
    org_password = main_window.org_password_edit.text().strip()
    new_password = main_window.new_password_edit.text().strip()

    if not all((org_password, new_password)):
        MyQLabelTip("原密码和新密码不能为空", container, False)
        return
    try:
        params = {'org_password': org_password, 'new_password': new_password}
        is_success, message = change_password(gcache.current_user['username'], params)
        if is_success:
            MyQLabelTip("修改成功, 请重新登录", container)
            # 修改密码成功之后触发退出登录
            main_window.logout()
        else:
            MyQLabelTip(message, container, is_success)
    except Exception as e:
        QMessageBox.critical(main_window, "操作失败", f"更新过程中发生错误：{str(e)}")
