from NationalEducationRadio.service import db


class PlayLog(db.Model):
    """PlayLog ORM

    播放音檔的紀錄。

    Attributes
        play_log_id: 流水號
        audio: 音檔
        user: 使用者
        star_time: 進入音檔的時間
        end_time: 離開音檔的時間
    """

    __tablename__ = "play_logs"
    play_log_id = db.Column(db.Integer, primary_key=True)
   # audio = db.Column(db.Integer, db.ForeignKey("audio.audio_id"))
   # user = db.Column(db.Integer, db.ForeignKey("users.id"))
    audio = db.Column(db.Integer)
    user = db.Column(db.Integer)
    star_time = db.Column(db.Text(collation='utf8_unicode_ci'))
    end_time = db.Column(db.Text(collation='utf8_unicode_ci'))

    def __repr__(self):
        return self.play_log_id
