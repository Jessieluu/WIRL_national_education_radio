from NationalEducationRadio.service import db


class Category(db.Model):
    """category ORM

    分類的資料表。

    Attributes
        category_id: 流水號
        category_name : 分類的名稱

    """

    __tablename__ = "category"
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(64, collation='utf8_unicode_ci'))

    channels = db.relationship('Channel', backref='category')

    def __repr__(self):
        return self.category_name