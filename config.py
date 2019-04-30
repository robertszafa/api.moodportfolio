from flask import Flask, Blueprint
from flask_mysqldb import MySQL
from flask_restful import Api
from flask_cors import CORS
from mailjet_rest import Client



app = Flask(__name__, static_folder='../static/dist', template_folder='../static')
CORS(app)


# Config

# MYSQL
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'team40'
app.config['MYSQL_PASSWORD'] = 'Password12345!'
app.config['MYSQL_DB'] = 'moodportfolio'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

# EMAIL
api_key = '6d3e2eff8e6c4cb73ef8f7e0dfcfbe2f'
api_secret = 'a256c5bb0a86d1e99f5d18678e4649a9'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

api_bp = Blueprint('api', __name__)
api = Api(api_bp)
app.register_blueprint(api_bp)