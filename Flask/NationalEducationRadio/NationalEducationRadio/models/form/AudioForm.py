from flask.ext.wtf import Form

from wtforms import StringField, FileField, SelectField, HiddenField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from NationalEducationRadio.models.db.Channel import Channel

class AudioForm(Form):
    """
    音檔表單
    """
    audio_id = HiddenField()
    audio_name = StringField(validators=[DataRequired(message="輸入欲新增之音檔名稱")])
    audio_channel = HiddenField()
    audio_file = FileField(validators=[DataRequired(message="請選擇上傳音檔")])
    audio_question = FileField(validators=[DataRequired(message="請選擇上傳題目CSV")])

    def uncheckFileUpload(self):
    	self.audio_file.validators = []
    	self.audio_question.validators = []