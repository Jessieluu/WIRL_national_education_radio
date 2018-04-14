from NationalEducationRadio.service import db


class KeywordsTable(db.Model):
    """PlayLog ORM

    關鍵字總表。

    Attributes
        keywords: 流水號
        keyword1: 左邊關鍵字
        keyword2: 右邊關鍵字
        count: 總計
    """

    __tablename__ = "keywords_table"
    keywords_id = db.Column(db.Integer, primary_key=True)
    keyword1 = db.Column(db.String(255, collation='utf8_unicode_ci'))
    keyword2 = db.Column(db.String(255, collation='utf8_unicode_ci'))
    count = db.Column(db.Integer)

    def __repr__(self):
        return self.play_log_id
