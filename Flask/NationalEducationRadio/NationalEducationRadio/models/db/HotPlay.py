from NationalEducationRadio.service import db


class HotPlay(db.Model):
    """HotPlay ORM

    熱門節目

    Attributes
        audio_id: 音檔ID
        count: 播放次數
    """

    __tablename__ = "hot_play"
    audio_id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    

    def __repr__(self):
        return self.audio_id
