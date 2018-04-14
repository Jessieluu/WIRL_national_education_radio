from flask import Flask, Blueprint
from flask.ext.sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://root:wiki1424@localhost/national_education_radio'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '908a561008fd5f88a3a86e20add4ab3f'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['GOOGLE_ID'] = "559429341471-ng1iicn7jj2uhe1uq9tu439jovo1kr87.apps.googleusercontent.com"
app.config['GOOGLE_SECRET'] = "vxt6PjEYgspP1lQHvZ6JDJLb"
app.debug = True
app.secret_key = 'development'


db = SQLAlchemy(app)

blueprint = {'radio': Blueprint('radio', __name__),
             'admin': Blueprint('admin', __name__)}
             
def get_blueprint(key):
    return blueprint[key]

login_manager = LoginManager()
login_manager.login_view = 'radio.login'
