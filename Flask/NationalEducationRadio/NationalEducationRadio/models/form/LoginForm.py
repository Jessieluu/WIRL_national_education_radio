from flask.ext.wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(Form):
    """
    登入表單

    這邊的命名有點問題，name指得應該是使用者註冊的自定義名稱
    name -> account 才對 
    """

    account = StringField(validators=[DataRequired(message="請輸入你的帳號。")])
    password = PasswordField(validators=[DataRequired(message="請輸入你的密碼。")])
