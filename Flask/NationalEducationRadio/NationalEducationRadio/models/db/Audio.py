from NationalEducationRadio.service import db


class Audio(db.Model):
    """Audio ORM

    音檔的資料表。

    Attributes
        audio_id: 流水號
        audio_name: 名稱
        channel_id: 節目id
        audio_file: 檔案名稱
        audio_question: 題目資訊
        keyword: 儲存關鍵字，依照排序使用JSON格式
        raw_keyword : keyword
    """

    __tablename__ = "audio"
    audio_id = db.Column(db.Integer, primary_key=True)
    audio_name = db.Column(db.String(64, collation='utf8_unicode_ci'))
    audio_channel = db.Column(db.Integer, db.ForeignKey("channel.channel_id"))
    audio_file = db.Column(db.String(255, collation='utf8_unicode_ci'))
    audio_question = db.Column(db.Text(collation='utf8_unicode_ci'))
    keyword = db.Column(db.Text(collation='utf8_unicode_ci'))
    raw_keyword = db.Column(db.Text(collation='utf8_unicode_ci'))
    similar_audio = db.Column(db.Text(collation='utf8_unicode_ci'))

    records = db.relationship('Record', backref='audio')

    def __repr__(self):
        return self.audio_name

    @property
    def no(self):
        audios = Audio.query.filter_by(audio_channel=self.audio_channel).all()
        i = 0
        for audio in audios:
            i += 1
            if audio.audio_id == self.audio_id:
                return i
        return 0
