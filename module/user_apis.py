import re
from module.common import get_password_hash, verify_password
from setting.global_variant import gcache
from db_data.manager import db


def validate_email(email: str) -> bool:
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)


def validate_phone(phone: str) -> bool:
    return re.match(r'^1[3-9]\d{9}$', phone)


def register(regist_data: dict) -> tuple:
    user_obj = db.get_user(regist_data['username'])
    if user_obj:
        return False, ("错误", "用户名已注册")

    if not all([regist_data['username'], regist_data['password']]):
        return False, ("错误", "用户名和密码必填")

    # 验证手机格式
    if regist_data['phone']:
        if not validate_phone(regist_data['phone']):
            return False, ("错误", "手机号格式不正确")

    # 验证邮箱格式
    if regist_data['email']:
        if not validate_email(regist_data['email']):
            return False, ("错误", "邮箱格式不正确")

    db.create_user(regist_data)
    return True, (None, None)


def login(username: str, password: str) -> tuple:
    """用户登录"""
    user_obj = db.get_user(username)
    if not user_obj:
        return False, ("错误", "用户名不存在, 请先注册")

    if verify_password(password, user_obj['password']):
        gcache.current_user = user_obj
        db.update_user_last_login(username)
        return True, (None, None)
    else:
        return False, ("错误", "密码错误")


def edit_profile(username: str, params: dict):
    email = params.get('email')
    if email:
        if not validate_email(params['email']):
            return False, ("错误", "邮箱格式不正确")
        if db.get_user_list({'email': email}):
            return False, ("错误", "该邮箱已注册")

    phone = params.get('phone')
    if phone:
        if not validate_phone(params['phone']):
            return False, ("错误", "手机号格式不正确")
        if db.get_user_list({'phone': phone}):
            return False, ("错误", "该手机号已注册")

    # 检查是否有修改其他的参数
    if set(params.keys()) - {'email', 'phone'}:
        return False, ("错误", "此内容暂时不允许修改")

    db.update_user_info(username, params)
    if gcache.current_user == username:
        user = gcache.current_user
        for key, val in params.items():
            user[key] = val
        gcache.current_user = user
    return True, (None, None)


def change_password(username: str, params: dict) -> tuple:
    """修改用户密码"""

    user_obj = db.get_user(username)
    if not user_obj:
        return False, ("错误", "用户名不存在, 请先注册")
    
    if verify_password(params['org_password'], user_obj['password']):
        password = get_password_hash(params['new_password'])
        db.update_user_info(username, {'password': password})
        return True, (None, None)
    else:
        return False, ("错误", "原密码错误")


