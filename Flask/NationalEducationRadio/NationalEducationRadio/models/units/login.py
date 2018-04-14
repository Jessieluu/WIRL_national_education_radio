from flask import redirect, url_for, session
from functools import wraps
from NationalEducationRadio.models.db.User import AccessLevel


def permission_required(permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            """
            使用and判斷權限
            """
            if int(session['level']) & permissions > 0:
                return f(*args, **kwargs)
            elif session.get('level') & AccessLevel.USER > 0:
                return redirect(url_for('admin.page'))
            else:
                return redirect(url_for('radio.login'))
        return decorated_function
    return decorator


def admin_required(f):
    """
    系統管理者權限
    :param f: 下一個函數
    :return: 繼續執行函數或是轉址
    """
    return permission_required(AccessLevel.ADMIN_USER)(f)


def user_required(f):
    """
    使用者權限
    :param f: 下一個函數
    :return: 繼續執行函數或是轉址
    """
    return permission_required(AccessLevel.USER)(f)



def backstage_required(f):
    """
    後台權限
    :param f: 下一個函數
    :return: 繼續執行函數或是轉址
    """
    return permission_required(AccessLevel.ADMIN_USER)(f)
