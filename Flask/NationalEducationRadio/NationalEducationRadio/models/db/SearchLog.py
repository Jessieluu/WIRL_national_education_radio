from NationalEducationRadio.service import db


class SearchLog(db.Model):
    """SearchLog ORM

    搜尋紀錄

    Attributes
        search_id: 流水號
        audio: 音檔
        user: 使用者
        star_time: 進入音檔的時間
        end_time: 離開音檔的時間
    """

    __tablename__ = "search_logs"
    search_id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("users.id"))
    search_text = db.Column(db.String(64, collation='utf8_unicode_ci'))

    def __repr__(self):
        return self.search_text
