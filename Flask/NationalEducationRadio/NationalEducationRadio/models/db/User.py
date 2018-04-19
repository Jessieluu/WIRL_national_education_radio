from NationalEducationRadio.service import db


class User(db.Model):
    """User ORM

    題目的資料表。

    Attributes
        id: 流水號
        company_id: 連結到Company的Company.id
        password: 使用者的密碼(sha256)
        roc_id: 身份證字號
        work_id: 工號
        account: 使用者帳號
        name: 使用者姓名
        company: 相應的Company
        level: 回傳使用者的權限
        scores: 相應的Score
        is_anonymous: 只是用來判斷是否登入了？

    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(64, collation='utf8_unicode_ci'))
    account = db.Column(db.String(64, collation='utf8_unicode_ci'))
    operation_ranks = db.Column(db.String(64, collation='utf8_unicode_ci'))
    name = db.Column(db.String(64, collation='utf8_unicode_ci'))
    FBuserID = db.Column(db.String(255))
    FBAccessToken = db.Column(db.String(255))
    GOOGLEuserID = db.Column(db.String(255))
    level = db.Column(db.SmallInteger)
    most_use_time = db.Column(db.String(64, collation='utf8_unicode_ci'), default="evening")

    is_anonymous = False

    records = db.relationship('Record', backref='user')

    def get_id(self):
        return self.id

    def set_access_level(self, level):
        if level is AccessLevel:
            self.level = self.level | level

    def unset_access_level(self, level):
        if level is AccessLevel:
            self.level = self.level ^ level

    def check_access_level(self, level):
        if self.level & level > 0:
            return True
        return False

    def __repr__(self):
        return '<User %r>' % self.name

    def chinese_level(self):
        """回傳使用者的權限（文字）"""
        if self.level == AccessLevel.ADMIN_USER:
            return '系統管理者'
        else:
            return '使用者'

    @property
    def serialize(self):
        """
        回傳給jqgrid
        """
        level = self.chinese_level()
        return {
            "id":       self.id,
            "account":  self.account,
            "name":     self.name,
            "password": '*' * 24,
            "level":    level
        }

    @staticmethod
    def is_active():
        """
        WTF
        """
        return True

    @staticmethod
    def is_authenticated():
        """
        WTF
        """
        return True


class AccessLevel:
    """使用者權限表

    USER: 一般使用者
    ADMIN_USER: 所有權限。

    """
    USER = 0x00
    ADMIN_USER = 0x01
