from NationalEducationRadio.service import db


class OperationLog(db.Model):
    """OperationLog ORM

    播放音檔時的操作記錄。

    Attributes
        operation_log_id: 流水號
        play_log: 播放音檔的紀錄
        operation_code: 操作代碼
        operation_value: 操作內容
        timestamp: 操作時間

    """

    __tablename__ = "operation_logs"
    operation_log_id = db.Column(db.Integer, primary_key=True)
    play_log = db.Column(db.Integer, db.ForeignKey("play_logs.play_log_id"))
    operation_code = db.Column(db.Integer)
    operation_value = db.Column(db.String(64, collation='utf8_unicode_ci'))
    timestamp = db.Column(db.Text(collation='utf8_unicode_ci'))

    def __repr__(self):
        return self.keyword

class OperationCode:
    """操作代碼

    PLAY_PAUSE: 播放/暫停按鈕
    GO_NEXT_AUDIO: 前往下一個音檔的ID
    SEEK_BAR: 音檔移動時間
    ACTIVE_MODE: 互動模式切換

    """
    PLAY_PAUSE = 0x01
    GO_NEXT_AUDIO = 0x02
    SEEK_BAR = 0x04
    ACTIVE_MODE = 0x08