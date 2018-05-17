from NationalEducationRadio.service import db


class SearchSelectedLog(db.Model):
    """SearchSelectedLog ORM

    搜尋後選擇音檔紀錄

    Attributes
        search_selected_id: 流水號
        search_id:搜尋ID
        audio: 音檔
    """

    __tablename__ = "search_selected_logs"
    search_selected_id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer)
    audio = db.Column(db.Integer)

    def __repr__(self):
        return self.search_selected_id
