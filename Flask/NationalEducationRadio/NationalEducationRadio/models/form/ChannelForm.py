from flask.ext.wtf import Form

from wtforms import StringField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from NationalEducationRadio.models.db.Category import Category

class ChannelForm(Form):
    """
    廣播節目表單
    """
    channel_id = HiddenField()
    channel_name = StringField(validators=[DataRequired(message="輸入欲新增之節目名稱")])
    channel_category = QuerySelectField(query_factory=lambda: Category.query.all())
    channel_memo = TextAreaField(validators=[DataRequired(message="請輸入節目簡介")])
