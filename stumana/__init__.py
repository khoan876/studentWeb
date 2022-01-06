from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babelex import Babel

app = Flask(__name__)
app.secret_key = 'osdoskdskods!@#dokko2o1ko1k2- 1-_!_!$(@$_!$!$)$!s'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456789@localhost/mystumana?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'

db = SQLAlchemy(app=app)

login = LoginManager(app=app)

babel = Babel(app=app)


@babel.localeselector
def get_locale():
    # Put your logic here. Application can store locale in
    # user profile, cookie, session, etc.
    return 'vi'



