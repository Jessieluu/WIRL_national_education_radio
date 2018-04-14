from NationalEducationRadio.service import db


class Channel(db.Model):
    """Channel ORM

    廣播節目的資料表。

    Attributes
        channel_id: 流水號
        channel_category : 連結到category的category.category_id
        channel_name : 節目的名稱
        channel_memo : 節目的說明

    """

    __tablename__ = "channel"
    channel_id = db.Column(db.Integer, primary_key=True)
    channel_category = db.Column(db.Integer, db.ForeignKey("category.category_id"))
    channel_name = db.Column(db.String(64, collation='utf8_unicode_ci'))
    channel_memo = db.Column(db.Text(collation='utf8_unicode_ci'))

    audios = db.relationship('Audio', backref='channel')

    def __repr__(self):
        return self.channel_name
