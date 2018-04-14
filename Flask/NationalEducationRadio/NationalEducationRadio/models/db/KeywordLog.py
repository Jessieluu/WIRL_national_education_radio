from NationalEducationRadio.service import db


class KeywordLog(db.Model):
    """KeywordLog ORM

    儲存關鍵字紀錄。

    Attributes
        keyword_log_id: 流水號
        user: 使用者
        keyword: 搜尋的關鍵字

    """

    __tablename__ = "keyword_logs"
    keyword_log_id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("users.id"))
    keyword = db.Column(db.String(64, collation='utf8_unicode_ci'))

    def __repr__(self):
        return self.keyword_log_id
