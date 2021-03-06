from flask.ext.wtf import Form
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class CaptionForm(Form):
    """
    傳送關鍵字用的表單

    """

    caption_id = HiddenField(validators=[DataRequired(message="不能沒有 ID ")])
    caption_content = StringField(widget=TextArea(), validators=[DataRequired(message="請匯入逐字稿")])
