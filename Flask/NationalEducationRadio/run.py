# -*- coding: utf-8 -*-
import sys

from flask.ext.login import current_user
from flask_wtf.csrf import CsrfProtect

from NationalEducationRadio.service import app, db, login_manager, get_blueprint
from NationalEducationRadio.models.db.User import User, AccessLevel
from migration import create_data

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

login_manager.init_app(app)
CsrfProtect(app)


@app.context_processor
def context_processor():
    return dict(current_user=current_user, AccessLevel=AccessLevel)

app.register_blueprint(get_blueprint('admin'), url_prefix='/admin')
app.register_blueprint(get_blueprint('radio'), url_prefix='/radio')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'create_db':
            if len(sys.argv) > 2 and sys.argv[2] == 'drop':
                db.drop_all()
                print("Droped.")
            db.create_all()
            print("Done.")
        if sys.argv[1] == 'create_data':
            create_data()
            print("Done.")

    else:
        app.run(host='0.0.0.0', debug=True, threaded=True)
