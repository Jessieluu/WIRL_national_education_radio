from NationalEducationRadio.service import db


class TimeHotPlay(db.Model):
    """TimeHotPlay ORM

    熱門節目

    Attributes
        audio_id: 音檔ID
        count: 播放次數
        time_zone: 播放時段
    """

    __tablename__ = "time_hot_play"
    # audio_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    audio_id = db.Column(db.Integer)
    count = db.Column(db.Integer)
    time_zone = db.Column(db.Text(collation='utf8_unicode_ci'))



def __repr__(self):
        return self.audio_id
