from NationalEducationRadio.service import db

class Record(db.Model):
    """Audio ORM

    音檔的資料表。

    Attributes
        audio_id: 流水號
        audio_name: 名稱
        channel_id: 節目id
        audio_file: 檔案名稱
        audio_question: 題目資訊

    """

    __tablename__ = "records"
    record_id = db.Column(db.Integer, primary_key=True)
    audio_id = db.Column(db.Integer, db.ForeignKey("audio.audio_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    record_data = db.Column(db.Text(collation='utf8_unicode_ci'))

    def __repr__(self):
        return self.audio.audio_name
